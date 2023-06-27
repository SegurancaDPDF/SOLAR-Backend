# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip
import logging
import re
import requests
import six

from celery import shared_task
from constance import config
from django.conf import settings
from django.utils import timezone

from atendimento.atendimento.models import (
    Defensor as AtendimentoDefensor,
    Documento as AtendimentoDocumento,
    Encaminhamento,
    Pessoa as AtendimentoPessoa
)

from assistido.models import PessoaAssistida
from core.core_utils import executar_se_constance_ativo

re_captura_nao_numericos = re.compile(r'\D*')

logger = logging.getLogger(__name__)


# envia uma notificação para o chatbot Luna. Ela recebe o CPF do assistido, 
# o número do atendimento e uma mensagem como parâmetros e retorna a resposta 
# da requisição feita ao chatbot
def chatbot_notificar(assistido_cpf, atendimento_numero, message):
    """
    curl -H \"Content-Type: application/json\" \
    -d '{\"recipient\": {\"assistido_cpf\": \"11122233344\"}, \"message\": \"A data de seu atendimento foi alterada\"}' \
    -X POST https://luna.defensoria.to.def.br/api/v1/webhook

    Args:
        assistido_cpf: numero de cpf sem pontuacao
        message: string de ate 1999 caracteres
        luna_url:

    Returns:
        response instance from python-request post function

    """  # noqa: E501

    if not settings.CHATBOT_LUNA_WEBHOOK_URL:
        raise Exception(u'Nenhum webhook cadastrado para acesso ao chatbot')

    if not settings.CHATBOT_LUNA_API_TOKEN:
        raise Exception(u'Nenhum token de autorização cadastrado para acesso ao chatbot')

    # TODO: Verificar como tratar o limite de caracteres da Luna Chatbot sem bloquear a Luna Web
    # if message and len(message) >= 2000:
    #    raise Exception(u'A mensagem excede o limite de 1999 caracteres')

    cpf_assistido_somente_numeros = ''

    if assistido_cpf and isinstance(assistido_cpf, (six.string_types, six.binary_type)):
        cpf_assistido_somente_numeros = re_captura_nao_numericos.sub('', assistido_cpf)

    if cpf_assistido_somente_numeros == '':
        raise Exception(u'O formato do CPF é inválido')

    authorization = 'Token {}'.format(settings.CHATBOT_LUNA_API_TOKEN)

    headers = {
        'user-agent': 'SOLAR/{}'.format(settings.VERSION),
        'Authorization': authorization
    }

    data = {
        'recipient': {
            'assistido_cpf': cpf_assistido_somente_numeros
        },
        'atendimento_numero': atendimento_numero,
        'message': message
    }

    response = None

    for luna_url in settings.CHATBOT_LUNA_WEBHOOK_URL:
        response = requests.post(
            url=luna_url,
            json=data,
            headers=headers,
            verify=settings.CHATBOT_LUNA_VERIFY_CERTFILE
        )

    return response


# retorna uma instância da classe PessoaAssistida que é o requerente principal do atendimento.
def get_requerente_atendimento(atendimento):
    """

    Args:
        atendimento: Instancia de atendimento

    Returns:
        instancia de assistido.PessoaAssistida ou None se nao encontrar
    """
    if atendimento.inicial_id:
        at_inicial_id = atendimento.inicial_id
    else:
        at_inicial_id = atendimento.id

    requerente = PessoaAssistida.objects.only(
        'id',
        'cpf',
        'nome',
    ).filter(
        aderiu_luna_chatbot=True,
        atendimentos__atendimento__id=at_inicial_id,
        atendimentos__responsavel=True,
        atendimentos__tipo=AtendimentoPessoa.TIPO_REQUERENTE
    ).first()

    return requerente


# envia uma notificacao para Luna requerente de um atendimento específico
@shared_task
@executar_se_constance_ativo('USAR_NOTIFICACOES_ASSISTIDO_VIA_CHATBOT')
def chatbot_notificar_requerente(atendimento, requerente, mensagem):

    response = chatbot_notificar(
        assistido_cpf=requerente.cpf,
        atendimento_numero=atendimento.numero,
        message=mensagem,
    )

    if response.status_code == 200:
        return {
            'atendimento': atendimento.numero,
            'requerente': requerente.cpf,
            'mensagem': mensagem,
            'luna_response': response.json()
        }
    elif response.status_code == 404:
        return response.content.decode()
    else:
        raise Exception(response.status_code, response.content.decode())


