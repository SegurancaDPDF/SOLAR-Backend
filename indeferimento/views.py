# -*- coding: utf-8 -*-
import calendar
import json
from datetime import date, datetime, time, timedelta

from constance import config
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import transaction
from django.db.models import Count, F, Q, Case, When, BooleanField, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import ListView
import re

from atendimento.atendimento.models import Defensor as Atendimento, Documento as AtendimentoDocumento, Tarefa
from atendimento.atendimento.services import preencher_campos_ged
from contrib import constantes
from contrib.models import Util
from core.models import (
    Classe as CoreClasse,
    Documento as CoreDocumento,
    Evento as CoreEvento,
    ModeloDocumento as CoreModeloDocumento,
    Processo as CoreProcesso,
    TipoEvento as CoreTipoEvento,
)
from core.views import EventoCreateView, EventoUpdateView
from djdocuments.views.documentos import create_document_from_document_template
from indeferimento.models import Indeferimento
from . import forms
from notificacoes.tasks import (
    notificar_processo_de_indeferimento
)


@login_required
def index(request, nucleo_id, setor_id=None):

    if not hasattr(request.user.servidor, 'defensor'):
        return redirect('index')

    defensor = request.user.servidor.defensor

    # obtém a lista de atuações em defensorias vinculadas ao núcleo selecionado
    atuacoes = defensor.atuacoes(vigentes=True).filter(
        defensoria__nucleo_id=nucleo_id,
        defensoria__nucleo__indeferimento=True
    )

    # se foi passado a defensora, a seleciona como atuação padrão
    if setor_id:
        atuacao = atuacoes.filter(defensoria_id=setor_id).first()
    else:
        atuacao = atuacoes.first()

    if not atuacao:
        return redirect('index')

    setor = atuacao.defensoria
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

    eventos = CoreEvento.objects.select_related(
        'processo__indeferimento__defensor__servidor',
        'processo__classe',
        'tipo',
    ).ativos().filter(
        setor_criacao=setor,
        processo__tipo=CoreProcesso.TIPO_INDEFERIMENTO
    )

    eventos_mes = eventos.filter(
        data_referencia__range=[data_ini, data_fim]
    )

    eventos_mes = eventos.filter(
        data_referencia__range=[data_ini, data_fim]
    )

    decisoes = eventos.filter(
        tipo__tipo=CoreTipoEvento.TIPO_DECISAO
    )

    decisoes_mes = decisoes.filter(
        data_referencia__range=[data_ini, data_fim]
    )

    # Dados para o calendário - eventos
    calendario_eventos = {}
    for dia in eventos_mes.extra(
        select={'dia': "DATE_PART('day', data_referencia)"}
    ).values(
        'dia'
    ).annotate(
        total=Count('id')
    ).order_by('dia'):
        calendario_eventos[dia['dia']] = dia['total']

    # Dados para o calendário - decisões
    calendario_decisoes = {}
    for dia in decisoes_mes.extra(
        select={'dia': "DATE_PART('day', data_referencia)"}
    ).values(
        'dia'
    ).annotate(
        total=Count('id')
    ).order_by('dia'):
        calendario_decisoes[dia['dia']] = dia['total']

    processos = Indeferimento.objects.select_related(
        'processo__setor_atual',
        'processo__setor_encaminhado',
        'processo__classe',
        'defensor__servidor',
        'pessoa',
    ).ativos().exclude(
        processo__situacao=CoreProcesso.SITUACAO_PETICIONAMENTO
    )

    if not setor.nucleo.indeferimento_pode_receber_impedimento:
        processos = processos.exclude(processo__classe__tipo=CoreClasse.TIPO_IMPEDIMENTO)

    processos_recebidos = processos.filter(
        processo__situacao=CoreProcesso.SITUACAO_MOVIMENTO,
        processo__setor_encaminhado=setor
    ).annotate(
        setor_atual_indeferimento=Case(
            When(processo__setor_atual__nucleo__indeferimento=True, then=True),
            output_field=BooleanField()
        )
    ).order_by('setor_atual_indeferimento', 'processo__modificado_em')

    processos_neste_setor = processos.filter(
        processo__situacao=CoreProcesso.SITUACAO_MOVIMENTO,
        processo__setor_atual=setor,
        processo__setor_encaminhado=None
    ).order_by('processo__modificado_em')

    processos_encaminhados = processos.filter(
        processo__situacao=CoreProcesso.SITUACAO_MOVIMENTO,
        processo__setor_atual=setor
    ).exclude(
        processo__setor_encaminhado=None
    ).order_by('-processo__modificado_em')

    processos_baixados = processos.filter(
        processo__situacao=CoreProcesso.SITUACAO_BAIXADO
    ).order_by('-processo__baixado_em')

    tab_processos = []

    tab_processos.append({
        'id': 'solicitacoes_recebidas',
        'nome': 'Recebidos',
        'itens': processos_recebidos
    })

    tab_processos.append({
        'id': 'processos_neste_setor',
        'nome': 'Em análise',
        'itens': processos_neste_setor
    })

    tab_processos.append({
        'id': 'processos_encaminhados',
        'nome': 'Encaminhados',
        'itens': processos_encaminhados
    })

    if setor.nucleo.indeferimento_pode_registrar_decisao:
        tab_processos.append({
            'id': 'solicitacoes_deferidas',
            'nome': 'Deferidos',
            'itens': processos.deferidos().order_by('-processo__modificado_em')[:10]
        })

        tab_processos.append({
            'id': 'solicitacoes_indeferidas',
            'nome': 'Indeferidos',
            'itens': processos.indeferidos().order_by('-processo__modificado_em')[:10]
        })

    if setor.nucleo.indeferimento_pode_registrar_baixa:
        tab_processos.append({
            'id': 'solicitacoes_baixadas',
            'nome': 'Baixados',
            'itens': processos_baixados[:10]
        })

    total_processos = processos.count()

    # Principais classes de processos
    top_classes = processos.annotate(
        nome=F('processo__classe__nome')
    ).values(
        'nome'
    ).annotate(
        total=Count('nome')
    ).filter(
        total__gt=0
    ).order_by('-total')[:5]

    # Subtrai top classes do total de processos
    outras_classes = total_processos

    for classe in top_classes:
        outras_classes -= classe['total']

    # ultimos_eventos = solicitacoes_avaliadas.order_by('-data_avaliacao')[:10]

    ultimos_eventos = eventos.select_related(
        'processo__indeferimento__defensor',
        'processo__indeferimento__pessoa',
    ).order_by(
        '-cadastrado_em'
    )[:10]

    return render(
        request=request,
        template_name="indeferimento/index.html",
        context={
            'angular': 'IndeferimentoIndexCtrl',
            'atuacao': atuacao,
            'atuacoes': atuacoes,
            'calendario_decisoes': calendario_decisoes,
            'calendario_eventos': calendario_eventos,
            'calendario': calendario,
            'data_ref': data_ref,
            'Indeferimento': Indeferimento,
            'nucleo_id': nucleo_id,
            'outras_classes': outras_classes,
            'setor': setor,
            'tab_processos': tab_processos,
            'top_classes': top_classes,
            'total_processos_avaliados': processos.avaliados().count(),
            'total_processos_deferidos': processos.deferidos().count(),
            'total_processos_indeferidos': processos.indeferidos().count(),
            'total_processos': total_processos,
            'ultimos_eventos': ultimos_eventos,
        },
    )


