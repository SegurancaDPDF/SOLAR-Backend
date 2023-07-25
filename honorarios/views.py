# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import re
from datetime import date, datetime, time, timedelta

import reversion

from constance import config
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import IntegrityError
from django.db.models import Q, Sum, Max
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.decorators.cache import never_cache

from assistido.models import PessoaAssistida
from atendimento.atendimento.models import Defensor as Atendimento
from contrib import constantes
from contrib.models import Comarca, Util
from contrib.utils import validar_cnpj
from processo.honorarios.models import AlertaProcessoMovimento
from defensor.models import Atuacao, Defensor
from processo.processo.forms import HonorarioFaseForm, AnaliseFaseForm
from processo.processo.models import Parte, Processo, Fase

from .forms import movimentoForm, BuscarHonorariosForm, BuscarAnaliseForm, MovimentoSuspencaoForm, SuspenderForm
from .models import Honorario, Movimento, Analise, Documento


@login_required
@permission_required('honorarios.view_honorario')
def index(request):
    # lógica para filtrar a lista de honorários com base em um parâmetro de busca
    if not request.GET.get('page'):
        request.session['filtro_honorario'] = None

    if request.POST:
        filtro = request.POST.get('filtro_honorario', '')
        request.session['filtro_honorario'] = filtro
        page = ''
    else:
        page = request.GET.get('page')
        if request.session.get('filtro_honorario'):
            filtro = request.session.get('filtro_honorario')
        else:
            filtro = ''

    lista_honorarios = Honorario.objects.filter(
        (
            Q(fase__processo__numero__icontains=filtro) |
            Q(fase__processo__numero_puro__icontains=filtro)
        ) &
        Q(ativo=True) &
        Q(possivel=True)
    )
    dados_honorarios = None
    lista_ultimas_alteracoes = None

    lista_honorarios = lista_honorarios.order_by('situacao', '-data_cadastro').values_list(
                         'id',
                         'fase__processo__numero',
                         'defensor__servidor__nome',
                         'data_cadastro',
                         'situacao'
            )

    paginacao = Paginator(lista_honorarios, 10)

    try:
        processos = paginacao.page(page)
    except PageNotAnInteger:
        processos = paginacao.page(1)
    except EmptyPage:
        processos = paginacao.page(paginacao.num_pages)

    # Dados globais
    total_recursos = Honorario.objects.filter(ativo=True, situacao=Honorario.TIPO_RECURSO).count()
    total_processos_solar = Processo.objects.filter(ativo=True, tipo=Processo.TIPO_EPROC).count()
    total_transitados = Honorario.objects.filter(ativo=True, situacao=Honorario.TIPO_TRANSITADO_JULGADO).count()

    total_transitados_geral = Movimento.objects.filter(ativo=True).exclude(tipo=Movimento.TIPO_ANOTACAO).values('honorario').annotate(max=Max('tipo'))  # noqa: E501
    total_transitados_aguardando = len([x for x in total_transitados_geral if x['max'] == Movimento.TIPO_AGUARDANDO_PET])  # noqa: E501
    total_transitados_peticionado = len([x for x in total_transitados_geral if x['max'] == Movimento.TIPO_PETICAO])
    total_transitados_encaminhado = len([x for x in total_transitados_geral if x['max'] == Movimento.TIPO_ENCAMINHADO_DEF])  # noqa: E501
    total_transitados_protocolado = len([x for x in total_transitados_geral if x['max'] == Movimento.TIPO_PROTOCOLO])
    total_transitados_suspenso = len([x for x in total_transitados_geral if x['max'] == Movimento.TIPO_SUSPENSAO])
    total_transitados_baixado = len([x for x in total_transitados_geral if x['max'] == Movimento.TIPO_BAIXA])

    total_honorarios = Movimento.objects.filter(ativo=True, honorario__ativo=True).aggregate(Sum('valor_efetivo'))
    total_honorarios_estimado = Movimento.objects.filter(ativo=True, honorario__ativo=True).aggregate(Sum('valor_estimado'))  # noqa: E501

    movimentos_realizados = Movimento.objects.filter(ativo=True, honorario__ativo=True).order_by('-data_cadastro')[:4]
    movimentos_realizados = movimentos_realizados.values_list(
                         'honorario__id',
                         'honorario__fase__processo__numero',
                         'data_cadastro',
                         'tipo'
            )

    hoje = date.today()
    suspensos = Honorario.objects.filter(
        Q(ativo=True) &
        Q(suspenso=True) &
        Q(suspenso_ate__gte=date.today()) &
        Q(suspenso_ate__lte=(hoje + timedelta(days=30)))
    ).order_by(
        'suspenso_ate',
    ).values_list(
        'id',
        'fase__processo__numero',
        'defensor__servidor__nome',
        'suspenso_ate'
    )[:10]
    # retorna o resultado renderizado para o template "processo/honorarios/index.html"
    return render(request=request, template_name="processo/honorarios/index.html", context=locals())


