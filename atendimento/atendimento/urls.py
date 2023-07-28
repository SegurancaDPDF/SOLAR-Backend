# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required, permission_required
from rest_framework import routers

# Modulos locais
from . import views


urlpatterns = [

    url(r'^$', views.index, name='atendimento_index'),

    url(r'^index/', include([
        url(r'^get/$', views.index_get, name='atendimento_index_get'),
        url(r'^documentos/get/$', views.index_get_documentos, name='atendimento_index_get_documentos'),
        url(r'^resumo/get/$', views.index_get_resumo, name='atendimento_index_get_resumo'),
        url(r'^tarefas/get/$', views.index_get_tarefas, name='atendimento_index_get_tarefas'),
    ])),

    url(r'^buscar/$', views.buscar, name='atendimento_buscar'),
    url(r'^distribuir/$', views.distribuir, name='atendimento_distribuir'),
    url(r'^distribuir/salvar/$', views.distribuir_salvar, name='atendimento_distribuir_salvar'),
    url(r'^listar/$', views.listar, name='atendimento_listar'),
    url(r'^visualizar/([0-9.-]+)/$', views.visualizar, name='atendimento_visualizar'),
    url(r'^cronometro/$', views.cronometro, name='atendimento_cronometro'),

    url(r'^acesso/$', views.visualizar_acesso, name='atendimento_acesso_visualizar'),
    url(r'^acesso/([0-9.-]+)/conceder/$', views.conceder_acesso_por_id, name='atendimento_acesso_conceder_por_id'),
    url(r'^acesso/([0-9.-]+)/revogar/$', views.revogar_acesso_por_id, name='atendimento_acesso_revogar_por_id'),

    url(r'^acompanhamento/$', login_required(views.AcompanhamentoIndex.as_view()), name='atendimento_acompanhamento'),
    url(r'^acompanhamento/defensoria/(?P<defensoria_id>\d+)/painel/(?P<painel>(sem-peca|peca-digitada|peca-assinada|peticionado|sem-peca-juridica|peticionado-juridica))/$', login_required(views.AcompanhamentoPainel.as_view()), name='atendimento_acompanhamento_defensoria_painel'),  # noqa: E501

    url(r'^129/', include('atendimento.precadastro.urls')),
    url(r'^agendamento/', include('atendimento.agendamento.urls')),
    url(r'^encaminhamento/', include('atendimento.encaminhamento.urls')),
    url(r'^informacao/', include('atendimento.informacao.urls')),
    url(r'^informacao_assistido/', include('atendimento.informacao_assistido.urls')),
    url(r'^qualificacao/', include('atendimento.qualificacao.urls')),
    url(r'^recepcao/', include('atendimento.recepcao.urls')),

    url(r'^perfil/$', views.perfil, name='atendimento_perfil'),
    url(r'^assuntos/get/$', views.assuntos_get, name='atendimento_assuntos_get'),
    url(r'^assuntos/listar/$', views.assuntos_listar, name='atendimento_assuntos_listar'),
    url(r'^assuntos/salvar/$', views.salvar_assunto, name='atendimento_assunto_salvar'),
    url(r'^assuntos/excluir/$', views.excluir_assunto, name='atendimento_assunto_salvar'),
    url(r'^assuntos/mover/$', views.mover_assunto, name='atendimento_assunto_mover'),

    url(r'^formas/listar/defensor/$', views.listar_forma_atendimento_defensor, name='listar_forma_atendimento_defensor'),  # noqa: E501

    url(r'^([0-9.-]+)/remeter_atendimento/$', views.remeter_atendimento, name='remeter_atendimento'),

    url(r'^([0-9.-]+)/$', views.atender, name='atendimento_atender'),
    url(r'^([0-9.-]+)/ocultar/([0-9.-]+)/$', views.ocultar, name='atendimento_ocultar'),
    url(r'^([0-9.-]+)/salvar/$', views.salvar, name='atendimento_salvar'),

    url(r'^([0-9.-]+)/atender/tab/atividades/$', views.atender_tab_atividades, name='atendimento_atender_tab_atividades'),  # noqa
    url(r'^([0-9.-]+)/atender/tab/documentos/$', views.atender_tab_documentos, name='atendimento_atender_tab_documentos'),  # noqa
    url(r'^([0-9.-]+)/atender/tab/documentos/documentos_download/$', views.download_documentos_anexos, name='download_documentos_anexos'),  # noqa
    url(r'^([0-9.-]+)/atender/tab/tarefas/$', views.atender_tab_tarefas, name='atendimento_atender_tab_tarefas'),
    url(r'^([0-9.-]+)/atender/tab/historico/$', views.atender_tab_historico, name='atendimento_atender_tab_historico'),
    url(r'^([0-9.-]+)/atender/tab/processos/$', views.atender_tab_processos, name='atendimento_atender_tab_processos'),
    url(r'^([0-9.-]+)/atender/tab/processos/eproc/$', views.atender_tab_processos_eproc, name='atendimento_atender_tab_processos_eproc'),  # noqa
    url(r'^([0-9.-]+)/atender/tab/propacs/$', views.atender_tab_procedimentos, name='atendimento_atender_tab_procedimentos'),  # noqa
    url(r'^([0-9.-]+)/atender/tab/oficios/$', views.atender_tab_oficios, name='atendimento_atender_tab_oficios'),
    url(r'^([0-9.-]+)/atender/tab/outros/$', views.atender_tab_outros, name='atendimento_atender_tab_outros'),

    url(r'^([0-9.-]+)/atender/get/$', views.atender_get, name='atendimento_atender_get'),
    url(r'^([0-9.-]+)/atender/processos/get/$', views.atender_processos_get, name='atendimento_atender_processos_get'),
    url(r'^([0-9.-]+)/atender/outros/get/$', views.atender_outros_get, name='atendimento_atender_outros_get'),

    url(r'^([0-9.-]+)/atender/procedimentos/propacs/get/$', views.atender_procedimentos_propacs_get,
        name='atendimento_atender_propacs_procedimentos_get'),

    url(r'^excluir/$', views.excluir, name='atendimento_excluir'),
    url(r'^([0-9.-]+)/excluir/$', views.excluir, name='atendimento_excluir'),
    url(r'^([0-9.-]+)/finalizar/$', views.finalizar, name='atendimento_finalizar'),
    url(r'^([0-9.-]+)/json/get/$', views.get_json, name='atendimento_json_get'),
    url(r'^([0-9.-]+)/json/get/permissao/$',
        views.get_json_permissao_atendimento_botoes,
        name='atendimento_json_get_permissao_botoes'
        ),
    url(r'^([0-9.-]+)/json/get/pessoas/([0-9.-]+)/$', views.get_json_pessoas, name='atendimento_json_get_pessoas'),
    url(r'^([0-9.-]+)/json/get/documentos/$', views.get_json_documentos, name='atendimento_json_get_documentos'),
    url(r'^([0-9.-]+)/arvore/json/get/$', views.get_arvore_json, name='atendimento_arvore_json_get'),

    url(r'^([0-9.-]+)/acesso/$', views.listar_acesso, name='atendimento_acesso_listar'),
    url(r'^([0-9.-]+)/acesso/conceder/$', views.conceder_acesso, name='atendimento_acesso_conceder'),
    url(r'^([0-9.-]+)/acesso/revogar/$', views.revogar_acesso, name='atendimento_acesso_revogar'),
    url(r'^([0-9.-]+)/acesso/solicitar/$', views.solicitar_acesso, name='atendimento_acesso_solicitar'),

    url(r'^([0-9.-]+)/atividade/resumo/get/', views.get_resumo_atividade, name='atendimento_get_resumo_atividade'),
    url(r'^([0-9.-]+)/atividade/salvar/', views.salvar_atividade, name='atendimento_salvar_atividade'),

    url(r'^([0-9.-]+)/cronometro/$', views.cronometro, name='atendimento_cronometro'),

    url(r'^([0-9.-]+)/documento/$', views.listar_documento, name='atendimento_documento_listar'),
    url(r'^([0-9.-]+)/documento/salvar/$', views.salvar_documento, name='atendimento_documento_salvar'),
    url(r'^([0-9.-]+)/documento/excluir/$', views.excluir_documento, name='atendimento_documento_excluir'),
    url(r'^documento/agendar/$', views.agendar_documento, name='atendimento_documento_agendar'),
    url(r'^documento/analisar/$', views.analisar_documento, name='atendimento_documento_analisar'),

    url(r'^([0-9.-]+)/comunidade/salvar/$', views.salvar_comunidade, name='atendimento_comunidade_salvar'),
    url(r'^([0-9.-]+)/comunidade/listar/$', views.listar_comunidade, name='atendimento_comunidade_listar'),

    url(r'^([0-9.-]+)/defensorias/$', views.listar_defensorias, name='atendimento_tarefa_listar'),
    url(r'^([0-9.-]+)/tarefa/salvar/$', views.salvar_tarefa, name='atendimento_tarefa_salvar'),
    url(r'^([0-9.-]+)/tarefa/excluir/$', views.excluir_tarefa, name='atendimento_tarefa_excluir'),
    url(r'^([0-9.-]+)/tarefa/finalizar/$', views.finalizar_tarefa, name='atendimento_tarefa_finalizar'),
    url(r'^([0-9.-]+)/tarefa/responder/$', views.responder_tarefa, name='atendimento_tarefa_responder'),

    url(r'^([0-9.-]+)/oficio/salvar/', views.salvar_oficio, name='atendimento_salvar_oficio'),

    url(r'^tarefa/([0-9.-]+)/get/$', views.get_tarefa, name='atendimento_tarefa_visualizar'),
    url(r'^tarefa/([0-9.-]+)/visualizar/$', views.visualizar_tarefa, name='atendimento_tarefa_visualizar'),
    url(r'^tarefas/buscar/$',
        permission_required('atendimento.add_tarefa')
        (views.BuscarTarefas.as_view()),
        name='atendimento_tarefas_buscar'),
    url(r'^tarefas/finalizar/$',
        views.FinalizarTarefas.as_view(),
        name='atendimento_tarefas_finalizar'),

    url(r'^documento_tarefa_vincular/(?P<document_pk>\d+)/(?P<pk>\d+)/$',
        views.VincularDocumentoTarefa.as_view(),
        name='atendimento_tarefa_vincular'),

    url(r'^([0-9.-]+)/formulario/listar/', views.listar_formulario, name='atendimento_listar_formulario'),
    url(r'^([0-9.-]+)/formulario/salvar/', views.salvar_formulario, name='atendimento_salvar_formulario'),

    url(r'^([0-9.-]+)/unificar/([0-9.-]+)/$', views.unificar, name='atendimento_unificar'),
    url(r'^([0-9.-]+)/assunto/salvar/$', views.vincular_assuntos, name='atendimento_assunto_vincular'),

    url(r'^documento/excluir/', views.excluir_documento),
    url(r'^documento/listar/', views.listar_documento),
    url(r'^documento/pendentes/buscar/$', views.listar_atendimento_documentos_pendentes,
        name='atendimento_documentos_pendentes'),

    url(r'^([0-9.-]+)/vulnerabilidades/get/$', views.listar_vulnerabilidades,
        name='listar_vulnerabilidades'),

    url(r'^([0-9.-]+)/vulnerabilidades/salvar/$', views.salvar_vulnerabilidades,
        name='salvar_vulnerabilidades'),

    url(r'^(?P<atendimento_numero>\d+)/', include([
        url(r'^anotacao/', include([
            url(r'^nova/$',
                login_required(views.AnotacaoCreateView.as_view()),
                name='atendimento_nova_anotacao'),
        ])),
        url(r'^notificacao/', include([
            url(r'^nova/$',
                login_required(views.NotificacaoCreateView.as_view()),
                name='atendimento_nova_notificacao'),
        ])),
        url(r'^ged/criar/$',
            login_required(views.DocumentoCriarParaAtendimento.as_view()),
            name='atendimento_ged_criar'),
        url(r'^ged/auto/criar/$',
            login_required(views.auto_criar_documento_ged),
            name='atendimento_ged_auto_criar'),
        url(r'^ged/criar-via-modelo-publico/$',
            login_required(views.DocumentoCriarParaAtendimentoViaModeloPublico.as_view()),
            name='atendimento_ged_criar_via_modelo_publico'),
        url(r'^indeferimento/', include([
            url(r'^impedimento-form/$',
                views.atendimento_indeferimento_impedimento_form,
                name='atendimento_indeferimento_impedimento_form'),
            url(r'^suspeicao-form/$',
                views.atendimento_indeferimento_suspeicao_form,
                name='atendimento_indeferimento_suspeicao_form'),
            url(r'^negacao-procedimento-form/$',
                views.atendimento_indeferimento_negacao_procedimento_form,
                name='atendimento_indeferimento_negacao_procedimento_form'),
            url(r'^negacao-form/$',
                views.atendimento_indeferimento_negacao_form,
                name='atendimento_indeferimento_negacao_form'),
        ])),
        url(r'^nucleo/', include([
            url(r'^solicitar-form/$',
                views.solicitar_nucleo_form,
                name='atendimento_nucleo_solicitar_form'),
            url(r'^solicitar/$',
                views.solicitar_nucleo,
                name='atendimento_nucleo_solicitar'),
            url(r'^responder/$',
                views.responder_nucleo,
                name='atendimento_nucleo_responder'),
        ])),
        url(r'^visulizacao-body/$',
            views.atendimento_visualizacao_body,
            name='atendimento_visualizacao_body'),
    ])),
]


router_atendimento = routers.SimpleRouter()

router_atendimento.register(
    r'pastas-documentos',
    views.PastaDocumentoViewSet,
    basename='pasta-documentos'
)
