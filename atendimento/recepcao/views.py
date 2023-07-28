# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import json as simplejson
import logging
from datetime import date, datetime

# Bibliotecas de terceiros
from constance import config
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

# Solar
from assistido.models import PessoaAssistida
from atendimento.agendamento.utils import formata_mensagem_whatsapp_agendamento_efetuado
from atendimento.atendimento.models import Defensor as AtendimentoDefensor
from atendimento.atendimento.models import Pessoa as AtendimentoPessoa
from atendimento.atendimento.models import Atendimento
from comarca.models import Guiche, Predio
from contrib import constantes
from contrib.models import Comarca, Enum, Servidor, Util, Estado
from defensor.models import Atuacao
from notificacoes.tasks import notificar_atendimento_liberado
from nucleo.itinerante.models import Evento
from nucleo.nadep.models import Aprisionamento, Atendimento as AtendimentoPreso
from painel.models import Painel
from relatorios.models import Local, Relatorio
from atendimento.precadastro.forms import EnderecoForm

logger = logging.getLogger(__name__)


@login_required
def index(request):

    if request.session.get('ligacao_id'):
        return redirect('{}?next={}'.format(reverse('precadastro_index'), reverse('recepcao_index')))

    # Se servidor vinculado a um itinerante ativo, redireciona
    if Evento.objects.filter(
            data_inicial__lte=date.today(),
            data_final__gte=date.today(),
            participantes=request.user.servidor,
            ativo=True):

        return redirect('itinerante_distribuir')

    if request.session.get('comarca'):
        comarca = Comarca.objects.get(id=request.session.get('comarca'))
    else:
        comarca = request.user.servidor.comarca

    request.session['nucleo'] = None

    if comarca.predios.filter(ativo=True).exists() and request.session.get('predio', None) is None:
        return redirect('recepcao_index_predio')

    if request.session.get('predio'):
        return redirect('recepcao_marcados_predio', comarca.id, request.session.get('predio'))
    else:
        return redirect('recepcao_marcados_comarca', comarca.id)


@login_required
def index_predio(request):

    predios = Predio.objects.filter(comarca=request.session.get('comarca', 0), ativo=True).order_by('nome')

    if len(predios) == 1:
        request.session['predio'] = predios.first().id
        return redirect('recepcao_index')

    return render(request=request, template_name="atendimento/recepcao/predios.html", context=locals())


@login_required
def predio_set(request, predio_id):
    request.session['predio'] = predio_id
    return redirect('recepcao_index')


@login_required
def marcados_comarca(request, comarca_id, predio_id=None):
    angular = 'RecepcaoMarcadosCtrl'

    comarca = comarca_id
    guiche = request.session.get('guiche')

    if predio_id:
        predio = Predio.objects.get(id=predio_id)

    if guiche is None:
        guiche = 0

    return render(request=request, template_name="atendimento/recepcao/marcados.html", context=locals())


