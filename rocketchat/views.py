# standard
import json
from datetime import datetime
from secrets import compare_digest

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db.transaction import atomic, non_atomic_requests
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# third-party
import requests
from constance import config

# project
from atendimento.atendimento.models import Atendimento
from atendimento.atendimento.models import Documento as AtendimentoDocumento
from atendimento.atendimento.models import PastaDocumento


def chat_com_assistido(request, uuid_atendimento):
    atendimento = Atendimento.objects.get(uuid=uuid_atendimento)
    pessoa = atendimento.get_requerente()
    pode_abrir_link = False
    esta_na_hora_marcada = False

    data_hora = atendimento.data_agendamento
    data_hora_atual = datetime.now()
    diferenca = atendimento.data_agendamento - data_hora_atual

    if diferenca.seconds <= 900 or diferenca.seconds >= 85500:  # 15 minutos antes ou depois
        esta_na_hora_marcada = True

    if atendimento:
        pode_abrir_link = True

    return render(request=request, template_name="rocketchat/atendimento_chat.html", context=locals())


@csrf_exempt
@require_POST
@non_atomic_requests
def webhook(request, *args, **kwargs):
    given_token = request.headers.get("X-Rocketchat-Livechat-Token", "")

    if not compare_digest(given_token, config.WEBHOOK_ROCKET_TOKEN):
        return HttpResponseForbidden(
            "Token Incorreto.",
            content_type="text/plain",
        )

    payload = json.loads(request.body)
    if not payload.get('topic'):  # processa payload somente quando não é teste
        processa_webhook_payload(request, payload)
    return HttpResponse("Payload recebido.", content_type="text/plain")


@atomic
def processa_webhook_payload(request, payload):
    numero_atendimento = payload['visitor']['customFields']['link_atendimento_solar'][-13:-1]
    usuario = User.objects.filter(username=payload['agent']['username']).last().servidor
    if not usuario:
        usuario = User.objects.filter(servidor__ativo=True).first().servidor

    historico = "Atendimento realizado via RocketChat."
    conversa = processa_chat(payload['messages'], numero_atendimento)

    arquivo = ContentFile(conversa.encode('utf-8'))
    arquivo.content_type = 'text/plain'

    Atendimento.objects.filter(numero=numero_atendimento).update(
        historico=historico,
        data_atendimento=datetime.now(),
        atendido_por=usuario
    )

    atendimento = Atendimento.objects.get(numero=numero_atendimento)

    pasta_documento_rocket = PastaDocumento.objects.filter(
        atendimento__numero=numero_atendimento,
        nome="Conversas Rocket.Chat"
    ).first()

    if pasta_documento_rocket is None:
        pasta_documento_rocket = PastaDocumento(
            atendimento=atendimento,
            nome="Conversas Rocket.Chat",
            descricao="Pasta gerada automaticamente para armazenamento de conversas"
        )
        pasta_documento_rocket.save()

    atendimento_documento = AtendimentoDocumento(
        atendimento=atendimento,
        nome="{}.txt".format(datetime.now().strftime('%d/%m/%Y às %H:%M:%S')),
        data_enviado=datetime.now()
    )
    atendimento_documento.pasta = pasta_documento_rocket
    atendimento_documento.arquivo.save('conversa_rocket_chat.txt', arquivo)
    atendimento_documento.save()


def insere_arquivos_atendimento(arquivo, numero_atendimento):
    url = arquivo['fileUpload']['publicFilePath']
    upload = ContentFile(requests.get(url, verify=False).content, name=arquivo['file']['name'])

    AtendimentoDocumento(
        atendimento=Atendimento.objects.get(numero=numero_atendimento),
        nome=arquivo['file']['name'],
        data_enviado=datetime.now(),
        analisar=True,
        arquivo=upload
    ).save()


def processa_chat(mensagens, numero_atendimento):
    chat = "Para iniciar esta conversa o assistido concordou com a afirmaçao abaixo:\n"
    chat += "'Você concorda que seus dados pessoais serão processados "
    chat += "e transmitidos de acordo com a Lei Geral de Proteção "
    chat += "de Dados?'\n\n"
    for mensagem in mensagens:
        if mensagem.get('msg'):
            chat += '{} disse: \n"{}"'.format(mensagem['u']['name'], mensagem['msg'])
        if mensagem.get('attachments'):
            chat += '{} enviou o seguinte arquivo: {}'.format(
                mensagem['u']['name'],
                processa_nomes_arquivos(mensagem['attachments'])
            )
            insere_arquivos_atendimento(mensagem, numero_atendimento)
        formato = '%Y-%m-%dT%H:%M:%S.%fz'
        chat += '\nEm {}\n\n'.format(str(datetime.strptime(mensagem['ts'], formato).strftime('%d/%m/%Y às %H:%M:%S')))

    return chat


def processa_nomes_arquivos(arquivos):
    anotacao_arquivos = ""
    for arquivo in arquivos:
        anotacao_arquivos += arquivo['title']
    return anotacao_arquivos
