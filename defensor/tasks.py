# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging
from datetime import datetime, timedelta

# Bibliotecas de terceiros
from celery import shared_task
from django.db.models import F, Q
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail

# Solar
from contrib.models import Defensoria
from procapi_client.services import APIAviso
from processo.processo.models import Distribuicao, Parte, Processo

# Modulos locais
from .services import consultar_api_plantao, desativa_atuacao
from .models import Atuacao, Defensor

__author__ = 'amx-dev'
logger = logging.getLogger(__name__)


@shared_task
def verifica_plantao_api():
    try:
        consultar_api_plantao()
    except KeyError:
        logger.error(u'ERRO ao Acessar e carregar dados do plantão = {0}'.format(datetime.now()))
        return False
    return True


@shared_task
def desativa_atuacao_encerrada():
    try:
        resposta = desativa_atuacao()
        return u'Processado fila: {0} registros afetados em {1}'.format(resposta, datetime.now())
    except Exception as e:
        logger.error(u'ERRO ao desativar atuações em {0}, erro {1}'.format(datetime.now(), e))
        return False


@shared_task(queue="prioridade")
def enviar_email_extrato_plantao(data_final=None, dias=1):

    # Obtém lista de atuações do plantão que encerraram agora
    atuacoes = Atuacao.objects.filter(
        defensoria__nucleo__plantao=True
    ).order_by(
        'defensoria_id'
    ).distinct(
        'defensoria_id'
    )

    if data_final:
        atuacoes = atuacoes.filter(data_final=data_final)
    else:
        termino = datetime.now()
        inicio = termino - timedelta(days=dias)
        atuacoes = atuacoes.filter(data_final__range=[inicio, termino], foi_enviado_email_plantao=False)

    total_emails = 0

    for atuacao in atuacoes:

        # Obtém lista de processos cadastrados no plantão
        partes = Parte.objects.filter(
            defensoria_cadastro=atuacao.defensoria,
            data_cadastro__range=[atuacao.data_inicial, atuacao.data_final],
            ativo=True
        )

        # Identifica setor(es) que serão notificados com a lista completa
        if atuacao.defensoria.mae:
            total_emails += enviar_email_extrato_plantao_defensoria(atuacao, atuacao.defensoria.mae, partes, True, False)  # noqa: E501

        # Obtém lista de defensorias responsáveis pelos processos originados no plantão
        defensorias_ids = partes.order_by(
            'defensoria'
        ).distinct().values_list(
            'defensoria', flat=True
        )

        # Envia e-mail para cada defensoria responsável com a lista dos processos originados no plantão
        for defensoria_id in defensorias_ids:

            defensoria = Defensoria.objects.get(id=defensoria_id)

            partes_defensoria = partes.filter(
                defensoria=defensoria
            )

            total_emails += enviar_email_extrato_plantao_defensoria(atuacao, defensoria, partes_defensoria, False, True)

        # Marca que e-mail da atuação já foi enviado para evitar envio em duplicidade
        atuacao.foi_enviado_email_plantao = True
        atuacao.save()

    return '{} e-mails enviados!'.format(total_emails)


