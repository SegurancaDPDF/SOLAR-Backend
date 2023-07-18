# -*- coding: utf-8 -*-
# Importações necessárias

from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import calendar
import re
from datetime import date, datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from django.views.decorators.cache import never_cache

from assistido.models import PessoaAssistida
from atendimento.atendimento.forms import DocumentoForm
from atendimento.atendimento.models import (
    Defensor as Atendimento, Documento as AtendimentoDocumento, Tarefa, TarefaVisualizacao,
    AtendimentoParticipante)
from defensor.models import Atuacao
from relatorios.models import Local, Relatorio

from nucleo_diligencia.forms import DistribuirNucleoDiligenciaForm

re_numero_ged = re.compile(r'^(\d*)V(\d*)$')
re_numero_cnpj = re.compile(r'^[0-9]{2}[\.]?[0-9]{3}[\.]?[0-9]{3}[\/]?[0-9]{4}[\-]?[0-9]{2}$')
re_numero_cpf = re.compile(
    r'^([0-9]{2}[\.]?[0-9]{3}[\.]?[0-9]{3}[\/]?[0-9]{4}[-]?[0-9]{2})|([0-9]{3}[\.]?[0-9]{3}[\.]?[0-9]{3}[-]?[0-9]{2})$'
)
#  interface para atendimento


@never_cache
@login_required
def atender_pessoa(request, pessoa, atendimento_numero):

    pessoa = get_object_or_404(PessoaAssistida, id=pessoa, desativado_em=None)

    respostas = Atendimento.objects.filter(
        ativo=True,
        origem__ativo=True,
        origem__partes__pessoa=pessoa,
        numero=atendimento_numero,
        defensoria__nucleo__diligencia=True,
    )

    atendimento = respostas.first()

    if not atendimento:
        raise Http404

    atividades = Atendimento.objects.filter(
        ativo=True,
        tipo=Atendimento.TIPO_ATIVIDADE,
        origem=atendimento,
        origem__ativo=True,
        origem__defensor__defensoria__nucleo__diligencia=True,
        origem__origem__partes__pessoa=pessoa,
    ).order_by(
        '-data_atendimento'
    )

    atividades_andamento = atividades.filter(
        origem__data_atendimento=None
    )

    documentos = AtendimentoDocumento.objects.filter(
        atendimento__in=atividades_andamento,
        ativo=True
    ).order_by('documento_online__esta_assinado', 'nome')

    hoje = datetime.now()
    dia_min = datetime(hoje.year, hoje.month, 1)
    dia_max = datetime(hoje.year, hoje.month, calendar.monthrange(hoje.year, hoje.month)[1])

    form = DocumentoForm()

    angular = 'NucleoDiligenciaAtividadeCtrl'

    return render(request=request, template_name="nucleo_diligencia/atender.html", context=locals())

# função para exibir um modal de confirmação


@never_cache
@login_required
def confirmar_pessoa(request, pessoa_id, atendimento_numero):

    pessoa = PessoaAssistida.objects.get(id=pessoa_id)

    atendimentos_pessoa = Atendimento.objects.filter(
        ativo=True,
        origem__ativo=True,
        origem__partes__pessoa_id=pessoa_id,
        data_atendimento=None,
        numero=atendimento_numero
    ).order_by('atendimento__retorno__data_agendamento')

    return render(
        request=request,
        template_name="nucleo_diligencia/modal_nucleo_diligencia_distribuir_body.html",
        context=locals()
    )


@never_cache
@login_required
def distribuir_pessoa(request, pessoa, atendimento_numero):

    if request.method == 'POST':

        atendimento = get_object_or_404(Atendimento, numero=atendimento_numero, ativo=True)
        form = DistribuirNucleoDiligenciaForm(request.POST, instance=atendimento)

        servidores_id = request.POST.getlist('participantes')

        if not servidores_id:
            messages.error(request, u'O(s) participante(s) devem ser selecionados!')

        if form.is_valid():
            atendimento.distribuido_por = request.user.servidor
            atendimento.data_distribuido = datetime.now()
            atendimento.save()

            # Salva o cargo do atendente em AtendimentosParticipantes
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
                    cargo_id=atuacao.cargo_id
                )

            # Recupera tarefa do atendimento
            tarefa = atendimento.origem.tarefa_set.filter(prioridade=Tarefa.PRIORIDADE_ALERTA).first()

            # Se existir tarefa, marca como visualizada
            if tarefa:
                TarefaVisualizacao.objects.get_or_create(
                    tarefa=tarefa,
                    visualizada_por=request.user.servidor
                )

            # recupera documento do pedido que também esteja vinculado a um processo
            documento_processo = atendimento.origem.documento_set.exclude(
                documento_online__core_documentos=None
            ).first()

            # se existir vinculo com processo, confirma recebimento
            if documento_processo:
                processo = documento_processo.documento_online.core_documentos.first().processo
                processo.confirmar_recebimento()

        return redirect('nucleo_diligencia_atender_pessoa', pessoa=pessoa, atendimento_numero=atendimento_numero)

    else:

        return redirect(request.META.get('HTTP_REFERER', '/'))

