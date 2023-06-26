# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import json as simplejson
import logging
from datetime import datetime

# Bibliotecas de terceiros
from constance import config

from django.views.decorators.cache import never_cache
import reversion
from django.contrib.auth.decorators import login_required, permission_required
from django.core.cache import cache
from django.db.models import F, Prefetch
from django.http import JsonResponse
from django.shortcuts import render


# Solar
from contrib.models import Defensoria, Util
from defensor.models import Defensor

# Modulos locais
from .forms import AgendaForm, EventoForm
from .models import Agenda, Evento


logger = logging.getLogger(__name__)


@login_required
@permission_required('evento.add_evento')
def index(request):

    if request.user.has_perm(perm='evento.auth_evento'):
        diretoria = None
    else:
        diretoria = request.user.servidor.coordenadoria()

    angular = 'EventoCtrl'

    return render(request=request, template_name="evento/index.html", context=locals())


@login_required
@permission_required('evento.delete_evento')
@reversion.create_revision(atomic=False)
def excluir(request):
    if request.method == 'POST':

        dados = simplejson.loads(request.body)
        success = True

        try:

            evento = Evento.objects.get(id=dados['id'])
            evento.excluir(excluido_por=request.user.servidor, excluir_filhos=True)

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_delete(request.user, evento))

        except Exception as e:
            erro = 'Erro ao excluir evento %s \n %s ' % (dados['id'], e)
            logger.error(erro)
            success = False

        return JsonResponse({'success': success})

    return JsonResponse({'success': False})


@login_required
@permission_required('evento.delete_evento')
@reversion.create_revision(atomic=False)
def excluir_parcial(request):
    if request.method == 'POST':

        dados = simplejson.loads(request.body)
        error = None
        success = True

        try:

            # Exclui todos os filhos selecionados
            for filho in dados['eventos']:
                if filho.get('selecionado'):
                    evento = Evento.objects.get(id=filho.get('id'))
                    evento.excluir(excluido_por=request.user.servidor, excluir_filhos=False)

            # Exclui o evento pai se ele também foi selecionado
            if dados.get('selecionado'):

                evento = Evento.objects.get(id=dados.get('id'))
                evento.excluir(excluido_por=request.user.servidor, excluir_filhos=False)

                # Se sobraram filhos ativos, define o primeiro como novo pai dos demais
                if evento.eventos().exists():

                    novo_pai = evento.eventos().first()
                    novo_pai.pai = None
                    novo_pai.save()

                    evento.eventos().update(pai=novo_pai)

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_delete(request.user, evento))

        except Exception as e:
            error = 'Erro ao excluir evento %s \n %s ' % (dados.get('id'), e)
            logger.error(error)
            success = False

        return JsonResponse({'success': success})

    return JsonResponse({'success': False, 'error': error})


@never_cache
@login_required
def listar(request):
    """
    Recupera lista de eventos ativos
    :param request:
    :return: JSON
    """

    cache_key = 'evento.listar:'
    cache_data = cache.get(cache_key)

    if not cache_data:

        # recupera eventos e gera array json
        eventos = Evento.objects.select_related(
            'comarca',
            'defensoria',
            'categoria_de_agenda',
            'cadastrado_por__usuario'
        ).prefetch_related(
            Prefetch(
                'filhos',
                queryset=Evento.objects.select_related(
                    'cadastrado_por__usuario',
                    'comarca',
                    'defensoria',
                    'categoria_de_agenda',
                ).filter(ativo=True)
            )
        ).filter(
            ativo=True,
            pai=None,
            tipo=Evento.TIPO_BLOQUEIO,
            data_fim__gte=datetime.today()
        ).order_by('-data_ini')

        cache_data = eventos_to_dict(eventos)
        try:
            cache.set(cache_key, cache_data)
        except Exception as e:
            logger.error(e.args[0])

    return JsonResponse(cache_data, safe=False)