@never_cache
@login_required
def processo(request, honorario_id):

    # verificar permissao internamente.

    try:
        honorario = Honorario.objects.get(pk=honorario_id, ativo=True, possivel=True)
    except Honorario.DoesNotExist:
        messages.error(request, u'Erro: Honorário Não encontrado')
        return redirect('index')

    processo = honorario.fase.processo
    atendimento = Atendimento.objects.filter(
        parte__processo=processo,
        parte__ativo=True,
        ativo=True
    ).first()

    anotacoes = honorario.lista_movimentos_geral.filter(tipo=Movimento.TIPO_ANOTACAO)
    aguardando_peticao = honorario.lista_movimentos.filter(tipo=Movimento.TIPO_AGUARDANDO_PET)
    peticao = honorario.lista_movimentos.filter(tipo=Movimento.TIPO_PETICAO)
    encaminhamento_defensor = honorario.lista_movimentos.filter(tipo=Movimento.TIPO_ENCAMINHADO_DEF)
    protocolo = honorario.lista_movimentos.filter(tipo=Movimento.TIPO_PROTOCOLO)
    baixa = honorario.lista_movimentos.filter(tipo=Movimento.TIPO_BAIXA)

    defensores = Defensor.objects.filter(eh_defensor=True, ativo=True)

    movimentos_realizados = Movimento.objects.filter(honorario=honorario, ativo=True, ).order_by('-data_cadastro')

    atualizacoes = AlertaProcessoMovimento.objects.filter(honorario=honorario, ativo=True,).order_by('-data_cadastro')

    return render(request=request, template_name="processo/honorarios/processo.html", context=locals())


@login_required
def honorario_id(request, honorario_id):

    try:
        honorario = Honorario.objects.get(pk=honorario_id, ativo=True)
        data = Util.object_to_dict(honorario)
    except Honorario.DoesNotExist:
        return JsonResponse({'erro': True, 'msg': u'Erro ao recuperar o Honorario id %s' % honorario_id})

    return JsonResponse(data)


# funções de salvamento, edição e visibilidade de movimentos e documentos relacionados aos honorários
@login_required
def salvar_movimento(request):
    tipo = request.POST.get('tipo_movimento', None)
    id = request.POST.get('honorario_id', None)
    if tipo and id:
        movimento = Movimento(honorario_id=id, tipo=int(tipo), cadastrado_por=request.user.servidor)
        form = movimentoForm(request.POST, request.FILES, instance=movimento)

        if form.is_valid():
            form.save()
            messages.success(request, u' Cadastrado com sucesso!')
        else:
            messages.error(request, form.errors)

        return redirect('honorarios_processo', id)
    else:
        messages.error(request, u'Erro ao salvar dados')
        return redirect(index)


@reversion.create_revision(atomic=False)
@login_required
def editar_movimento(request):
    # edita um movimento existente relacionado a um honorário no banco de dados
    id = request.POST.get('movimento_id', None)
    if id:
        movimento = Movimento.objects.get(pk=id)
        form = movimentoForm(request.POST, request.FILES, instance=movimento)

        if form.is_valid():
            form.save()

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_save(request.user, movimento, False))
            messages.success(request, u' Editado com sucesso!')
        else:
            messages.error(request, form.errors)

        return redirect('honorarios_processo', movimento.honorario.id)
    else:
        messages.error(request, u'Erro ao salvar dados')
        return redirect(index)


@reversion.create_revision(atomic=False)
@login_required
def salvar_documento_movimento(request):
    # salva um novo documento relacionado a um movimento de honorário no banco de dados
    if request.method == 'POST':
        movimento_id = request.POST.get('documento_movimento_id', None)
        anexo = request.FILES.get('documento_anexo', None)
        if movimento_id and anexo:
            try:
                movimento_obj = Movimento.objects.get(pk=movimento_id)
                documento_movimento = Documento(movimento=movimento_obj, nome=anexo.name, anexo=anexo)
                documento_movimento.save()
                reversion.set_user(request.user)
                reversion.set_comment(Util.get_comment_save(request.user, documento_movimento, True))
                messages.success(request, u' Cadastrado com sucesso!')
            except Exception as e:
                messages.error(request, 'Erro ao Salvar o documento - Erro:{0}'.format(e))

            return redirect('honorarios_processo', movimento_obj.honorario.id)

    messages.error(request, u'Erro ao salvar documentos')
    return redirect(index)


@reversion.create_revision(atomic=False)
@login_required
def visibilidade_documento_movimento(request, documento_id):
    # altera a visibilidade de um documento relacionado a um movimento de honorário
    documento = Documento.objects.get(id=documento_id, ativo=True)
    try:
        if documento.visivel:
            documento.visivel = False
            messages.success(request, u' Documento Excluído com sucesso!')
        else:
            documento.visivel = True
            messages.success(request, u' Documento Recuperado com sucesso!')

        documento.save()
        reversion.set_user(request.user)
        reversion.set_comment(Util.get_comment_save(request.user, documento, False))
        return redirect('honorarios_processo', documento.movimento.honorario.id)

    except Exception as e:
        messages.error(request, 'Erro ao alterar o documento {0} - Erro:{1}'.format(documento.none, e))
    return redirect(index)


@login_required
@reversion.create_revision(atomic=False)
@permission_required('honorarios.view_honorario')
def altera_situacao(request):
    # altera a situação de um honorário no banco de dados
    if request.method == 'POST':
        posssivel = request.POST.get('honorario_possivel', '')
        id = request.POST.get('honorario_id', '')
        honorario = Honorario.objects.get(pk=id)
        honorario.situacao = posssivel
        honorario.save()
        reversion.set_user(request.user)
        reversion.set_comment(Util.get_comment_save(request.user, honorario, False)+' Editou o campo Situação')

        messages.success(request, u'Situação alterada com sucesso')
        return redirect('honorarios_processo', id)
    else:
        return redirect(index)


