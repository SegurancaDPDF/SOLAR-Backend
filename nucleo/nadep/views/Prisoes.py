# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
from datetime import datetime, date, timedelta
import json as simplejson
import re
import uuid

# Bibliotecas de terceiros
import math
import reversion
import six
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

# Solar
from assistido.models import Pessoa, PessoaAssistida
from contrib.models import Estado, Util, Defensoria
from nucleo.nadep.forms import (
    PrisaoForm,
    CadastrarTransferenciaForm,
    CadastrarFaltaForm,
    CadastrarRemissaoForm,
    PrisaoSalvarForm,
    GuiaForm,
    CadastrarInterrupcaoForm,
    CadastrarMudancaRegimeForm,
    CadastrarDetracaoForm,
    BuscarAtendimentoForm,
    LiquidarPenaForm,
    BaixarPrisaoForm
)
from nucleo.nadep.models import (
    Atendimento,
    Prisao,
    Aprisionamento,
    Falta,
    Remissao,
    Interrupcao,
    PenaRestritiva,
    RestricaoPrestacaoServico,
    MudancaRegime,
    Soltura,
    Historico,
)

from nucleo.nadep.services import Preso as ServicesPreso, AnoMesDia
from processo.processo.models import Fase, Parte, Processo
from relatorios.models import Local, Relatorio


@login_required
@permission_required('nadep.view_prisao')
def buscar_prisao(request):
    """ Exibe pagina com todas prisoes cadastradas """

    if request.method == 'POST':

        registros = []
        numero_registros = 25
        filtro = simplejson.loads(request.body)
        form = BuscarAtendimentoForm(filtro)

        hoje = date.today()

        if form.is_valid():

            prisoes_list = Prisao.objects.filter(Q(ativo=True)).exclude(data_prisao=None).order_by('-data_prisao')

            if 'comarca' in filtro and filtro['comarca']:
                prisoes_list = prisoes_list.filter((
                    Q(parte__processo__comarca=filtro['comarca'])
                ))

            if 'defensoria' in filtro and filtro['defensoria']:
                prisoes_list = prisoes_list.filter((
                    Q(parte__defensoria_id=filtro['defensoria'])
                ))

            if 'defensor' in filtro and filtro['defensor']:

                defensorias = Defensoria.objects.filter(
                    Q(all_atuacoes__defensor=filtro['defensor']) &
                    Q(all_atuacoes__ativo=True) &
                    (
                        (
                            Q(all_atuacoes__data_inicial__lte=datetime.now()) &
                            Q(all_atuacoes__data_final=None)
                        ) |
                        (
                            Q(all_atuacoes__data_inicial__lte=datetime.now()) &
                            Q(all_atuacoes__data_final__gte=datetime.now())
                        )
                    )
                ).distinct().values('id')

                prisoes_list = prisoes_list.filter(
                    Q(parte__defensoria__in=defensorias)
                )

            if 'filtro' in filtro and filtro['filtro']:

                filtro_numero = re.sub('[^0-9]', '',  filtro['filtro'])

                if len(filtro_numero) == 11:  # CPF

                    prisoes_list = prisoes_list.filter(pessoa__cpf=filtro_numero)

                elif len(filtro_numero) > 0:  # Numero do Processo

                    prisoes_list = prisoes_list.filter(parte__processo__numero_puro=filtro_numero)

                else:

                    prisoes_list = prisoes_list.filter(
                        pessoa__nome_norm__startswith=Util.normalize(filtro['filtro']),
                    )

            if form.cleaned_data['data_ini']:
                prisoes_list = prisoes_list.filter(
                    data_prisao__gte=form.cleaned_data['data_ini']
                )

            if form.cleaned_data['data_fim']:
                prisoes_list = prisoes_list.filter(
                    data_prisao__lte=form.cleaned_data['data_fim']
                )

            primeiro = filtro['pagina'] * numero_registros
            ultimo = primeiro + numero_registros

            if filtro['pagina'] == 0:
                filtro['total'] = prisoes_list.count()
                filtro['paginas'] = math.ceil(float(filtro['total']) / numero_registros)

            prisoes_list = prisoes_list[primeiro:ultimo]

            prisoes_list = prisoes_list.values(
                'id',
                'tipo',
                'pessoa__id',
                'pessoa__nome',
                'data_prisao',
                'processo__numero',
                'processo__acao__nome',
                'tipificacao__nome',
                'estabelecimento_penal__nome',
                'parte__defensoria__nome'
            )

            for prisao in prisoes_list:

                if prisao['data_prisao']:
                    prisao['dias_preso'] = AnoMesDia(dia=(hoje - prisao['data_prisao']).days).__str__()

                registros.append(prisao)

        return JsonResponse(
            {
                'registros': registros,
                'pagina': filtro['pagina'],
                'paginas': filtro['paginas'] if 'paginas' in filtro else 0,
                'ultima': filtro['pagina'] == filtro['paginas'] - 1 if 'paginas' in filtro else True,
                'total': filtro['total'],
            }, safe=False)

    form = BuscarAtendimentoForm(request.GET)
    angular = 'BuscarPrisaoCtrl'

    return render(request=request, template_name="nadep/buscar_prisao.html", context=locals())


@login_required
@permission_required('nadep.view_prisao')
def buscar_prisao_pessoa_json(request, pessoa_id):
    arr = []

    for prisao in Prisao.objects.filter(pessoa=pessoa_id, ativo=True):
        arr.append({
            'id': prisao.id,
            'tipificacao': prisao.tipificacao.nome if prisao.tipificacao else None,
            'tipo': {'id': prisao.get_tipo(), 'nome': prisao.LISTA_TIPO[prisao.get_tipo()][1]},
            'processo': {'numero': prisao.processo.numero} if prisao.processo else None,
            'solto': not prisao.aprisionamentos.ativos().em_andamento().exists(),
        })

    return JsonResponse(arr, safe=False)


@login_required
@permission_required('nadep.view_prisao')
def buscar_prisao_por_data(request, ano, mes, dia):
    """ Exibe pagina com todas prisoes cadastradas na data informada """

    page = request.GET.get('page')

    prisoes_list = Prisao.objects.filter(
        Q(ativo=True, data_prisao__year=ano, data_prisao__month=mes, data_prisao__day=dia)).order_by('-data_prisao')
    paginacao = Paginator(prisoes_list, 9)

    try:
        prisoes = paginacao.page(page)
    except PageNotAnInteger:
        prisoes = paginacao.page(1)
    except EmptyPage:
        prisoes = paginacao.page(paginacao.num_pages)

    return render(request=request, template_name="nadep/buscar_prisao.html", context=locals())