@never_cache
@login_required
def marcados_comarca_get(request, comarca_id, predio_id=None):
    dados = []

    status = int(request.GET.get('status'))
    contador = request.GET.get('cont')

    if not contador or contador != u'1':
        contador = None

    database_view = ' '
    orderby = ''

    atrasado = False

    if status == 1:
        database_view = ' vw_atendimentos_dia_aguardando'

        orderby = ' ORDER BY prioridade desc, extrapauta, data_agendamento'

    elif status == 2:
        database_view = ' vw_atendimentos_dia_atrasados'
        atrasado = True

        orderby = ' ORDER BY prioridade desc, data_agendamento'

    elif status == 3:
        database_view = ' vw_atendimentos_dia_liberados'

        orderby = ' ORDER BY prioridade desc, data_atendimento_recepcao'

    elif status == 4:
        database_view = ' vw_atendimentos_dia_em_atendimento'

        orderby = ' ORDER BY horario_atendimento_recepcao'

    elif status == 5:
        database_view = ' vw_atendimentos_dia_atendidos'

        orderby = ' ORDER BY data_atendimento desc'

    select_dados = "*"
    if contador:
        select_dados = 'COUNT(atendimento_ptr_id) as atendimento_ptr_id'

    query = "SELECT %s FROM %s WHERE comarca_id = %s" % (select_dados, database_view, comarca_id)

    if predio_id:
        predio = Predio.objects.get(id=predio_id)

        if not predio.visao_comarca:
            query += " AND predio_id = %s" % predio_id

    if not contador:
        query += orderby

    atendimentos = AtendimentoDefensor.objects.raw(query)

    if contador:
        dados = {'qtd': list(atendimentos)[0].id}
    else:
        for a in atendimentos:

            if a.data_atendimento_recepcao and not a.data_atendimento:
                cron = a.cronometro_set.filter(termino__gte=a.data_atendimento_recepcao).order_by('-termino').first()
            else:
                cron = None

            dados.append({
                'id': a.id,
                'numero': a.numero,
                'tipo': a.LISTA_TIPO[a.tipo][1],
                'tipo_id': a.tipo,
                'requerente': {
                    'id': a.requerente_id,
                    'pessoa_id': a.requerente_pessoa_id,
                    'nome': a.requerente_nome,
                    'nome_social': a.requerente_nome_social if a.requerente_nome_social else None,
                    'apelido': a.requerente_apelido if a.requerente_apelido else None,
                    'cpf': a.requerente_cpf,
                    'tipo': a.requerente_tipo,
                },
                'requerido': {
                    'id': a.requerido_id,
                    'pessoa_id': a.requerido_pessoa_id,
                    'nome': a.requerido_nome,
                    'nome_social': a.requerido_nome_social if a.requerido_nome_social else None,
                    'apelido': a.requerido_apelido if a.requerido_apelido else None,
                    'tipo': a.requerido_tipo,
                },
                'area': a.area_nome,
                'pedido': a.qualificacao_titulo,
                'horario': a.horario,
                'horario_atendimento': a.horario_atendimento,
                'horario_atendimento_recepcao': a.horario_atendimento_recepcao,
                'atrasado': atrasado,  # noqa
                'historico_agendamento': a.historico_recepcao,
                'historico_recepcao': a.historico_recepcao,
                'historico_atendimento': a.historico_atendimento,
                'defensoria': {
                    'id': a.defensoria_id,
                    'codigo': a.defensoria_codigo,
                    'nome': a.defensoria_nome
                },
                'defensor': {
                    'nome': a.defensor_nome if a.defensor_nome else None,
                    'username': a.defensor_username if a.defensor_username else None,
                },
                'substituto': {
                    'nome': a.substituto_nome if a.substituto_nome else None,
                    'username': a.substituto_username if a.substituto_username else None,
                },
                'guiche': 0,
                'extra': a.extra,
                'agenda': a.agenda.nome,
                'telefones': [],
                'prazo': a.prazo,
                'prioridade': a.prioridade,
                'atividades': a.atividades,
                'apoio': (a.tipo == Atendimento.TIPO_NUCLEO),
                'em_atendimento': {
                    'servidor': cron.servidor.nome if cron.servidor else None,
                    'data_inicio': cron.inicio
                } if cron else None,
                'forma_atendimento': a.forma_atendimento_id,
                'status': status
            })

    return JsonResponse(dados, safe=False)