@login_required
@reversion.create_revision(atomic=False)
@permission_required('honorarios.view_honorario')
def altera_recurso_gerado(request):
    # altera o número do recurso gerado para um honorário no banco de dados
    if request.method == 'POST':
        numero = re.sub('[^0-9]', '', request.POST.get('numero_recurso', ''))
        id = request.POST.get('honorario_id', '')
        honorario = Honorario.objects.get(pk=id)
        honorario.numero_recurso_gerado = numero
        if numero != '':
            recurso = Processo.objects.filter(numero=numero, ativo=True)
            if recurso:
                honorario.recurso_vinculado = recurso.first()

        if request.POST.get('recurso_finalizado', '') == 'true':
            honorario.recurso_finalizado = True
            # mudanca de tipo do processo para Transitado em julgado, porem com numero de recurso
            honorario.situacao = Honorario.TIPO_TRANSITADO_JULGADO
        honorario.save()

        reversion.set_user(request.user)
        reversion.set_comment(Util.get_comment_save(request.user, honorario, False)+' Editou o campo Recurso Gerado e recurso_finalizado = {0} e Situacao = {1}'.format(honorario.recurso_finalizado, honorario.get_situacao_display()))  # noqa: E501

        messages.success(request, u'Número de recurso gerado, cadastrado com sucesso!')
        return redirect('honorarios_processo', id)
    else:
        return redirect(index)


@login_required
@permission_required('honorarios.view_honorario')
def transitados_julgados_list(request):
    # lógica para filtrar a lista de honorários transitados julgados com base em um parâmetro de busca

    if not request.GET.get('page'):
        request.session['filtro_honorario'] = None

    if request.POST:
        filtro = request.POST.get('filtro_honorario', '')
        request.session['filtro_honorario'] = filtro
        page = ''
    else:
        page = request.GET.get('page')
        if request.session.get('filtro_honorario'):
            filtro = request.session.get('filtro_honorario')
        else:
            filtro = ''

    transitados_julgados = Honorario.objects.filter(
        (
            Q(fase__processo__numero__icontains=filtro) |
            Q(fase__processo__numero_puro__icontains=filtro)
        ) &
        Q(situacao=Honorario.TIPO_TRANSITADO_JULGADO) &
        Q(ativo=True) &
        Q(possivel=True)
    ).order_by('-data_cadastro')

    transitados_julgados = transitados_julgados.annotate(
        movimentacao=Max('movimentos_honorario__tipo')
    ).values_list(
        'id',
        'fase__processo__numero',
        'defensor__servidor__nome',
        'data_cadastro',
        'movimentacao',
        'valor_estimado',
        'valor_efetivo',
        'fase__processo__grau'
    )

    paginacao = Paginator(transitados_julgados, 50)

    try:
        processos = paginacao.page(page)
    except PageNotAnInteger:
        processos = paginacao.page(1)
    except EmptyPage:
        processos = paginacao.page(paginacao.num_pages)
    return render(request=request, template_name="processo/honorarios/transitados_julgados.html", context=locals())


@login_required
@permission_required('honorarios.view_honorario')
def transitados_julgados_list_defensor(request):
    # lógica para filtrar a lista de honorários transitados julgados por defensor com base em um parâmetro de busca

    if not request.GET.get('page'):
        request.session['filtro_honorario'] = None

    if request.POST:
        filtro = request.POST.get('filtro_honorario', '')
        request.session['filtro_honorario'] = filtro
        page = ''
    else:
        page = request.GET.get('page')
        if request.session.get('filtro_honorario'):
            filtro = request.session.get('filtro_honorario')
        else:
            filtro = ''

    transitados_julgados = Honorario.objects.select_related(
        'fase__processo'
    ).filter(
        (
            Q(fase__processo__numero__icontains=filtro) |
            Q(fase__processo__numero_puro__icontains=filtro)
        ) &
        Q(situacao=Honorario.TIPO_TRANSITADO_JULGADO) &
        Q(ativo=True) &
        Q(possivel=True)
    ).order_by('-data_cadastro')

    transitados_julgados = transitados_julgados.annotate(max_tipo=Max('movimentos_honorario__tipo'))
    transitados_julgados = transitados_julgados.filter(max_tipo=Movimento.TIPO_ENCAMINHADO_DEF)

    paginacao = Paginator(transitados_julgados, 50)
    movimentos_realizados = Movimento.objects.filter(ativo=True, cadastrado_por=request.user.servidor).order_by('-data_cadastro')[:30]  # noqa: E501

    try:
        processos = paginacao.page(page)
    except PageNotAnInteger:
        processos = paginacao.page(1)
    except EmptyPage:
        processos = paginacao.page(paginacao.num_pages)
    return render(
        request=request,
        template_name="processo/honorarios/transitados_julgados_encaminhados.html",
        context=locals()
    )


@login_required
@permission_required('honorarios.view_honorario')
def recusos_list(request):
    # lógica para filtrar a lista de recursos (honorários em fase de recurso) com base em um parâmetro de busca

    if not request.GET.get('page'):
        request.session['filtro_honorario'] = None

    if request.POST:
        filtro = request.POST.get('filtro_honorario', '')
        request.session['filtro_honorario'] = filtro
        page = ''
    else:
        page = request.GET.get('page')
        if request.session.get('filtro_honorario'):
            filtro = request.session.get('filtro_honorario')
        else:
            filtro = ''

    recursos = Honorario.objects.filter(
        (
            Q(fase__processo__numero__icontains=filtro) |
            Q(fase__processo__numero_puro__icontains=filtro)
        ) &
        Q(situacao=Honorario.TIPO_RECURSO) &
        Q(ativo=True) &
        Q(possivel=True)
    ).order_by('-data_cadastro')

    recursos = recursos.values_list(
        'id',
        'fase__processo__numero',
        'defensor__servidor__nome',
        'data_cadastro',
        'numero_recurso_gerado',
        'fase__processo__grau'
    )

    paginacao = Paginator(recursos, 50)

    try:
        processos = paginacao.page(page)
    except PageNotAnInteger:
        processos = paginacao.page(1)
    except EmptyPage:
        processos = paginacao.page(paginacao.num_pages)
    return render(request=request, template_name="processo/honorarios/recursos.html", context=locals())