@login_required
@reversion.create_revision(atomic=False)
@permission_required('nadep.add_prisao')
def cadastrar_prisao(request, pessoa_id):

    pessoa = Pessoa.objects.get(id=pessoa_id)

    if request.GET.get('parte'):
        parte = Parte.objects.get(id=request.GET.get('parte'))
        prisao = Prisao(processo=parte.processo, parte=parte)
    else:
        return redirect('nadep_visualizar_pessoa', pessoa_id)

    if request.GET.get('inquerito'):
        inquerito = Processo.objects.filter(numero_puro=request.GET.get('inquerito')).first()

    estado_padrao = Estado.objects.get(uf=settings.SIGLA_UF.upper())
    municipio_padrao = None

    if prisao.estabelecimento_penal and prisao.estabelecimento_penal.endereco:
        municipio_padrao = prisao.estabelecimento_penal.endereco.municipio

    initial = {
        'pessoa': pessoa.id,
        'processo': prisao.processo,
        'parte': prisao.parte,
        'tipo': prisao.get_tipo(),
        'estado': request.POST.get('prisao-estado', prisao.local_prisao.estado if prisao.local_prisao else estado_padrao),  # noqa: E501
        'municipio': request.POST.get('prisao-municipio', municipio_padrao),
        'cadastrado_por': request.user.servidor
    }

    if request.method == 'POST':

        if prisao.get_tipo() == Prisao.TIPO_CONDENADO:
            form = PrisaoSalvarForm(request.POST, instance=prisao, initial=initial, prefix='prisao')
        else:
            form = PrisaoForm(request.POST, instance=prisao, initial=initial, prefix='prisao')

        if form.is_valid():

            prisao = form.save(commit=False)

            if prisao.get_tipo() == Prisao.TIPO_PROVISORIO and prisao.resultado_sentenca == Prisao.SENTENCA_CONDENADO:

                prisao.save()

                if hasattr(prisao, 'originada'):
                    guia = prisao.originada
                else:
                    guia = Prisao(origem=prisao, tipo=Prisao.TIPO_CONDENADO)

                form_guia = PrisaoSalvarForm(request.POST, instance=guia, initial=initial, prefix='prisao')

                if form_guia.is_valid():

                    guia = form_guia.save(commit=False)

                    if request.POST.get('guia-processo') and request.POST.get('guia-parte'):
                        guia.processo = Processo.objects.filter(id=request.POST.get('guia-processo')).first()
                        guia.parte = Parte.objects.filter(id=request.POST.get('guia-parte')).first()
                    else:
                        guia.processo = None
                        guia.parte = None

                    guia.save()

            else:

                if request.POST.get('guia-processo') and request.POST.get('guia-parte'):
                    prisao.processo = Processo.objects.filter(id=request.POST.get('guia-processo')).first()
                    prisao.parte = Parte.objects.filter(id=request.POST.get('guia-parte')).first()

                prisao.save()

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_save(request.user, prisao, False))

            return redirect('nadep_visualizar_pessoa', prisao.pessoa.id)
    else:
        form = PrisaoForm(instance=prisao, initial=initial, prefix='prisao')

    form_guia = GuiaForm(instance=prisao, initial=initial, prefix='prisao')

    angular_app = 'siapApp'
    angular = 'BuscarProcessoCtrl'

    return render(request=request, template_name="nadep/cadastrar_prisao.html", context=locals())


@login_required
@reversion.create_revision(atomic=False)
@permission_required('nadep.change_prisao')
def editar_prisao(request, prisao_id):

    prisao = get_object_or_404(Prisao, id=prisao_id, ativo=True)

    if request.GET.get('parte') and prisao.processo and prisao.processo.acao and prisao.processo.acao.inquerito:

        parte = Parte.objects.filter(id=request.GET.get('parte')).first()

        if (parte and
                parte.atendimento.requerente and
                prisao.parte.atendimento.requerente and
                parte.atendimento.requerente.pessoa_id == prisao.parte.atendimento.requerente.pessoa_id):

            prisao.parte = parte
            prisao.processo = parte.processo
            prisao.save()

            messages.success(request, 'Inquérito Policial convertido em Ação Penal com sucesso!')

        else:

            messages.error(request, 'Não foi possível converter Inquérito Policial em Ação Penal: partes divergentes!')

    pessoa = prisao.pessoa
    processo = prisao.processo

    estado_padrao = Estado.objects.get(uf=settings.SIGLA_UF.upper())
    municipio_padrao = None

    if prisao.estabelecimento_penal and prisao.estabelecimento_penal.endereco:
        municipio_padrao = prisao.estabelecimento_penal.endereco.municipio

    initial = {
        'estado': request.POST.get('prisao-estado', prisao.local_prisao.estado if prisao.local_prisao else estado_padrao),  # noqa: E501
        'municipio': request.POST.get('prisao-municipio', municipio_padrao)
    }

    if request.method == 'POST':

        if request.GET.get('duplicar'):
            prisao.origem_id = prisao.id
            prisao.id = None

        if prisao.get_tipo() == Prisao.TIPO_CONDENADO:
            form = PrisaoSalvarForm(request.POST, instance=prisao, initial=initial, prefix='prisao')
        else:
            form = PrisaoForm(request.POST, instance=prisao, initial=initial, prefix='prisao')

        if form.is_valid():

            prisao = form.save(commit=False)

            if prisao.get_tipo() == Prisao.TIPO_PROVISORIO and prisao.resultado_sentenca == Prisao.SENTENCA_CONDENADO:

                prisao.save()

                if hasattr(prisao, 'originada') and prisao.originada.tipo == Prisao.TIPO_PROVISORIO:
                    guia = prisao.originada
                else:
                    guia = Prisao(origem=prisao, tipo=Prisao.TIPO_CONDENADO)

                form_guia = PrisaoSalvarForm(request.POST, instance=guia, initial=initial, prefix='prisao')

                if form_guia.is_valid():

                    guia = form_guia.save(commit=False)

                    if request.POST.get('guia-processo') and request.POST.get('guia-parte'):
                        guia.processo = Processo.objects.filter(id=request.POST.get('guia-processo')).first()
                        guia.parte = Parte.objects.filter(id=request.POST.get('guia-parte')).first()
                    else:
                        guia.processo = None
                        guia.parte = None

                    guia.save()

            else:

                if request.POST.get('guia-processo') and request.POST.get('guia-parte'):
                    prisao.processo = Processo.objects.filter(id=request.POST.get('guia-processo')).first()
                    prisao.parte = Parte.objects.filter(id=request.POST.get('guia-parte')).first()

                prisao.save()

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_save(request.user, prisao, False))

            return redirect('nadep_visualizar_pessoa', prisao.pessoa.id)

        else:

            form = PrisaoForm(request.POST, instance=prisao, initial=initial, prefix='prisao')
            form.is_valid()
    else:

        form = PrisaoForm(instance=prisao, initial=initial, prefix='prisao')

    if hasattr(prisao, 'originada') and prisao.originada.tipo == Prisao.TIPO_PROVISORIO:
        form_guia = GuiaForm(instance=prisao.originada, initial=initial, prefix='prisao')
    else:
        form_guia = GuiaForm(instance=prisao, initial=initial, prefix='prisao')

    angular_app = 'siapApp'
    angular = 'BuscarProcessoCtrl'

    return render(request=request, template_name="nadep/cadastrar_prisao.html", context=locals())


