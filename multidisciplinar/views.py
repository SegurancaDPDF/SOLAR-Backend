# -*- coding: utf-8 -*-
# Importações necessárias

import calendar
from datetime import date, datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Case, When, Value, IntegerField, F, Q, Max, Prefetch
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from django.views.decorators.cache import never_cache

from atendimento.atendimento.models import Defensor as Atendimento, Tarefa, AtendimentoParticipante
from contrib.models import Servidor, Comarca, Defensoria
from defensor.models import Defensor, Atuacao
from relatorios.models import Local, Relatorio

from .forms import DistribuirMultidisciplinarForm

# Função para distribuir atendimento multidisciplinar


@never_cache
@login_required
def distribuir_atendimento(request, atendimento):

    atendimento = get_object_or_404(Atendimento, numero=atendimento, ativo=True)

    if request.method == 'POST':

        form = DistribuirMultidisciplinarForm(request.POST, instance=atendimento)

        servidores_id = request.POST.getlist('participantes')

        if not servidores_id:
            messages.error(request, u'O(s) participante(s) devem ser selecionados!')

        elif form.is_valid():
            atendimento.distribuido_por = request.user.servidor
            atendimento.data_distribuido = datetime.now()
            atendimento.save()

            # Remove AtendimentoParticipante em que o servidor não estiver na lista de participantes
            atendimento.participantes_atendimentos.filter(
                Q(atendimento_id=atendimento.id) &
                ~Q(servidor__id__in=servidores_id)
            ).delete()

            for servidor_id in servidores_id:
                atuacao = Atuacao.objects.filter(
                    Q(defensor__servidor__id=servidor_id) &
                    Q(data_inicial__lte=atendimento.data_distribuido) &
                    (
                        Q(data_final=None) |
                        Q(data_final__gte=atendimento.data_distribuido)
                    )
                ).only('cargo__id').first()

                AtendimentoParticipante.objects.update_or_create(
                    atendimento=atendimento,
                    servidor_id=servidor_id,
                    defaults={
                        'cargo_id': atuacao.cargo_id
                    }
                )

            messages.success(request, u'Atendimento distribuído com sucesso!')

    return redirect('multidisciplinar_index_comarca', atendimento.defensoria.comarca_id)

# Função para exibir a página inicial do módulo multidisciplinar


@never_cache
@login_required
def index(request):

    if hasattr(request.user.servidor, 'defensor'):

        comarca = request.user.servidor.comarca_id
        defensor = request.user.servidor.defensor

        atuacoes = defensor.atuacoes(vigentes=True).filter(
            defensoria__nucleo__multidisciplinar=True
        ).order_by('data_inicial')

        if atuacoes.exists():
            if not atuacoes.filter(defensoria__comarca=comarca).exists():
                comarca = atuacoes.first().defensoria.comarca_id
            return redirect('multidisciplinar_index_comarca', comarca=comarca)

    return redirect('index')

# Função de visualização que exibe a página inicial para uma comarca específica no módulo multidisciplinar.
# Realiza consultas e cálculos para exibir informações relevantes na página, como calendário, atividades e solicitações.