@never_cache
@login_required
@permission_required('honorarios.view_honorario')
def atualizacoes_list(request):
    # lógica para filtrar a lista de atualizações de processos com honorários com base em um parâmetro de busca

    if not request.GET.get('page'):
        request.session['filtro_honorario'] = None

    if request.POST:
        filtro = request.POST.get('filtro_honorario', '')
        request.session['filtro_honorario'] = filtro
        page = ''
    else:
        page = request.GET.get('page')
        if request.session.get('filtro_honorario'):
            filtro = request.session.get('filtro_honorario')
        else:
            filtro = ''

    atualizacoes_dist = AlertaProcessoMovimento.objects.filter(
        Q(ativo=True) &
        Q(honorario__ativo=True) &
        Q(honorario__possivel=True) &
        Q(honorario__baixado=False) &
        (
            Q(honorario__fase__processo__numero__icontains=filtro) |
            Q(honorario__fase__processo__numero_puro__icontains=filtro)
        )

    ).distinct('honorario__id').order_by('honorario__id', 'visualizado', '-data_cadastro')

    atualizacoes = AlertaProcessoMovimento.objects.filter(
        id__in=atualizacoes_dist
    ).order_by('visualizado', '-data_cadastro').values_list(
        'honorario__id',
        'mensagem',
        'data_cadastro',
        'visualizado',
        'data_visualizado',
        'visualizado_por_nome'
    )

    paginacao = Paginator(atualizacoes, 50)

    try:
        processos = paginacao.page(page)
    except PageNotAnInteger:
        processos = paginacao.page(1)
    except EmptyPage:
        processos = paginacao.page(paginacao.num_pages)
    return render(request=request, template_name="processo/honorarios/atualizacoes.html", context=locals())


@login_required
@permission_required('honorarios.view_honorario')
def visualiza_alertas(request, honorario_id):
    # marca os alertas relacionados a um honorário como visualizados

    try:
        AlertaProcessoMovimento.objects.filter(
            honorario__id=honorario_id,
            ativo=True,
            visualizado=False
        ).update(
            visualizado_por=request.user.servidor,
            visualizado_por_nome=request.user.servidor.nome,
            data_visualizado=datetime.now(),
            visualizado=True
            )
        error = False
    except KeyError:
        error = True

    if error:
        messages.error(request, u'Erro! Verificação de atualizações se encontra indisponível no momento!')
    else:
        messages.success(request, u'Verificação de atualizações realizada com sucesso!')

    return redirect('honorarios_processo', honorario_id)


@never_cache
@login_required
@permission_required('honorarios.view_honorario')
def preanalise_list(request):
    # lógica para filtrar a lista de honorários em pré-análise com base em um parâmetro de busca
    atuacao = None
    if hasattr(request.user.servidor, 'defensor'):
        atuacao = request.user.servidor.defensor.all_atuacoes.vigentes().filter(
            defensoria__nucleo__honorario=True
        ).first()

    if not request.GET.get('page'):
        request.session['filtro_honorario'] = None

    if 'page' not in request.GET:
        request.session['filtro_honorario'] = request.GET

    page = request.GET.get('page')
    form = BuscarAnaliseForm(request.session.get('filtro_honorario'))

    if form.is_valid():

        processo_honorarios_list = Honorario.objects.filter(ativo=True).values('fase__processo__id')
        processo_analise_id_list = Analise.objects.filter(ativo=True).values('fase__processo__id')

        processo_analise_list = Fase.objects.filter(
            atividade=Fase.ATIVIDADE_SENTENCA,
            ativo=True,
            processo__tipo=Processo.TIPO_EPROC,
            processo__ativo=True
        ).exclude(
            processo__id__in=processo_honorarios_list
        ).exclude(
            processo__id__in=processo_analise_id_list
        )

        filtro = request.session.get('filtro_honorario')

        if 'comarca' in filtro and filtro['comarca']:
            processo_analise_list = processo_analise_list.filter((
                 Q(processo__comarca_id=filtro['comarca'])
             ))

        if 'area' in filtro and filtro['area']:
            processo_analise_list = processo_analise_list.filter((
                Q(processo__area_id=filtro['area'])
            ))

        if 'data_ini' in filtro and form.cleaned_data['data_ini']:
            data_ini = form.cleaned_data['data_ini']

            processo_analise_list = processo_analise_list.filter((
                Q(data_cadastro__gte=data_ini)
            ))

        if 'data_fim' in filtro and form.cleaned_data['data_fim']:
            data_fim = form.cleaned_data['data_fim']
            data_fim = datetime.combine(data_fim, time.max)

            processo_analise_list = processo_analise_list.filter((
                Q(data_cadastro__lte=data_fim)
            ))

        if 'numero' in filtro and filtro['numero']:

            numero = re.sub('[^0-9]', '', filtro['numero'])

            if numero.isdigit():
                processo_analise_list = processo_analise_list.filter((
                    Q(processo__numero_puro__icontains=numero)
                ))
            else:
                processo_analise_list = processo_analise_list.filter((
                    Q(processo__acao__nome__icontains=filtro['numero'])
                ))

        processo_analise_list = processo_analise_list.order_by(
            'data_cadastro',
            'id',
            '-processo__parte__ativo',
            '-processo__parte__atendimento__ativo'
        ).distinct(
            'data_cadastro',
            'id'
        ).values_list(
            'id',
            'processo__numero',
            'processo__chave',
            'processo__numero_puro',
            'processo__grau',
            'processo__area__nome',
            'processo__comarca__nome',
            'data_cadastro',
            'defensor_cadastro__servidor__nome',
            'processo__acao__nome',
            'processo__parte__atendimento__numero'
        )

        paginacao = Paginator(processo_analise_list, 50)

        try:
            processos = paginacao.page(page)
        except PageNotAnInteger:
            processos = paginacao.page(1)
        except EmptyPage:
            processos = paginacao.page(paginacao.num_pages)

    angular = 'HonorariosCtrl'
    return render(request=request, template_name="processo/honorarios/pre_analise.html", context=locals())