@login_required
@reversion.create_revision(atomic=False)
@permission_required('nadep.delete_prisao')
def excluir_prisao(request, prisao_id):
    dados = simplejson.loads(request.body)

    try:
        prisao = Prisao.objects.get(id=dados['id'])
        prisao.excluir(request.user)
        return JsonResponse({'success': True, 'message': 'Prisão Excluída'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@permission_required('nadep.change_prisao')
def baixar_preso(request, pessoa_id):

    pessoa = get_object_or_404(PessoaAssistida, id=pessoa_id, desativado_em=None)

    if request.method == 'POST':

        form = BaixarPrisaoForm(request.POST)

        if form.is_valid():

            preso = ServicesPreso(pessoa)

            for prisao in preso.prisoes:

                prisao.data_baixa = form.cleaned_data['data_baixa']
                prisao.motivo_baixa = form.cleaned_data['motivo_baixa']
                prisao.baixado_por = request.user.servidor
                prisao.save()

                # registra histórico de evento
                ev_prisao = prisao.eventos.filter(evento=Historico.EVENTO_BAIXA).first()

                if not ev_prisao:
                    ev_prisao = Historico(
                        pessoa=prisao.pessoa,
                        evento=Historico.EVENTO_BAIXA,
                        cadastrado_por=prisao.baixado_por)

                ev_prisao.data_registro = prisao.data_baixa
                ev_prisao.historico = u'Baixado em: <b>{:%d/%m/%Y}</b><br/>Processo: <b>{}</b><br/>Motivo: <b>{}</b>'.format(  # noqa
                    prisao.data_baixa,
                    prisao.processo.numero,
                    prisao.motivo_baixa.nome)

                ev_prisao.save()
                prisao.eventos.add(ev_prisao)

            messages.success(request, 'Baixa de prisões realizada com sucesso!')

        return redirect(request.META.get('HTTP_REFERER', '/'))

    else:

        form = BaixarPrisaoForm()

        return render(
            request,
            template_name="nadep/modal_registrar_baixa_form.html",
            context={
                'pessoa': pessoa,
                'form': form,
            })


@login_required
@permission_required('nadep.view_prisao')
def visualizar_prisao(request, prisao_id):
    """
    Realiza uma busca por uma prisão e retorna um usuário, um processo, uma lista de atendimento e uma lista
    de andamentos do processo
    """

    prisao = get_object_or_404(Prisao, id=prisao_id, ativo=True)
    pessoa = prisao.pessoa
    atendimentos = Atendimento.objects.filter(prisao_id=prisao_id, ativo=True)
    fases = Fase.objects.filter(processo=prisao.processo, ativo=True).order_by('data_protocolo')

    angular = 'PrisaoCtrl'

    return render(request=request, template_name="nadep/visualizar_prisao.html", context=locals())


@login_required
@reversion.create_revision(atomic=False)
@permission_required('nadep.add_prisao')
def converter_prisao(request, prisao_id):

    if request.method == 'POST' and request.is_ajax():

        dados = simplejson.loads(request.body)
        privativa = Prisao.objects.get(id=prisao_id)

        horas, minutos = dados['duracao_pena']['horas'].split(':')

        if hasattr(privativa, 'originada'):
            restritiva = privativa.originada
        else:
            restritiva = Prisao()
            restritiva.__dict__.update(privativa.__dict__)
            restritiva.origem = privativa
            restritiva.pk = None

        restritiva.duracao_pena_anos = 0
        restritiva.duracao_pena_meses = 0
        restritiva.duracao_pena_dias = 0
        restritiva.duracao_pena_horas = timedelta(hours=int(horas), minutes=int(minutos))
        restritiva.multa = 0
        restritiva.pena = Prisao.PENA_RESTRITIVA

        # primeira vez para poder vincular restricoes
        restritiva.save()

        for restricao in dados['restricoes']:

            if dados['restricoes'][restricao]:

                restricao, nova = PenaRestritiva.objects.get_or_create(
                    prisao=restritiva, restricao=int(restricao)
                )

                if restricao.restricao == PenaRestritiva.RESTRICAO_PRESTACAO_PECUNIARIA:
                    if 'prestacao_pecuniaria' in dados:
                        restritiva.prestacao_pecuniaria = dados['prestacao_pecuniaria']

        # segunda vez para gerar o evento com restricoes
        restritiva.save()

        reversion.set_user(request.user)
        reversion.set_comment(Util.get_comment_save(request.user, restritiva, not hasattr(privativa, 'originada')))

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})


@never_cache
@login_required
def cadastrar_transferencia(request, pessoa_id):
    aprisionamento = Aprisionamento(situacao=Aprisionamento.SITUACAO_PRESO,
                                    origem_cadastro=Aprisionamento.ORIGEM_REGISTRO,
                                    cadastrado_por=request.user.servidor)

    dados = simplejson.loads(request.body)
    dados['data_inicial'] = dados['data_inicial'][:10]

    form = CadastrarTransferenciaForm(dados, instance=aprisionamento)

    if form.is_valid():

        aprisionamento = form.save()

        # altera dados da parte processual
        parte = aprisionamento.prisao.parte
        parte.defensor_id = dados.get('defensor')
        parte.defensoria_id = dados.get('defensoria')
        parte.save()

        return JsonResponse({'success': True})

    else:
        return JsonResponse({
            'success': False,
            'errors': [({'field': k, 'message': v[0]}) for k, v in form.errors.items()]
        })