@never_cache
@login_required
def desbloqueio_listar(request):
    """
    Recupera lista de desbloqueios ativos
    :param request:
    :return: JSON
    """

    cache_key = 'evento.desbloqueio_listar:'
    cache_data = cache.get(cache_key)

    if not cache_data:

        # recupera eventos e gera array json
        eventos = Evento.objects.select_related(
            'comarca',
            'defensoria',
            'cadastrado_por__usuario',
            'autorizado_por__usuario',
        ).prefetch_related(
            Prefetch(
                'filhos',
                queryset=Evento.objects.select_related(
                    'comarca',
                    'defensoria',
                ).filter(ativo=True).order_by('comarca__nome', 'defensoria__numero')
            )
        ).filter(
            ativo=True,
            pai=None,
            tipo=Evento.TIPO_PERMISSAO,
            data_validade__gte=datetime.today()
        ).order_by('-data_ini')

        cache_data = eventos_to_dict(eventos)
        cache.set(cache_key, cache_data)

    return JsonResponse(cache_data, safe=False)


def eventos_to_dict(eventos):

    arr = Util.json_serialize(eventos)

    # passa por todos eventos e inclui eventos filhos
    for i, evento in enumerate(eventos):

        arr[i]['comarca'] = Util.object_to_dict(evento.comarca, {})
        arr[i]['defensoria'] = Util.object_to_dict(evento.defensoria, {})
        arr[i]['categoria_de_agenda'] = Util.object_to_dict(evento.categoria_de_agenda, {})
        arr[i]['eventos'] = Util.json_serialize(evento.filhos.all())

        for j, filho in enumerate(evento.filhos.all()):
            arr[i]['eventos'][j]['comarca'] = Util.object_to_dict(filho.comarca, {})
            arr[i]['eventos'][j]['defensoria'] = Util.object_to_dict(filho.defensoria, {})
            arr[i]['eventos'][j]['categoria_de_agenda'] = Util.object_to_dict(filho.categoria_de_agenda, {})

        if evento.cadastrado_por:
            arr[i]['cadastrado_por'] = {
                'id': evento.cadastrado_por.id,
                'nome': evento.cadastrado_por.nome,
                'username': evento.cadastrado_por.usuario.username
            }

        if evento.autorizado_por:
            arr[i]['autorizado_por'] = {
                'id': evento.autorizado_por.id,
                'nome': evento.autorizado_por.nome,
                'username': evento.autorizado_por.usuario.username
            }

    return arr


@login_required
@permission_required('evento.add_evento')
def salvar(request):
    errors = []
    dados = simplejson.loads(request.body)

    # converte json string para date
    dados['data_ini'] = Util.json_to_date(dados['data_ini'])
    dados['data_fim'] = Util.json_to_date(dados['data_fim'])
    dados['data_validade'] = Util.json_to_date(dados.get('data_validade'))
    eventos = []

    # Evento para diretoria e comarcas
    if 'diretoria' in dados and type(dados['diretoria']) is dict:

        for comarca in dados['diretoria']['comarcas']:

            if 'selected' in comarca and comarca['selected']:

                dados['comarca'] = comarca['id']

                form = EventoForm(dados, instance=Evento(cadastrado_por=request.user.servidor))

                if form.is_valid():

                    if 'pai' in dados:
                        eventos.append(form.save(commit=False))
                    else:
                        evento = form.save()
                        dados['pai'] = evento.id

                else:

                    errors += [({'field': k, 'message': v[0]}) for k, v in form.errors.items()]
                    break

    # Evento para defensor e defensorias
    elif 'defensor' in dados and dados['defensor']:

        atuacoes = dados['defensor']['atuacoes']
        dados['defensor'] = dados['defensor']['id']

        for atuacao in atuacoes:

            dados['defensoria'] = atuacao['defensoria']['id']

            # Verifica se todas as categorias estão selecionadas
            todas_categorias_selecionadas = True
            for categoria in atuacao['defensoria']['categorias_de_agendas']:
                if not categoria.get('selected'):
                    todas_categorias_selecionadas = False

            # Se todas categorias estiverem selecionadas, marca atuação (para criar apenas um evento pra todas)
            if todas_categorias_selecionadas:
                atuacao['selected'] = True

            # Evento por atuação/defensoria
            if atuacao.get('selected'):

                form = EventoForm(dados, instance=Evento(cadastrado_por=request.user.servidor))

                if form.is_valid():

                    if 'pai' in dados:
                        eventos.append(form.save(commit=False))
                    else:
                        evento = form.save()
                        dados['pai'] = evento.id

                else:

                    errors += [({'field': k, 'message': v[0]}) for k, v in form.errors.items()]
                    break

            # Evento por categoria de agenda
            else:

                for categoria in atuacao['defensoria']['categorias_de_agendas']:

                    if categoria.get('selected'):

                        dados['categoria_de_agenda'] = categoria.get('id')

                        form = EventoForm(dados, instance=Evento(cadastrado_por=request.user.servidor))

                        if form.is_valid():

                            if 'pai' in dados:
                                eventos.append(form.save(commit=False))
                            else:
                                evento = form.save()
                                dados['pai'] = evento.id

                        else:

                            errors += [({'field': k, 'message': v[0]}) for k, v in form.errors.items()]
                            break

    # Evento para defensorias
    elif 'defensorias' in dados and dados['defensorias']:

        eventos = []

        for defensoria in dados['defensorias']:

            defensoria = Defensoria.objects.get(id=defensoria)

            dados['defensoria'] = defensoria.id
            dados['comarca'] = defensoria.comarca_id

            form = EventoForm(dados, instance=Evento(cadastrado_por=request.user.servidor))

            if form.is_valid():

                if 'pai' in dados:
                    eventos.append(form.save(commit=False))
                else:
                    evento = form.save()
                    dados['pai'] = evento.id

            else:

                errors += [({'field': k, 'message': v[0]}) for k, v in form.errors.items()]
                break

    # Evento geral (todos)
    else:

        form = EventoForm(dados, instance=Evento(cadastrado_por=request.user.servidor))

        if form.is_valid():
            evento = form.save()
        else:
            errors += [({'field': k, 'message': v[0]}) for k, v in form.errors.items()]

    if len(eventos):
        Evento.objects.bulk_create(eventos)

    return JsonResponse({'success': (len(errors) == 0), 'errors': errors})