@never_cache
@login_required
def index_comarca(request, comarca):

    if not hasattr(request.user.servidor, 'defensor'):
        return redirect('index')

    defensor = request.user.servidor.defensor
    permissao_distribuir = request.user.is_superuser or request.user.has_perm(perm='nucleo.admin_multidisciplinar')

    comarcas = list(set(defensor.atuacoes(vigentes=True).filter(
        defensoria__nucleo__multidisciplinar=True
    ).values_list('defensoria__comarca_id', 'defensoria__comarca__nome').distinct()))

    atuacao = defensor.atuacoes(vigentes=True).filter(
        defensoria__nucleo__multidisciplinar=True,
        defensoria__comarca=comarca
    )

    defensorias_id = list(set(atuacao.values_list('defensoria_id', flat=True)))

    pode_cadastrar_atividade_extraordinaria = atuacao.filter(
        defensoria__pode_cadastrar_atividade_extraordinaria=True
    ).exists()

    comarca_nome = Comarca.objects.get(pk=comarca).nome

    data_ref = datetime.now()
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

    q_apoio = Q(data_agendamento__range=[data_ini, data_fim])
    q_apoio &= Q(remarcado=None)
    q_apoio &= Q(ativo=True)

    if atuacao.count() > 1:
        q_apoio &= Q(defensoria__in=defensorias_id)
    else:
        q_apoio &= Q(defensoria=atuacao.first().defensoria)

    apoios = Atendimento.objects.filter(q_apoio)

    calendario_apoios = {}
    for dia in apoios.extra(
        select={'dia': "DATE_PART('day', atendimento_atendimento.data_agendamento)"}
    ).values(
        'dia'
    ).annotate(
        total=Count('id')
    ).order_by('dia'):
        calendario_apoios[dia['dia']] = dia['total']

    tarefas = Tarefa.objects.filter(
        atendimento__defensor__defensoria__in=defensorias_id,
        data_final__range=[data_ini, data_fim]
    )

    calendario_tarefas = {}
    for dia in tarefas.extra(
        select={'dia': "DATE_PART('day', atendimento_tarefa.data_final)"}
    ).values(
        'dia'
    ).annotate(
        total=Count('id')
    ).order_by('dia'):
        calendario_tarefas[dia['dia']] = dia['total']

    # todo: recuperar apenas campos necessários (only)
    q_solicitacoes = Q(remarcado=None)
    q_solicitacoes &= Q(ativo=True)

    if atuacao.count() > 1:
        q_solicitacoes &= Q(defensoria__in=defensorias_id)
    else:
        q_solicitacoes &= Q(defensoria=atuacao.first().defensoria)

    solicitacoes = Atendimento.objects.select_related(
        'qualificacao__area',
        'cadastrado_por__usuario',
        'atendido_por__usuario',
        'origem__defensor__defensoria',
    ).prefetch_related(
        Prefetch(
            'participantes',
            queryset=Servidor.objects.select_related(
                'usuario'
            )
        )
    ).annotate(
        total=Sum(
            Case(
                When(filhos__ativo=True, filhos__tipo=Atendimento.TIPO_ATIVIDADE, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ),
        distribuido=Count('participantes')
    ).filter(
        q_solicitacoes
    ).order_by(
        'tipo',
        '-data_atendimento',
        'data_agendamento'
    )

    # agendada = solicitacoes sem filhos ativos, sem participantes vinculados
    solicitacoes_agendadas = solicitacoes.filter(
        data_atendimento=None,
        total=0,
        distribuido=0
    )

    # distribuidas = solicitacoes sem filhos ativos, com participantes vinculados
    solicitacoes_distribuidas = solicitacoes.filter(
        data_atendimento=None,
        total=0,
        distribuido__gt=0
    )

    # andamento = solicitacoes com pelo menos um filho ativo
    solicitacoes_andamento = solicitacoes.filter(
        data_atendimento=None,
        total__gt=0
    )

    # finalizadas = solicitacoes finalizadas
    solicitacoes_finalizadas = solicitacoes.filter(
        data_atendimento__range=[data_ref - timedelta(days=30), datetime.combine(data_ref, time.max)]
    )

    mostrar_todas = request.GET.get('mostrar_todas', str(permissao_distribuir)).lower() == 'true'

    # mostra apenas as atividades do usuário logado
    if not mostrar_todas:

        solicitacoes_distribuidas = solicitacoes_distribuidas.filter(
            participantes=request.user.servidor
        )

        solicitacoes_andamento = solicitacoes_andamento.filter(
            participantes=request.user.servidor
        )

        solicitacoes_finalizadas = solicitacoes_finalizadas.filter(
            participantes=request.user.servidor
        )

    solicitacoes_agendadas_count = len(solicitacoes_agendadas)
    solicitacoes_distribuidas_count = len(solicitacoes_distribuidas)
    solicitacoes_andamento_count = len(solicitacoes_andamento)
    solicitacoes_finalizadas_count = len(solicitacoes_finalizadas)

    tot_solicitacoes_finalizadas = solicitacoes.exclude(data_atendimento=None).count()

    q_atividades = Q(remarcado=None)
    q_atividades &= Q(ativo=True)
    q_atividades &= Q(filhos__tipo=Atendimento.TIPO_ATIVIDADE)
    q_atividades &= Q(filhos__ativo=True)

    if atuacao.count() > 1:
        q_atividades &= Q(defensoria__in=defensorias_id)
    else:
        q_atividades &= Q(defensoria=atuacao.first().defensoria)

    atividades = Atendimento.objects.filter(q_atividades)

    tot_atividades = atividades.aggregate(total=Count('filhos'))

    top_atividades = atividades.annotate(
        titulo=F('filhos__qualificacao__titulo')
    ).values(
        'titulo'
    ).annotate(
        total=Count('titulo')
    ).order_by('-total')[:3]

    for atividade in top_atividades:
        tot_atividades['total'] -= atividade['total']

    if request.GET.get('distribuir'):

        solicitacoes_nao_finalizadas = solicitacoes.exclude(
            data_atendimento__range=[data_ref - timedelta(days=90), datetime.combine(data_ref, time.max)]
        )

        distribuir = solicitacoes_nao_finalizadas.filter(numero=request.GET.get('distribuir')).first()

        if distribuir is None:

            messages.error(request, 'Erro ao distribuir: atendimento não encontrado!')

        else:

            distribuir_participantes = distribuir.participantes.all().values_list('id', flat=True)

            participantes = distribuir.defensoria.all_atuacoes.filter(
                Q(data_inicial__lte=datetime.now()) &
                (
                    Q(data_final__gte=datetime.now()) |
                    Q(data_final=None)
                ) &
                Q(defensor__servidor__usuario__is_superuser=False)
            ).order_by(
                'defensor__servidor__nome'
            ).annotate(
                ultimo_atendimento=Max('defensor__servidor__atendimentos__defensor__data_distribuido')
            ).values(
                'ultimo_atendimento',
                'defensor__servidor_id',
                'defensor__servidor__nome',
                'cargo__nome',
                'defensoria__nome',
            ).order_by('ultimo_atendimento', 'defensor__servidor__nome')

    relatorios = Relatorio.objects.filter(
        papeis=request.user.servidor.papel,
        locais__pagina=Local.PAG_MULTIDISCIPLINAR_INDEX
    ).ativos()

    angular = 'ImprimirCtrl'

    return render(request=request, template_name="multidisciplinar/index.html", context=locals())

# Função de visualização que retorna uma lista de cargos relacionados ao módulo multidisciplinar.
# Utiliza consultas no modelo Defensor para obter os cargos e retorna a lista como resposta JSON.


@login_required
def listar_cargos(request):

    cargos = Defensor.objects.filter(
            all_atuacoes__defensoria__nucleo__multidisciplinar=True
        ).exclude(
            all_atuacoes__cargo=None
        ).distinct().order_by(
            'all_atuacoes__cargo__nome'
        ).values_list(
            'all_atuacoes__cargo__id', 'all_atuacoes__cargo__nome'
        )

    return JsonResponse([{'id': x[0], 'nome': x[1]} for x in cargos], safe=False)

# Função de visualização que retorna uma lista de defensorias relacionadas ao módulo multidisciplinar.
# Utiliza consultas no modelo Defensoria para obter as defensorias e retorna a lista como resposta JSON.


@login_required
def listar_defensorias(request):

    defensorias = Defensoria.objects.filter(
        nucleo__multidisciplinar=True
    ).values('id', 'nome')

    return JsonResponse(list(defensorias), safe=False)