@login_required
def editar_solicitacao(request, processo_uuid):
    return nova_solicitacao(request=request, processo_uuid=processo_uuid)


@login_required
def nova_solicitacao(request, tipo=None, processo_uuid=None):

    indeferimento = None

    if request.method == 'POST':
        dados = request.POST
    else:
        dados = request.GET

    # Se uuid do processo informado, carrega dados a partir do registro existente
    if processo_uuid:
        indeferimento = get_object_or_404(
            Indeferimento,
            processo__uuid=processo_uuid,
            processo__situacao=CoreProcesso.SITUACAO_PETICIONAMENTO,
            processo__desativado_em=None
        )
        atendimento = indeferimento.atendimento
        tipo = indeferimento.processo.classe.tipo
        dados = {
            'pessoa': indeferimento.pessoa_id,
            'classe': indeferimento.processo.classe_id,
            'medida_pretendida': indeferimento.medida_pretendida,
            'justificativa': indeferimento.justificativa,
            'setor_encaminhado': indeferimento.processo.setor_encaminhado_id,
            'setores_notificados': list(indeferimento.processo.setores_notificados.values_list('id', flat=True))
        }
    else:

        try:
            atendimento = Atendimento.objects.get(numero=dados.get('atendimento'))
        except Atendimento.DoesNotExist:
            messages.error(request, 'Informações inconsistentes! Por favor, tente novamente.')
            return redirect('index')

    if tipo == CoreClasse.TIPO_IMPEDIMENTO:
        form_solicitacao = forms.NovoImpedimentoForm(
            dados,
            invisivel=True,
            atendimento=atendimento
        )
    elif tipo == CoreClasse.TIPO_SUSPEICAO:
        form_solicitacao = forms.NovaSuspeicaoForm(
            dados,
            invisivel=True,
            atendimento=atendimento
        )
    elif tipo == CoreClasse.TIPO_NEGACAO_PROCEDIMENTO:
        form_solicitacao = forms.NovaNegacaoProcedimentoForm(
            dados,
            invisivel=True,
            atendimento=atendimento
        )
    elif tipo in [CoreClasse.TIPO_NEGACAO, CoreClasse.TIPO_NEGACAO_HIPOSSUFICIENCIA]:
        form_solicitacao = forms.NovaNegacaoForm(
            dados,
            invisivel=True,
            atendimento=atendimento
        )
    else:
        raise Exception('"{}" não é um tipo válido para criar nova solicitação de indeferimento!'.format(tipo))

    if not form_solicitacao.is_valid():
        raise Exception('Não foi possível criar nova solicitação: dados inválidos!')

    dados = form_solicitacao.data

    if not indeferimento:

        try:
            indeferimento = Indeferimento.objects.get_or_create_atendimento_pessoa(
                atendimento=atendimento,
                atuacao_id=dados.get('atuacao_cadastro'),
                pessoa_id=dados.get('pessoa'),
                classe_id=dados.get('classe'),
                setor_encaminhado_id=dados.get('setor_encaminhado'),
                setores_notificados_ids=dados.getlist('setores_notificados'),
                justificativa=dados.get('justificativa'),
                medida_pretendida=dados.get('medida_pretendida'),
            )
        except Exception as ex:
            messages.error(request, str(ex))
            return redirect('{}#/historico'.format(reverse('atendimento_atender', args=[atendimento.numero])))

        if tipo in [CoreClasse.TIPO_NEGACAO, CoreClasse.TIPO_NEGACAO_HIPOSSUFICIENCIA]:
            messages.success(request, u'Solicitação Registrada com Sucesso!')

            if config.NOTIFICAR_PROCESSO_DE_INDEFERIMENTO:
                notificar_processo_de_indeferimento.apply_async(
                    kwargs={
                        'user_remetente_id': request.user.id,
                        'processo_id': indeferimento.processo.id
                        },
                    queue='sobdemanda'
                    )
            return redirect('{}#/historico'.format(reverse('atendimento_atender', args=[atendimento.numero])))

    # cancela operação se evento recurso já finalizado
    if indeferimento.processo.eventos.ativos().filter(em_edicao=False).exists():

        messages.error(request, 'Indeferimento de atendimento já registrado para {}'.format(indeferimento.pessoa))
        return redirect('{}#/historico'.format(reverse('atendimento_atender', args=[atendimento.numero])))

    else:

        # recupera evento recurso em edição
        evento = indeferimento.processo.eventos.ativos().filter(em_edicao=True).first()

        if not evento:

            tipo_evento = CoreTipoEvento.objects.filter(
                tipo_processo=CoreProcesso.TIPO_INDEFERIMENTO,
                tipo=CoreTipoEvento.TIPO_PETICAO,
            ).first()

            if tipo_evento:

                evento = CoreEvento.objects.create(
                    processo=indeferimento.processo,
                    tipo=tipo_evento,
                    setor_criacao=indeferimento.processo.setor_criacao,
                    data_referencia=timezone.now(),
                    numero=indeferimento.processo.eventos.count() + 1,
                    em_edicao=True
                )

                for modelo in indeferimento.processo.classe.modelos_documentos.all():

                    documento, novo = CoreDocumento.objects.get_or_create(
                        processo=indeferimento.processo,
                        evento=evento,
                        tipo=modelo.tipo_documento,
                        modelo=modelo,
                        desativado_em=None,
                        defaults={
                            'nome': u'{} - {}'.format(modelo.nome, indeferimento.pessoa.nome).upper(),
                        }
                    )

                    if modelo.tipo == CoreModeloDocumento.TIPO_GED and not documento.documento:

                        documento.documento = create_document_from_document_template(
                            request.user,
                            evento.setor_criacao,
                            modelo.ged_modelo,
                            modelo.nome,
                        )

                        documento.documento = preencher_campos_ged(
                            documento=documento.documento,
                            context_conteudo={
                                'defensoria': documento.documento.grupo_dono,
                                'atendimento': atendimento,
                                'pessoa': indeferimento.pessoa,
                                'razao': indeferimento.processo.classe,
                                'justificativa': dados.get('justificativa'),
                                'medida_pretendida': dados.get('medida_pretendida'),
                                'hoje': date.today(),
                            },
                            fallback_to_conteudo=True
                        )

                        documento.documento.esta_pronto_para_assinar = True
                        documento.documento.save()
                        documento.save()

    return render(
        request,
        template_name="indeferimento/nova_solicitacao.html",
        context={
            'setor': indeferimento.defensoria,
            'dados': dados,
            'pessoa': indeferimento.pessoa,
            'atendimento': atendimento,
            'indeferimento': indeferimento,
            'processo': indeferimento.processo,
            'evento': evento,
            'form_solicitacao': form_solicitacao,
            'pode_registrar': not evento.documentos.ativos().pendentes().exists(),
            'report_params': {
                'indeferimento_id': indeferimento.id,
                'justificativa': indeferimento.justificativa,
                'medida_pretendida': indeferimento.medida_pretendida
            },
            'form_action': reverse('indeferimento:salvar_solicitacao', kwargs={
                'processo_uuid': indeferimento.processo.uuid
            }),
            'form_anexar_arquivo_next': reverse('indeferimento:editar_solicitacao', kwargs={
                'processo_uuid': indeferimento.processo.uuid
            }),
            'recurso': False,
            'angular': 'NucleoDPGCtrl',
        })