@never_cache
@login_required
@permission_required('honorarios.view_honorario')
def analise_list(request):
    # lógica para filtrar a lista de honorários em análise com base em um parâmetro de busca
    ...
    atuacao = None
    if hasattr(request.user.servidor, 'defensor'):
        atuacao = request.user.servidor.defensor.all_atuacoes.vigentes().filter(
            defensoria__nucleo__honorario=True
        ).first()

    filtro_s = request.session.get('filtro_honorario')

    if not request.GET.get('page'):
        request.session['filtro_honorario'] = None

    if 'page' not in request.GET:
        request.session['filtro_honorario'] = request.GET

    page = request.GET.get('page')
    form = BuscarAnaliseForm(request.session.get('filtro_honorario'))

    if form.is_valid():
        processo_analise_list = Analise.objects.filter(
            fase__ativo=True,
            fase__processo__tipo=Processo.TIPO_EPROC,
            fase__processo__ativo=True,
            fase__tipo__sentenca=True,
            fase__honorario=None
        )

        filtro = request.session.get('filtro_honorario')

        if 'comarca' in filtro and filtro['comarca']:
            processo_analise_list = processo_analise_list.filter((
                 Q(fase__processo__comarca_id=filtro['comarca'])
             ))

        if 'area' in filtro and filtro['area']:
            processo_analise_list = processo_analise_list.filter((
                Q(fase__processo__area_id=filtro['area'])
            ))

        if 'data_ini' in filtro and form.cleaned_data['data_ini']:
            data_ini = form.cleaned_data['data_ini']

            processo_analise_list = processo_analise_list.filter((
                Q(fase__data_cadastro__gte=data_ini) |
                Q(fase__data_cadastro__gte=data_ini)
            ))

        if 'data_fim' in filtro and form.cleaned_data['data_fim']:
            data_fim = form.cleaned_data['data_fim']
            data_fim = datetime.combine(data_fim, time.max)

            processo_analise_list = processo_analise_list.filter((
                Q(fase__data_cadastro__lte=data_fim) |
                Q(fase__data_cadastro__lte=data_fim)
            ))

        if 'numero' in filtro and filtro['numero']:

            numero = re.sub('[^0-9]', '', filtro['numero'])

            if numero.isdigit():
                processo_analise_list = processo_analise_list.filter((
                    Q(fase__processo__numero_puro__icontains=numero)
                ))
            else:
                processo_analise_list = processo_analise_list.filter((
                    Q(fase__processo__acao__nome__icontains=filtro['numero'])
                ))

        processo_analise_list = processo_analise_list.order_by(
            'data_cadastro',
            'id',
            '-fase__processo__parte__ativo',
            '-fase__processo__parte__atendimento__ativo'
        ).distinct(
            'data_cadastro',
            'id'
        ).values_list(
            'id',
            'fase__processo__numero',
            'fase__processo__chave',
            'fase__processo__numero_puro',
            'fase__processo__grau',
            'fase__processo__area__nome',
            'fase__processo__comarca__nome',
            'fase__data_cadastro',
            'fase__defensor_cadastro__servidor__nome',
            'data_cadastro',
            'cadastrado_por__nome',
            'motivo',
            'fase__id',
            'fase__processo__acao__nome',
            'fase__processo__parte__atendimento__numero'
        )

        paginacao = Paginator(processo_analise_list, 50)

        try:
            processos = paginacao.page(page)
        except PageNotAnInteger:
            processos = paginacao.page(1)
        except EmptyPage:
            processos = paginacao.page(paginacao.num_pages)

    angular = 'HonorariosCtrl'
    return render(request=request, template_name="processo/honorarios/em_analise.html", context=locals())


@login_required
@permission_required('honorarios.view_honorario')
def impossibilidade_honorarios(request, fase_id):
    # cria um registro de honorário com a situação de impossibilidade para a fase especificada
    try:
        fase = Fase.objects.get(id=fase_id, ativo=True)
        Honorario.objects.create(
            fase=fase,
            cadastrado_por=request.user.servidor
        )
    except ObjectDoesNotExist:
        error = True
    except IntegrityError:
        error = True
    else:
        error = False

    if request.GET.get('next'):

        if error:
            messages.error(request, u'Erro ao gerenciar possibilidade de honorário do processo {0}!'.format(fase.processo.numero))  # noqa: E501
        else:
            messages.success(request, u'Impossibilidade de honorário do processo {0} gerenciada com sucesso!'.format(fase.processo.numero))  # noqa: E501

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    else:

        return JsonResponse({'error': error})