# função para redirecionar o usuário para a página apropriada


@never_cache
@login_required
def index(request):

    if hasattr(request.user.servidor, 'defensor'):

        defensor = request.user.servidor.defensor
        atuacao = defensor.atuacoes(vigentes=True).filter(defensoria__nucleo__diligencia=True).first()

        if atuacao:
            return redirect('nucleo_diligencia_index_comarca', comarca=atuacao.defensoria.comarca_id)
        else:
            return redirect('index')

    return redirect('index')

# função para exibir o índice da comarca para um defensor


@login_required
def index_comarca(request, comarca):

    if not hasattr(request.user.servidor, 'defensor'):
        return redirect('index')

    defensor = request.user.servidor.defensor

    atuacao = defensor.atuacoes(vigentes=True).filter(
        defensoria__nucleo__diligencia=True,
        defensoria__comarca=comarca
    ).first()

    if atuacao is None:
        return redirect('index')

    comarcas = defensor.atuacoes(vigentes=True).filter(
        defensoria__nucleo__diligencia=True
    ).values_list('defensoria__comarca_id', 'defensoria__comarca__nome').distinct()

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

    apoios = Atendimento.objects.filter(
        defensoria=atuacao.defensoria,
        data_agendamento__range=[data_ini, data_fim],
        remarcado=None,
        ativo=True
    )

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
        atendimento__defensor__defensoria=atuacao.defensoria,
        data_final__range=[data_ini, data_fim],
        ativo=True
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

    # Filtros para as solicitações
    q_solicitacao_todas = (
        Q(atendimentos__atendimento__filhos__defensor__defensoria=atuacao.defensoria) &
        Q(atendimentos__atendimento__filhos__tipo=Atendimento.TIPO_NUCLEO) &
        Q(atendimentos__atendimento__filhos__ativo=True) &
        Q(atendimentos__atendimento__documento__ativo=True)
    )

    q_solicitacao_agendada = (
        q_solicitacao_todas &
        Q(atendimentos__atendimento__filhos__data_atendimento=None) &
        Q(atendimentos__atendimento__filhos__participantes=None)
    )

    q_solicitacao_em_andamento = (
        q_solicitacao_todas &
        Q(atendimentos__atendimento__filhos__data_atendimento=None) &
        Q(atendimentos__atendimento__filhos__participantes__gt=0)
    )

    q_solicitacao_finalizada = (
        q_solicitacao_todas &
        Q(atendimentos__atendimento__filhos__data_atendimento__isnull=False)
    )

    filtro_solicitacao = request.GET.get('filtro_solicitacao')

    # Se tiver feito uma Busca de Solicitação
    if filtro_solicitacao:

        filtro_ged = None
        filtro_solicitacao = filtro_solicitacao.upper()

        # Se buscou por número GED
        if re_numero_ged.match(filtro_solicitacao):
            filtro_ged = int(re_numero_ged.match(filtro_solicitacao).group(1))

            q_filtro_solicitacao = Q(atendimentos__atendimento__documento__documento_online__pk=filtro_ged)

        # Se buscou por CPF ou CNPJ
        elif re_numero_cpf.match(filtro_solicitacao) or re_numero_cnpj.match(filtro_solicitacao):
            filtro_cpf_cnpj = filtro_solicitacao.replace('.', '').replace('-', '')
            q_filtro_solicitacao = Q(cpf=filtro_cpf_cnpj)

        # Se buscou por nome do assistido, defensoria, nome ou assunto do documento
        else:
            # TODO: otimizar para quando for Busca de Defensoria
            # TODO: criar bloqueio quando fizer buscas muito abrangentes (exemplo: "Maria")

            q_filtro_solicitacao = (
                Q(atendimentos__atendimento__defensor__defensoria__nome__icontains=filtro_solicitacao) |
                Q(atendimentos__atendimento__documento__nome__icontains=filtro_solicitacao) |
                Q(atendimentos__atendimento__documento__documento_online__assunto__icontains=filtro_solicitacao) |
                Q(nome_norm__icontains=filtro_solicitacao)
            )

        q_solicitacao_agendada &= q_filtro_solicitacao
        q_solicitacao_em_andamento &= q_filtro_solicitacao
        q_solicitacao_finalizada &= q_filtro_solicitacao

    else:
        # Caso não esteja fazendo uma busca irá bloquear para trazer no máximo os últimos 30 dias
        q_solicitacao_finalizada &= Q(
            atendimentos__atendimento__filhos__data_atendimento__range=[data_ref - timedelta(days=30),
                                                                        datetime.combine(data_ref, time.max)]
        )

    atividades = Atendimento.objects.filter(
        defensoria=atuacao.defensoria,
        remarcado=None,
        ativo=True,
        filhos__tipo=Atendimento.TIPO_ATIVIDADE,
        filhos__ativo=True
    )

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

    # Atenção! busque pelos filhos, o vinculo com a pessoa fica na solicitação de apoio, não no atendimento inicial
    # agendada = solicitacoes sem filhos ativos, sem participantes vinculados

    solicitacoes_agendadas = PessoaAssistida.objects.filter(q_solicitacao_agendada).annotate(
        data_agendamento=F('atendimentos__atendimento__filhos__data_agendamento'),
        numero=F('atendimentos__atendimento__filhos__numero'),
        setor_origem=F('atendimentos__atendimento__defensor__defensoria__nome'),
    ).values(
        'id',
        'nome',
        'numero',
        'setor_origem',
        'data_agendamento',
        'enderecos',
        'enderecos__logradouro',
        'enderecos__numero',
        'enderecos__bairro__nome',
        'enderecos__municipio__nome',
        'enderecos__municipio__estado__uf',
        'enderecos__desativado_em',
        'atendimentos__atendimento__documento__nome',
    ).order_by(
        'data_agendamento',
        'nome',
        'atendimentos__atendimento__filhos__numero',
        'atendimentos__atendimento__documento__data_cadastro',
        '-enderecos__principal',
        '-enderecos__desativado_em',
    ).distinct(
        'data_agendamento',
        'nome',
        'atendimentos__atendimento__filhos__numero'
    )

    # Atenção! busque pelos filhos, o vinculo com a pessoa fica na solicitação de apoio, não no atendimento inicial
    # andamento = solicitacoes com pelo menos um filho ativo

    solicitacoes_andamento = PessoaAssistida.objects.filter(q_solicitacao_em_andamento).annotate(
        data_agendamento=F('atendimentos__atendimento__filhos__data_agendamento'),
        numero=F('atendimentos__atendimento__filhos__numero'),
        setor_origem=F('atendimentos__atendimento__defensor__defensoria__nome'),
    ).values(
        'id',
        'nome',
        'numero',
        'setor_origem',
        'data_agendamento',
        'enderecos',
        'enderecos__logradouro',
        'enderecos__numero',
        'enderecos__bairro__nome',
        'enderecos__municipio__nome',
        'enderecos__municipio__estado__uf',
        'enderecos__desativado_em',
        'atendimentos__atendimento__filhos__participantes__nome',
        'atendimentos__atendimento__documento__nome',
    ).order_by(
        'data_agendamento',
        'nome',
        'atendimentos__atendimento__filhos__numero',
        'atendimentos__atendimento__documento__data_cadastro',
        '-enderecos__principal',
        '-enderecos__desativado_em',
    ).distinct(
        'data_agendamento',
        'nome',
        'atendimentos__atendimento__filhos__numero'
    )

    # Atenção! busque pelos filhos, o vinculo com a pessoa fica na solicitação de apoio, não no atendimento inicial
    # finalizadas = solicitacoes finalizadas

    solicitacoes_finalizadas = PessoaAssistida.objects.filter(q_solicitacao_finalizada).annotate(
        data_atendimento=F('atendimentos__atendimento__filhos__data_atendimento'),
        numero=F('atendimentos__atendimento__filhos__numero'),
        setor_origem=F('atendimentos__atendimento__defensor__defensoria__nome'),
    ).values(
        'id',
        'nome',
        'numero',
        'setor_origem',
        'data_atendimento',
        'enderecos',
        'enderecos__logradouro',
        'enderecos__numero',
        'enderecos__bairro__nome',
        'enderecos__municipio__nome',
        'enderecos__municipio__estado__uf',
        'enderecos__desativado_em',
        'atendimentos__atendimento__filhos__participantes__nome',
        'atendimentos__atendimento__documento__nome',
    ).order_by(
        'data_atendimento',
        'nome',
        'atendimentos__atendimento__filhos__numero',
        'atendimentos__atendimento__documento__data_cadastro',
        '-enderecos__principal',
        '-enderecos__desativado_em',
    ).distinct(
        'data_atendimento',
        'nome',
        'atendimentos__atendimento__filhos__numero'
    )

    solicitacoes_agendadas_count = solicitacoes_agendadas.count()
    solicitacoes_andamento_count = solicitacoes_andamento.count()
    solicitacoes_finalizadas_count = solicitacoes_finalizadas.count()

    ultimas_atividades = Atendimento.objects.filter(
        participantes=request.user.servidor,
        origem__defensor__defensoria=atuacao.defensoria,
        origem__ativo=True,
        ativo=True
    ).order_by('-data_atendimento')[:15]

    relatorios = Relatorio.objects.filter(
        papeis=request.user.servidor.papel,
        locais__pagina=Local.PAG_DILIGENCIA_INDEX
    ).ativos()

    angular = 'ImprimirCtrl'

    return render(request, "nucleo_diligencia/index.html", context=locals())