@never_cache
@login_required
def cadastrar_soltura(request, pessoa_id):

    dados = simplejson.loads(request.body)

    if 'data_inicial' in dados:
        dados['data_inicial'] = dados['data_inicial'][:10]
    else:
        return JsonResponse({'success': False, 'errors': ['Informe uma data válida']})

    aprisionamento = Aprisionamento.objects.filter(
        prisao=dados['prisao'],
        data_final=None,
        ativo=True
    ).first()

    if aprisionamento:

        aprisionamento.situacao = Aprisionamento.SITUACAO_SOLTO
        aprisionamento.data_final = dados['data_inicial']
        aprisionamento.save()

        prisao = Prisao.objects.get(id=dados['prisao'])

        soltura = Soltura(
            aprisionamento=aprisionamento,
            processo=prisao.processo,
            tipo=dados['tipo'],
            historico=dados['historico'],
            cadastrado_por=request.user.servidor
        )

        soltura.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'errors': ['Não existe um aprisionamento cadastrado para esse processo']})


@login_required
@reversion.create_revision(atomic=False)
def cadastrar_falta(request, pessoa_id):

    dados = simplejson.loads(request.body)

    if 'id' in dados and dados['id']:
        falta = Falta.objects.get(id=dados['id'])
    else:
        falta = Falta(cadastrado_por=request.user.servidor)

    form = CadastrarFaltaForm(dados, instance=falta)

    if form.is_valid():

        if not falta.processo:
            falta.processo = Processo.objects.create(numero=str(uuid.uuid4()), tipo=Processo.TIPO_PAD)
            Parte.objects.create(processo=falta.processo)

        novo = (falta.id is None)
        falta = form.save()

        falta.remissoes.update(
            data_exclusao=datetime.now(),
            excluido_por=request.user.servidor,
            ativo=False
        )

        if falta.resultado == Falta.RESULTADO_PROCEDENTE:
            if 'remissoes' in dados:
                for remissao in dados['remissoes']:
                    if remissao['desconto'] > 0:
                        Remissao.objects.create(
                            falta=falta,
                            pessoa=falta.pessoa,
                            data_inicial=falta.data_fato,
                            data_final=falta.data_fato,
                            dias_registro=remissao['desconto'] * -1,
                            dias_remissao=remissao['desconto'] * -1,
                            para_progressao=remissao['para_progressao'],
                            cadastrado_por=request.user.servidor
                        )

        reversion.set_user(request.user)
        reversion.set_comment(Util.get_comment_save(request.user, falta, novo))

        return JsonResponse({'success': True})

    else:
        return JsonResponse({'success': False})


@never_cache
@login_required
@reversion.create_revision(atomic=False)
def excluir_falta(request, pessoa_id):

    dados = simplejson.loads(request.body)

    try:
        falta = Falta.objects.get(id=dados['id'])
        falta.excluir(request.user)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def get_falta(request, pessoa_id):

    faltas = Falta.objects.filter(
        pessoa_id=pessoa_id,
        ativo=True
    ).values(
        'id',
        'data_fato',
        'observacao',
        'cadastrado_por__nome',
        'data_cadastro',
        'numero_pad',
        'processo_id',
        'processo__numero_puro',
        'processo__grau',
        'estabelecimento_penal',
        'estabelecimento_penal__nome',
        'resultado'
    ).order_by('data_fato')

    for falta in faltas:
        falta['pessoa'] = int(pessoa_id)
        falta['cadastrado_por'] = falta.pop('cadastrado_por__nome')
        falta['processo_numero'] = falta.pop('processo__numero_puro')
        falta['processo_grau'] = falta.pop('processo__grau')
        falta['estabelecimento_penal_nome'] = falta.pop('estabelecimento_penal__nome')
    return JsonResponse({'faltas': list(faltas), 'LISTA': {'RESULTADO': dict(Falta.LISTA_RESULTADO)}}, safe=False)


@login_required
@reversion.create_revision(atomic=False)
def cadastrar_remissao(request, pessoa_id):

    dados = simplejson.loads(request.body)

    if 'id' in dados and dados['id']:
        remissao = Remissao.objects.get(id=dados['id'])
    else:
        remissao = Remissao(cadastrado_por=request.user.servidor)

    form = CadastrarRemissaoForm(dados, instance=remissao)

    if form.is_valid():

        novo = (remissao.id is None)
        remissao = form.save()

        reversion.set_user(request.user)
        reversion.set_comment(Util.get_comment_save(request.user, remissao, novo))

        return JsonResponse({'success': True})

    else:
        return JsonResponse({'success': False})


@login_required
@reversion.create_revision(atomic=False)
def excluir_remissao(request, pessoa_id):

    dados = simplejson.loads(request.body)

    try:
        remissao = Remissao.objects.get(id=dados['id'])
        remissao.excluir(request.user)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@never_cache
@login_required
def get_remissao(request, pessoa_id):

    total = 0
    remissoes = Remissao.objects.filter(
        pessoa_id=pessoa_id,
        ativo=True
    ).values(
        'id',
        'data_inicial',
        'data_final',
        'tipo',
        'para_progressao',
        'dias_registro',
        'dias_remissao',
        'cadastrado_por__nome',
        'falta_id',
        'falta__observacao',
        'data_cadastro'
    ).order_by('data_inicial', 'para_progressao')

    for remissao in remissoes:
        total += remissao['dias_remissao']
        remissao['pessoa'] = int(pessoa_id)
        remissao['cadastrado_por'] = remissao.pop('cadastrado_por__nome')
        remissao['falta_observacao'] = remissao.pop('falta__observacao')

    return JsonResponse({
        'total': total,
        'remissoes': list(remissoes),
        'LISTA': {'TIPO': dict(Remissao.LISTA_TIPO)}}, safe=False)


@never_cache
@login_required
def get_total_remissao_periodo(request, pessoa_id):

    total = Remissao.objects.filter(
        pessoa_id=pessoa_id,
        ativo=True
    ).order_by(
        'para_progressao'
    ).values(
        'para_progressao'
    ).annotate(
        total=Sum('dias_remissao')
    )

    if request.method == 'POST':

        dados = simplejson.loads(request.body)

        if dados['data_referencia']:
            total = total.filter(data_final__lt=dados['data_referencia'][:10])

    return JsonResponse(list(total), safe=False)


