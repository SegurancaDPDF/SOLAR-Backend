# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import json as simplejson

# Bibliotecas de terceiros
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect

# Modulos locais
from .models import Formulario, Nucleo


# funcão para redirecionar o usuário para a página adequada com base no tipo de Núcleo selecionado
@login_required
def index(request, nucleo_id):

    nucleo = Nucleo.objects.get(id=nucleo_id)
    request.session['nucleo'] = nucleo

    # verifica o tipo de núcleo e redireciona para as páginas corretas
    if nucleo.multidisciplinar:
        return redirect('multidisciplinar_index')
    elif nucleo.diligencia:
        return redirect('nucleo_diligencia_index')
    elif nucleo.indeferimento and not nucleo.agendamento:
        return redirect('indeferimento:index', nucleo_id=nucleo.id)
    else:
        return redirect('atendimento_index')


# funcao para listar todos os núcleos ativos em formato JSON
@login_required
def listar(request):
    from contrib.models import Util

    nucleos = Nucleo.objects.filter(ativo=True).order_by('nome')

    return JsonResponse({'success': True, 'nucleos': Util.json_serialize(nucleos)})


# funcão para listar todas as defensorias em formato JSON com base em alguns filtros
@login_required
def listar_defensorias(request):
    from defensor.models import Atuacao
    from contrib.models import Defensoria

    if request.method == 'POST' and request.is_ajax():
        dados = simplejson.loads(request.body)
    else:
        dados = request.GET

    defensorias = Defensoria.objects.filter(
        ativo=True,
        all_atuacoes__tipo=Atuacao.TIPO_TITULARIDADE,
        all_atuacoes__ativo=True,
    ).exclude(
        nucleo=None
    ).order_by(
        'numero',
        'nome',
        'comarca__nome'
    ).values(
        'id',
        'nome',
        'comarca__nome',
        'nucleo__id',
        'nucleo__apoio',
        'nucleo__diligencia',
        'nucleo__indeferimento',
        'nucleo__indeferimento_pode_receber_negacao',
        'nucleo__indeferimento_pode_receber_suspeicao',
        'nucleo__indeferimento_pode_receber_impedimento',
        'nucleo__indeferimento_pode_registrar_decisao',
        'nucleo__indeferimento_pode_registrar_baixa',
    ).distinct()

    # filtros adicionais com base nos parâmetros passados
    if 'nucleo' in dados and dados['nucleo']:
        defensorias = defensorias.filter(nucleo=dados['nucleo'])

    if 'multidisciplinar' in dados:
        multidisciplinar = True if dados['multidisciplinar'] in (True, 'True', 'true') else False
        defensorias = defensorias.filter(nucleo__multidisciplinar=multidisciplinar)

    if 'indeferimento' in dados:
        indeferimento = True if dados['indeferimento'] in (True, 'True', 'true') else False
        defensorias = defensorias.filter(nucleo__indeferimento=indeferimento)

    if 'propac' in dados and dados['propac']:
        defensorias = Defensoria.objects.filter(nucleo__propac=True).order_by('nome').values('id', 'nome')

    return JsonResponse({'success': True, 'defensorias': list(defensorias)})


# funcão para listar os formulários de um núcleo específico em formato JSON
@login_required
def listar_formularios(request, nucleo_id):
    cache_key = 'nucleo.listar_formularios:'
    cache_data = cache.get(cache_key)
    formularios = []

    if not cache_data:

        for formulario in Formulario.objects.filter(nucleo=nucleo_id, ativo=True):

            item = {
                'id': formulario.id,
                'texto': formulario.texto,
                'perguntas': []}

            for pergunta in formulario.perguntas:
                item['perguntas'].append({
                    'id': pergunta.id,
                    'texto': pergunta.texto,
                    'tipo': pergunta.tipo,
                    'alternativas': pergunta.alternativas,
                    'resposta': None})

            formularios.append(item)

        cache_data = formularios
        cache.set(cache_key, cache_data, 60 * 60 * 24 * 30)  # cache 1 mes

    return JsonResponse({'success': True, 'formularios': formularios})