# envia uma notificacao para o requerente de um atendimento de agendamento.
@shared_task
@executar_se_constance_ativo('USAR_NOTIFICACOES_ASSISTIDO_VIA_CHATBOT')
def chatbot_notificar_requerente_agendamento(numero, remarcado=False):
    atendimento = AtendimentoDefensor.objects.select_related(
        'inicial'
    ).only(
        'id',
        'inicial',
        'numero',
        'data_agendamento',
        'data_atendimento'
    ).get(
        numero=numero
    )

    requerente = get_requerente_atendimento(atendimento)

    if requerente is None:
        return {
            'sucesso': False,
            'mensagem': 'O requerente principal do atendimento {} não aderiu à Luna'.format(atendimento.numero)
        }

    template = ''

    if remarcado:
        template = config.LUNA_MENSAGEM_AGENDAMENTO_REMARCACAO
    elif atendimento.tipo == AtendimentoDefensor.TIPO_INICIAL:
        template = config.LUNA_MENSAGEM_AGENDAMENTO_INICIAL
    else:
        template = config.LUNA_MENSAGEM_AGENDAMENTO_RETORNO

    template = template.format(atendimento=atendimento)

    return chatbot_notificar_requerente(
        atendimento=atendimento,
        requerente=requerente,
        mensagem=template
    )


@shared_task
@executar_se_constance_ativo('USAR_NOTIFICACOES_ASSISTIDO_VIA_CHATBOT')
def chatbot_notificar_requerente_atendimento(numero, pessoa_id):

    # pessoa que será notificada
    requerente = PessoaAssistida.objects.only(
        'id',
        'cpf',
        'nome',
    ).filter(
        id=pessoa_id,
        aderiu_luna_chatbot=True
    ).first()

    if requerente is None:
        return {
            'sucesso': False,
            'mensagem': 'O requerente {} não aderiu à Luna'.format(pessoa_id)
        }

    # anotação que será enviada na notificacao
    anotacao = AtendimentoDefensor.objects.only(
        'id',
        'numero',
        'origem_id',
        'cadastrado_por',
        'historico'
    ).get(
        numero=numero
    )

    # atendimento vinculado à anotacao
    atendimento = AtendimentoDefensor.objects.select_related(
        'defensoria',
        'qualificacao__area',
    ).only(
        'id',
        'numero',
        'defensoria',
        'qualificacao',
    ).get(
        id=anotacao.origem_id
    )

    template = config.LUNA_MENSAGEM_ANOTACAO.format(
        atendimento=atendimento,
        anotacao=anotacao
    )

    dados_retorno = chatbot_notificar_requerente(
        atendimento=anotacao,
        requerente=requerente,
        mensagem=template
    )

    # atualiza data da notificacao
    anotacao.data_atendimento = timezone.now()
    anotacao.save()

    # força desativação da árvore do atendimento (signals não executa aqui)
    if anotacao.at_inicial:
        anotacao.at_inicial.arvore.excluir()

    return dados_retorno


@shared_task
@executar_se_constance_ativo('USAR_NOTIFICACOES_ASSISTIDO_VIA_CHATBOT')
def chatbot_notificar_requerente_documento(documento_id):

    # documento que será usado para notificacao
    documento = AtendimentoDocumento.objects.get(id=documento_id)
    atendimento = documento.atendimento

    requerente = get_requerente_atendimento(atendimento)

    if requerente is None:
        return {
            'sucesso': False,
            'mensagem': 'O requerente principal do atendimento {} não aderiu à Luna'.format(atendimento.numero)
        }

    template = config.LUNA_MENSAGEM_DOCUMENTO_PENDENTE.format(
        atendimento=atendimento,
        documento=documento
    )

    return chatbot_notificar_requerente(
        atendimento=atendimento,
        requerente=requerente,
        mensagem=template
    )


# envia uma notificacao para o requerente de um encaminhamento externo
@shared_task
@executar_se_constance_ativo('USAR_NOTIFICACOES_ASSISTIDO_VIA_CHATBOT')
def chatbot_notificar_requerente_encaminhamento_externo(numero, encaminhamento_id):
    atendimento = AtendimentoDefensor.objects.get(numero=numero)
    encaminhamento = Encaminhamento.objects.get(id=encaminhamento_id)
    requerente = get_requerente_atendimento(atendimento)

    if requerente is None:
        return {
            'sucesso': False,
            'mensagem': 'O requerente principal do atendimento {} não aderiu à Luna'.format(atendimento.numero)
        }

    template = config.LUNA_MENSAGEM_ENCAMINHAMENTO_EXTERNO.format(
        atendimento=atendimento,
        encaminhamento=encaminhamento
    )

    return chatbot_notificar_requerente(
        atendimento=atendimento,
        requerente=requerente,
        mensagem=template
    )


# envia uma notificacao para o requerente de um atendimento que foi excluído
@shared_task
@executar_se_constance_ativo('USAR_NOTIFICACOES_ASSISTIDO_VIA_CHATBOT')
def chatbot_notificar_requerente_exclusao(numero):
    atendimento = AtendimentoDefensor.objects.get(numero=numero)
    requerente = get_requerente_atendimento(atendimento)

    if requerente is None:
        return {
            'sucesso': False,
            'mensagem': 'O requerente principal do atendimento {} não aderiu à Luna'.format(atendimento.numero)
        }

    template = config.LUNA_MENSAGEM_AGENDAMENTO_EXCLUSAO.format(atendimento=atendimento)

    return chatbot_notificar_requerente(
        atendimento=atendimento,
        requerente=requerente,
        mensagem=template
    )