@never_cache
@login_required
def get_prisao(request, pessoa_id):

    pessoa = PessoaAssistida.objects.get(id=pessoa_id)
    preso = ServicesPreso(pessoa)

    prisoes = {}
    for prisao in preso.prisoes:
        prisoes[prisao.id] = {
            'id': prisao.id,
            'estabelecimento_penal': prisao.estabelecimento_penal.nome if prisao.estabelecimento_penal else None,
            'data_fato': prisao.data_fato,
            'data_prisao': prisao.data_prisao,
            'dias_preso': prisao.dias_preso,
            'regime_inicial': prisao.regime_inicial,
            'regime_atual': prisao.regime_atual,
            'duracao_pena': prisao.duracao_pena,
            'processo': {
                'numero': prisao.processo.numero,
                'numero_puro': prisao.processo.numero_puro,
                'chave': prisao.processo.chave,
                'grau': prisao.processo.grau,
                'classe': prisao.processo.acao.nome if prisao.processo.acao else None,
                'assuntos': [assunto.nome for assunto in prisao.processo.assuntos.all()]
            } if prisao.processo else {},
            'tipificacao': prisao.tipificacao.nome if prisao.tipificacao else None,
            'tipo': prisao.get_tipo(),
            'pena': prisao.pena,
            'parte': {'atendimento': prisao.parte.atendimento.numero} if prisao.parte and prisao.parte.atendimento else {},  # noqa
            'resultado_pronuncia': prisao.resultado_pronuncia,
            'origem': prisao.origem_id,
            'restricoes': {},
            'tentado_consumado': prisao.tentado_consumado,
        }

    prisoes_inativas = {}
    for prisao in preso.prisoes_inativas():
        prisoes_inativas[prisao.id] = {
            'id': prisao.id,
            'estabelecimento_penal': prisao.estabelecimento_penal.nome,
            'data_prisao': prisao.data_prisao,
            'dias_preso': prisao.dias_preso,
            'regime_inicial': prisao.regime_inicial,
            'regime_atual': prisao.regime_atual,
            'duracao_pena': prisao.duracao_pena,
            'processo': {
                'numero': prisao.processo.numero,
                'numero_puro': prisao.processo.numero_puro,
                'chave': prisao.processo.chave,
                'grau': prisao.processo.grau,
                'classe': prisao.processo.acao.nome if prisao.processo.acao else None,
                'assuntos': [assunto.nome for assunto in prisao.processo.assuntos.all()]
            } if prisao.processo else {},
            'tipificacao': prisao.tipificacao.nome,
            'tipo': prisao.get_tipo(),
            'pena': prisao.pena,
            'parte': {'atendimento': prisao.parte.atendimento.numero} if prisao.parte else {},
            'resultado_pronuncia': prisao.resultado_pronuncia,
            'originada': prisao.originada.id if hasattr(prisao, 'originada') else None,
            'tentado_consumado': prisao.tentado_consumado,
        }

    perm_delete_prisao = request.user.has_perm(perm='nadep.delete_prisao')

    return JsonResponse({
        'prisoes': prisoes,
        'prisoes_inativas': prisoes_inativas,
        'LISTA': {
            'PENA': dict(Prisao.LISTA_PENA),
            'TIPO': dict(Prisao.LISTA_TIPO),
            'SITUACAO': dict(Prisao.LISTA_SITUACAO),
            'REGIME': dict(Prisao.LISTA_REGIME),
            'PRONUNCIA': dict(Prisao.LISTA_PRONUNCIA),
            'SENTENCA': dict(Prisao.LISTA_SENTENCA),
            'RESTRICAO': dict(PenaRestritiva.LISTA_RESTRICAO),
            'TENTADO_CONSUMADO': dict(Prisao.LISTA_TIPO_CRIME),
        },
        'permissao_delete_prisao': perm_delete_prisao
    }, safe=False)


@never_cache
@login_required
def get_guia(request, pessoa_id):

    pessoa = PessoaAssistida.objects.get(id=pessoa_id)
    preso = ServicesPreso(pessoa)

    preso = {
        'id': pessoa.id,
        'pena_cumprida': preso.pena_cumprida(),
        'duracao_total_pena': preso.duracao_total_pena(),
        'prisoes': [{
                        'id': prisao.id,
                        'processo': {
                            'numero': prisao.processo.numero,
                            'numero_puro': prisao.processo.numero_puro,
                            'chave': prisao.processo.chave,
                            'grau': prisao.processo.grau,
                        } if prisao.processo else {},
                        'tipificacao': prisao.tipificacao.nome if prisao.tipificacao else None,
                        'data_fato': prisao.data_fato,
                        'data_prisao': prisao.data_prisao,
                        'data_sentenca_condenatoria': prisao.data_sentenca_condenatoria,
                        'regime_inicial': prisao.regime_inicial,
                        'regime_atual': prisao.regime_atual,
                        'duracao_pena': prisao.duracao_pena,
                        'dias_preso': prisao.dias_preso,
                        'fracao_pr': None if prisao.get_fracao_pr is None else prisao.get_fracao_pr.__str__(),
                        'fracao_lc': None if prisao.get_fracao_lc is None else prisao.get_fracao_lc.__str__(),
                        'pena': prisao.pena,
                        'prestacao_pecuniaria': prisao.prestacao_pecuniaria,
                        'restricoes': [restricao.restricao for restricao in prisao.penarestritiva_set.all()],
                        'tentado_consumado': prisao.tentado_consumado,
                    } for prisao in preso.prisoes_condenado()]
    }

    return JsonResponse({
        'preso': preso,
        'LISTA': {
            'REGIME': dict(Prisao.LISTA_REGIME),
            'RESTRICAO': dict(PenaRestritiva.LISTA_RESTRICAO),
            'TENTADO_CONSUMADO': dict(Prisao.LISTA_TIPO_CRIME),
        }
    }, safe=False)