@never_cache
@login_required
def atendimento(request, atendimento_id, tipo=-1, responsavel=0, cadastrado=0, pessoa_id=None):
    """Utilizado para carregar os dados da página de Liberar Atendimento pela Recepção.
        Também por outros módulos para alterar requerentes e requeridos.
    """
    if request.GET.get('pessoa_id'):
        return redirect('recepcao_atendimento', atendimento_id, tipo, responsavel, cadastrado,
                        request.GET.get('pessoa_id'))

    tipo = int(tipo)
    atendimento = get_object_or_404(AtendimentoDefensor, numero=atendimento_id, ativo=True)

    # Verifica se é um pedido de apoio (se possui filho TIPO_NUCLEO)
    atendimento_para_apoio = atendimento.filhos.filter(
        tipo=Atendimento.TIPO_NUCLEO,
        ativo=True
    ).exists()

    # Se é um pedido de apoio, procura por último atendimento válido para receber uploads (que não seja pedido de apoio)
    if atendimento_para_apoio:
        atendimento_para_upload = AtendimentoDefensor.objects.filter(
            (
                Q(id=atendimento.inicial_id) |
                Q(inicial=atendimento.inicial_id)
            ) &
            (
                (
                    Q(tipo__in=[
                        Atendimento.TIPO_INICIAL,
                        Atendimento.TIPO_RETORNO,
                        Atendimento.TIPO_INTERESSADO,
                        Atendimento.TIPO_VISITA]) & ~
                    Q(data_atendimento=None)
                ) |
                Q(tipo=Atendimento.TIPO_PROCESSO)
            ) &
            Q(ativo=True)
        ).exclude(
            filhos__tipo=Atendimento.TIPO_NUCLEO
        ).order_by(
            '-data_atendimento'
        ).first()
    else:
        atendimento_para_upload = atendimento

    hoje = date.today()
    dia_um = datetime(hoje.year, hoje.month, 1)

    # altera qualificacao se solicitado para este atendimento e não realizado ou realizado no mês corrente
    if request.session.get('qualificacao_id') \
            and atendimento.id == request.session.get('atendimento_id') \
            and atendimento.data_atendimento is None:

        # recupera e aplica qualificacao da sessao
        atendimento.qualificacao_id = request.session['qualificacao_id']
        atendimento.save()

        # remove qualificacao da sessao
        request.session['qualificacao_id'] = None
        request.session['atendimento_id'] = None

    # adicionar pessoa
    if pessoa_id is not None:

        if responsavel == '1':
            responsavel = True
        elif tipo == 0 and atendimento.requerente is None:
            responsavel = True
        elif tipo == 1 and atendimento.requerido is None:
            responsavel = True
        else:
            responsavel = False

        pessoa, novo = atendimento.add_pessoa(pessoa_id=pessoa_id, tipo=tipo, responsavel=responsavel)

        if atendimento.get_requerentes().exists():
            atendimento.set_requerente(atendimento.get_requerentes().first().pessoa)

        if atendimento.get_requeridos().exists():
            atendimento.set_requerido(atendimento.get_requeridos().first().pessoa)

        if novo:
            messages.success(request, u'Pessoa vinculada ao atendimento')
        else:

            if cadastrado:
                messages.success(request, u'Dados pessoais alterados.')
            else:
                messages.error(request, u'Pessoa já vinculada ao atendimento')

        return redirect("recepcao_atendimento", atendimento_id, tipo)

    # libera se atendimento marcado pra hoje
    hoje = date.today()
    liberado = (atendimento.data_agendamento and atendimento.data_agendamento.date() == hoje)

    processo = atendimento.processo
    tipo_processo = True if atendimento.tipo == atendimento.TIPO_PROCESSO else False

    if processo:
        processo_parte = atendimento.get_processo_partes().filter(processo=processo).first()
    else:
        processo_parte = None

    relatorios_btn_carta_convite = Relatorio.objects.filter(
        papeis=request.user.servidor.papel,
        locais__pagina=Local.PAG_RECEPCAO_DETALHES_BTN_CARTA_CONVITE
    ).ativos()

    relatorios_btn_requerente = Relatorio.objects.filter(
        papeis=request.user.servidor.papel,
        locais__pagina=Local.PAG_RECEPCAO_DETALHES_BTN_REQUERENTE
    ).ativos()

    relatorios_btn_requerido = Relatorio.objects.filter(
        papeis=request.user.servidor.papel,
        locais__pagina=Local.PAG_RECEPCAO_DETALHES_BTN_REQUERIDO
    ).ativos()

    atuacao_atual = atendimento.get_atuacao()
    atuacoes_predio = []

    if atuacao_atual:
        atuacoes_predio = Atuacao.objects.vigentes(
            inicio=atendimento.data_agendamento
        ).filter(
            defensoria__predio=atuacao_atual.defensoria.predio,
            tipo__in=[Atuacao.TIPO_TITULARIDADE, Atuacao.TIPO_ACUMULACAO]
        ).distinct()

    if request.GET.get('prev'):
        voltar_url = request.GET.get('prev')
        if request.GET.get('prev_params'):
            voltar_url = '{}?'.format(voltar_url.split('?')[0])
            for k, v in iter(simplejson.loads(request.GET.get('prev_params')).items()):
                voltar_url = voltar_url + '{}={}&'.format(k, v)
        request.session['recepcao_atendimento_voltar_url'] = voltar_url

    # Link para redirecionamento no caso da exclusão
    pode_excluir = atendimento.pode_excluir(request.user) and atendimento.tipo != Atendimento.TIPO_PROCESSO
    next_excluir = reverse('recepcao_index')
    if config.ATIVAR_BOTAO_PRE_CADASTRO:
        endereco_form_initial = {
            'estado': Estado.objects.get(uf__iexact=settings.SIGLA_UF)
        }
        # forms
        endereco_form = EnderecoForm(initial=endereco_form_initial)
        sigla_uf = settings.SIGLA_UF.upper()

    angular = 'RecepcaoAtendimentoCtrl'

    if atendimento.data_agendamento and atendimento.requerente:

        fonezap = atendimento.requerente.pessoa.telefone_para_whatsapp

        if fonezap:
            mensagem_whatsapp_com_documentos = formata_mensagem_whatsapp_agendamento_efetuado(atendimento, True)
            mensagem_whatsapp_sem_documentos = formata_mensagem_whatsapp_agendamento_efetuado(atendimento, False)

    return render(request=request, template_name="atendimento/recepcao/atendimento.html", context=locals())