def enviar_email_extrato_plantao_defensoria(atuacao_plantao, defensoria, partes, notificar_defensoria, notificar_defensores):  # noqa: E501

    # TODO: Criar template p/ preenchimento com as tags do Django (ver GED)
    # Monta estrutura do e-mail
    html_message = f'Defensoria Plantão: <b>{atuacao_plantao.defensoria.nome}</b><br/>'
    html_message += f'Defensoria Natural: <b>{defensoria.nome}</b><br/>'

    if partes.exists():

        html_message += 'Processo(s):<br/>'
        html_message += '<table style="width: 100%; table-layout: fixed;" cellpadding="3px" border="1px">'

        for parte in partes:
            html_message += '<tr>'
            html_message += f'''
                <td>
                    <a href="https://solar.defensoria.to.def.br/atendimento/{parte.atendimento.numero}/#/processo/{parte.processo.numero_puro}/grau/{parte.processo.grau}">
                        {parte.processo.numero}
                    </a>
                </td>
                <td>{parte.processo.acao}</td>
                <td>{parte.atendimento.requerente}</td>
                <td>{parte.defensoria}</td>
            '''
            html_message += '</tr>'

        html_message += '</table>'

    else:

        html_message += 'Processo(s): <b>Nenhum processo cadastrado no período do plantão</b><br/>'

    html_message += '<i>Resolução-CSDP nº 209, de 19 de abril de 2021.</i></br>'
    html_message += '<i>Notificação enviada automaticamente. Não responda este email.</i>'

    lista_distribuicao = []

    if notificar_defensoria:
        lista_distribuicao.append(defensoria.email)

    if notificar_defensores:
        if defensoria.all_atuacoes.nao_lotacoes().vigentes().exists():
            for atuacao in defensoria.all_atuacoes.nao_lotacoes().vigentes():
                lista_distribuicao.append(atuacao.defensor.servidor.usuario.email)
        else:
            lista_distribuicao.append(atuacao_plantao.defensor.servidor.usuario.email)

    if lista_distribuicao:
        send_mail(
            f'[SOLAR] Relatório de Plantão {atuacao_plantao.data_inicial:%d/%m/%Y} a {atuacao_plantao.data_final:%d/%m/%Y}',  # noqa: E501
            '',
            settings.DEFAULT_FROM_EMAIL,
            lista_distribuicao,
            html_message=html_message,
            fail_silently=False,
        )

    return len(lista_distribuicao)


# busca os defensores que tem processos distribuídos e ainda não receberam um e-mail de extrato recentemente.
@shared_task(queue="prioridade")
def enviar_email_extrato_processos_distribuidos():

    defensores = Distribuicao.objects.filter(
        Q(distribuido_defensor__isnull=False) &
        (
            Q(cadastrado_em__gt=F('distribuido_defensor__data_envio_ultimo_email_distribuicao_processos')) |
            Q(distribuido_defensor__data_envio_ultimo_email_distribuicao_processos=None)
        )
    ).distinct('distribuido_defensor')

    for defensor in defensores:
        enviar_email_extrato_processos_distribuidos_defensor.apply_async(kwargs={
            'defensor_id': defensor.distribuido_defensor_id
        }, queue='geral')


@shared_task(queue="geral")
def enviar_email_extrato_processos_distribuidos_defensor(defensor_id):

    site = Site.objects.get_current()
    defensor = Defensor.objects.get(id=defensor_id)

    html_message = f'Defensor(a): <b>{defensor.nome}</b><br/>'

    html_message += 'Processo(s):<br/>'
    html_message += '<table style="width: 100%; table-layout: fixed;" cellpadding="3px" border="1px">'

    processos_distribuidos = Distribuicao.objects.filter(distribuido_defensor=defensor)

    if defensor.data_envio_ultimo_email_distribuicao_processos is not None:
        processos_distribuidos = processos_distribuidos.filter(
            cadastrado_em__gt=defensor.data_envio_ultimo_email_distribuicao_processos
        )

    data_envio_ultimo_email_distribuicao_processos = None

    for distribuicao in processos_distribuidos.order_by('cadastrado_em'):

        data_envio_ultimo_email_distribuicao_processos = distribuicao.cadastrado_em

        acao_processo = ''
        if distribuicao.processo:
            acao_processo = distribuicao.processo.acao

        numero_processo = Processo.formatar_numero(distribuicao.numero_processo)

        sucesso, resposta = APIAviso().consultar(distribuicao.numero_aviso)
        nome_assistido = resposta['destinatario']['pessoa']['nome']

        html_message += '<tr>'
        html_message += f'''
            <td>
                <a href="https://{site.domain}/processo/listar/?filtro={distribuicao.numero_processo}">
                    {numero_processo}
                </a>
            </td>
            <td>{acao_processo}</td>
            <td>{nome_assistido}</td>
            <td>{distribuicao.distribuido_defensoria}</td>
        '''
        html_message += '</tr>'

    html_message += '</table>'

    html_message += '<i>Notificação enviada automaticamente. Não responda este email.</i>'

    send_mail(
        '[SOLAR] Extrato Processos Distribuídos',
        '',
        settings.DEFAULT_FROM_EMAIL,
        [defensor.servidor.usuario.email],
        html_message=html_message,
        fail_silently=False,
    )

    if data_envio_ultimo_email_distribuicao_processos is not None:
        defensor.data_envio_ultimo_email_distribuicao_processos = data_envio_ultimo_email_distribuicao_processos
        defensor.save()
