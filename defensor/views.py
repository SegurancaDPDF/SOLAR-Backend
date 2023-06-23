# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import json as simplejson
import logging
from datetime import date, datetime, time

# Bibliotecas de terceiros
from constance import config
from dateutil.parser import parse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.cache import cache
from django.db.models import F, Q, Count
from django.http import JsonResponse
from django.shortcuts import redirect, render
import math

from django.views.decorators.cache import never_cache
import reversion

# Solar
from atendimento.atendimento.models import Defensor as Atendimento
from contrib.models import Util
from evento.models import Agenda

# Modulos locais
from .forms import AtuacaoForm, DocumentoForm, ExcluirAtuacaoForm, LotacaoForm, BuscarEditalPlantaoForm, InscricaoPlantaoForm  # noqa: E501
from .models import Atuacao, Defensor, Documento, EditalConcorrenciaPlantao, InscricaoEditalPlantao, VagaEditalPlantao


logger = logging.getLogger(__name__)


@login_required
@permission_required('defensor.add_atuacao')
def atuacao_index(request):
    angular = 'AtuacaoCtrl'

    return render(request=request, template_name="defensor/atuacao.html", context=locals())


def listar_to_json(atuacoes, defensores):

    arr = {}

    # inclui select_related para reduzir as consultas ao banco de dados
    defensores = defensores.select_related('servidor__usuario')

    for defensor in defensores:
        arr[defensor.servidor.usuario.username] = {
            'id': defensor.id,
            'nome': defensor.servidor.nome,
            'username': defensor.servidor.usuario.username,
            'titular': [],
            'nucleos': list(defensor.nucleos_id)
        }

    atuacoes = atuacoes.values(
        'id',
        'servidor__usuario__username',
        'all_atuacoes__tipo',
        'all_atuacoes__data_inicial',
        'all_atuacoes__data_final',
        'all_atuacoes__defensoria_id',
        'all_atuacoes__defensoria__nome',
        'all_atuacoes__defensoria__nucleo__nome',
        'all_atuacoes__defensoria__grau',
        'all_atuacoes__tipo',
        'all_atuacoes__tipo',
        'all_atuacoes__documento__tipo',
        'all_atuacoes__documento__numero',
        'all_atuacoes__documento__data',
    )

    for atuacao in atuacoes:

        documento = {
            'tipo': None if atuacao['all_atuacoes__documento__tipo'] is None else Documento.LISTA_TIPO[atuacao['all_atuacoes__documento__tipo']][1],  # noqa
            'numero': atuacao['all_atuacoes__documento__numero'],
            'data': atuacao['all_atuacoes__documento__data'],
        }

        if documento['tipo'] and documento['numero'] and documento['data']:
            documento['nome'] = '{tipo} {numero} de {data:%d/%m/%Y}'.format(**documento)

        arr[atuacao['servidor__usuario__username']]['titular'].append({
            'tipo': atuacao['all_atuacoes__tipo'],
            'data_ini': Util.date_to_json(atuacao['all_atuacoes__data_inicial']),
            'data_fim': Util.date_to_json(atuacao['all_atuacoes__data_final']),
            'defensoria': {
                'id': atuacao['all_atuacoes__defensoria_id'],
                'nome': atuacao['all_atuacoes__defensoria__nome'],
                'nucleo': atuacao['all_atuacoes__defensoria__nucleo__nome'],
                'grau': atuacao['all_atuacoes__defensoria__grau']
            },
            'documento': documento,
        })

    new_arr = []
    for key in arr:
        new_arr.append(arr[key])

    return sorted(new_arr, key=lambda defensor: defensor['username'])


@never_cache
@login_required
def listar_plantao(request, ano=None):
    """
    Retorna lista de defensores e respectivas atuações
    :param request:
    :param ano: Ano de referência
    :return: json object
    """
    data = simplejson.loads(request.body)

    atuacoes = Defensor.objects.filter(
        Q(all_atuacoes__data_inicial__lte=Util.json_to_date(data['data_final'])) &
        (
            Q(all_atuacoes__data_final__gte=Util.json_to_date(data['data_inicial'])) |
            Q(all_atuacoes__data_final=None)
        ) &
        Q(all_atuacoes__defensoria__nucleo__plantao=True) &
        ~Q(all_atuacoes__tipo=Atuacao.TIPO_LOTACAO)
    )

    return JsonResponse(listar_to_json(atuacoes, atuacoes), safe=False)