@login_required
@permission_required('evento.add_evento')
def agenda_index(request):
    defensor = Defensor.objects.get(id=request.GET.get('defensor'))
    hora_inicial = config.HORA_INICIAL_AGENDA_DEFENSOR
    simultaneos = config.SIMULTANEOS_AGENDA_DEFENSOR
    angular = 'EventoCtrl'

    return render(request=request, template_name="evento/agenda.html", context=locals())


@never_cache
@login_required
def agenda_listar(request, defensor_id):
    """
    Recupera lista de agendas ativas do defensor
    :param request:
    :param defensor_id: id do defensor
    :return: JSON
    """

    cache_key = 'evento.agenda_listar:%s' % defensor_id
    cache_data = cache.get(cache_key)

    if not cache_data:

        # recupera agendas e gera array json
        agendas = Agenda.objects.annotate(
            itinerante=F('atuacao__defensoria__nucleo__itinerante')
        ).select_related(
            'cadastrado_por__usuario',
            'atuacao__defensoria__nucleo',
        ).prefetch_related(
            'atuacao__defensoria__categorias_de_agendas'
        ).filter(
            defensor_id=defensor_id,
            data_fim__gte=datetime.today(),
            pai=None,
            ativo=True)

        arr = []

        # passa por todos eventos e inclui eventos filhos
        for i, agenda in enumerate(agendas):

            arr.append(agenda.to_json())
            arr[i]['pode_excluir'] = not agenda.itinerante

            for filho in agenda.agendas():
                arr[i]['agendas'].append(filho.to_json())

        cache_data = arr
        cache.set(cache_key, cache_data)

    return JsonResponse(cache_data, safe=False)


@never_cache
@login_required
def agenda_listar_por_atuacao(request, atuacao_id):

    # recupera agendas e gera array json
    agendas = Agenda.objects.filter(atuacao_id=atuacao_id, data_fim__gte=datetime.today(), ativo=True)
    arr = []

    # passa por todos eventos e inclui eventos filhos
    for i, agenda in enumerate(agendas):
        arr.append(agenda.to_json())

    return JsonResponse(arr, safe=False)


