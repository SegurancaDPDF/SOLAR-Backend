# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
import calendar
from datetime import date, timedelta, datetime, time
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, Count
from django.http import Http404
from django.shortcuts import redirect, render


# Solar
from django.views.decorators.cache import never_cache
from assistido.models import PessoaAssistida
from contrib.models import Comarca, Defensoria
from nucleo.nadep.models import (
    Atendimento,
    EstabelecimentoPenal,
    Prisao,
    CalculoExecucaoPenal,
    MudancaRegime,
    Aprisionamento
)
from nucleo.nadep.services import Prisao as ServicesPrisao, Preso as ServicesPreso
from processo.processo.models import Audiencia


@never_cache
@login_required
def index(request):
    # calcula algumas estatísticas e informações para exibir na página inicial
    total_presos = Prisao.objects.filter(ativo=True).order_by(
        'pessoa__nome',
        'pessoa__id'
    ).distinct(
        'pessoa__nome',
        'pessoa__id'
    ).count()
    total_pessoas = PessoaAssistida.objects.ativos().count()
    total_atendimentos = Atendimento.objects.filter(ativo=True).count()
    total_estabelecimentos = EstabelecimentoPenal.objects.filter(ativo=True).count()

    progressoes = ServicesPrisao.list_progressao_defensor(request.user.servidor.defensor)

    return render(request=request, template_name="nadep/index.html", context=locals())