@login_required
def novo_impedimento(request):
    return nova_solicitacao(request=request, tipo=CoreClasse.TIPO_IMPEDIMENTO)


@login_required
def nova_suspeicao(request):
    return nova_solicitacao(request=request, tipo=CoreClasse.TIPO_SUSPEICAO)


@login_required
def nova_negacao_procedimento(request):
    return nova_solicitacao(request=request, tipo=CoreClasse.TIPO_NEGACAO_PROCEDIMENTO)


@login_required
def nova_negacao(request):
    return nova_solicitacao(request=request, tipo=CoreClasse.TIPO_NEGACAO)


@login_required
def ver_solicitacao(request, setor_id, nucleo_id, processo_uuid):

    if not hasattr(request.user.servidor, 'defensor'):
        return redirect('index')

    defensor = request.user.servidor.defensor
    atuacao = defensor.atuacoes(vigentes=True).filter(defensoria__id=setor_id).first()

    if not atuacao:
        atuacao = defensor.atuacoes(vigentes=True).filter(defensoria__nucleo_id=nucleo_id).first()

    if not atuacao:
        return redirect('index')

    indeferimento = get_object_or_404(Indeferimento, processo__uuid=processo_uuid, processo__desativado_em=None)
    processo = indeferimento.processo

    if processo.setor_encaminhado_id == atuacao.defensoria_id:
        try:
            processo.confirmar_recebimento()
        except Exception as e:
            messages.error(request, str(e))
            return redirect(request.META.get('HTTP_REFERER', '/'))

    eventos = indeferimento.processo.eventos.select_related(
        'tipo',
        'setor_criacao',
        'setor_encaminhado',
        'cadastrado_por',
    ).prefetch_related(
        Prefetch(
            'documentos',
            queryset=CoreDocumento.objects.select_related('documento').ativos().validos().ordem_alfabetica()
        )
    ).ativos().ordem_crescente()

    documentos_atendimento = indeferimento.atendimento.documentos.filter(
        (
            Q(pessoa=indeferimento.pessoa) | Q(pessoa=None)
        ) &
        (
            ~Q(arquivo='') |
            Q(documento_online__esta_assinado=True)
        ) &
        Q(impedimento=None)
    ).order_by('nome')

    return render(
        request,
        template_name="indeferimento/ver_solicitacao.html",
        context={
            'setor': atuacao.defensoria,
            'indeferimento': indeferimento,
            'processo': indeferimento.processo,
            'eventos': eventos,
            'documentos_atendimento': documentos_atendimento,
            'agora': datetime.now(),
            'CoreTipoEvento': CoreTipoEvento,
            'angular': 'NucleoDPGCtrl'
        })