@login_required
@permission_required('honorarios.view_honorario')
def impossibilidade_honorarios_check(request):
    # marca como impossível um conjunto de honorários selecionados
    check_list = request.POST.getlist('honorario-checkbox', None)

    if check_list:
        fases = Fase.objects.filter(id__in=check_list, ativo=True, honorario=None)

        for fase in fases:
            honorario = Honorario(fase=fase, cadastrado_por=request.user.servidor)
            honorario.save()
        error = False
    else:
        error = True

    if error:
        messages.error(request, u'Erro! Selecione pelo menos um processo!')
    else:
        messages.success(request, u'Impossibilidade dos {} processos selecionados foi gerenciada com sucesso!'.format(fases.count()))  # noqa: E501

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@permission_required('honorarios.view_honorario')
def impossibilidade_honorario_cadastrado(request, honorario_id):
    # marca um registro de honorário como excluído, quando possível e ativo
    try:

        honorario = Honorario.objects.get(pk=honorario_id)
        if honorario.situacao == Honorario.TIPO_NOVO and honorario.possivel and honorario.ativo:
            honorario.excluido_por = request.user.servidor
            honorario.data_exclusao = datetime.now()
            honorario.possivel = False
            honorario.save()
            error = False
        else:
            error = True
    except ObjectDoesNotExist:
        error = True

    if request.GET.get('next'):

        if error:
            messages.error(request, u'Erro ao excluir o honorário do processo {0}!'.format(honorario.fase.processo.numero))  # noqa: E501
        else:
            messages.success(request, u'Honorário do processo {0} excluído com sucesso!'.format(honorario.fase.processo.numero))  # noqa: E501

        return HttpResponseRedirect(request.GET.get('next'))

    else:

        return JsonResponse({'error': error})


@login_required
@permission_required('honorarios.view_honorario')
def possibilidade_honorarios(request):
    # cria ou atualiza um registro de honorário para gerenciar a possibilidade de honorários em uma fase específica
    dados = request.POST.copy()

    try:

        fase = Fase.objects.get(id=request.POST.get('honorario-fase'), ativo=True)
        redirecionar_para_honorario = False

        if hasattr(fase, 'honorario') and not fase.honorario.possivel:
            honorario = fase.honorario
            redirecionar_para_honorario = True
        else:
            honorario = Honorario(fase=fase, cadastrado_por=request.user.servidor)

        form = HonorarioFaseForm(dados, instance=honorario, prefix='honorario')

        if form.is_valid():
            form.save()
        else:
            error = True

        error = False

    except IntegrityError:
        error = True
    except ObjectDoesNotExist:
        error = True

    if error:
        messages.error(request, 'Erro ao gerenciar possibilidade de honorário: Dados inconsistentes!')
        return JsonResponse({'error': error})
    else:

        messages.success(request, u'Possibilidade de honorário do processo {0} gerenciada com sucesso!'.format(fase.processo.numero))  # noqa: E501

        if redirecionar_para_honorario:
            return redirect('honorarios_processo', honorario.id)
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@permission_required('honorarios.view_honorario')
def criar_analise(request):
    # cria uma análise de honorários para uma fase específica e define um motivo de pendência (se houver)
    dados = request.POST.copy()
    try:
        motivo_pendencia = request.POST.get('honorario-motivo', None)
        fase = Fase.objects.get(id=request.POST.get('honorario-fase'), ativo=True, honorario=None)
        analise = Analise(fase=fase, motivo=motivo_pendencia, cadastrado_por=request.user.servidor)
        if motivo_pendencia:
            form = AnaliseFaseForm(dados, instance=analise, prefix='honorario')
            if form.is_valid():
                form.save()
            else:
                error = True
        else:
            analise.save()

        error = False
    except ObjectDoesNotExist:
        error = True

    if error:
        messages.error(request, u'Erro ao gerenciar análise de honorário do processo {0}!'.format(fase.processo.numero))
        return JsonResponse({'error': error})
    else:
        if motivo_pendencia:
            messages.success(request, u'Processo {0} enviado para análise de pendência!'.format(fase.processo.numero))
        else:
            messages.success(request, u'Processo {0} Enviado para análise!'.format(fase.processo.numero))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@permission_required('honorarios.view_honorario')
def analise_honorarios_check(request):
    # cria análises de honorários para um conjunto de fases selecionadas
    check_list = request.POST.getlist('honorario-checkbox', None)

    if check_list:
        fases = Fase.objects.filter(id__in=check_list, ativo=True, honorario=None)

        for fase in fases:
            analise = Analise(fase=fase, cadastrado_por=request.user.servidor)
            analise.save()
        error = False
    else:
        error = True

    if error:
        messages.error(request, u'Erro! Selecione pelo menos um processo!')
    else:
        messages.success(request, u'{0} Processos enviados para análise!'.format(fases.count()))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@never_cache
