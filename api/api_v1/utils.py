# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import re
import operator
import functools
import json
from constance import config
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils.crypto import get_random_string

from atendimento.atendimento.models import Defensor as AtendimentoDefensor, FormaAtendimento, Pessoa
from contrib.models import Comarca, Defensoria, Servidor
from defensor.models import Atuacao
from assistido.models import PessoaAssistida
from evento.models import Agenda
from procapi_client.services import APIProcesso
from processo.processo.models import Processo, Parte

TIPOS_ATENDIMENTO_VALIDOS_PARA_AGENDAMENTO_RETORNO = (
    AtendimentoDefensor.TIPO_INICIAL,
    AtendimentoDefensor.TIPO_RETORNO,
    AtendimentoDefensor.TIPO_ENCAMINHAMENTO
)

RE_CARACTERES_NUMERICOS = re.compile(r'[^0-9]')


def get_atendimento_inicial(numero):
    try:
        atendimento = AtendimentoDefensor.objects.get(
            numero=numero
        )
        if atendimento.inicial:
            at_inicial = atendimento.inicial
        else:
            at_inicial = atendimento
    except AtendimentoDefensor.DoesNotExist:
        return None

    return at_inicial


def get_numero_atendimento_inicial(numero):
    atendimento = get_atendimento_inicial(numero)

    if atendimento.inicial_id:
        numero_at_inicial = atendimento.inicial.numero
    else:
        numero_at_inicial = atendimento.numero
    return numero_at_inicial


def get_ultimo_atendimento(numero_at_inicial):
    q = Q()
    q &= Q(ativo=True)
    q &= Q(remarcado=None)
    q &= Q(excluido_por=None)
    q &= Q(tipo__in=TIPOS_ATENDIMENTO_VALIDOS_PARA_AGENDAMENTO_RETORNO)
    q &= functools.reduce(operator.or_,
                          [(Q(inicial=None) & Q(numero=numero_at_inicial)), Q(inicial__numero=numero_at_inicial)])

    atendimento = AtendimentoDefensor.objects.order_by(
        '-data_agendamento',
        '-data_cadastro'
    ).only(
        'id',
        'defensoria_id',
        'inicial',
        'remarcado',
        'tipo',
        'numero',
        'data_agendamento',
        'data_atendimento'
    ).filter(q).first()

    return atendimento