@login_required
def baixar_solicitacao(request, nucleo_id, processo_uuid, tipo):

    indeferimento = get_object_or_404(
        Indeferimento,
        processo__uuid=processo_uuid,
        processo__desativado_em=None)

    processo = indeferimento.processo
    historico = request.POST.get('historico', dict(Indeferimento.LISTA_BAIXA)[int(tipo)])

    if processo.baixar(historico=historico):

        indeferimento.tipo_baixa = tipo
        indeferimento.save()

        messages.success(
            request,
            'Indeferimento nº {} baixado com sucesso!'.format(processo.numero)
        )

    else:

        messages.error(
            request,
            'Erro ao baixar Indeferimento nº {}: informações inconsistentes!'.format(processo.numero)
        )

    return redirect('indeferimento:ver_solicitacao', setor_id=processo.setor_atual.id, nucleo_id=nucleo_id,
                    processo_uuid=processo.uuid)


@login_required
def avaliar_solicitacao(request, nucleo_id, processo_uuid, resultado):

    indeferimento = get_object_or_404(
        Indeferimento,
        processo__uuid=processo_uuid,
        processo__desativado_em=None)

    processo = indeferimento.processo
    qtd_decisao = indeferimento.decisoes.count()

    if not indeferimento.baixado:

        indeferimento.resultado = resultado
        indeferimento.save()

        # Cria tarefa para defensoria de origem caso seja negativa de recurso da Classe Especial
        agora = timezone.now()

        if processo.classe.tipo == CoreClasse.TIPO_NEGACAO_PROCEDIMENTO:

            if qtd_decisao > 1:
                messages.success(request, u'Solicitação reavaliada com sucesso!')
                titulo = 'NEGATIVA {} REAVALIADA'.format(indeferimento.processo.numero)
            else:
                messages.success(request, u'Solicitação avaliada com sucesso!')
                titulo = 'NEGATIVA {} AVALIADA'.format(indeferimento.processo.numero)

            for setor_notificado in indeferimento.processo.setores_notificados.all():
                Tarefa.objects.create(
                    atendimento=indeferimento.atendimento,
                    resposta_para=indeferimento.defensoria,
                    setor_responsavel=setor_notificado,
                    prioridade=Tarefa.PRIORIDADE_ALERTA,
                    titulo=titulo,
                    descricao=processo.classe.nome,
                    data_inicial=agora,
                    cadastrado_por=request.user.servidor
                )

    else:

        messages.error(request, u'Não foi possível registrar a avaliação da solicitação!')

    return redirect('indeferimento:ver_solicitacao', setor_id=processo.setor_atual.id,
                    nucleo_id=processo.setor_atual.nucleo_id, processo_uuid=processo.uuid)