@never_cache
@login_required
def get_processo(request, pessoa_id):

    pessoa = PessoaAssistida.objects.get(id=pessoa_id)
    preso = ServicesPreso(pessoa)

    preso = {
        'id': pessoa.id,
        'partes': [{
            'id': parte.id,
            'prisoes': parte.prisoes.count(),
            'processo': {
                'numero': parte.processo.numero,
                'numero_puro': parte.processo.numero_puro,
                'chave': parte.processo.chave,
                'grau': parte.processo.grau,
                'comarca': parte.processo.comarca.nome if parte.processo.comarca else None,
                'area': parte.processo.area.nome if parte.processo.area else None,
                'vara': parte.processo.vara.nome if parte.processo.vara else None,
                'acao': parte.processo.acao.nome if parte.processo.acao else None,
                'autores': [{
                    'defensor': autor.defensor.nome if autor.defensor else None,
                    'atendimento': {
                        'numero': autor.atendimento.numero,
                        'tipo': autor.atendimento.tipo,
                        'requerente': autor.atendimento.requerente.nome if autor.atendimento.requerente else None,
                    },
                } for autor in parte.processo.autores],
                'reus': [{
                    'defensor': reu.defensor.nome if reu.defensor else None,
                    'atendimento': {
                        'numero': reu.atendimento.numero,
                        'tipo': reu.atendimento.tipo,
                        'requerente': reu.atendimento.requerente.nome if reu.atendimento.requerente else None,
                    },
                } for reu in parte.processo.reus],
            }
        } for parte in preso.partes()]
    }

    return JsonResponse({'preso': preso}, safe=False)


@never_cache
@login_required
def get_calculo(request, pessoa_id):

    pessoa = PessoaAssistida.objects.get(id=pessoa_id)
    preso = ServicesPreso(pessoa)
    guia = preso.prisoes_condenado().first()

    if guia and request.GET.get('db'):
        data_base = datetime.strptime(request.GET.get('db'), '%Y%m%d').date()
        preso = ServicesPreso(pessoa, data_base=data_base)
        guia.data_base = data_base
        guia.save()

    guias = preso.prisoes_condenado()

    if guia and (guia.regime_atual is not None or guia.regime_inicial is not None):
        preso.salvar_calculo(cadastrado_por=request.user.servidor)

    calculo = {
        'execucao': {
            'id': guias[0].id,
            'numero': guias[0].processo.numero if guias[0].processo else None,
            'estabelecimento_penal': guias[0].estabelecimento_penal_id,
        } if guias else None,
        'pena_total': preso.duracao_total_pena(),
        'pena_cumprida': preso.pena_cumprida(),
        'pena_restante': preso.pena_restante(),
        'data_base': preso.data_base,
        'data_prisao_definitiva': preso.data_prisao_definitiva(),
        'progressao': {
            'data_base': preso.data_base,
            'remissoes': preso.total_remissoes_pr(),
            'pena_cumprida': preso.calcular_pena_cumprida_pr().to_dict(),
            'fracoes': [{
                'fracao': key.__str__(),
                'pena_imposta': fracao.pena_imposta.to_dict(),
                'pena_cumprida': fracao.pena_cumprida.to_dict(),
                'diferenca': fracao.dif_penas().to_dict(),
                'calculo': fracao.calculo_pr().to_dict(),
            } for key, fracao in six.iteritems(preso.calcular_fracoes_progressao_regime())],
            'soma_pena_cumprida': preso.calcular_soma_pena_cumprida_progressao_regime().to_dict(),
            'soma_fracoes': preso.calcular_soma_fracoes_progressao_regime().to_dict(),
        },
        'data_progressao_regime': preso.calcular_data_progressao_regime(),
        'livramento': {
            'data_base': preso.data_prisao_definitiva(),
            'fracoes': [{
                'fracao': key.__str__(),
                'pena_imposta': fracao.pena_imposta.to_dict(),
                'calculo': fracao.calculo_pr().to_dict(),
            } for key, fracao in six.iteritems(preso.calcular_fracoes_livramento_condicial())],
            'soma_fracoes': preso.calcular_soma_fracoes_livramento_condicional().to_dict(),
        },
        'data_livramento_condicional': preso.calcular_data_livramento_condicial(),
        'data_termino': preso.calcular_data_termino_pena(),
        'regime_atual': guias[0].regime_atual if guias else None,
        'guias': [{
            'id': g.id,
            'numero': g.processo.numero if g.processo else None,
            'duracao_pena': g.duracao_pena,
        } for g in guias],
        'remissoes': preso.total_remissoes(),
        'detracoes': preso.total_detracoes(),
        'interrupcoes': preso.total_interrupcoes(),
        'condicao': guias[0].regime_inicial if guias else None,
        'cadastrado_por': {
            'id': request.user.servidor.id,
            'nome': request.user.servidor.nome,
            'username': request.user.username,
        },
        'data_cadastro': datetime.now(),
    }

    return JsonResponse(calculo, safe=False)


@never_cache
@login_required
def get_aprisionamento(request, pessoa_id):

    pessoa = PessoaAssistida.objects.get(id=pessoa_id)
    preso = ServicesPreso(pessoa)

    aprisionamentos = [{
        'id': prisao.id,
        'data_inicial': prisao.data_inicial,
        'data_final': prisao.data_final,
        'estabelecimento_penal': {
            'id': prisao.estabelecimento_penal_id,
            'nome': prisao.estabelecimento_penal.nome,
            'municipio': prisao.estabelecimento_penal.endereco.municipio_id
        } if prisao.estabelecimento_penal else None,
        'data_cadastro': prisao.data_cadastro,
        'cadastrado_por': {
            'id': prisao.cadastrado_por_id,
            'nome': prisao.cadastrado_por.nome,
            'username': prisao.cadastrado_por.usuario.username,
        } if prisao.cadastrado_por else None,
        'prisao': {
            'id': prisao.prisao.id,
            'tipo': prisao.prisao.get_tipo(),
            'processo': {
                'numero': prisao.prisao.processo.numero,
            } if prisao.prisao.processo else None
        },
        'dias_preso': prisao.dias_preso,
        'duracao': AnoMesDia.calcular_diff_data(prisao.data_inicial, (prisao.data_final if prisao.data_final else datetime.now()) + timedelta(days=1)).to_dict(),  # noqa
        'historico': prisao.historico,
        'situacao': prisao.situacao,
        'detracao': prisao.detracao,
        'ativo': prisao.ativo,
    } for prisao in preso.aprisionamentos()]

    return JsonResponse({
        'preso': int(pessoa_id),
        'aprisionamentos': list(aprisionamentos),
        'total': preso.total_aprisionamentos(),
        'total_detracao': preso.total_detracoes(),
        'LISTA': {'SITUACAO': dict(Aprisionamento.LISTA_SITUACAO), 'TIPO': dict(Prisao.LISTA_TIPO)}
    }, safe=False)