@login_required
def atendimento_adicionar_pessoa(request):
    if request.method == 'POST':
        dados = simplejson.loads(request.body)

        atendimento_id = dados.get('atendimento_id')
        pessoa_id = dados.get('pessoa_id')
        responsavel = dados.get('responsavel')
        cadastrado = dados.get('cadastrado')
        tipo_envolvido = dados.get('tipo_envolvido')

        sucesso = False
        mensagem = u'Erro ao adicionar pessoa!'
        resposta = {}

        if pessoa_id:
            try:
                atendimento = AtendimentoDefensor.objects.filter(id=atendimento_id, ativo=True).first()

                if responsavel == '1':
                    responsavel = True
                elif tipo_envolvido == AtendimentoPessoa.TIPO_REQUERENTE and atendimento.requerente is None:
                    responsavel = True
                elif tipo_envolvido == AtendimentoPessoa.TIPO_REQUERIDO and atendimento.requerido is None:
                    responsavel = True
                else:
                    responsavel = False

                pessoa, novo = atendimento.add_pessoa(pessoa_id=pessoa_id, tipo=tipo_envolvido, responsavel=responsavel)

                if atendimento.get_requerentes().exists():
                    atendimento.set_requerente(atendimento.get_requerentes().first().pessoa)

                if atendimento.get_requeridos().exists():
                    atendimento.set_requerido(atendimento.get_requeridos().first().pessoa)

                # busca as filiações
                filiacao = []

                for f in pessoa.pessoa.filiacoes.all():
                    filiacao.append({'nome': f.nome})

                # busca a foto da pessoa
                from assistido.models import PessoaAssistida
                foto = PessoaAssistida.objects.filter(id=pessoa.pessoa.id).first().get_foto()

                # tratamento para saber se é requerente ou requerido
                eh_requerente = True

                if tipo_envolvido == AtendimentoPessoa.TIPO_REQUERIDO:
                    eh_requerente = False

                # cria dict para retornar dados json
                pessoa_dict = {
                    'pessoa_id': pessoa.pessoa.id,
                    'nome': pessoa.pessoa.nome,
                    'nome_tratado': pessoa.pessoa.nome_tratado,
                    'possui_nome_social': pessoa.pessoa.possui_nome_social(),
                    'possui_nome_fantasia': pessoa.pessoa.possui_nome_fantasia(),
                    'eh_pessoa_fisica': pessoa.pessoa.eh_pessoa_fisica,
                    'cpf': pessoa.pessoa.cpf,
                    'data_nascimento': pessoa.pessoa.data_nascimento,
                    'idoso': pessoa.pessoa.idoso,
                    'pne': pessoa.pessoa.pne,
                    'responsavel': pessoa.responsavel,
                    'interessado': False,
                    'eh_requerente': eh_requerente,
                    'eh_requerido': not eh_requerente,
                    'filiacao': filiacao,
                    'foto': foto
                }

                resposta['pessoa'] = pessoa_dict

                if novo:
                    mensagem = u'Pessoa vinculada ao atendimento'
                else:
                    if cadastrado:
                        mensagem = u'Dados pessoais alterados.'
                    else:
                        mensagem = u'Pessoa já vinculada ao atendimento'

                sucesso = True

            except Exception as e:
                mensagem = str(e)

        resposta['sucesso'] = sucesso
        resposta['mensagem'] = mensagem

        return JsonResponse(resposta)