@login_required
def salvar_solicitacao(request, processo_uuid):

    indeferimento = get_object_or_404(
        Indeferimento,
        processo__uuid=processo_uuid,
        processo__desativado_em=None)

    processo = indeferimento.processo
    peticao = processo.eventos.ativos().filter(em_edicao=True)

    # cancela operação se evento recurso já finalizado
    if processo.situacao == CoreProcesso.SITUACAO_PETICIONAMENTO and peticao.exists():

        # Marca evento como encaminhado e encerra edição
        evento = peticao.first()
        evento.data_referencia = timezone.now()
        evento.setor_encaminhado = processo.setor_encaminhado
        evento.em_edicao = False
        evento.save()

        # Marca processo como em movimento
        processo.situacao = CoreProcesso.SITUACAO_MOVIMENTO
        processo.save()

        # Cria tarefa para defensoria de origem
        if processo.classe.tipo == CoreClasse.TIPO_NEGACAO_PROCEDIMENTO:
            for setor_notificado in indeferimento.processo.setores_notificados.all():
                Tarefa.objects.create(
                    atendimento=indeferimento.atendimento,
                    resposta_para=indeferimento.defensoria,
                    setor_responsavel=setor_notificado,
                    prioridade=Tarefa.PRIORIDADE_ALERTA,
                    titulo=processo.classe.get_tipo_display().upper(),
                    descricao=processo.classe.nome,
                    data_inicial=evento.data_referencia,
                    data_final=evento.data_referencia + timedelta(days=30),
                    cadastrado_por=evento.cadastrado_por.servidor
                )
        if config.NOTIFICAR_PROCESSO_DE_INDEFERIMENTO:
            notificar_processo_de_indeferimento.apply_async(
                    kwargs={
                        'user_remetente_id': request.user.id,
                        'processo_id': indeferimento.processo.id
                        },
                    queue='sobdemanda'
                    )
        messages.success(request, u'Solicitação Registrada com Sucesso!')

    else:

        messages.error(request, u'Processo já registrado para esse indeferimento!')

    return redirect('{}#/historico'.format(reverse('atendimento_atender', args=[indeferimento.atendimento.numero])))