@never_cache
@login_required
def get_interrupcao(request, pessoa_id):

    interrupcoes = Interrupcao.objects.filter(pessoa_id=pessoa_id, ativo=True).order_by('data_inicial')

    hoje = date.today()
    total = AnoMesDia()
    for interrupcao in interrupcoes:
        total += AnoMesDia.calcular_diff_data(interrupcao.data_inicial, interrupcao.data_final if interrupcao.data_final else hoje)  # noqa

    interrupcoes = [{
        'id': interrupcao.id,
        'data_inicial': interrupcao.data_inicial,
        'data_final': interrupcao.data_final if interrupcao.data_final else None,
        'dias': interrupcao.dias,
        'duracao': AnoMesDia.calcular_diff_data(interrupcao.data_inicial, interrupcao.data_final if interrupcao.data_final else hoje).to_dict(),  # noqa
        'observacao': interrupcao.observacao,
        'data_cadastro': interrupcao.data_cadastro,
        'cadastrado_por': {
            'id': interrupcao.cadastrado_por_id,
            'nome': interrupcao.cadastrado_por.nome,
            'username': interrupcao.cadastrado_por.usuario.username,
        } if interrupcao.cadastrado_por else {},
        'pessoa': int(pessoa_id),
    } for interrupcao in interrupcoes]

    return JsonResponse({
        'preso': int(pessoa_id),
        'interrupcoes': list(interrupcoes),
        'total': total.to_dict(),
    }, safe=False)


@login_required
@reversion.create_revision(atomic=False)
def cadastrar_interrupcao(request, pessoa_id):

    dados = simplejson.loads(request.body)

    dados['data_inicial'] = dados['data_inicial'][:10] if 'data_inicial' in dados and dados['data_inicial'] else None
    dados['data_final'] = dados['data_final'][:10] if 'data_final' in dados and dados['data_final'] else None

    if 'id' in dados and dados['id']:
        interrupcao = Interrupcao.objects.get(id=dados['id'])
    else:
        interrupcao = Interrupcao(cadastrado_por=request.user.servidor)

    form = CadastrarInterrupcaoForm(dados, instance=interrupcao)

    if form.is_valid():

        novo = (interrupcao.id is None)
        interrupcao = form.save()

        reversion.set_user(request.user)
        reversion.set_comment(Util.get_comment_save(request.user, interrupcao, novo))

        return JsonResponse({'success': True})

    else:
        return JsonResponse({'success': False, 'errors': [({'field': k, 'message': v[0]}) for k, v in form.errors.items()]})  # noqa


@login_required
@reversion.create_revision(atomic=False)
def excluir_interrupcao(request, pessoa_id):

    dados = simplejson.loads(request.body)

    try:
        interrupcao = Interrupcao.objects.get(id=dados['id'])
        interrupcao.excluir(request.user)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@reversion.create_revision(atomic=False)
def cadastrar_aprisionamento(request, pessoa_id):

    dados = simplejson.loads(request.body)

    dados['data_inicial'] = dados.get('data_inicial', '')[:10]
    dados['data_final'] = dados.get('data_final', '')[:10]

    if 'id' in dados and dados['id']:
        detracao = Aprisionamento.objects.get(id=dados['id'])
    else:
        detracao = Aprisionamento(cadastrado_por=request.user.servidor, detracao=True)

    form = CadastrarDetracaoForm(dados, instance=detracao)

    if form.is_valid():

        novo = (detracao.id is None)
        form.save()

        reversion.set_user(request.user)
        reversion.set_comment(Util.get_comment_save(request.user, detracao, novo))

        return JsonResponse({'success': True})

    else:
        return JsonResponse({
            'success': False,
            'errors': [({'field': k, 'message': v[0]}) for k, v in form.errors.items()]
        })


@login_required
@reversion.create_revision(atomic=False)
def excluir_aprisionamento(request, pessoa_id):

    dados = simplejson.loads(request.body)

    try:
        aprisionamento = Aprisionamento.objects.get(id=dados['id'])
        aprisionamento.excluir(request.user)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@never_cache
@login_required
@reversion.create_revision(atomic=False)
def get_horas(request, prisao_id):

    prisao = Prisao.objects.get(id=prisao_id)

    if not prisao.penarestritiva_set.filter(restricao=PenaRestritiva.RESTRICAO_PRESTACAO_SERVICO).exists():
        return JsonResponse({
            'success': False,
        }, safe=False)

    horas_registro = []
    horas_cumpridas = timedelta()

    for hora in prisao.restricaoprestacaoservico_set.filter(ativo=True).order_by('data_referencia'):
        horas_registro.append({
            'id': hora.id,
            'prisao': prisao.id,
            'ano': hora.data_referencia.year,
            'mes': hora.data_referencia.month,
            'horas': hora.horas_to_string()
        })
        horas_cumpridas += hora.horas_trabalhadas

    if horas_cumpridas.total_seconds() and prisao.duracao_pena_horas.total_seconds():
        porcentagem = round(horas_cumpridas.total_seconds() / prisao.duracao_pena_horas.total_seconds() * 100, 2)
    else:
        porcentagem = 0

    horas_restantes = prisao.duracao_pena_horas - horas_cumpridas

    if prisao.duracao_pena_horas:
        horas, minutos = divmod(prisao.duracao_pena_horas.total_seconds() / 60, 60)
        pena_total = '{0:d}:{1:02d}'.format(int(horas), int(minutos))
    else:
        pena_total = '0:00'

    if horas_cumpridas:
        horas, minutos = divmod(horas_cumpridas.total_seconds() / 60, 60)
        horas_cumpridas_str = '{0:d}:{1:02d}'.format(int(horas), int(minutos))
    else:
        horas_cumpridas_str = '0:00'

    if horas_restantes and horas_restantes.days < 0:
        horas, minutos = divmod(horas_restantes.total_seconds() * -1 / 60, 60)
        horas_excedidas_str = '{0:d}:{1:02d}'.format(int(horas), int(minutos))
        horas_restantes_str = '0:00'
    else:
        horas, minutos = divmod(horas_restantes.total_seconds() / 60, 60)
        horas_restantes_str = '{0:d}:{1:02d}'.format(int(horas), int(minutos))
        horas_excedidas_str = '0:00'

    pena_cumprida_dias = AnoMesDia(dia=int(horas_cumpridas.total_seconds() / 3600), mod_ano=365, mod_mes=30)
    pena_restante_dias = AnoMesDia(dia=int(horas_restantes.total_seconds() / 3600), mod_ano=365, mod_mes=30)

    relatorios = Relatorio.objects.filter(
        papeis=request.user.servidor.papel,
        locais__pagina=Local.PAG_LIVRE_DETALHES_BTN_CALCULO_HORAS
    ).ativos()

    return JsonResponse({
        'success': True,
        'horas': horas_registro,
        'resumo': {
            'processo': prisao.processo.numero,
            'pena_total': pena_total,
            'horas_cumpridas': horas_cumpridas_str,
            'horas_restantes': horas_restantes_str,
            'horas_excedidas': horas_excedidas_str,
            'pena_cumprida_dias': pena_cumprida_dias.to_dict(),
            'pena_restante_dias': pena_restante_dias.to_dict(),
            'porcentagem': porcentagem
        },
        'consultado_por': {
            'id': request.user.servidor.id,
            'nome': request.user.servidor.nome,
            'username': request.user.username,
        },
        'relatorios': [relatorio.to_dict() for relatorio in relatorios],
        'data_consulta': datetime.now()
    }, safe=False)


