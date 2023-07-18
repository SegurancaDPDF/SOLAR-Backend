# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from celery import shared_task
from constance import config
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.functions import Length
from django.utils import timezone
from urlobject import URLObject
from django.contrib.sites.models import Site
from django.urls import reverse
# SOLAR
from assistido.models import PessoaAssistida
from atendimento.atendimento.models import Defensor as AtendimentoDefensor
from defensor.models import Atuacao
from processo.processo.models import Manifestacao

# Local
from .utils import send_notify

# Retorna uma lista de usuários associados aos setores especificados.

def get_lista_usuarios_dos_setores(setor_id=None, setores_list=None, somente_responsaveis=False):

    if setor_id is None and setores_list is None:
        raise Exception('Informe um setor ou uma lista de setores')

    agora = timezone.now()
# Constrói as condições da consulta utilizando os objetos Q do Django
    q = Q(cpf_len=11)
    q &= Q(servidor__defensor__all_atuacoes__ativo=True)

    if somente_responsaveis:
        q &= Q(servidor__defensor__all_atuacoes__tipo__in=[
            Atuacao.TIPO_SUBSTITUICAO,
            Atuacao.TIPO_ACUMULACAO,
            Atuacao.TIPO_TITULARIDADE]
        )

    if setor_id:
        q &= Q(servidor__defensor__all_atuacoes__defensoria_id=setor_id)
    else:
        q &= Q(servidor__defensor__all_atuacoes__defensoria_id__in=setores_list)

    q &= Q(servidor__defensor__all_atuacoes__data_inicial__lte=agora)
    q &= (
            Q(servidor__defensor__all_atuacoes__data_final__gte=agora) |
            Q(servidor__defensor__all_atuacoes__data_final=None)
        )

    # recupera lista de usuarios lotados no setor
    usuarios = User.objects.annotate(
        cpf_len=Length('servidor__cpf')
    ).filter(q)

    return usuarios


@shared_task
def notificar_atendimento_liberado(user_remetente_id, url_callback, atendimento_numero):
    """Notifica todos usuarios do setor que atendimento foi liberado pela recepção"""

    if not config.USAR_NOTIFICACOES_SIGNO:
        return 'A notificacao via SIGNO esta desabilitada'

    atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero, ativo=True)

    user_remetente = User.objects.get(id=user_remetente_id)
    users_destinatarios_list = get_lista_usuarios_dos_setores(setor_id=atendimento.defensoria_id)

    # envia notificacao para usuarios
    resposta = send_notify(
        mensagem='{} liberado(a) para ser atendido(a) às {:%d/%m/%Y %H:%M}'.format(
            atendimento.requerente.nome,
            atendimento.data_agendamento
        ),
        titulo='ATENDIMENTO LIBERADO',
        url_callback=url_callback,
        users_destinatarios_list=users_destinatarios_list,
        user_remetente=user_remetente,
        notification_module='recepção')

    if resposta:
        return resposta.json()


@shared_task
def notificar_alteracao_cadastro_assistido(user_remetente_id, url_callback, assistido_id):
    """Notifica todos usuarios dos setores que já atenderam o assistido que seu cadastro foi modificado"""

    if not config.USAR_NOTIFICACOES_SIGNO:
        return 'A notificacao via SIGNO esta desabilitada'

    assistido = PessoaAssistida.objects.get(id=assistido_id)
    defensorias = []

    # procura por todos atendimentos iniciais do asistido e adiciona ultima defensoria que atendeu na lista
    for parte in assistido.atendimentos.filter(ativo=True, atendimento__ativo=True).exclude(atendimento__defensor=None):
        atendimento = parte.atendimento
        defensorias.append(atendimento.at_final.defensoria_id)

    user_remetente = User.objects.get(id=user_remetente_id)
    users_destinatarios_list = get_lista_usuarios_dos_setores(setores_list=set(defensorias))

    # envia notificacao para usuarios
    resposta = send_notify(
        mensagem='{} teve o cadastro alterado em {:%d/%m/%Y %H:%M}'.format(
            assistido.nome,
            assistido.modificado_em
        ),
        titulo='CADASTRO ASSISTIDO ALTERADO',
        url_callback=url_callback,
        users_destinatarios_list=users_destinatarios_list,
        user_remetente=user_remetente,
        notification_module='recepção')

    if resposta:
        return resposta.json()