@login_required
def novo_recurso(request, processo_uuid):
    dados = None

    if request.method == 'POST':
        dados = json.loads(request.body)

    indeferimento = get_object_or_404(Indeferimento, processo__uuid=processo_uuid, processo__desativado_em=None)
    pessoa = indeferimento.pessoa
    qualificacao = indeferimento.processo.classe

    evento = None

    # recursos do processo
    recursos = indeferimento.processo.eventos.ativos().tipo_recurso()

    # cancela operação se evento recurso já finalizado
    if recursos.filter(em_edicao=False).exists():

        messages.error(request, 'Recurso já registrado para esse indeferimento!')

        return redirect('{}#/historico'.format(reverse('atendimento_atender', args=[indeferimento.atendimento.numero])))

    else:

        # recupera evento recurso em edição
        evento = recursos.filter(em_edicao=True).first()

        if not evento:

            tipo_evento = CoreTipoEvento.objects.filter(
                tipo_processo=CoreProcesso.TIPO_INDEFERIMENTO,
                tipo=CoreTipoEvento.TIPO_RECURSO,
            ).first()

            if tipo_evento:

                evento = CoreEvento.objects.create(
                    processo=indeferimento.processo,
                    tipo=tipo_evento,
                    setor_criacao=indeferimento.processo.setor_criacao,
                    data_referencia=timezone.now(),
                    numero=indeferimento.processo.eventos.count() + 1,
                    em_edicao=True
                )

                for modelo in qualificacao.modelos_documentos.all():

                    documento, novo = CoreDocumento.objects.get_or_create(
                        processo=indeferimento.processo,
                        evento=evento,
                        tipo=modelo.tipo_documento,
                        modelo=modelo,
                        desativado_em=None,
                        defaults={
                            'nome': u'{} - {}'.format(modelo.nome, pessoa.nome).upper(),
                        }
                    )

                    if modelo.tipo == CoreModeloDocumento.TIPO_GED and not documento.documento:

                        documento.documento = create_document_from_document_template(
                            request.user,
                            evento.setor_criacao,
                            modelo.ged_modelo,
                            modelo.nome,
                        )

                        documento.documento = preencher_campos_ged(
                            documento=documento.documento,
                            context_conteudo={
                                'defensoria': documento.documento.grupo_dono,
                                'atendimento': indeferimento.atendimento,
                                'pessoa': pessoa,
                                'justificativa': indeferimento.justificativa,
                                'hoje': date.today(),
                                'indeferimento': indeferimento,
                                'defensor_unidade_atual': indeferimento.atendimento.defensor.nome,
                            },
                            fallback_to_conteudo=True
                        )

                        documento.documento.save()
                        documento.save()

    return render(
        request=request,
        template_name="indeferimento/nova_solicitacao.html",
        context={
            'setor': indeferimento.processo.setor_criacao,
            'dados': dados,
            'pessoa': indeferimento.pessoa,
            'atendimento': indeferimento.atendimento,
            'indeferimento': indeferimento,
            'processo': indeferimento.processo,
            'evento': evento,
            'pode_registrar': not evento.documentos.ativos().pendentes().exists(),
            'report_params': {
                'indeferimento_id': indeferimento.id,
                'justificativa': indeferimento.justificativa,
                'medida_pretendida': indeferimento.medida_pretendida
            },
            'form_action': reverse('indeferimento:salvar_recurso', kwargs={
                'processo_uuid': indeferimento.processo.uuid
            }),
            'recurso': True,
            'angular': 'NucleoDPGCtrl',
        }
    )


@login_required
def novo_recurso_form(request, processo_uuid):

    indeferimento = get_object_or_404(Indeferimento, processo__uuid=processo_uuid, processo__desativado_em=None)
    processo = indeferimento.processo

    if request.method == 'POST':

        form_recurso = forms.NovoRecursoForm(request.POST, instance=indeferimento)

        if form_recurso.is_valid():

            indeferimento = form_recurso.save()

            processo.setor_encaminhado_id = request.POST.get('setor_encaminhado')
            processo.save()

            return redirect(request.POST.get('next'))

        else:

            return redirect(request.META.get('HTTP_REFERER', '/'))

    else:

        return render(
            request=request,
            template_name="indeferimento/novo_recurso_form.html",
            context={
                'processo': indeferimento.processo,
                'form': forms.NovoRecursoForm(),
                'indeferimento': indeferimento,
            }
        )


@login_required
def salvar_recurso(request, processo_uuid):

    indeferimento = get_object_or_404(Indeferimento, processo__uuid=processo_uuid, processo__desativado_em=None)
    processo = indeferimento.processo

    if request.method == 'POST':

        evento = processo.eventos.get(
            em_edicao=True,
            desativado_por=None
        )

        # Marca evento como encaminhado e encerra edição
        evento.setor_encaminhado_id = processo.setor_encaminhado_id
        evento.data_referencia = timezone.now()
        evento.em_edicao = False
        evento.save()

        # Encaminha processo para novo setor
        processo.setor_atual_id = evento.setor_criacao_id
        processo.situacao = CoreProcesso.SITUACAO_MOVIMENTO
        processo.save()

        messages.success(request, u'Recurso registrado com sucesso!')

    else:

        messages.error(request, u'Erro ao registrar o recurso: preencha todos os campos solicitados!')

    return redirect('{}#/historico'.format(reverse('atendimento_atender', args=[indeferimento.atendimento.numero])))