@login_required
def get_json_atendimento_liberar(request, atendimento_numero):
    dados = {}

    qualificacao = None
    area = None

    atendimento = AtendimentoDefensor.objects.filter(numero=atendimento_numero).first()

    if atendimento.qualificacao:
        qualificacao = atendimento.qualificacao.titulo
        area = atendimento.qualificacao.area.nome

    preso = False
    if atendimento.requerente:
        if Aprisionamento.objects.filter(
            prisao__pessoa=atendimento.requerente.pessoa_id,
            data_final=None,
            ativo=True
        ).exists():
            preso = True

    dados_atendimento = {
        'id': atendimento.id,
        'numero': atendimento.numero,
        'data_cadastro': atendimento.data_cadastro.strftime('%Y-%m-%d'),
        'data_agendamento': atendimento.data_agendamento.strftime(
            '%Y-%m-%d') if atendimento.data_agendamento else None,
        'area': area,
        'pedido': qualificacao,
        'defensoria': atendimento.defensoria.nome if atendimento.defensoria else None,
        'preso': preso,
        'tipo': atendimento.tipo
    }

    defensor = {
        'nome': atendimento.defensor.nome,
        'foto': atendimento.defensor.servidor.get_foto()
    }

    # r1 = requerente_responsavel
    r1 = None

    for p in atendimento.get_requerentes():
        if p.responsavel:
            r1 = p

    if r1:
        filiacao = []
        if r1.pessoa.tipo == constantes.TIPO_PESSOA_FISICA:
            for f in r1.pessoa.filiacoes.all():
                filiacao.append({'nome': f.nome})

        # r1 = requerente_responsavel
        r1_nome = r1.pessoa.nome
        r1_data_nascimento = None

        if r1.pessoa.tipo == constantes.TIPO_PESSOA_FISICA:
            if r1.pessoa.nome_social:
                r1_nome = r1.pessoa.nome_social

            if r1.pessoa.data_nascimento:
                r1_data_nascimento = r1.pessoa.data_nascimento.isoformat()
        else:
            if r1.pessoa.apelido:
                r1_nome = r1.pessoa.apelido

        r1_dict = {
            'nome': r1_nome,
            'foto': r1.pessoa.get_foto(),
            'cpf': r1.pessoa.cpf,
            'data_nascimento': r1_data_nascimento,
            'eh_pessoa_fisica': r1.pessoa.eh_pessoa_fisica,
            'filiacao': filiacao,
            'preso': preso,
            'idade': r1.pessoa.idade,
            'idoso': r1.pessoa.idoso,
            'pne': r1.pessoa.pne
        }

        # tratamento para só liberar o botão 'Salvar e Liberar' caso o responsável não seja PJ
        liberar_atendimento_pj_sem_pf = True

        if not config.LIBERAR_ATENDIMENTO_PJ_SEM_PF:
            liberar_atendimento_pj_sem_pf = atendimento.requerentes.filter(
                pessoa__tipo=constantes.TIPO_PESSOA_FISICA
            ).exists()

        dados['requerente_responsavel'] = r1_dict
        dados['liberar_atendimento_pj_sem_pf'] = liberar_atendimento_pj_sem_pf
    else:
        # Casos em que não há requerente responsável
        dados['liberar_atendimento_pj_sem_pf'] = False

    dados['atendimento'] = dados_atendimento
    dados['defensor'] = defensor

    return JsonResponse(dados)