@shared_task
def notificar_documento_assinado_e_finalizado(user_remetente_id, url_callback, documento_id):
    from djdocuments.models import Documento as DocumentoGED

    if not config.USAR_NOTIFICACOES_SIGNO:
        return 'A notificacao via SIGNO esta desabilitada'

    documento = DocumentoGED.objects.get(id=documento_id)

    user_remetente = User.objects.get(id=user_remetente_id)
    users_destinatarios_list = [documento.criado_por]

    # envia notificacao para usuarios
    resposta = send_notify(
        mensagem='O documento {} foi finalizado em {:%d/%m/%Y %H:%M}'.format(
            documento.identificador_versao,
            documento.modificado_em
        ),
        titulo='DOCUMENTO ASSINADO',
        url_callback=url_callback,
        users_destinatarios_list=users_destinatarios_list,
        user_remetente=user_remetente,
        notification_module='GED')

    if resposta:
        return resposta.json()


@shared_task
def notificar_documento_pronto_para_assinar(user_remetente_id, url_callback, documento_id):
    from djdocuments.models import Documento as DocumentoGED

    if not config.USAR_NOTIFICACOES_SIGNO:
        return 'A notificacao via SIGNO esta desabilitada'

    documento = DocumentoGED.objects.get(id=documento_id)
    assinaturas = documento.assinaturas.filter(ativo=True, esta_assinado=False)
    users_destinatarios_list = []

    # descobre assinante quando não tem assinado_por
    assinaturas_grupo = assinaturas.filter(assinado_por=None).values_list('grupo_assinante_id', flat=True)
    users_destinatarios_list = tuple(get_lista_usuarios_dos_setores(
        setores_list=assinaturas_grupo,
        somente_responsaveis=True
    ))

    # envia direto para assinante quando assinado_por for especificado
    assinaturas_usuario = assinaturas.exclude(assinado_por=None).values_list('assinado_por_id', flat=True)
    users_destinatarios_list += tuple(User.objects.filter(id__in=assinaturas_usuario))

    user_remetente = User.objects.get(id=user_remetente_id)

    # envia notificacao para usuarios
    resposta = send_notify(
        mensagem='O documento {} está pronto para ser assinado'.format(
            documento.identificador_versao
        ),
        titulo='ASSINATURA PENDENTE',
        url_callback=url_callback,
        users_destinatarios_list=set(users_destinatarios_list),
        user_remetente=user_remetente,
        notification_module='GED')

    if resposta:
        return resposta.json()


@shared_task
def notificar_pendencia_assinatura(user_remetente_id, url_callback, assinatura_id):
    from djdocuments.models import Assinatura as AssinaturaGED

    if not config.USAR_NOTIFICACOES_SIGNO:
        return 'A notificacao via SIGNO esta desabilitada'

    assinatura = AssinaturaGED.objects.get(id=assinatura_id, ativo=True)
    users_destinatarios_list = []

    if assinatura.assinado_por:
        users_destinatarios_list = [assinatura.assinado_por]
    else:
        users_destinatarios_list = tuple(get_lista_usuarios_dos_setores(
            setor_id=assinatura.grupo_assinante_id,
            somente_responsaveis=True
        ))

    user_remetente = User.objects.get(id=user_remetente_id)

    # envia notificacao para usuarios
    resposta = send_notify(
        mensagem='O documento {} está pronto para ser assinado'.format(
            assinatura.documento.identificador_versao
        ),
        titulo='ASSINATURA PENDENTE',
        url_callback=url_callback,
        users_destinatarios_list=set(users_destinatarios_list),
        user_remetente=user_remetente,
        notification_module='GED')

    if resposta:
        return resposta.json()