@login_required
def novo_evento_form(request, nucleo_id, processo_uuid, tipo):

    indeferimento = get_object_or_404(Indeferimento, processo__uuid=processo_uuid, processo__desativado_em=None)
    processo = indeferimento.processo

    form_evento = forms.NovoEventoIndeferimentoForm(
        instance=CoreEvento(processo=processo),
        tipo=tipo,
    )

    return render(
        request,
        template_name="indeferimento/modal_novo_evento_form.html",
        context={
            'nucleo_id': nucleo_id,
            'processo': processo,
            'form_evento': form_evento,
            'tipo_evento': tipo,
            'TipoEvento': CoreTipoEvento
        })


@login_required
def novo_evento_anotacao_form(request, nucleo_id, processo_uuid):
    return novo_evento_form(request, nucleo_id, processo_uuid, CoreTipoEvento.TIPO_ANOTACAO)


@login_required
def novo_evento_encaminhamento_form(request, nucleo_id, processo_uuid):
    return novo_evento_form(request, nucleo_id, processo_uuid, CoreTipoEvento.TIPO_ENCAMINHAMENTO)


@login_required
def novo_evento_decisao_form(request, nucleo_id, processo_uuid):
    return novo_evento_form(request, nucleo_id, processo_uuid, CoreTipoEvento.TIPO_DECISAO)


@login_required
def nova_diligencia_form(request, nucleo_id, processo_uuid):

    indeferimento = get_object_or_404(Indeferimento, processo__uuid=processo_uuid, processo__desativado_em=None)
    processo = indeferimento.processo

    atendimento = Atendimento(
        tipo=Atendimento.TIPO_INICIAL
    )

    form_diligencia = forms.AgendarDiligenciaIndeferimentoForm(
        instance=atendimento,
        processo=processo
    )

    return render(
        request,
        template_name="indeferimento/modal_nucleo_diligencia_form.html",
        context={
            'nucleo_id': nucleo_id,
            'processo': processo,
            'form_diligencia': form_diligencia,
        })


@login_required
def salvar_diligencia(request, nucleo_id, processo_uuid):

    indeferimento = get_object_or_404(Indeferimento, processo__uuid=processo_uuid, processo__desativado_em=None)
    processo = indeferimento.processo

    resposta = Atendimento(
        tipo=Atendimento.TIPO_NUCLEO,
        cadastrado_por=request.user.servidor
    )

    form_diligencia = forms.AgendarDiligenciaIndeferimentoForm(
        request.POST,
        instance=resposta,
        processo=processo,
    )

    if form_diligencia.is_valid():

        with transaction.atomic():
            resposta = form_diligencia.save(commit=False)

            agora = timezone.now()
            servidor = request.user.servidor

            # cria pedido de apoio (obrigatório para módulo diligência)
            pedido = Atendimento.objects.create(
                tipo=Atendimento.TIPO_RETORNO,
                data_agendamento=agora,
                data_atendimento=agora,
                cadastrado_por=servidor,
                agendado_por=servidor,
                atendido_por=servidor,
                defensor=processo.setor_atual.all_atuacoes.vigentes().titularidades().first().defensor,
                defensoria=processo.setor_atual,
                qualificacao=resposta.qualificacao,
                historico=form_diligencia.cleaned_data['historico'],
            )

            # adiciona pessoa ao pedido de apoio
            pedido.add_requerente(indeferimento.pessoa_id)

            # recupera tipo de evento encaminhamento
            tipo_evento = CoreTipoEvento.objects.filter(
                tipo_processo=CoreProcesso.TIPO_INDEFERIMENTO,
                tipo=CoreTipoEvento.TIPO_ENCAMINHAMENTO,
            ).first()

            # cria evento de encaminhamento no processo
            evento = CoreEvento.objects.create(
                processo=processo,
                numero=processo.eventos.count()+1,
                setor_criacao=processo.setor_atual,
                setor_encaminhado=resposta.defensoria,
                data_referencia=agora,
                historico=pedido.historico,
                tipo=tipo_evento
            )

            # encaminha processo para novo setor
            if evento.setor_encaminhado:
                processo.setor_encaminhado = evento.setor_encaminhado
                processo.save()

            # unifica lista de documentos
            documentos = [form_diligencia.cleaned_data['documento']] + list(form_diligencia.cleaned_data['anexos'])

            for documento in documentos:

                # adiciona documentos ao pedido de apoio
                AtendimentoDocumento.objects.create(
                    atendimento=pedido,
                    pessoa=indeferimento.pessoa,
                    documento_online=documento.documento,
                    arquivo=documento.arquivo,
                    nome=documento.nome,
                    cadastrado_por=servidor,
                    enviado_por=servidor,
                    data_enviado=agora,
                )

                # adiciona documentos ao evento do processo
                CoreDocumento.objects.create(
                    processo=evento.processo,
                    evento=evento,
                    tipo=documento.tipo,
                    nome=documento.nome,
                    documento=documento.documento,
                    arquivo=documento.arquivo,
                )

            # dados adicionais da resposta da diligência
            resposta.origem = pedido
            resposta.nucleo = resposta.defensoria.nucleo
            resposta.defensor = resposta.defensoria.all_atuacoes.vigentes().titularidades().first().defensor
            resposta.save()

            messages.success(request, 'Solicitação de diligência registrada com sucesso!')

    else:

        messages.error(request, 'Erro ao solictar diligência: informações inconsistentes!')

    return redirect('indeferimento:ver_solicitacao', setor_id=processo.setor_atual.id, nucleo_id=nucleo_id,
                    processo_uuid=processo_uuid)