@login_required
@permission_required('honorarios.view_honorario')
def relatorios_list(request):
    # lógica para filtrar a lista de honorários em análise com base em critérios de busca
    if not request.GET.get('page'):
        request.session['filtro_honorario'] = None

    if 'page' not in request.GET:
        request.session['filtro_honorario'] = request.GET

    page = request.GET.get('page')
    form = BuscarHonorariosForm(request.session.get('filtro_honorario'))

    honorarios_list = Honorario.objects.filter(
        ativo=True,
        possivel=True
    ).order_by(
        '-data_cadastro'
    )

    if form.is_valid():
        filtro = request.session.get('filtro_honorario')

        if 'comarca' in filtro and filtro['comarca']:
            honorarios_list = honorarios_list.filter((
                Q(fase__processo__comarca_id=filtro['comarca'])
            ))

        if 'situacao' in filtro and filtro['situacao']:
            honorarios_list = honorarios_list.filter((
                Q(situacao=filtro['situacao'])
            ))

            if int(filtro['situacao']) == Honorario.TIPO_TRANSITADO_JULGADO:
                if 'movimentacao' in filtro and filtro['movimentacao']:

                    honorarios_list = honorarios_list.annotate(max_tipo=Max('movimentos_honorario__tipo'))
                    honorarios_list = honorarios_list.filter(max_tipo=filtro['movimentacao'])

        if form.cleaned_data['data_ini']:
            data_ini = form.cleaned_data['data_ini']

            honorarios_list = honorarios_list.filter((
                Q(data_cadastro__gte=data_ini) |
                Q(data_cadastro__gte=data_ini)
            ))

        if form.cleaned_data['data_fim']:
            data_fim = form.cleaned_data['data_fim']
            data_fim = datetime.combine(data_fim, time.max)

            honorarios_list = honorarios_list.filter((
                Q(data_cadastro__lte=data_fim) |
                Q(data_cadastro__lte=data_fim)
            ))

    else:
        messages.error(request, form.errors)

    honorarios_list = honorarios_list.annotate(
        movimentacao=Max('movimentos_honorario__tipo')
    ).order_by(
        '-data_cadastro',
    ).values_list(
        'id',
        'fase__processo__numero',
        'data_cadastro',
        'fase__processo__comarca__nome',
        'defensor__servidor__nome',
        'situacao',
        'movimentacao',
        'fase__processo__grau',
    )

    paginacao = Paginator(honorarios_list, 50)

    try:
        processos = paginacao.page(page)
    except PageNotAnInteger:
        processos = paginacao.page(1)
    except EmptyPage:
        processos = paginacao.page(paginacao.num_pages)
    comarcas = Comarca.objects.ativos().order_by('nome')
    return render(request=request, template_name="processo/honorarios/relatorios.html", context=locals())


@login_required
@permission_required('honorarios.change_honorario')
def suspender(request, honorario_id):
    # define um registro de honorário como suspenso e cria um movimento de suspensão relacionado
    honorario = get_object_or_404(
        Honorario,
        id=honorario_id,
        ativo=True)

    honorario.suspenso = True
    form = SuspenderForm(request.POST, instance=honorario)

    movimento = Movimento(honorario=honorario, tipo=Movimento.TIPO_SUSPENSAO, cadastrado_por=request.user.servidor)
    form_movimento = MovimentoSuspencaoForm(request.POST, instance=movimento)

    if form.is_valid() and form_movimento.is_valid():

        form.save()
        form_movimento.save()

        messages.success(request, u'Honorário foi suspenso com sucesso!')

    else:

        messages.error(request, u'Não foi possível suspender este processo!')

    return redirect('honorarios_processo', honorario_id)


@never_cache
@login_required
@permission_required('honorarios.view_honorario')
def suspensos_list(request):
    # lista os honorários suspensos e suas informações relacionadas
    if not request.GET.get('page'):
        request.session['filtro_honorario'] = None

    if request.POST:
        filtro = request.POST.get('filtro_honorario', '')
        request.session['filtro_honorario'] = filtro
        page = ''
    else:
        page = request.GET.get('page')
        if request.session.get('filtro_honorario'):
            filtro = request.session.get('filtro_honorario')
        else:
            filtro = ''

    transitados_julgados = Honorario.objects.annotate(
        movimentacao=Max('movimentos_honorario__tipo')
    ).filter(
        Q(ativo=True) &
        Q(suspenso=True) &
        Q(suspenso_ate__lte=(date.today() + timedelta(days=30)))
    ).order_by(
        'suspenso_ate',
    ).values_list(
        'id',
        'fase__processo__numero',
        'defensor__servidor__nome',
        'data_cadastro',
        'movimentacao',
        'valor_estimado',
        'valor_efetivo',
        'fase__processo__grau',
        'suspenso_ate'
    )

    paginacao = Paginator(transitados_julgados, 50)

    try:
        processos = paginacao.page(page)
    except PageNotAnInteger:
        processos = paginacao.page(1)
    except EmptyPage:
        processos = paginacao.page(paginacao.num_pages)
    return render(request=request, template_name="processo/honorarios/suspensos.html", context=locals())