@login_required
@reversion.create_revision(atomic=False)
def salvar_horas(request, prisao_id):

    if request.method == 'POST' and request.is_ajax():

        dados = simplejson.loads(request.body)

        prisao = Prisao.objects.get(id=prisao_id)

        horas, minutos = dados['horas'].split(':')

        hora, hora_new = RestricaoPrestacaoServico.objects.get_or_create(
            prisao=prisao,
            data_referencia=date(year=int(dados['ano']), month=int(dados['mes']), day=1),
            defaults={
                'cadastrado_por': request.user.servidor,
                'horas_trabalhadas': timedelta(hours=int(horas), minutes=int(minutos)),
            }
        )

        if not hora_new:
            hora.horas_trabalhadas = timedelta(hours=int(horas), minutes=int(minutos))
            hora.data_exclusao = None
            hora.excluido_por = None
            hora.ativo = True
            hora.save()

        reversion.set_user(request.user)
        reversion.set_comment(Util.get_comment_save(request.user, hora, hora_new))

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})


@login_required
@reversion.create_revision(atomic=False)
def excluir_horas(request, prisao_id):

    if request.method == 'POST' and request.is_ajax():

        dados = simplejson.loads(request.body)

        hora = RestricaoPrestacaoServico.objects.get(id=dados['id'])
        hora.data_exclusao = datetime.now()
        hora.excluido_por = request.user.servidor
        hora.ativo = False
        hora.save()

        reversion.set_user(request.user)
        reversion.set_comment(Util.get_comment_delete(request.user, hora))

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})


@login_required
@reversion.create_revision(atomic=False)
def alterar_regime(request, prisao_id):

    dados = simplejson.loads(request.body)

    dados['prisao'] = dados['prisao']['id']

    if int(dados['regime']) == Prisao.REGIME_ABERTO:
        dados['estabelecimento_penal'] = None
    else:
        dados['estabelecimento_penal'] = dados['estabelecimento_penal']['id']

    form = CadastrarMudancaRegimeForm(dados, instance=MudancaRegime(cadastrado_por=request.user.servidor))

    if form.is_valid():

        regime = form.save()

        reversion.set_user(request.user)
        reversion.set_comment(Util.get_comment_save(request.user, regime, True))

        preso = ServicesPreso(regime.prisao.pessoa)

        for prisao in preso.prisoes_condenado():
            prisao.data_base = regime.data_base
            prisao.regime_atual = regime.regime
            prisao.estabelecimento_penal = regime.estabelecimento_penal
            prisao.save()

        aprisionamento = Aprisionamento.objects.filter(
            prisao__pessoa=regime.prisao.pessoa, data_final=None, ativo=True
        ).first()

        if regime.estabelecimento_penal:

            if not aprisionamento or aprisionamento.estabelecimento_penal != regime.estabelecimento_penal:

                aprisionamento = Aprisionamento(
                    prisao=regime.prisao,
                    estabelecimento_penal=regime.estabelecimento_penal,
                    data_inicial=regime.data_registro,
                    historico=regime.historico,
                    situacao=Aprisionamento.SITUACAO_PRESO,
                    origem_cadastro=Aprisionamento.ORIGEM_MUDANCA_REGIME,
                    cadastrado_por=request.user.servidor
                )

                aprisionamento.save()

        elif aprisionamento:

            aprisionamento.data_final = regime.data_registro
            aprisionamento.situacao = Aprisionamento.SITUACAO_SOLTO
            aprisionamento.save()

        if regime.tipo == MudancaRegime.TIPO_PROGRESSAO:
            for remissao in Remissao.objects.filter(pessoa=prisao.pessoa, para_progressao=True, ativo=True):
                remissao.para_progressao = False
                remissao.save()

        return JsonResponse({'success': True})

    else:
        return JsonResponse({
            'success': False,
            'errors': [({'field': k, 'message': v[0]}) for k, v in form.errors.items()]
        })


@login_required
@reversion.create_revision(atomic=False)
def liquidar_pena(request, prisao_id):

    dados = simplejson.loads(request.body)

    prisao = Prisao.objects.get(id=dados['prisao']['id'])

    reversion.set_user(request.user)
    reversion.set_comment(Util.get_comment_save(request.user, prisao, True))

    preso = ServicesPreso(prisao.pessoa)

    for prisao in preso.prisoes_condenado():

        form = LiquidarPenaForm(dados, instance=prisao)

        if form.is_valid():
            form.save()

    aprisionamento = Aprisionamento.objects.filter(
        prisao__pessoa=prisao.pessoa,
        prisao__tipo=Prisao.TIPO_CONDENADO,
        data_final=None,
        ativo=True
    ).first()

    if aprisionamento:
        aprisionamento.data_final = prisao.data_liquidacao
        aprisionamento.situacao = Aprisionamento.SITUACAO_SOLTO
        aprisionamento.save()

    return JsonResponse({'success': True})


@never_cache
@login_required
def get_historico(request, pessoa_id):

    historico = Historico.objects.filter(
        pessoa=pessoa_id, ativo=True
    ).order_by(
        'data_registro'
    ).values(
        'id',
        'evento',
        'historico',
        'data_registro',
        'data_cadastro',
        'cadastrado_por',
        'cadastrado_por__nome',
        'cadastrado_por__usuario__username',
    )

    for evento in historico:
        evento['cadastrado_por'] = {
            'id': evento.pop('cadastrado_por'),
            'nome': evento.pop('cadastrado_por__nome'),
            'username': evento.pop('cadastrado_por__usuario__username'),
        }

    return JsonResponse({'historico': list(historico), 'LISTA': {'EVENTO': dict(Historico.LISTA_EVENTO)}}, safe=False)
