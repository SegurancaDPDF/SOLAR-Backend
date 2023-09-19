# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required

# Modulos locais
from processo.processo import views

urlpatterns = [

    url(r'^distribuicao/', include(('processo.distribuicao.urls', 'distribuicao'), namespace='distribuicao')),
    url(r'^associacao/', include(('processo.associacao.urls', 'associacao'), namespace='associacao')),
    url(r'^honorarios/', include('processo.honorarios.urls')),
    url(r'^intimacao/', include(('processo.intimacao.urls', 'intimacao'), namespace='intimacao')),
    url(r'^peticionamento/', include(('processo.peticionamento.urls', 'peticionamento'), namespace='peticionamento')),

    url(r'^acessar/$', views.acessar, name='processo_acessar'),
    url(r'^identificar/$', login_required(views.IdentificarView.as_view()), name='processo_identificar'),
    url(r'^listar/$', views.listar, name='processo_listar'),
    url(r'^salvar/$', views.salvar, name='processo_salvar'),
    url(r'^numero_processos_com_atualizacao_pendentes/$',
        views.numero_processos_com_atualizacao_pendentes,
        name='numero_processos_com_atualizacao_pendentes'
        ),

    url(r'^extra/salvar/$', views.salvar_extra, name='processo_extra_salvar'),

    url(r'^([0-9.-]+)/get/json/$', views.get_json, name='processo_get_json'),
    url(r'^parte/([0-9.-]+)/json/get/permissao/$',
        views.get_json_permissao_processo_botoes,
        name='processo_json_get_permissao_botoes'
        ),

    url(r'^pendente/defensor/([0-9.-]+)/get/$',
        views.get_pendentes_por_defensor,
        name='processo_pendente_eproc_get_json'
        ),
    url(r'^pendente/defensor/relogio/set/$',
        views.set_pendentes_relogio,
        name='processo_pendente_relogio_set'
        ),

    url(r'^(?P<processo_numero>\d+)/grau/(?P<processo_grau>\d+)/visualizar/$',
        login_required(views.VisualizarView.as_view()),
        name='processo_visualizar'
             ''),
    url(r'^([0-9.-]+)/fase/listar/$', views.listar_fases, name='processo_listar_fases'),
    url(r'^(?P<processo_numero>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/fase/listar/$',
        views.listar_fases,
        name='processo_listar_fases'
             ''),
    url(r'^([0-9.-]+)/parte/([0-9.-]+)/excluir/$', views.excluir_parte, name='processo_parte_excluir'),
    url(r'^parte/transferir/$', views.transferir_parte, name='processo_parte_transferir'),

    url(r'^acao/listar/$', views.listar_acao, name='processo_acao_listar'),

    url(r'^audiencia/listar/$', views.listar_audiencias, name='processo_audiencias'),
    url(r'^audiencia/remanejar/$', views.remanejar_audiencia, name='processo_audiencias_remanejar'),
    url(r'^audiencia/([0-9.-]+)/realizar/$', views.realizar_audiencia, name='processo_audiencia_realizar'),

    url(r'^fase/salvar/$', views.salvar_fase, name='processo_fase_salvar'),
    url(r'^fase/([0-9.-]+)/get/json/$', views.get_json_fase, name='processo_fase_get_json'),
    url(r'^fase/([0-9.-]+)/excluir/$', views.excluir_fase, name='processo_fase_excluir'),
    url(r'^fase/documento/listar/$', views.listar_documento_fase, name='processo_fase_documento_listar'),
    url(r'^fase/documento/salvar/$', views.salvar_documento_fase, name='processo_fase_documento_salvar'),
    url(r'^fase/documento/([0-9.-]+)/excluir/$', views.excluir_documento_fase, name='processo_fase_documento_excluir'),
    url(r'^fase/tipo/listar/$', views.listar_fase_tipo, name='processo_listar_fase_tipo'),

    url(r'^parte/situacao/salvar$', views.salvar_situacao_parte, name='salvar_situacao_parte'),
    url(r'^partes/get$', views.get_partes_processos, name='partes_situacao_get'),
]
