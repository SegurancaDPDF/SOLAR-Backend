from celery import shared_task
from constance import config
from django.conf import settings
from django.core.mail import send_mail

from processo.processo.models import Manifestacao


@shared_task
def enviar_email_confirmacao_protocolo(manifestacao_id):

    # obtem a manifestacao com base no ID fornecido
    manifestacao = Manifestacao.objects.get(id=manifestacao_id)

    # verifica se a situacao da manifestacao é protocolo
    if manifestacao.situacao != Manifestacao.SITUACAO_PROTOCOLADO:
        return {
            'sucesso': False,
            'mensagem': 'A manifestação ainda não foi protocolada'
        }

    # verifica se há uma mensagem configurada para o email de confirmação de protocolo
    if len(config.EMAIL_PROCESSO_MANIFESTACAO_PROTOCOLO) == 0:
        return {
            'sucesso': False,
            'mensagem': 'Não há mensagem configura em EMAIL_PROCESSO_MANIFESTACAO_PROTOCOLO'
        }

    # cria uma lista para armazenar os emails dos requerentes da manifestação
    lista_distribuicao = []

    # percorre os requerentes associados à manifestação para obter seus emails
    for requerente in manifestacao.parte.atendimento.requerentes:
        if requerente.pessoa.email:
            lista_distribuicao.append(requerente.pessoa.email)

    # verifica se há pelo menos um email de requerente cadastrado
    if len(lista_distribuicao) == 0:
        return {
            'sucesso': False,
            'mensagem': 'Nenhum requerente possui e-mail cadastrado'
        }

    template = config.EMAIL_PROCESSO_MANIFESTACAO_PROTOCOLO.format(manifestacao=manifestacao)

    # envia o email de confirmacao do protocolo da manifestacao
    send_mail(
        '[SOLAR] Confirmação de Protocolo de Processo',
        '',
        settings.DEFAULT_FROM_EMAIL,
        lista_distribuicao,
        html_message=template,
        fail_silently=False,
    )

    # retorna uma mensagem de sucesso indicando que o email foi enviado
    return {
        'sucesso': True,
        'mensagem': 'E-mail enviado com sucesso!'
    }