def criar_agendamento(atendimento_numero, pessoas_assistidas_ids, qualificacao_id, anotacao, agenda_id=None,
                      data_agendamento=None, comarca_id=None, defensoria_id=None, categoria_agenda=None,
                      usuario_criador=None, defensor_titular_id=None, defensor_substituto_id=None,
                      processo_numero=None, commit=True, atendimento_tipo_ligacao=True, request=None):

    agenda = None
    forma_atendimento = None

    # recupera dados do usuário
    servidor_criador_id = Servidor.objects.filter(usuario=usuario_criador).values_list('id', flat=True).first()

    # valores padrão
    at_inicial = None
    at_tipo = AtendimentoDefensor.TIPO_INICIAL
    pessoa_assistida_id = pessoas_assistidas_ids[0]
    processo_procapi = None
    ultimo_atendimento = None

    # verifica se foi passado a agenda ou a defensoria
    if agenda_id is None and defensoria_id is None and comarca_id is None:
        raise ValidationError(u'Informe o ID da agenda, defensoria ou comarca')

    # se número do processo foi informado, valida existência com ProcAPI
    if processo_numero is not None:

        sucesso, resposta = APIProcesso(processo_numero, request).consultar()

        if sucesso:
            processo_procapi = resposta
        else:
            raise ValidationError(u'O número do processo não pôde ser validado!')

    # se passou um número de atendimento, é um agendamento de retorno
    if atendimento_numero:

        # recupera dados do atendimento inicial
        at_inicial = get_atendimento_inicial(numero=atendimento_numero)
        at_tipo = AtendimentoDefensor.TIPO_RETORNO

        if not at_inicial:
            raise AtendimentoDefensor.DoesNotExist(u'Atendimento {} não existe!'.format(atendimento_numero))

        # valida se pessoa é um dos requerentes do atendimento
        if not PessoaAssistida.objects.ativos().filter(
            pk=pessoa_assistida_id,
            atendimentos__atendimento__numero=at_inicial.numero,
            atendimentos__ativo=True,
            atendimentos__tipo=Pessoa.TIPO_REQUERENTE
        ).exists():
            raise ValidationError(u'A pessoa não é um dos requerentes do atendimento informado!')

        # recupera dados do último atendimento da árvore
        ultimo_atendimento = get_ultimo_atendimento(at_inicial.numero)

        # valida se útlimo atendimento foi realizado
        if ultimo_atendimento.data_atendimento is None:
            raise ValidationError(u'Já existe um retorno marcado para este atendimento!')

        # recupera qualificação do último atendimento da árvore
        qualificacao_id = ultimo_atendimento.qualificacao_id

    elif qualificacao_id is None:
        raise ValidationError(u'É necessário informar uma qualificação para um agendamento inicial!')

    defensoria = None
    comarca = None
    atuacao = None
    defensor_id = defensor_titular_id
    substituto_id = defensor_substituto_id

    if agenda_id:

        # Agendamento com agenda definida: recupera dados da agenda
        # TODO: Verificar se horário da agenda ainda está disponível (AgendarView.verificar_disponibilidade_horario)

        if data_agendamento is None:
            raise ValidationError(u'A data/hora de agendamento deve ser informado em agendamento normal!')

        agenda = Agenda.objects.select_related('atuacao__defensor', 'atuacao__defensoria').get(id=agenda_id)
        defensoria = agenda.atuacao.defensoria
        comarca = defensoria.comarca
        atuacao = agenda.atuacao

    else:

        # Agendamento sem agenda definida: recupera dados da defensoria e comarca informadas
        comarca = Comarca.objects.get(id=comarca_id)

        # Se defensoria não foi informada, identifica a partir da comarca
        # TODO: Implementar regras de distribuição automática a partir das informações fornecidas no pré-agendamento
        if defensoria_id is None:
            try:
                defensoria = Defensoria.objects.get(
                    comarca=comarca.diretoria,
                    agendamento_online=True
                )
            except Defensoria.DoesNotExist:
                raise ValidationError(
                    'Nenhuma defensoria habilitada para receber agendamentos de {}'.format(comarca.nome)
                )
            except Defensoria.MultipleObjectsReturned:
                raise ValidationError(
                    'Impossível saber qual das defensorias habilitadas pode receber agendamentos de {}'.format(comarca.nome)  # noqa: E501
                )
        else:
            defensoria = Defensoria.objects.get(id=defensoria_id)

        # Se agendamento inicial: muda tipo pra pré-agendamento (ligação)
        if at_tipo == AtendimentoDefensor.TIPO_INICIAL and atendimento_tipo_ligacao:
            atuacao = defensoria.all_atuacoes.nao_lotacoes().vigentes().order_by('tipo').first()
            at_tipo = AtendimentoDefensor.TIPO_LIGACAO
            data_agendamento = None

    # Se defensor não informado, obtém defensor/substituto a partir da atuação
    if defensor_id is None:

        if atuacao is None:
            raise ValidationError(u'Nenhum defensor atuando na {} para receber um agendamento!'.format(defensoria.nome))

        # Recupera informações do defensor titular e substituto a partir da atuação identificada
        if atuacao.tipo == Atuacao.TIPO_SUBSTITUICAO:
            defensor_id = atuacao.titular_id
            substituto_id = atuacao.defensor_id
        else:
            defensor_id = atuacao.defensor_id
            substituto_id = None

    # Se categoria não foi informada, assume categoria do último atendimento ou primeira categoria da defensoria
    if categoria_agenda is None:
        if at_inicial:
            categoria_agenda = at_inicial.at_final.agenda_id
        elif defensoria.categorias_de_agendas.exists():
            categoria_agenda = defensoria.categorias_de_agendas.first().id
        else:
            categoria_agenda = 1

    # Retorna um erro se a defensoria não possuir vínculo com a categoria informada
    if not defensoria.categorias_de_agendas.filter(id=categoria_agenda).exists():
        if config.ATIVAR_BOTAO_REMETER_ATENDIMENTO:
            categoria_agenda = defensoria.categorias_de_agendas.first().id
        else:
            raise ValidationError(u'A defensoria {} não está habilitada para receber esse agendamento!'.format(defensoria.nome))  # noqa: E501

    # TODO: Unificar mesma verificação feita em "atendimento\agendamento\views.py"
    # Se habilitado, identifica forma de atendimento do dia
    if agenda and config.EXIBIR_PRESENCIAL_REMOTO_AGENDAMENTO:

        horarios = json.loads(agenda.conciliacao)  # converte string json em objeto
        formas_atendimento = horarios.pop('forma_atendimento', None)  # obtém objecto com as formas de atendimento

        # Se encontrado, obtém forma de atendimento para a data do agendamento
        if formas_atendimento and str(categoria_agenda) in formas_atendimento:
            forma_atendimento = formas_atendimento[str(categoria_agenda)][data_agendamento.weekday()]
            # Obtém lista de formas de atendimento disponíveis para a recepção
            formas_atendimento = FormaAtendimento.objects.vigentes().filter(aparece_recepcao=True)
            # Se é dígito, procura pelo id
            if forma_atendimento and forma_atendimento.isnumeric():
                forma_atendimento = formas_atendimento.filter(id=forma_atendimento).first()
            # Se texto, procura pelo tipo (presencial ou não)
            elif forma_atendimento == 'P':
                forma_atendimento = formas_atendimento.filter(presencial=True).first()
            elif forma_atendimento == 'R':
                forma_atendimento = formas_atendimento.filter(presencial=False).first()
            else:
                forma_atendimento = None

    # Se defensoria do agendamento de retorno mudou, é um encaminhamento
    if ultimo_atendimento and ultimo_atendimento.defensoria_id != defensoria.id:
        at_tipo = AtendimentoDefensor.TIPO_ENCAMINHAMENTO

    dados_novo_agendamento = {
        'data_agendamento': data_agendamento,
        'agenda_id': categoria_agenda,  # aqui a agenda se refere à categoria de agenda (evento.Categoria)
        'forma_atendimento': forma_atendimento,
        'agendado_por_id': servidor_criador_id,
        'cadastrado_por_id': servidor_criador_id,
        'qualificacao_id': qualificacao_id,
        'comarca': comarca,
        'defensoria': defensoria,
        'inicial': at_inicial,
        'tipo': at_tipo,
        'historico_recepcao': anotacao,
        'defensor_id': defensor_id,
        'substituto_id': substituto_id,
        'ativo': True,
    }

    atendimento_agendamento = AtendimentoDefensor(**dados_novo_agendamento)

    if commit:
        with transaction.atomic():
            atendimento_agendamento.save()
            # Se inicial, vincula pessoa ao atendimento
            if at_tipo in [AtendimentoDefensor.TIPO_LIGACAO, AtendimentoDefensor.TIPO_INICIAL]:
                # Adiciona requerente principal
                atendimento_agendamento.set_requerente(pessoa_assistida_id)
                # Adiciona outros requerentes
                for pessoa_assistida_id in pessoas_assistidas_ids[1:]:
                    atendimento_agendamento.add_requerente(pessoa_assistida_id)
                # Se processo informado, vincula ao agendamento
                if processo_procapi is not None:
                    processo, novo = Processo.objects.get_or_create(
                        numero_puro=processo_procapi['numero'],
                        grau=processo_procapi['grau'],
                        defaults={
                            'numero': processo_procapi['numero'],
                            'chave': processo_procapi['chave'],
                            'cadastrado_por': usuario_criador,
                            'ativo': True
                        }
                    )
                    Parte.objects.get_or_create(
                        processo=processo,
                        atendimento=atendimento_agendamento
                    )

    return atendimento_agendamento