@never_cache
@login_required
@permission_required('honorarios.view_honorario')
def impossibilidade_list(request):
    # lista os honorários com impossibilidade de pagamento com base em critérios de busca
    ...
    atuacao = None
    if hasattr(request.user.servidor, 'defensor'):
        atuacao = request.user.servidor.defensor.all_atuacoes.vigentes().filter(
            defensoria__nucleo__honorario=True
        ).first()

    filtro_s = request.session.get('filtro_honorario')

    if not request.GET.get('page'):
        request.session['filtro_honorario'] = None

    if 'page' not in request.GET:
        request.session['filtro_honorario'] = request.GET

    page = request.GET.get('page')
    form = BuscarAnaliseForm(request.session.get('filtro_honorario'))

    if form.is_valid():
        processo_analise_list = Honorario.objects.filter(
            fase__ativo=True,
            fase__processo__tipo=Processo.TIPO_EPROC,
            fase__processo__ativo=True,
            fase__tipo__sentenca=True,
            possivel=False
        )

        filtro = request.session.get('filtro_honorario')

        if 'comarca' in filtro and filtro['comarca']:
            processo_analise_list = processo_analise_list.filter((
                 Q(fase__processo__comarca_id=filtro['comarca'])
             ))

        if 'area' in filtro and filtro['area']:
            processo_analise_list = processo_analise_list.filter((
                Q(fase__processo__area_id=filtro['area'])
            ))

        if 'data_ini' in filtro and form.cleaned_data['data_ini']:
            data_ini = form.cleaned_data['data_ini']

            processo_analise_list = processo_analise_list.filter((
                Q(fase__data_cadastro__gte=data_ini) |
                Q(fase__data_cadastro__gte=data_ini)
            ))

        if 'data_fim' in filtro and form.cleaned_data['data_fim']:
            data_fim = form.cleaned_data['data_fim']
            data_fim = datetime.combine(data_fim, time.max)

            processo_analise_list = processo_analise_list.filter((
                Q(fase__data_cadastro__lte=data_fim) |
                Q(fase__data_cadastro__lte=data_fim)
            ))

        if 'numero' in filtro and filtro['numero']:

            numero = re.sub('[^0-9]', '', filtro['numero'])

            if numero.isdigit():
                processo_analise_list = processo_analise_list.filter((
                    Q(fase__processo__numero_puro__icontains=numero)
                ))
            else:
                processo_analise_list = processo_analise_list.filter((
                    Q(fase__processo__acao__nome__icontains=filtro['numero'])
                ))

        processo_analise_list = processo_analise_list.order_by(
            '-data_cadastro',
            'id',
            '-fase__processo__parte__ativo',
            '-fase__processo__parte__atendimento__ativo'
        ).distinct(
            'data_cadastro',
            'id'
        ).values_list(
            'id',
            'fase__processo__numero',
            'fase__processo__chave',
            'fase__processo__numero_puro',
            'fase__processo__grau',
            'fase__processo__area__nome',
            'fase__processo__comarca__nome',
            'fase__data_cadastro',
            'fase__defensor_cadastro__servidor__nome',
            'data_cadastro',
            'cadastrado_por__nome',
            'fase__analises__motivo',
            'fase__id',
            'fase__processo__acao__nome',
            'fase__processo__parte__atendimento__numero'
        )

        paginacao = Paginator(processo_analise_list, 50)

        try:
            processos = paginacao.page(page)
        except PageNotAnInteger:
            processos = paginacao.page(1)
        except EmptyPage:
            processos = paginacao.page(paginacao.num_pages)

    angular = 'HonorariosCtrl'
    return render(request=request, template_name="processo/honorarios/impossibilidade.html", context=locals())


@login_required
@permission_required('honorarios.change_honorario')
def criar_atendimento(request, honorario_id):
    # cria um atendimento relacionado a um registro de honorário, vinculando as informações corretas
    honorario = get_object_or_404(
        Honorario,
        id=honorario_id,
        ativo=True
    )

    atendimento = honorario.atendimento

    if atendimento is None:

        if not validar_cnpj(config.CNPJ_INSTITUICAO):
            messages.error(request, u'Não foi possível criar um atendimento: CNPJ da Defensoria inválido!')
            return redirect('honorarios_processo', honorario_id)

        if not hasattr(request.user.servidor, 'defensor'):
            messages.error(request, u'Não foi possível criar um atendimento: Usuário não é um defensor/assessor!')
            return redirect('honorarios_processo', honorario_id)

        defensor = request.user.servidor.defensor

        atuacao = defensor.all_atuacoes.vigentes().filter(
            defensoria__nucleo__honorario=True
        ).first()

        if not atuacao:
            messages.error(request, u'Não foi possível criar um atendimento: Usuário sem lotação válida!')
            return redirect('honorarios_processo', honorario_id)

        if not defensor.eh_defensor:
            atuacao = Atuacao.objects.vigentes().filter(
                defensoria=atuacao.defensoria,
                defensor__eh_defensor=True
            ).order_by(
                '-data_inicial'
            ).first()

        if not atuacao:
            messages.error(request, u'Não foi possível criar um atendimento: Nenhum defensor vinculado!')
            return redirect('honorarios_processo', honorario_id)

        atendimento = Atendimento.objects.create(
            tipo=Atendimento.TIPO_PROCESSO,
            defensoria=atuacao.defensoria,
            defensor=atuacao.titular if atuacao.titular else atuacao.defensor,
            substituto=atuacao.defensor if atuacao.titular else None,
            qualificacao=honorario.fase.processo.acao.qualificacao_set.ativos().first()
        )

        try:
            pessoa, _ = PessoaAssistida.objects.get_or_create(
                cpf=config.CNPJ_INSTITUICAO,
                desativado_em=None,
                defaults={
                    'tipo': constantes.TIPO_PESSOA_JURIDICA,
                    'nome': config.NOME_INSTITUICAO,
                    'apelido': config.NOME_INSTITUICAO
                }
            )
        except PessoaAssistida.MultipleObjectsReturned:
            messages.error(request, u'Não foi possível criar um atendimento: CNPJ da Defensoria cadastrado em duplicidade!')  # noqa: E501
            return redirect('honorarios_processo', honorario_id)

        atendimento.set_requerente(pessoa.id)

        processo = honorario.fase.processo

        if processo.pre_cadastro or not processo.ativo:
            processo.pre_cadastro = False
            processo.ativo = True
            processo.data_exclusao = None
            processo.excluido_por = None
            processo.save()

        Parte.objects.create(
            processo=processo,
            atendimento=atendimento,
            parte=Parte.TIPO_AUTOR,
            defensoria=atendimento.defensoria,
            defensoria_cadastro=atendimento.defensoria,
            defensor_cadastro=atendimento.defensor,
        )

        if not honorario.has_aguard_peti:
            Movimento.objects.create(
                honorario=honorario,
                tipo=Movimento.TIPO_AGUARDANDO_PET,
                valor_estimado=honorario.valor_estimado,
                anotacao='(Movimentado automaticamente. Atendimento p/ Processo nº {})'.format(atendimento.numero),
                cadastrado_por=request.user.servidor
            )

        honorario.atendimento = atendimento
        honorario.save()

    return redirect('{}#/documentos'.format(reverse('atendimento_atender', args=[atendimento.numero])))
