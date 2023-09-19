from django.conf import settings
from django.core.mail import send_mail

from celery import shared_task
from constance import config

from processo.processo.models import Manifestacao


@shared_task
def enviar_email_confirmacao_protocolo(manifestacao_id):

    manifestacao = Manifestacao.objects.get(id=manifestacao_id)

    if manifestacao.situacao != Manifestacao.SITUACAO_PROTOCOLADO:
        return {
            'sucesso': False,
            'mensagem': 'A manifestação ainda não foi protocolada'
        }

    if len(config.EMAIL_PROCESSO_MANIFESTACAO_PROTOCOLO) == 0:
        return {
            'sucesso': False,
            'mensagem': 'Não há mensagem configura em EMAIL_PROCESSO_MANIFESTACAO_PROTOCOLO'
        }

    lista_distribuicao = []

    for requerente in manifestacao.parte.atendimento.requerentes:
        if requerente.pessoa.email:
            lista_distribuicao.append(requerente.pessoa.email)

    if len(lista_distribuicao) == 0:
        return {
            'sucesso': False,
            'mensagem': 'Nenhum requerente possui e-mail cadastrado'
        }

    template = config.EMAIL_PROCESSO_MANIFESTACAO_PROTOCOLO.format(manifestacao=manifestacao)

    send_mail(
        '[SOLAR] Confirmação de Protocolo de Processo',
        '',
        settings.DEFAULT_FROM_EMAIL,
        lista_distribuicao,
        html_message=template,
        fail_silently=False,
    )

    return {
        'sucesso': True,
        'mensagem': 'E-mail enviado com sucesso!'
    }