@login_required
@transaction.atomic
def salvar_atendimento(request):
    """Utilizado para Salvar e Liberar o atendimento pela Recepção"""

    if request.method == 'POST':

        atendimento = get_object_or_404(AtendimentoDefensor, id=request.POST['id_atendimento'], ativo=True)
        agendamento = (request.POST.get('agendamento') == 'true')

        # Atualiza a anotação do agendamento sem criar atendimento para recepção
        if agendamento:

            if atendimento.data_cadastro.date() == date.today() and atendimento.cadastrado_por == request.user.servidor:
                atendimento.historico_recepcao = request.POST['historico_recepcao']
                atendimento.save()
                messages.success(request, u'Anotação do agendamento atualizada!')
            else:
                messages.error(request, u'Não foi possível atualizar a anotação do agendamento!')

            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Cria/atualiza atendimento da repceção somente se não tem agendamento ou agendado para hoje
        elif not atendimento.data_agendamento or atendimento.data_agendamento.date() == date.today():

            agora = datetime.now()
            prioridade = int(request.POST.get('prioridade'))

            if atendimento.prioridade != prioridade:
                atendimento.prioridade = prioridade
                atendimento.save()

            atendimento_recepcao, created = Atendimento.objects.get_or_create(
                origem=atendimento,
                tipo=Atendimento.TIPO_RECEPCAO,
                ativo=True
            )

            if created:
                atendimento_recepcao.cadastrado_por = request.user.servidor

            if not atendimento_recepcao.data_atendimento:
                atendimento_recepcao.atendido_por = request.user.servidor
                atendimento_recepcao.data_atendimento = agora

            atendimento_recepcao.modificado_por = request.user.servidor
            atendimento_recepcao.historico = request.POST['historico_recepcao']
            atendimento_recepcao.save()

            if atendimento.prioridade != prioridade:
                atendimento.prioridade = prioridade
                atendimento.save()

            if hasattr(atendimento.at_inicial, 'arvore'):
                atendimento.at_inicial.arvore.ativo = False
                atendimento.at_inicial.arvore.save()

            messages.success(request, u'Pré-atendimento realizado.')

            if config.NOTIFICAR_LIBERACAO_ATENDIMENTO_RECEPCAO:
                # cria a tarefa no celery para notificar usuarios sobre a liberação do atendimento pela recepção
                notificar_atendimento_liberado.apply_async(kwargs={
                    'user_remetente_id': request.user.id,
                    'url_callback': request.build_absolute_uri(
                        reverse('atendimento_atender', args=[atendimento.numero])
                    ),
                    'atendimento_numero': atendimento.numero,
                }, queue='sobdemanda')

        else:

            messages.error(request, u'Não foi possível alterar as informações do agendamento!')

        return redirect('recepcao_index')

    else:

        return HttpResponseNotAllowed(['POST'])


@login_required
def buscar_pessoa(request):
    import re

    if request.method == 'POST':

        data = simplejson.loads(request.body)
        pessoas_json = []

        if 'query' in data and 'atendimento_id' in data:

            filtro = data['query']

            if filtro:

                nomes = Util.text_to_soundex(filtro)
                cpf = re.sub('[^a-zA-Z0-9]', '', filtro)

                q = Q(desativado_em=None)

                # Se a busca for por CPF
                if cpf.isnumeric():
                    q &= Q(cpf=cpf)
                else:
                    # Se a busca for por nome, nome_social ou nome fantasia de PJ (apelido)

                    # Se a consulta for com um nome com a quantidade de caracteres menos do que o mínimo configurado
                    # será retornada uma mensagem de alerta para que o usuário faça filtros mais elaborados
                    if config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MIN_CARACTERES and \
                       len(filtro) < config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MIN_CARACTERES:  # noqa: E501
                        return JsonResponse({
                            'request': data['request'],
                            'sucesso': False,
                            'mensagem': 'Erro: Aumente o texto para {} caracter(es) ou mais e tente novamente.'.format(
                                config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MIN_CARACTERES
                            )
                        })

                    q_nome = Q()
                    for nome in nomes:
                        q_nome &= Q(nome_soundex__icontains=nome)

                    # Só busca por nome social caso seja tipo pessoa física
                    q_nome_social = Q(
                        Q(tipo=constantes.TIPO_PESSOA_FISICA) &
                        Q(nome_social__icontains=filtro)
                    )

                    # Só busca por nome fantasia (apelido) caso seja tipo pessoa jurídica
                    q_nome_fantasia = Q(
                        Q(tipo=constantes.TIPO_PESSOA_JURIDICA) &
                        Q(apelido__icontains=filtro)
                    )

                    q &= Q(q_nome | q_nome_social | q_nome_fantasia)

                filtro_pessoas_count = PessoaAssistida.objects.filter(q).count()

                if config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MAX_PESSOAS and filtro_pessoas_count > config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MAX_PESSOAS:  # noqa: E501
                    return JsonResponse({
                        'request': data['request'],
                        'sucesso': False,
                        'mensagem': 'Erro: Seriam retornadas mais de {} pessoas. Busque pelo CPF ou CNPJ e tente novamente'.format(  # noqa: E501
                            config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MAX_PESSOAS
                        )
                    })

                filtro_pessoas = PessoaAssistida.objects.filter(q).distinct().order_by('nome')

                # remove as pessoas do atendimento atual
                atendimento = Atendimento.objects.get(id=data['atendimento_id'])
                filtro_pessoas = filtro_pessoas.exclude(id__in=atendimento.ids_todas_pessoas)

                for pessoa in filtro_pessoas:

                    filiacao = []

                    for f in pessoa.filiacoes.all():
                        filiacao.append({'nome': f.nome})

                    pessoas_json.append({
                        'pessoa_id': pessoa.id,
                        'nome': pessoa.nome,
                        'nome_tratado': pessoa.nome_tratado,
                        'possui_nome_social': pessoa.possui_nome_social(),
                        'possui_nome_fantasia': pessoa.possui_nome_fantasia(),
                        'eh_pessoa_fisica': pessoa.eh_pessoa_fisica,
                        'cpf': pessoa.cpf,
                        'data_nascimento': pessoa.data_nascimento,
                        'responsavel': 0,
                        'interessado': 0,
                        'eh_requerente': False,
                        'eh_requerido': False,
                        'filiacao': filiacao,
                        'foto': pessoa.get_foto()
                    })

        return JsonResponse({'request': data['request'], 'pessoas': pessoas_json, 'sucesso': True})

    return JsonResponse({'error': True})