class IndeferimentoListView(ListView):
    queryset = Indeferimento.objects.select_related(
        'pessoa',
        'atendimento',
        'processo',
        'processo__classe',
        'processo__setor_atual',
        'defensor__servidor__usuario',
    ).ativos().order_by(
        'processo__situacao',
        '-processo__cadastrado_em'
    )
    model = Indeferimento
    paginate_by = 50
    template_name = "indeferimento/buscar.html"

    def get_context_data(self, **kwargs):
        context = super(IndeferimentoListView, self).get_context_data(**kwargs)
        context.update({
                'form': forms.BuscarIndeferimentoForm(self.request.GET),
                'nucleo_id': self.request.GET.get('nucleo'),
                'filtro': self.request.GET.get('filtro'),
                'angular': 'NucleoDPGCtrl',
        })
        return context

    def get_queryset(self):

        queryset = super(IndeferimentoListView, self).get_queryset()
        q = Q()

        if self.request.GET.get('resultado'):
            q &= Q(resultado=self.request.GET.get('resultado'))

        if self.request.GET.get('tipo_baixa'):
            q &= Q(tipo_baixa=self.request.GET.get('tipo_baixa'))

        if self.request.GET.get('filtro'):

            filtro_texto = self.request.GET.get('filtro').strip()
            filtro_numero = re.sub('[^0-9]', '', filtro_texto)

            if len(filtro_numero) in [11, 14]:  # Numero do CPF ou CNPJ
                q &= Q(pessoa__cpf=filtro_numero)
            elif len(filtro_numero):
                q &= Q(processo__numero__icontains=filtro_texto)
            else:

                filtro_norm = Util.normalize(filtro_texto)

                # Filtro nome/razão social
                q_nome = Q(pessoa__nome_norm__istartswith=filtro_norm)

                # Só busca por nome social caso seja tipo pessoa física
                q_nome_social = Q(
                    Q(pessoa__tipo=constantes.TIPO_PESSOA_FISICA) &
                    Q(pessoa__nome_social__istartswith=filtro_texto)
                )

                # Só busca por nome fantasia (apelido) caso seja tipo pessoa jurídica
                q_nome_fantasia = Q(
                    Q(pessoa__tipo=constantes.TIPO_PESSOA_JURIDICA) &
                    Q(pessoa__apelido__istartswith=filtro_texto)
                )

                q &= Q(q_nome | q_nome_social | q_nome_fantasia)

        return queryset.filter(q)


class EventoIndeferimentoCreateView(EventoCreateView):
    def get_success_url(self):
        if self.object.em_edicao:
            kwargs = {'processo_uuid': self.kwargs['processo_uuid'], 'pk': self.object.pk}
            return reverse('indeferimento:evento_editar', kwargs=kwargs)
        else:
            return self.request.POST.get('next')


class EventoIndeferimentoUpdateView(EventoUpdateView):
    form_class = forms.EditarEventoIndeferimentoForm
    minimo_documentos = 1

    def get_success_url(self):
        kwargs = {'processo_uuid': self.kwargs['processo_uuid'], 'pk': self.object.pk}
        return reverse('indeferimento:evento_editar', kwargs=kwargs)