@never_cache
@login_required
def index_comarca(request, comarca_id):
    # realiza cálculos e consultas para exibir estatísticas sobre a comarca selecionada
    if hasattr(request.user.servidor, 'defensor'):
        defensor = request.user.servidor.defensor
    else:
        raise Http404

    comarca = Comarca.objects.get(id=comarca_id)

    if defensor:
        comarcas = Comarca.objects.filter(
            Q(defensoria__all_atuacoes__defensor=defensor) &
            Q(defensoria__all_atuacoes__ativo=True) &
            (
                (
                    Q(defensoria__all_atuacoes__data_inicial__lte=datetime.now()) &
                    Q(defensoria__all_atuacoes__data_final=None)
                ) |
                (
                    Q(defensoria__all_atuacoes__data_inicial__lte=datetime.now()) &
                    Q(defensoria__all_atuacoes__data_final__gte=datetime.now())
                )
            ) &
            Q(defensoria__nucleo=None)
        ).distinct().values('id', 'nome')

        defensorias = Defensoria.objects.filter(
            Q(all_atuacoes__defensor=defensor) &
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
            ) &
            Q(comarca=comarca) &
            Q(nucleo=None)
        ).distinct().values('id')

    total_presos_prov = []

    for dia in [10, 60, 81, 120]:

        data_inicial = date.today() - timedelta(days=dia)
        data_final = date.today()

        item = {
            'dias': dia,
            'data_inicial': data_inicial,
            'data_final': data_final,
            'total': Prisao.objects.filter(
                ativo=True,
                tipo=Prisao.TIPO_PROVISORIO,
                parte__defensoria__in=defensorias,
                data_prisao__range=[data_inicial, data_final]).count()
        }

        total_presos_prov.append(item)

    item = {
        'dias': '+120',
        'data_inicial': None,
        'data_final': date.today() - timedelta(days=121),
        'total': Prisao.objects.filter(
            ativo=True,
            tipo=Prisao.TIPO_PROVISORIO,
            parte__defensoria__in=defensorias,
            data_prisao__lte=date.today() - timedelta(days=121)).count()
    }

    total_presos_prov.append(item)

    data_ref = date.today()
    dia_semana, dias_mes = calendar.monthrange(data_ref.year, data_ref.month)

    data_ini = date(data_ref.year, data_ref.month, 1)
    data_fim = datetime.combine(date(data_ref.year, data_ref.month, dias_mes), time.max)

    calendario = []
    semana = []

    dia_semana = 0 if dia_semana == calendar.SUNDAY else dia_semana + 1

    for dia in range(dia_semana):
        semana.append(None)

    for dia in range(dias_mes):

        if dia_semana == 0:
            semana = []

        semana.append(dia+1)
        dia_semana += 1

        if dia_semana == 7 or dia == dias_mes - 1:
            calendario.append(semana)
            dia_semana = 0

    for dia in range(7 - len(semana)):
        semana.append(None)

    if defensor.eh_defensor:
        defensores = [defensor.id]
    else:
        defensores = list(defensor.lista_supervisores.values_list('id', flat=True))

    audiencias = Audiencia.objects.filter(
        Q(defensor_cadastro__in=defensores) &
        Q(data_protocolo__range=[data_ini, data_fim]) &
        Q(tipo__audiencia=True) &
        Q(ativo=True) &
        Q(processo__prisoes__ativo=True) &
        (
            (
                Q(processo__prisoes__tipo=Prisao.TIPO_PROVISORIO) & Q(processo__prisoes__resultado_sentenca=None)
            ) |
            (
                Q(processo__prisoes__tipo=Prisao.TIPO_CONDENADO) & ~Q(processo__prisoes__originada__pena=Prisao.PENA_RESTRITIVA)  # noqa
            )
        )
    )

    calendario_audiencias = {}
    for dia in audiencias.extra(
        select={'dia': "DATE_PART('day', processo_fase.data_protocolo)"}
    ).values(
        'dia'
    ).annotate(
        total=Count('id')
    ).order_by('dia'):
        calendario_audiencias[dia['dia']] = dia['total']

    visitas = Atendimento.objects.filter(
        Q(data_atendimento__range=[data_ini, data_fim]) &
        Q(tipo=Atendimento.TIPO_VISITA) &
        Q(ativo=True))

    if defensor.eh_defensor:
        visitas = visitas.filter(
            Q(defensoria__comarca=comarca) &
            (
                Q(defensor=defensor) |
                Q(substituto=defensor)
            ))
    else:
        visitas = visitas.filter(Q(defensoria__in=defensorias))

    calendario_visitas = {}
    for dia in visitas.extra(
        select={'dia': "DATE_PART('day', atendimento_atendimento.data_atendimento)"}
    ).values(
        'dia'
    ).annotate(
        total=Count('id')
    ).order_by('dia'):
        calendario_visitas[dia['dia']] = dia['total']

    total_visitas = visitas.order_by('prisao__pessoa__id').distinct('prisao__pessoa__id').count()

    total_presos = Prisao.objects.filter(
        Q(parte__defensoria__in=defensorias) &
        Q(ativo=True) &
        Q(data_baixa=None) &
        (
            (
                Q(tipo=Prisao.TIPO_PROVISORIO) &
                Q(resultado_sentenca=None) &
                Q(aprisionamentos__situacao=Aprisionamento.SITUACAO_PRESO) &
                Q(aprisionamentos__data_final=None)
            ) |
            (
                Q(tipo=Prisao.TIPO_CONDENADO) &
                Q(data_liquidacao=None) &
                ~Q(originada__pena=Prisao.PENA_RESTRITIVA)
            )
        )
    ).order_by('pessoa__id').distinct('pessoa__id').count()

    total_provisorios = Prisao.objects.filter(
        parte__defensoria__in=defensorias,
        tipo=Prisao.TIPO_PROVISORIO,
        resultado_sentenca=None,
        aprisionamentos__situacao=Aprisionamento.SITUACAO_PRESO,
        aprisionamentos__data_final=None,
        data_baixa=None,
        ativo=True,
    ).order_by('pessoa__id').distinct('pessoa__id').count()

    total_condenados = Prisao.objects.filter(
        parte__defensoria__in=defensorias,
        tipo=Prisao.TIPO_CONDENADO,
        data_baixa=None,
        ativo=True,
    ).exclude(
        originada__pena=Prisao.PENA_RESTRITIVA
    ).order_by('pessoa__id').distinct('pessoa__id').count()

    ultimas_prisoes = Prisao.objects.filter(
        Q(parte__defensoria__in=defensorias) &
        Q(ativo=True) &
        (
            (
                Q(tipo=Prisao.TIPO_PROVISORIO) & Q(resultado_sentenca=None)
            ) |
            (
                Q(tipo=Prisao.TIPO_CONDENADO) & ~Q(originada__pena=Prisao.PENA_RESTRITIVA)
            )
        )
    ).exclude(data_prisao=None).order_by('-data_prisao')[:5]

    ultimas_visitas = Atendimento.objects.filter(
        Q(prisao__ativo=True) &
        Q(remarcado=None) &
        Q(ativo=True)
    ).order_by('-data_agendamento', '-data_atendimento', '-data_cadastro')

    if defensor.eh_defensor:
        ultimas_visitas = ultimas_visitas.filter(
            Q(defensoria__comarca=comarca) &
            (
                Q(defensor=defensor) |
                Q(substituto=defensor)
            ))
    else:
        ultimas_visitas = ultimas_visitas.filter(Q(defensoria__in=defensorias))

    ultimas_visitas = ultimas_visitas[:5]

    progressoes = CalculoExecucaoPenal.objects.filter(
        execucao__parte__defensoria__in=defensorias,
        execucao__prisoes__data_baixa__isnull=True,
    ).exclude(
        regime_atual=Prisao.REGIME_ABERTO
    ).distinct()

    progressoes_atrasadas = progressoes.filter(
        data_progressao__lte=data_ref
    ).order_by('-data_progressao')

    progressoes_proximas = progressoes.filter(
        data_progressao__range=[data_ref + timedelta(days=1), data_ref + timedelta(days=90)]
    ).order_by('data_progressao')

    progressoes_realizadas = MudancaRegime.objects.filter(
        data_registro__range=[data_ref - timedelta(days=90), data_ref],
        prisao__parte__defensoria__in=defensorias,
        tipo=MudancaRegime.TIPO_PROGRESSAO,
        ativo=True
    )

    return render(request=request, template_name="nadep/index_comarca.html", context=locals())


@login_required
@permission_required('assistido.view_pessoaassistida')
def buscar_pessoa(request):  # view para buscar uma pessoa assistida
    from assistido.views import buscar as assistido_buscar_pessoa

    if request.method == 'POST':
        return assistido_buscar_pessoa(request)

    angular = 'BuscarPessoaModel'

    return render(request=request, template_name="nadep/buscar_pessoa.html", context=locals())


@never_cache
@login_required
@permission_required('assistido.view_pessoaassistida')
def visualizar_pessoa(request, pessoa_id=None):
    if request.GET.get('pessoa_id'):
        return redirect('nadep_visualizar_pessoa', request.GET.get('pessoa_id'))

    """Realiza uma busca por uma pessoa e retorna um usuário e uma lista de processos associados a ele"""
    try:

        pessoa = PessoaAssistida.objects.get(id=pessoa_id)
        preso = ServicesPreso(pessoa)

        if preso.prisoes_condenado():
            guia = preso.prisoes_condenado().first()
            if guia.data_base:
                preso = ServicesPreso(pessoa, data_base=guia.data_base)

    except PessoaAssistida.DoesNotExist:
        messages.info(request, u'Essa pessoa ainda não foi cadastrada.')

    hoje = date.today()
    angular_app = 'siapApp'

    return render(request=request, template_name="nadep/visualizar_pessoa.html", context=locals())