@login_required
def remover_pessoa(request):

    if request.method == 'POST':

        resposta = {
            'success': False
        }

        data = simplejson.loads(request.body)
        atendimento = get_object_or_404(Atendimento, id=data['atendimento_id'])

        pessoa = AtendimentoPessoa.objects.filter(
            atendimento=atendimento.at_inicial,
            pessoa_id=data['pessoa_id'],
            ativo=Enum.STATUS_ATIVO
        ).first()

        if pessoa:

            pessoa.ativo = Enum.STATUS_INATIVO
            pessoa.save()

            if pessoa.tipo == AtendimentoPessoa.TIPO_REQUERENTE:
                requerente = atendimento.get_requerente()
                if requerente:
                    atendimento.set_requerente(requerente.pessoa)
            elif pessoa.tipo == AtendimentoPessoa.TIPO_REQUERIDO:
                requerido = atendimento.get_requerido()
                if requerido:
                    atendimento.set_requerido(requerido.pessoa)

            resposta['success'] = True

        return JsonResponse(resposta)


@login_required
def alterar_interessado(request):
    """Utilizado para alterar o requerente Interessado"""

    resposta = {'success': False}

    if request.method == 'POST':

        data = simplejson.loads(request.body)
        atendimento = AtendimentoDefensor.objects.filter(id=data['atendimento_id']).first()

        if atendimento.tipo != atendimento.TIPO_PROCESSO:
            if atendimento.requerente:
                aprisionamento = Aprisionamento.objects.filter(
                    prisao__pessoa=atendimento.requerente.pessoa,
                    data_final=None,
                    ativo=True
                ).exists()

                if aprisionamento:
                    nadep = AtendimentoPreso()
                    nadep.__dict__.update(atendimento.__dict__)
                    nadep.interessado_id = data['pessoa_id']
                    nadep.save()

                    resposta['success'] = True

    return JsonResponse(resposta)


@login_required
def alterar_responsavel(request):
    """Utilizado para alterar o responsável pelo atendimento/processo, seja requerente ou requerido"""

    if request.method == 'POST':

        data = simplejson.loads(request.body)
        atendimento = AtendimentoDefensor.objects.get(id=data['atendimento_id'])

        if data['tipo'] == AtendimentoPessoa.TIPO_REQUERENTE:
            atendimento.set_requerente(data['pessoa_id'])
        else:
            atendimento.set_requerido(data['pessoa_id'])

        return JsonResponse({'success': True})


