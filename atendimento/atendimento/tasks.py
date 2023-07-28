# -*- coding: utf-8 -*-
from django.db.models.functions import Coalesce

from defensor.models import Defensor

__author__ = 'lucas.mo'

# Bibliotecas Padrao
from datetime import datetime
import json as simplejson

# Bibliotecas de terceiros
from celery import shared_task
from django.db import transaction
from django.db.models import Sum, Case, When, Value, IntegerField, F, Q

# SOLAR
from contrib.models import Util, Servidor

# Local
from .models import Atendimento, Documento, Defensor as AtendimentoDefensor, Arvore, Acordo, Pessoa


@shared_task
@transaction.atomic
def atendimento_cria_arvore(numero):
    """Utilizado para criar e atualizar o json da árvore de atendimento que é salvo em atendimento_arvore"""
    atendimento = AtendimentoDefensor.objects.filter(numero=numero, ativo=True, remarcado=None).first()

    if not atendimento:
        return None

    inicial = atendimento.at_inicial
    arvore = Arvore.objects.filter(atendimento=inicial).first()
    data_exclusao = None

    if arvore:
        data_exclusao = arvore.data_exclusao  # guarda data/hora da ultima revogacao da arvore

    datahora_inicio_task = datetime.now()  # guarda data/hora de inicio do processamento

    tipos_atendimentos = [Atendimento.TIPO_INICIAL,
                          Atendimento.TIPO_RETORNO,
                          Atendimento.TIPO_PROCESSO,
                          Atendimento.TIPO_VISITA,
                          Atendimento.TIPO_INTERESSADO,
                          Atendimento.TIPO_ENCAMINHAMENTO,
                          Atendimento.TIPO_ANOTACAO,
                          Atendimento.TIPO_NOTIFICACAO,
                          Atendimento.TIPO_ARQUIVAMENTO,
                          Atendimento.TIPO_DESARQUIVAMENTO]
    atendimentos_ids = [inicial.id]

    '''
        Atenção: Abordagem de vários filters individuais é proposital,
        o uso aninhado de Q em um único filter pode provocar muitos LEFT JOINS's
        sendo que alguns deles podem provocar FULL TABLE SCAN (mesmo existindo index)
    '''
    # Busca atendimento  do tipo retornos
    atendimentos_ids.extend(AtendimentoDefensor.objects.filter(
        inicial=inicial.id, tipo__in=tipos_atendimentos
        ).values_list('id', flat=True))
    # Busca atendimento  do tipo remarcados
    atendimentos_ids.extend(AtendimentoDefensor.objects.filter(
        remarcado=inicial.id, tipo__in=tipos_atendimentos
        ).values_list('id', flat=True))
    # Busca atendimento do tipo anotações ou alertas
    atendimentos_ids.extend(AtendimentoDefensor.objects.filter(
        origem=inicial.id, tipo__in=tipos_atendimentos
        ).values_list('id', flat=True))
    # Busca atendimento  do tipo anotações ou alertas
    atendimentos_ids.extend(AtendimentoDefensor.objects.filter(
        origem__inicial=inicial.id, tipo__in=tipos_atendimentos
        ).values_list('id', flat=True))

    # recupera historico de atendimentos baseado nos ID's
    atendimentos_lst = AtendimentoDefensor.objects.filter(
        id__in=atendimentos_ids
        ).annotate(
        tem_apoio=Sum(Case(When(filhos__ativo=True, filhos__tipo=Atendimento.TIPO_NUCLEO, then=Value(1)),
                      default=Value(0), output_field=IntegerField())),
    )

    assuntos_lst = atendimentos_lst.filter(
        assuntos__ativo=True
    ).values(
        'numero',
        'assuntos__id',
        'assuntos__titulo',
        'assuntos__descricao',
    )

    assuntos = {}
    for assunto in assuntos_lst:

        if not assunto['numero'] in assuntos:
            assuntos[assunto['numero']] = {}

        assuntos[assunto['numero']][assunto['assuntos__id']] = {
            'titulo': assunto['assuntos__titulo'],
            'descricao': assunto['assuntos__descricao'],
        }

    atendimentos_lst = atendimentos_lst.values(
        'id',
        'numero',
        'tipo',
        'data_cadastro',
        'data_agendamento',
        'data_atendimento',
        'data_finalizado',
        'data_modificacao',
        'data_exclusao',
        'inicial_id',
        'nucleo__nome',
        'nucleo__multidisciplinar',
        'nucleo__diligencia',
        'defensoria__id',
        'defensoria__nome',
        'defensor__id',
        'defensor__servidor__nome',
        'substituto_id',
        'agendado_por_id',
        'atendido_por_id',
        'cadastrado_por_id',
        'modificado_por_id',
        'excluido_por_id',
        'historico',
        'historico_recepcao',
        'acordo__id',
        'acordo__tipo',
        'acordo__termo__arquivo',
        'acordo__ativo',
        'qualificacao__id',
        'qualificacao__titulo',
        'qualificacao__area__nome',
        'atendimento__interessado__nome',
        'remarcado_id',
        'motivo_exclusao',
        'ativo',
        'atendimento__prisao_id',
        'atendimento__estabelecimento_penal_id',
        'atendimento__estabelecimento_penal__nome',
        'tem_apoio',
        'forma_atendimento_id',
        'forma_atendimento__nome',
    ).order_by(
        Coalesce('data_atendimento', 'data_agendamento'),
        'id'
    )

    atendimentos = []

    for a in atendimentos_lst:

        # Hack para diferenciar 'retorno' do 'pedido de apoio'
        if a['tem_apoio']:
            a['tipo'] = Atendimento.TIPO_NUCLEO_PEDIDO

        if len(atendimentos) and atendimentos[-1]['id'] == a['id']:

            obj = atendimentos[-1]

        else:

            agendado_por_nome = None
            if a['agendado_por_id']:
                servidor = Servidor.objects.filter(id=a['agendado_por_id']).values_list('nome', flat=True).order_by()
                agendado_por_nome = servidor[0]

            atendido_por_nome = None
            if a['atendido_por_id']:
                servidor = Servidor.objects.filter(id=a['atendido_por_id']).values_list('nome', flat=True).order_by()
                atendido_por_nome = servidor[0]

            cadastrado_por_nome = None
            if a['cadastrado_por_id']:
                servidor = Servidor.objects.filter(id=a['cadastrado_por_id']).values_list('nome', flat=True).order_by()
                cadastrado_por_nome = servidor[0]

            modificado_por_nome = None
            if a['modificado_por_id']:
                servidor = Servidor.objects.filter(id=a['modificado_por_id']).values_list('nome', flat=True).order_by()
                modificado_por_nome = servidor[0]

            excluido_por_nome = None
            if a['excluido_por_id']:
                servidor = Servidor.objects.filter(id=a['excluido_por_id']).values_list('nome', flat=True).order_by()
                excluido_por_nome = servidor[0]

            substituto_nome = None
            if a['substituto_id']:
                servidor = Defensor.objects.filter(
                    id=a['substituto_id']
                ).values_list(
                    'servidor__nome',
                    flat=True
                ).order_by()
                substituto_nome = servidor[0]

            # variável utilizada para mostrar a hora Extra-Pauta
            extra_pauta = False
            if (a['data_agendamento'] and a['data_agendamento'].hour == 0 and a['data_agendamento'].minute == 0 and
                    a['data_agendamento'].second == 0):
                extra_pauta = True

            obj = {
                'id': a['id'],
                'numero': a['numero'],
                'tipo': [a['tipo'], dict(AtendimentoDefensor.LISTA_TIPO).get(a['tipo'])],
                'data_cadastro': Util.date_to_json(a['data_cadastro']) if a['data_cadastro'] else None,
                'data_agendamento': Util.date_to_json(a['data_agendamento']) if a['data_agendamento'] else None,
                'extra_pauta': extra_pauta,
                'data_atendimento': Util.date_to_json(a['data_atendimento']) if a['data_atendimento'] else None,
                'data_finalizado': Util.date_to_json(a['data_finalizado']) if a['data_finalizado'] else None,
                'data_modificacao': Util.date_to_json(a['data_modificacao']) if a['data_modificacao'] else None,
                'data_exclusao': Util.date_to_json(a['data_exclusao']) if a['data_exclusao'] else None,
                'inicial_id': a['inicial_id'],
                'nucleo': a['nucleo__nome'],
                'multidisciplinar': a['nucleo__multidisciplinar'],
                'diligencia': a['nucleo__diligencia'],
                'defensoria_id': a['defensoria__id'],
                'defensoria': a['defensoria__nome'],
                'defensor_id': a['defensor__id'],
                'defensor': a['defensor__servidor__nome'],
                'substituto': substituto_nome,
                'agendado_por': agendado_por_nome,
                'atendido_por': atendido_por_nome,
                'cadastrado_por': cadastrado_por_nome,
                'modificado_por': modificado_por_nome,
                'excluido_por': excluido_por_nome,
                'historico': a['historico'],
                'historico_recepcao': a['historico_recepcao'],
                'realizado': False if a['data_atendimento'] is None else True,
                'anotacao': a['tipo'] == AtendimentoDefensor.TIPO_ANOTACAO,
                'arquivamento': a['tipo'] == AtendimentoDefensor.TIPO_ARQUIVAMENTO,
                'desarquivamento': a['tipo'] == AtendimentoDefensor.TIPO_DESARQUIVAMENTO,
                'notificacao': a['tipo'] == AtendimentoDefensor.TIPO_NOTIFICACAO,
                'processo': a['tipo'] == AtendimentoDefensor.TIPO_PROCESSO,
                'filhos': [],
                'documentos': [],
                'pessoas': {},
                'area': a['qualificacao__area__nome'],
                'qualificacao': a['qualificacao__titulo'],
                'qualificacao_id': a['qualificacao__id'],
                'assuntos': None,
                'interessado': a['atendimento__interessado__nome'],
                'remarcado': a['remarcado_id'],
                'motivo_exclusao': a['motivo_exclusao'],
                'forma_atendimento_id': a['forma_atendimento_id'],
                'forma_atendimento': a['forma_atendimento__nome'],
                'ativo': a['ativo'] and a['remarcado_id'] is None,
            }

            # Carrega dados de atendimento ao preso
            if a['atendimento__prisao_id'] and a['atendimento__estabelecimento_penal_id']:
                obj['preso'] = {
                    'estabelecimento_penal_id': a['atendimento__estabelecimento_penal_id'],
                    'estabelecimento_penal': a['atendimento__estabelecimento_penal__nome']
                }

            if a['acordo__ativo']:

                acordo_termo = None
                if a['acordo__termo__arquivo']:
                    acordo_termo = Acordo.objects.get(id=a['acordo__id']).termo.arquivo.url

                obj.update({
                    'acordo_id': a['acordo__id'],
                    'acordo_tipo': dict(Acordo.LISTA_TIPO)[a['acordo__tipo']] if a['acordo__tipo'] is not None else None, # noqa
                    'acordo_termo': acordo_termo,
                })

            if obj['numero'] in assuntos:
                obj['assuntos'] = assuntos[obj['numero']]

            atendimentos.append(obj)

        # busca as partes do atendimento
        if a['tipo'] == AtendimentoDefensor.TIPO_INICIAL:
            partes = Pessoa.objects.filter(
                atendimento_id=a['id'],
                atendimento__tipo=AtendimentoDefensor.TIPO_INICIAL,
                ativo=True
            ).only(
                'pessoa__id',
                'pessoa__nome',
                'pessoa__cpf'
            ).order_by()

            for parte in partes:
                obj['pessoas'][parte.pessoa.id] = {
                    'id': parte.pessoa.id,
                    'nome': parte.pessoa.nome,
                    'cpf': parte.pessoa.cpf
                }

        atendimento_loop = AtendimentoDefensor.objects.filter(id=a['id']).first()

        # busca os documentos do atendimento que está no atendimento_loop (está no loop de atendimento_lst)
        if a['ativo']:
            documentos = Documento.objects.filter(
                atendimento_id=a['id'],
                ativo=True
            ).all().only(
                'id',
                'nome',
                'arquivo'
            ).order_by()

            for documento in documentos:
                obj['documentos'].append({
                    'id': documento.id,
                    'nome': documento.nome,
                    'arquivo': documento.arquivo.url if documento.arquivo else None
                })

        if atendimento_loop.filhos.exists():
            for b in atendimento_loop.filhos.annotate(
                defensoria_id=F('defensor__defensoria_id'),
                defensoria_nome=F('defensor__defensoria__nome'),
            ).ativos().all().only(
                'id',
                'tipo',
                'numero',
                'historico',
                'qualificacao__id',
                'qualificacao__titulo',
                'atendido_por__nome',
                'data_agendamento',
                'data_atendimento'
            ).order_by(
                Coalesce('data_atendimento', 'data_agendamento'),
                'id'
            ):

                qualificacao_titulo = None
                qualificacao_id = None

                if b.qualificacao:
                    qualificacao_titulo = b.qualificacao.titulo
                    qualificacao_id = b.qualificacao.id

                atendido_por_nome = None

                if b.atendido_por:
                    atendido_por_nome = b.atendido_por.nome

                data_agendamento = None

                if b.data_agendamento:
                    data_agendamento = Util.date_to_json(b.data_agendamento)

                data_atendimento = None

                if b.data_atendimento:
                    data_atendimento = Util.date_to_json(b.data_atendimento)

                # tratamento dos dados em caso de Acordo no atendimento_filho
                acordo_id = None
                acordo_tipo = None
                acordo_arquivo = None

                acordo = Acordo.objects.filter(
                    atendimento_id=b.id,
                    ativo=True
                ).select_related(
                    'termo'
                ).only(
                    'id',
                    'termo__arquivo',
                    'tipo'
                ).first()

                if acordo and acordo.ativo:

                    acordo_id = acordo.id

                    if acordo.tipo:
                        acordo_tipo = dict(Acordo.LISTA_TIPO).get(acordo.tipo)

                    if acordo.termo and acordo.termo.arquivo:
                        acordo_arquivo = str(acordo.termo.arquivo.url)

                obj['filhos'].append({
                    'id': b.id,
                    'tipo': b.tipo,
                    'numero': b.numero,
                    'historico': b.historico,
                    'qualificacao': qualificacao_titulo,
                    'qualificacao_id': qualificacao_id,
                    'defensoria_id': b.defensoria_id,
                    'defensoria': b.defensoria_nome,
                    'atendido_por': atendido_por_nome,
                    'data_agendamento': data_agendamento,
                    'data_atendimento': data_atendimento,
                    'acordo_id': acordo_id,
                    'acordo_tipo': acordo_tipo,
                    'acordo_termo': acordo_arquivo
                 })

    for a in atendimentos:
        a['pessoas'] = [i for i in iter(a['pessoas'].values())]

    # Reordena remarcados para antes do atendimento novo
    for i, a in enumerate(atendimentos):
        if a['remarcado']:
            for j, b in enumerate(atendimentos):
                if b['id'] == a['remarcado']:
                    atendimentos.insert(j, atendimentos.pop(i))
                    break

    # verifica se a data da revogação foi alterada durante o processamento da task
    if data_exclusao:
        revogada_durante_a_task = Arvore.objects.filter(
            atendimento=inicial,
            data_exclusao__gt=data_exclusao
        ).exists()
    else:
        revogada_durante_a_task = Arvore.objects.filter(
            atendimento=inicial,
            data_exclusao__isnull=False
        ).exists()

    # dados de atualização da árvore
    data = {
        'conteudo': simplejson.dumps(atendimentos),
        'data_modificacao': datahora_inicio_task,
    }

    # atualiza status somente se a árvore não foi revogada durante o processamento da task
    if not revogada_durante_a_task:
        data.update({
            'data_exclusao': None,
            'ativo': True
        })

    # atualiza dados da árvore
    arvore, novo = Arvore.objects.update_or_create(
        atendimento=inicial,
        defaults=data
    )

    return arvore


def atendimento_buscar_acordo():
    pass


@shared_task
def invalidar_avores_atendimento():
    Arvore.objects.filter(ativo=True).update(ativo=False)