def create_chatbot_user(user_class, servidor_class, comarca_class):
    """

    Args:
        user_class:
        servidor_class:
        comarca_class:

    Returns:
        (new_user, new_servidor, status_code)

    status_code: -1 - user chatbot e servidor ja existem
    status_code: 0 - success create user and servidor
    status_code: 1 - user chatbot ja existe e foi criado uma nova instancia de servidor
    status_code: 2 - nao existe comarca cadastrada

    """
    status = -1
    existe_chatbot_user = True
    existe_servidor_chatbot = True
    existe_primeira_comarca = True
    if user_class.objects.filter(username=settings.CHATBOT_USERNAME).exists():
        chatbot_user = user_class.objects.get(username=settings.CHATBOT_USERNAME)
    else:
        # se nao existe usuario chatbot, entao cria ele
        existe_chatbot_user = False
        raw_random_password = get_random_string(
            length=10,
            allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ023456789'
        )

        chatbot_user = user_class()
        chatbot_user.username = settings.CHATBOT_USERNAME
        chatbot_user.first_name = settings.CHATBOT_FULL_NAME
        chatbot_user.password = make_password(raw_random_password)
        chatbot_user.save()

    if servidor_class.objects.filter(usuario__username=settings.CHATBOT_USERNAME).exists():
        servidor = servidor_class.objects.get(usuario__username=settings.CHATBOT_USERNAME)
        if not servidor.uso_interno:
            servidor.uso_interno = True
            servidor.save()
    else:
        existe_servidor_chatbot = False
        primeira_comarca_cadastrada_id = comarca_class.objects.filter(
            ativo=True
        ).order_by().order_by(
            'data_cadastro'
        ).values_list(
            'id',
            flat=True
        ).first()
        if primeira_comarca_cadastrada_id:
            # se existe primeira comarca
            existe_primeira_comarca = True
            servidor = Servidor()
            servidor.usuario_id = chatbot_user.pk
            servidor.cpf = '0'
            servidor.nome = chatbot_user.first_name
            servidor.ativo = True
            servidor.uso_interno = True
            servidor.comarca_id = primeira_comarca_cadastrada_id
            servidor.save()
        else:
            servidor = None
    if not existe_chatbot_user and not existe_servidor_chatbot:
        # tanto chatbot_user quanto servidor sao novos
        if existe_primeira_comarca:
            status = 0
        else:
            status = 2
    elif existe_servidor_chatbot and not existe_servidor_chatbot:
        status = 1

    return chatbot_user, servidor, status


def restringir_qualificacao(qualificacoes, defensorias):
    return qualificacoes.filter(
        Q(defensorias__isnull=True) |
        Q(defensorias__in=defensorias)
    )