@shared_task
def notificar_manifestacao_em_analise(manifestacao_id):
    if not config.USAR_NOTIFICACOES_SIGNO:
        return 'A notificacao via SIGNO esta desabilitada'

    manifestacao = Manifestacao.objects.get(id=manifestacao_id)

    url_callback = URLObject(
            reverse('peticionamento:visualizar', kwargs={'pk':manifestacao.id})
        )
    
    url_callback = '{}{}'.format(Site.objects.get_current().domain, url_callback)

    users_destinatarios_list = tuple(get_lista_usuarios_dos_setores(
            setor_id=manifestacao.defensoria.id,
            somente_responsaveis=True
        ))

    user_remetente = User.objects.get(id=manifestacao.cadastrado_por.id)

    # envia notificacao para usuarios
    resposta = send_notify(
        mensagem='A manifestação {} está pronto para análise'.format(
            manifestacao.id
        ),
        titulo='MANIFESTAÇÃO AGUARDANDO ANÁLISE',
        url_callback=url_callback,
        users_destinatarios_list=set(users_destinatarios_list),
        user_remetente=user_remetente,
        notification_module='PETICIONAMENTO')

    if resposta:
        return resposta.json()

@shared_task
def notificar_manifestacao_protocolada(manifestacao_id):

    if not config.USAR_NOTIFICACOES_SIGNO:
        return 'A notificacao via SIGNO esta desabilitada'

    manifestacao = Manifestacao.objects.get(id=manifestacao_id)

    url_callback = URLObject(
            reverse('peticionamento:visualizar', kwargs={'pk':manifestacao.id})
        )
    
    url_callback = '{}{}'.format(Site.objects.get_current().domain, url_callback)

    user_remetente = User.objects.get(id=manifestacao.enviado_por.id)


# envia notificacao para usuarios
    resposta = send_notify(
        mensagem='A manifestação {} foi protocolada'.format(
            manifestacao.id
        ),
        titulo='MANIFESTAÇÃO PROTOCOLADA COM SUCESSO' if manifestacao.situacao==Manifestacao.SITUACAO_PROTOCOLADO else 'MANIFESTAÇÃO COM ERRO DE PROTOCOLO',
        url_callback=url_callback,
        users_destinatarios_list=[user_remetente],
        user_remetente=user_remetente,
        notification_module='PETICIONAMENTO')
    print(resposta)
    if resposta:
        return resposta.json()

@shared_task
def notificar_processo_de_indeferimento(user_remetente_id, processo_id=None):

    if not config.USAR_NOTIFICACOES_SIGNO:
        return 'A notificacao via SIGNO esta desabilitada'
        
    from indeferimento.models import Indeferimento

    indeferimento = Indeferimento.objects.get(processo__id = processo_id)
    
    
    url_callback = URLObject(
            reverse('indeferimento:ver_solicitacao',
             kwargs={
                 'nucleo_id': indeferimento.processo.setor_encaminhado.nucleo.id,
                 'processo_uuid':indeferimento.processo.uuid,
                 'setor_id': indeferimento.processo.setor_encaminhado.id
                 }
             )
        )
    
    url_callback = '{}{}'.format(Site.objects.get_current().domain, url_callback)

    user_remetente = User.objects.get(id=user_remetente_id)

    users_destinatarios_list = tuple(get_lista_usuarios_dos_setores(
            setor_id=indeferimento.processo.setor_encaminhado.id,
            somente_responsaveis=False
        ))

    # envia notificacao para usuarios
    resposta = send_notify(
        mensagem='Atenção: O processo de indeferimento/impedimento/suspeição nº {} chegou para análise'.format(
            indeferimento.processo.numero
        ),
        titulo='NOTIFICAÇÃO - RECEBIMENTO DE PROCESSO',
        url_callback=url_callback,
        users_destinatarios_list=set(users_destinatarios_list),
        user_remetente=user_remetente,
        notification_module='INDEFERIMENTO')
    print(resposta)
    if resposta:
        return resposta.json()