@login_required
@permission_required('evento.add_evento')
@reversion.create_revision(atomic=False)
def agenda_salvar(request):
    errors = []
    dados = simplejson.loads(request.body)

    # converte json string para date
    dados['data_ini'] = Util.json_to_date(dados['data_ini'])
    dados['data_fim'] = Util.json_to_date(dados['data_fim'])

    for i, atuacao in enumerate(dados['defensor']['atuacoes']):

        if atuacao['agendamento']:

            horarios = []
            conciliacao = {}
            forma_atendimento = {}

            for agenda in atuacao['defensoria']['categorias_de_agendas']:
                conciliacao[agenda['id']] = []

                forma = []
                for dia in range(len(agenda['presencial'])):
                    if agenda['presencial'][dia] == agenda['remoto'][dia]:  # Misto
                        forma.append(None)
                    elif agenda['remoto'][dia]:  # Remoto
                        forma.append('R')
                    else:  # Presencial
                        forma.append('P')

                forma_atendimento[agenda['id']] = forma

            if 'horarios' in atuacao and not atuacao['errors']:

                for index, dia in enumerate(atuacao['horarios']):

                    # preenche campo 'Horario'
                    horarios.append(dia['horarios'])

                    # preenche campo 'Conciliacao'
                    for key, _ in iter(conciliacao.items()):
                        conciliacao[key].append(dia['conciliacao'][str(key)])

                if config.EXIBIR_PRESENCIAL_REMOTO_AGENDAMENTO:
                    conciliacao['forma_atendimento'] = forma_atendimento

                atuacao = {
                    'titulo': dados['titulo'],
                    'data_ini': dados['data_ini'],
                    'data_fim': dados['data_fim'],
                    'atuacao': atuacao['id'],
                    'hora_ini': atuacao['hora_ini'],
                    'hora_fim': atuacao['hora_fim'],
                    'vagas': atuacao['vagas'],
                    'duracao': atuacao['duracao'],
                    'simultaneos': atuacao['simultaneos'],
                    'horarios': None,
                    'conciliacao': simplejson.dumps(conciliacao),
                    'pai': dados['pai'] if 'pai' in dados else None
                }

                form = AgendaForm(atuacao, instance=Agenda(cadastrado_por=request.user.servidor))

                if form.is_valid():

                    agenda = form.save()

                    reversion.set_user(request.user)
                    reversion.set_comment(Util.get_comment_save(request.user, agenda, True))

                    if 'pai' not in dados:
                        dados['pai'] = agenda.id

                else:

                    errors += [({'field': k, 'message': v[0]}) for k, v in form.errors.items()]
                    break

                dados['defensor']['atuacoes'][i] = atuacao

    return JsonResponse({'success': (len(errors) == 0), 'errors': errors})


@login_required
@permission_required('evento.change_evento')
@reversion.create_revision()
def agenda_atualizar(request):

    dados_agenda = simplejson.loads(request.body)
    # recupera agendas e gera array json
    agenda = Agenda.objects.get(
        id=dados_agenda['id'],
        ativo=True)
    agenda.simultaneos = dados_agenda['simultaneos']
    agenda.save()
    return JsonResponse({'success': True})


@login_required
@permission_required('evento.add_evento')
def bloqueio_index(request):

    if request.method == 'POST':
        dados = request.POST.dict()
        dados['comarcas'] = request.POST.getlist('comarcas')
        dados = simplejson.dumps(dados)

    angular = 'EventoCtrl'

    return render(request=request, template_name="evento/bloqueio.html", context=locals())


@login_required
@reversion.create_revision(atomic=False)
def autorizar(request):

    resposta = {'success': False}

    if request.method == 'POST':

        dados = simplejson.loads(request.body)

        if request.user.is_superuser or request.user.has_perm(perm='evento.auth_evento'):

            try:

                evento = Evento.objects.get(id=dados['id'])
                evento.autorizar(request.user.servidor)

                reversion.set_user(request.user)
                reversion.set_comment(Util.get_comment_save(request.user, evento, False))

                resposta = {'success': True}

            except Exception as e:
                erro = 'Erro ao autorizar evento %s \n %s ' % (dados['id'], e)
                resposta = {'success': False, 'error': erro}
                logger.error(erro)

    return JsonResponse(resposta)