@login_required
def alterar_tipo_pessoa_envolvida(request):
    """Alterar o tipo de pessoa envolvida. Altera requerente para requerido e vice-versa"""

    resposta = {'sucesso': False}

    if request.method == 'POST':

        data = simplejson.loads(request.body)
        pessoa_id = data['pessoa_id']

        atendimento = AtendimentoDefensor.objects.filter(id=data['atendimento_id']).first()

        if atendimento:

            pessoa = AtendimentoPessoa.objects.filter(
                atendimento=atendimento.at_inicial,
                pessoa_id=pessoa_id,
                ativo=True
            ).only('tipo', 'responsavel').first()

            if pessoa and pessoa.tipo == AtendimentoPessoa.TIPO_REQUERENTE:

                atendimento.add_requerido(pessoa_id)

                # Se era o requerente responsável, define o próximo como responsável, se houver
                if pessoa.responsavel:
                    novo_requerente = atendimento.get_requerente()
                    if novo_requerente:
                        atendimento.set_requerente(novo_requerente.pessoa)

            elif pessoa and pessoa.tipo == AtendimentoPessoa.TIPO_REQUERIDO:

                atendimento.add_requerente(pessoa_id)

                # Se era o requerido responsável, define o próximo como responsável, se houver
                if pessoa.responsavel:
                    novo_requerido = atendimento.get_requerido()
                    if novo_requerido:
                        atendimento.set_requerido(novo_requerido.pessoa)

            resposta['sucesso'] = True

    return JsonResponse(resposta)


@login_required
def alterar_defensoria(request):
    """Altera defensoria do atendimento"""

    if request.method == 'POST':

        data = simplejson.loads(request.body)
        atendimento = get_object_or_404(AtendimentoDefensor, numero=data['atendimento_numero'], ativo=True)

        if atendimento:

            atuacao = Atuacao.objects.get(id=data['atuacao_id'])
            atuacao_substituicao = atuacao.substituicao.vigentes(inicio=atendimento.data_agendamento).first()

            if atuacao_substituicao:
                atendimento.substituto = atuacao.defensor
            else:
                atendimento.substituto = None

            atendimento.defensor = atuacao.defensor
            atendimento.defensoria = atuacao.defensoria
            atendimento.save()

            return JsonResponse({'success': True})

    return JsonResponse({'success': False})


@login_required
def publico(request):
    if request.method == 'POST':

        dados = []
        atendimentos = AtendimentoDefensor.objects.filter(
            data_agendamento__startswith=date.today(),
            ativo=True,
            remarcado=None,
            data_atendimento=None
        ).exclude(
            id__in=Atendimento.objects.filter(
                data_atendimento__startswith=date.today(),
                ativo=True,
                tipo=Atendimento.TIPO_RECEPCAO
            ).exclude(
                historico=None
            ).values_list('origem_id')
        ).order_by('data_agendamento')

        hora_atual = datetime.now()

        for a in atendimentos:
            diferenca = (a.data_agendamento - hora_atual).total_seconds() + (1 * 60)
            dados.append({
                'requerente': a.requerente.nome,
                'horario': a.data_agendamento.strftime('%H:%M'),
                'atrasado': 1 if diferenca <= 0 else 0
            })

        return JsonResponse(dados, safe=False)

    servidor = Servidor.objects.get(usuario_id=request.user.id)

    if request.session.get('comarca'):
        comarca = request.session.get('comarca')
    else:
        comarca = servidor.comarca.id

    return render(request=request, template_name="atendimento/recepcao/publico.html", context=locals())


@login_required
def alterar_predio(request):
    request.session['predio'] = None

    return redirect('recepcao_index')


@login_required
def chamar(request):

    if request.method == 'POST':

        data = simplejson.loads(request.body)

        try:
            atendimento = AtendimentoDefensor.objects.get(numero=data['atendimento']['numero'])
            defensoria = atendimento.defensoria
            guiche = Guiche.objects.filter(
                usuario_id=request.user.servidor.id,
                predio_id=defensoria.predio_id,
                ativo=True
            ).first()
        except Guiche.DoesNotExist:
            return JsonResponse({'success': False, 'msg': 'Usuário não possui guichê para este atendimento'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': e, 'msg': 'Ocorreu um erro, por favor tente novamente'})

        if not guiche:
            return JsonResponse({'success': False, 'msg': 'Usuário não possui guichê para o atendimento neste prédio'})

        senha, _ = Painel.objects.get_or_create(
            atendimento=atendimento,
            tipo=data['tipo'],
            defaults={
                'cadastrado_por': request.user,
                'predio_id': defensoria.predio_id
            }
        )

        if senha and senha.cadastrado_por != request.user:
            return JsonResponse({'success': False, 'msg': 'Este atendimento já foi notificado'})

        senha.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'msg': ''})