@never_cache
@login_required
def atuacao_listar(request, defensor_id):
    """
    Retorna lista de atuações ativas do defensor
    :param request:
    :param defensor_id:
    :return:
    """

    try:
        filtro = simplejson.loads(request.body)
        filtro['data_ini'] = datetime.strptime(filtro['data_ini'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
        filtro['data_fim'] = datetime.combine(datetime.strptime(filtro['data_fim'], '%Y-%m-%dT%H:%M:%S.%fZ').date(),
                                              time.max)
    except Exception:
        filtro = None

    cache_key = 'defensor.atuacao_listar:{}'.format(defensor_id)
    cache_data = cache.get(cache_key)

    if not cache_data or filtro:

        arr = []

        atuacoes = Atuacao.objects.filter(
            defensor=defensor_id
        ).order_by('-tipo', 'data_inicial', '-defensoria__nucleo')

        if filtro:
            if 'data_ini' in filtro:
                atuacoes = atuacoes.filter(Q(data_final__gte=filtro['data_ini']) | Q(data_final=None))

            if 'data_fim' in filtro:
                atuacoes = atuacoes.filter(Q(data_inicial__lte=filtro['data_fim']))
        else:
            atuacoes = atuacoes.filter(ativo=True)

        for atuacao in atuacoes:
            arr.append({
                'filtro': filtro,
                'id': atuacao.id,
                'atuacao': atuacao.tipo,
                'titular': atuacao.titular.nome if atuacao.titular else None,
                'defensoria': {
                    'id': atuacao.defensoria.id,
                    'nome': atuacao.defensoria.nome,
                    'codigo': atuacao.defensoria.codigo,
                    'possui_categoria_agenda': atuacao.defensoria.categorias_de_agendas.exists(),
                    'nucleo': atuacao.defensoria.nucleo.id if atuacao.defensoria.nucleo else None,
                    'plantao': atuacao.defensoria.nucleo.plantao if atuacao.defensoria.nucleo else False,
                    'itinerante': atuacao.defensoria.nucleo.itinerante if atuacao.defensoria.nucleo else False,
                    'grau': atuacao.defensoria.grau,
                    'categorias_de_agendas': list(atuacao.defensoria.categorias_de_agendas.all().values('id', 'nome', 'sigla'))  # noqa
                },
                'comarca': {
                    'id': atuacao.defensoria.comarca.id,
                    'nome': atuacao.defensoria.comarca.nome,
                },
                'agendamento': False if (
                    atuacao.defensoria.nucleo and not atuacao.defensoria.nucleo.agendamento
                ) else True,
                'pode_criar_agenda': False if (
                    atuacao.defensoria.nucleo and (
                        not atuacao.defensoria.nucleo.agendamento or
                        atuacao.defensoria.nucleo.itinerante or
                        atuacao.defensoria.nucleo.plantao
                    )
                ) else True,
                'data_ini': Util.date_to_json(atuacao.data_inicial),
                'data_fim': Util.date_to_json(atuacao.data_final),
                'data_cad': Util.date_to_json(atuacao.data_cadastro),
                'observacao': atuacao.observacao,
                'designacao_extraordinaria': atuacao.designacao_extraordinaria,
                'cadastrado_por': {
                    'id': atuacao.cadastrado_por.id,
                    'nome': atuacao.cadastrado_por.nome,
                    'username': atuacao.cadastrado_por.usuario.username,
                } if atuacao.cadastrado_por else None,
                'documento': {
                    'tipo': None if atuacao.documento.tipo is None else Documento.LISTA_TIPO[atuacao.documento.tipo][1],
                    'numero': atuacao.documento.numero,
                    'data': Util.date_to_json(atuacao.documento.data),
                } if atuacao.documento else None,
                'ativo': atuacao.ativo})

        cache_data = arr

        if not filtro:  # se nao tem filtro, atualiza cache
            cache.set(cache_key, cache_data)

    return JsonResponse(cache_data, safe=False)


@login_required
def atuacao_supervisores_listar(request):

    # identifica defensorias onde o usuario está lotado
    defensorias = set(request.user.servidor.defensor.atuacoes_vigentes().values_list('defensoria_id', flat=True))

    # identifica quais são os supervisores das defensorias
    atuacoes = Atuacao.objects.vigentes(ajustar_horario=False).filter(
        defensoria__in=defensorias,
        defensor__eh_defensor=True
    ).annotate(
        defensor_nome=F('defensor__servidor__nome'),
        defensoria_nome=F('defensoria__nome'),
        pode_vincular_processo_judicial=F('defensoria__pode_vincular_processo_judicial'),
    ).values(
        'id',
        'defensor_id',
        'defensor_nome',
        'defensoria_id',
        'defensoria_nome',
        'pode_vincular_processo_judicial',
    )

    return JsonResponse(list(atuacoes), safe=False)


@never_cache
@login_required
def defensoria_listar(request):
    """
    Retorna lista de defensorias que defensor atuou em determinado período
    :param request:
    :return:
    """

    try:
        dados = simplejson.loads(request.body)
        dados['data_ini'] = datetime.strptime(dados['data_ini'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
        dados['data_fim'] = datetime.combine(datetime.strptime(dados['data_fim'], '%Y-%m-%dT%H:%M:%S.%fZ').date(),
                                             time.max)
    except KeyError:
        return JsonResponse({'error': True})

    atuacoes = Atuacao.objects.filter(
        Q(defensor=dados['defensor']) &
        Q(data_inicial__lte=dados['data_fim']) & (
            Q(data_final__gte=dados['data_ini']) | Q(data_final=None)
        )
    ).order_by(
        'defensoria__comarca__nome',
        'defensoria__nome'
    ).distinct(
        'defensoria__id',
        'defensoria__nome',
        'defensoria__comarca__id',
        'defensoria__comarca__nome'
    ).values(
        'defensoria__id',
        'defensoria__nome',
        'defensoria__comarca__id',
        'defensoria__comarca__nome',
    )

    arr = []
    for atuacao in atuacoes:
        arr.append({
            'id': atuacao['defensoria__id'],
            'nome': atuacao['defensoria__nome'],
            'comarca': {
                'id': atuacao['defensoria__comarca__id'],
                'nome': atuacao['defensoria__comarca__nome'],
            },
        })

    return JsonResponse(arr, safe=False)


@never_cache
@login_required
def defensoria_substituido_listar(request):
    """
    Retorna lista de defensorias que defensor foi substituído em determinado período
    :param request:
    :return:
    """
    try:
        dados = simplejson.loads(request.body)
        dados['data_ini'] = datetime.strptime(dados['data_ini'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
        dados['data_fim'] = datetime.combine(datetime.strptime(dados['data_fim'], '%Y-%m-%dT%H:%M:%S.%fZ').date(),
                                             time.max)
    except KeyError:
        return JsonResponse({'error': True})

    atuacoes = Atuacao.objects.filter(
        Q(titular=dados['defensor']) &
        Q(data_inicial__lte=dados['data_fim']) &
        (
            Q(data_final__gte=dados['data_ini']) |
            Q(data_final=None)
        )
    ).order_by(
        'defensoria__comarca__nome',
        'defensoria__nome'
    ).distinct(
        'defensoria__id',
        'defensoria__nome',
        'defensoria__comarca__nome'
    ).values(
        'defensoria__id',
        'defensoria__nome'
    )

    arr = []
    for atuacao in atuacoes:
        arr.append({
            'id': atuacao['defensoria__id'],
            'nome': atuacao['defensoria__nome']})

    return JsonResponse(arr, safe=False)


@login_required
@reversion.create_revision(atomic=False)
@permission_required('defensor.add_atuacao')
def atuacao_salvar(request):
    """Utilizado para salvar a atuação de Defensor"""

    errors = []
    titular = []
    agendamentos = []

    dados = simplejson.loads(request.body)

    dados['data_inicial'] = datetime.combine(parse(dados['data_inicial']), time.min)

    if dados.get('data_final'):
        dados['data_final'] = datetime.combine(parse(dados['data_final']), time.max)
    else:
        dados['data_final'] = None

    if 'documento' in dados:
        if 'data' in dados['documento']:
            dados['documento']['data'] = parse(dados['documento']['data'])

    if dados['data_inicial'].date() < date.today():
        errors.append('Início não pode ser inferior a hoje.')

    atuacoes = Atuacao.objects.filter(
        Q(defensoria_id=dados['defensoria']) &
        (
            Q(data_final__gte=dados['data_inicial']) |
            Q(data_final=None)
        ) &
        ~Q(tipo=Atuacao.TIPO_LOTACAO) &
        Q(ativo=True))

    if dados['data_final']:

        if dados['data_final'] < dados['data_inicial']:
            errors.append('Término não pode ser inferior ao Início.')

        atuacoes = atuacoes.filter(
            Q(data_inicial__lte=dados['data_final'])
        )

    if dados['tipo'] == Atuacao.TIPO_SUBSTITUICAO:

        atuacoes = atuacoes.filter(
            tipo=Atuacao.TIPO_SUBSTITUICAO
        )

        # Verifica se período da substituição está dentro da titularidade/acumulação
        existe_atuacao_origem = Atuacao.objects.filter(
            Q(defensoria_id=dados['defensoria']) &
            Q(defensor_id=dados['titular']) &
            Q(tipo__in=[Atuacao.TIPO_TITULARIDADE, Atuacao.TIPO_ACUMULACAO]) &
            Q(data_inicial__lte=dados['data_inicial']) &
            (
                Q(data_final__gte=dados['data_final']) |
                Q(data_final=None)
            )
        ).exists()

        if not existe_atuacao_origem:
            errors.append('O período da substituição ultrapassa o periodo da titularidade/acumualção.')

    elif dados['tipo'] == Atuacao.TIPO_ACUMULACAO:
        atuacoes = atuacoes.filter(
            (Q(defensoria__nucleo=None) | Q(defensoria__nucleo__plantao=False))
        )

        if config.ATIVAR_MULTIPLAS_ATUACOES and config.QUANTIDADE_ATUACOES_ACUMULACAO:
            # Verificar a quantidade de defensores acumulados
            # E lençar um error caso o limite por defensoria seja excedido
            qte_defensor_acumulado = atuacoes.filter(
                tipo=Atuacao.TIPO_ACUMULACAO,
                data_final__gt=dados['data_inicial'].date()
            ).count()

            if not (qte_defensor_acumulado < config.QUANTIDADE_ATUACOES_ACUMULACAO):
                errors.append('Não é possível mais cadastrar defensores para acumulação nesta defensoria para esse período.')  # noqa: 501

    if not len(errors) and not config.ATIVAR_MULTIPLAS_ATUACOES and atuacoes.exists():

        for atuacao in atuacoes:
            if atuacao.data_final:
                errors.append('O(A) defensor(a) {0} já está {1} neste órgão de {2:%d/%m/%Y} a {3:%d/%m/%Y}'.format(
                    atuacao.defensor,
                    ['substituindo', 'acumulando', 'atuando'][atuacao.tipo],
                    atuacao.data_inicial,
                    atuacao.data_final
                ))
            else:
                errors.append('O(A) defensor(a) {0} já está {1} neste órgão desde {2:%d/%m/%Y}'.format(
                    atuacao.defensor, ['substituindo', 'acumulando', 'atuando'][atuacao.tipo], atuacao.data_inicial)
                )

    atuacao = None

    if not len(errors):

        form = AtuacaoForm(dados, instance=Atuacao(cadastrado_por=request.user.servidor))

        if form.is_valid():

            atuacao = form.save(commit=False)

            if 'documento' in dados:

                form_documento = DocumentoForm(dados['documento'])

                if form_documento.is_valid():
                    documento = form_documento.save()
                else:
                    documento = None

                atuacao.documento = documento

            atuacao.save()

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_save(request.user, atuacao, True))

            # Recupera totais de atendimentos que serão afetados (exceto substituição):
            if dados['tipo'] != Atuacao.TIPO_SUBSTITUICAO:

                agendamentos = Atendimento.objects.filter(
                    defensoria=dados['defensoria'],
                    data_agendamento__gte=dados['data_inicial'],
                    remarcado=None,
                    ativo=True
                ).annotate(
                    defensor_nome=F('defensor__servidor__nome')
                ).values(
                    'defensor_id', 'defensor_nome'
                ).annotate(
                    total=Count('defensor_id')
                ).order_by('defensor_id')

                if dados['data_final']:
                    agendamentos = agendamentos.filter(data_agendamento__lte=dados['data_final'])

        else:

            errors = [(k + ' - ' + v[0]) for k, v in form.errors.items()]

        if dados['tipo'] == Atuacao.TIPO_TITULARIDADE:
            for atuacao in Atuacao.objects.filter(
                    defensor_id=dados['defensor'],
                    tipo=Atuacao.TIPO_TITULARIDADE,
                    ativo=True):
                titular.append({'defensoria': {'id': atuacao.defensoria.id, 'nome': atuacao.defensoria.nome}})

    return JsonResponse(
        {
            'success': (errors == []),
            'errors': errors,
            'atuacao': atuacao.id if atuacao else None,
            'titular': titular,
            'agendamentos': list(agendamentos)
        })


@login_required
@reversion.create_revision(atomic=False)
@permission_required('defensor.delete_atuacao')
def atuacao_excluir(request):

    if request.is_ajax():
        dados = simplejson.loads(request.body)
        dados['data_final'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        dados = request.POST

    errors = []

    if dados.get('id'):

        form = ExcluirAtuacaoForm(dados, instance=Atuacao.objects.get(id=dados.get('id')))

        if form.is_valid():

            atuacao = form.save(commit=False)
            atuacao.excluir(request.user.servidor)

            agendas = Agenda.objects.filter(
                (
                    Q(atuacao=atuacao) | Q(pai__agenda__atuacao=atuacao)
                ) & Q(ativo=True))

            for agenda in agendas:
                agenda.excluir(request.user.servidor)

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_delete(request.user, atuacao))

            if not request.is_ajax():
                messages.success(request, u'Registro removido com sucesso!')

        else:

            if request.is_ajax():
                errors = [(k + ' - ' + v[0]) for k, v in form.errors.items()]

    if request.is_ajax():
        return JsonResponse({'success': (len(errors) == 0), 'error': errors})
    else:
        if request.POST.get('next'):
            return redirect(request.POST['next'])
        else:
            return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@reversion.create_revision(atomic=False)
@permission_required('defensor.add_atuacao')
def lotacao_salvar(request):
    """Utilizado para salvar lotação de servidor"""

    if request.method == 'POST':

        lotacao = Atuacao(tipo=Atuacao.TIPO_LOTACAO, cadastrado_por=request.user.servidor)
        form_lotacao = LotacaoForm(request.POST, prefix='lotacao', instance=lotacao)

        if form_lotacao.is_valid():

            lotacao = form_lotacao.save()

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_save(request.user, lotacao, True))

            messages.success(request, u'Servidor(a) {0} lotado(a) em {1}.'.format(lotacao.defensor, lotacao.defensoria))

        else:
            messages.error(request, u'Não foi possível registrar a lotação de {0} em {1}.')
            for k, v in form_lotacao.errors.items():
                messages.error(request, u'{0}: {1}'.format(k, v[0]))

    if request.POST.get('next'):
        return redirect(request.POST['next'])
    else:
        return redirect(request.META.get('HTTP_REFERER', '/'))


@never_cache
@login_required
@permission_required('defensor.view_inscricao_plantao')
def listar_editais_plantoes(request):

    if request.method == 'POST':

        registros = []
        numero_registros = 25
        filtro = simplejson.loads(request.body)
        form = BuscarEditalPlantaoForm(filtro)
        lista_editais = None

        if form.is_valid():
            if form.cleaned_data['data_inicial'] and form.cleaned_data['data_final']:
                data_ini = form.cleaned_data['data_inicial']
                data_fim = form.cleaned_data['data_final']
                data_fim = datetime.combine(data_fim, time.max)

                if data_ini <= data_fim.date():
                    lista_editais = EditalConcorrenciaPlantao.objects.filter(
                        Q(data_inicio__gte=data_ini) &
                        Q(data_inicio__lte=data_fim)
                    ).values().order_by('data_inicio')
            else:
                lista_editais = EditalConcorrenciaPlantao.objects.all().values().order_by('data_inicio')

        primeiro = filtro.get('pagina') * numero_registros
        ultimo = primeiro + numero_registros

        if filtro.get('pagina') == 0:
            filtro['total'] = lista_editais.count()
            filtro['paginas'] = math.ceil(float(filtro.get('total')) / numero_registros)

        lista_editais = lista_editais[primeiro:ultimo]

        for lista_edital in lista_editais:
            registros.append(lista_edital)

        return JsonResponse(
            {
                'defensor_id': request.user.servidor.defensor.id,
                'registros': registros,
                'pagina': filtro.get('pagina'),
                'paginas': filtro.get('paginas', 0),
                'ultima': filtro.get('pagina') == filtro.get('paginas') - 1 if filtro.get('paginas') else True,
                'total': filtro.get('total'),
            }, safe=False)

    form = BuscarEditalPlantaoForm(request.GET)
    angular = 'EditalPlantaoCtrl'

    return render(request=request, template_name="defensor/editais_plantoes.html", context=locals())


@never_cache
@login_required
@permission_required('defensor.view_inscricao_plantao')
def listar_vagas_plantoes(request, edital_id):

    if request.method == 'POST':

        vagas = []
        filtro_vagas = EditalConcorrenciaPlantao.objects.get(id=edital_id).vagas.all().values('id', 'data_inicio', 'data_final')  # noqa: E501
        for vaga in filtro_vagas:
            vaga_inserida = {
                'id': vaga['id'],
                'data': '{:%d/%m/%Y}'.format(vaga['data_inicio']) + " a " +
                        '{:%d/%m/%Y}'.format(vaga['data_final'])
            }
            vagas.append(vaga_inserida)

        return JsonResponse({'vagas': vagas}, safe=False)


@never_cache
@login_required
@permission_required('defensor.view_inscricao_plantao')
def listar_inscricoes_plantao(request, edital_id):
    form = BuscarEditalPlantaoForm(request.GET)
    angular = 'EditalPlantaoCtrl'
    registros = InscricaoEditalPlantao.objects.filter(edital_id=edital_id, ativo=True).order_by('vaga__data_inicio', 'defensor__posicao_lista_antiguidade')  # noqa: E501
    nao_ha_inscricoes = True
    if registros:
        nao_ha_inscricoes = False
    edital = EditalConcorrenciaPlantao.objects.get(id=edital_id).descricao

    return render(request=request, template_name="defensor/inscricoes_plantoes.html", context=locals())


@login_required
@permission_required('defensor.view_inscricao_plantao')
def inscrever_edital_plantao(request):

    if request.method == 'POST':
        dados = simplejson.loads(request.body)
        dados['defensor'] = request.user.servidor.defensor.id
        dados['vaga'] = VagaEditalPlantao.objects.get(id=dados['data']['id'])

        form = InscricaoPlantaoForm(dados)

        if form.is_valid("inscrever"):
            InscricaoEditalPlantao.objects.update_or_create(
                defensor_id=dados['defensor'],
                edital_id=dados['edital'],
                vaga=dados['vaga'],
                defaults={'ativo': True},
            )
        else:
            return JsonResponse({'success': False, 'errors': [({'field': k, 'message': v[0]}) for k, v in form.errors.items()]})  # noqa: E501

        return JsonResponse({'error': False, 'success': True})

    return JsonResponse({'error': True, 'success': False})


@login_required
@permission_required('defensor.view_inscricao_plantao')
def cancelar_inscricao_edital_plantao(request):

    if request.method == 'POST':
        dados = simplejson.loads(request.body)
        dados['defensor'] = request.user.servidor.defensor.id
        dados['vaga'] = VagaEditalPlantao.objects.get(id=dados['data']['id'])

        form = InscricaoPlantaoForm(dados)

        if form.is_valid("cancelar"):
            InscricaoEditalPlantao.objects.filter(
                defensor_id=dados['defensor'],
                edital_id=dados['edital'],
                vaga=dados['vaga'],
                ativo=True
            ).update(ativo=False)
        else:
            return JsonResponse({'success': False, 'errors': [({'field': k, 'message': v[0]}) for k, v in form.errors.items()]})  # noqa: E501

        return JsonResponse({'error': False, 'success': True})

    return JsonResponse({'error': True, 'success': False})


@never_cache
@login_required
def comarcas_listar(request, defensor_id, ano):
    """
    Retorna lista de comarcas que o defensor atua
    :param request:
    :param defensor_id:
    :param ano:
    :return:
    """
    cache_key = 'defensor.comarcas_listar:%s:%s' % (defensor_id, (ano if ano else ''))
    cache_data = cache.get(cache_key)

    if not cache_data:
        defensor = Defensor.objects.get(id=defensor_id)

        cache_data = defensor.comarcas(ano)
        cache.set(cache_key, cache_data)

    return JsonResponse(cache_data, safe=False)


@login_required
def substitutos_defensoria_listar(request, defensor_id, defensoria_id):

    arr = []

    for atuacao in Atuacao.objects.filter(
            tipo=Atuacao.TIPO_SUBSTITUICAO,
            titular=defensor_id,
            defensoria=defensoria_id,
            data_final__gte=datetime.now(),
            ativo=True
    ).order_by(
        'defensor__servidor__usuario__first_name'
    ).distinct(
        'defensor__servidor__usuario__first_name'
    ):
        arr.append({
            'id': atuacao.defensor.id,
            'nome': atuacao.defensor.nome,
            'data_ini': Util.date_to_json(atuacao.data_inicial),
            'data_fim': Util.date_to_json(atuacao.data_final),
        })

    return JsonResponse(arr, safe=False)


@never_cache
@login_required
def substitutos_listar(request, defensor_id):
    """
    Retorna lista de substitutos do defensor
    :param request:
    :param defensor_id:
    :return:
    """
    cache_key = 'defensor.substitutos_listar:%s' % defensor_id
    cache_data = cache.get(cache_key)
    if not cache_data:

        arr = []

        for atuacao in Atuacao.objects.filter(
                tipo=Atuacao.TIPO_SUBSTITUICAO,
                titular=defensor_id,
                data_inicial__lte=datetime.now(),
                data_final__gte=datetime.now()
        ).order_by(
            'defensor__servidor__usuario__first_name'
        ).distinct(
            'defensor__servidor__usuario__first_name'
        ):
            arr.append({
                'id': atuacao.defensor.id,
                'nome': atuacao.defensor.nome
            })

        cache_data = arr
        cache.set(cache_key, cache_data)

    return JsonResponse(cache_data, safe=False)


@never_cache
@login_required
def supervisores_listar_atuacoes(request, defensor_id):

    resposta = []
    defensor = Defensor.objects.filter(id=defensor_id).first()

    if defensor:

        defensorias = defensor.atuacoes_vigentes().values_list('defensoria_id', flat=True)
        atuacoes = Atuacao.objects.annotate(
            defensoria_nome=F('defensoria__nome'),
            defensor_nome=F('defensor__servidor__nome'),
        ).vigentes_por_defensoria(defensorias=defensorias).values(
            'id',
            'defensoria_id',
            'defensoria_nome',
            'defensor_id',
            'defensor_nome',
            'tipo',
            'data_inicial',
            'data_final'
        )

        resposta = list(atuacoes)

    return JsonResponse(resposta, safe=False)


@login_required
def remanejar_agendamentos(request, atuacao_id):

    if request.method == 'POST' and request.is_ajax():

        atuacao = Atuacao.objects.get(id=atuacao_id)
        dados = simplejson.loads(request.body)

        # Recupera totais de atendimentos afetados:
        agendamentos = Atendimento.objects.filter(
            defensoria=atuacao.defensoria,
            data_agendamento__gte=atuacao.data_inicial,
            remarcado=None,
            ativo=True)

        if atuacao.data_final:
            agendamentos = agendamentos.filter(data_agendamento__lte=atuacao.data_final)

        for defensor in dados:
            print(agendamentos.filter(defensor=defensor['defensor_id']).update(defensor=atuacao.defensor))

        return JsonResponse({'success': True}, safe=False)

    return JsonResponse({'success': False}, safe=False)
