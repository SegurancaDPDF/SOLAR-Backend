# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url

from . import views

__author__ = 'amx-dev'

urlpatterns = [
    url(r'^$', views.index, name='honorarios_index'),
    url(r'^([0-9.-]+)/$', views.processo, name='honorarios_processo'),
    url(r'^([0-9.-]+)/get/$', views.honorario_id, name='honorarios_processo_get'),
    url(r'^([0-9.-]+)/excluir/possivel/$',
        views.impossibilidade_honorario_cadastrado,
        name='honorarios_processo_excluir_possivel'
        ),
    url(r'^(?P<honorario_id>[0-9]+)/suspender/$', views.suspender, name='honorarios_suspender'),
    url(r'^(?P<honorario_id>[0-9]+)/criar-atendimento/$', views.criar_atendimento, name='honorarios_criar_atendimento'),
    url(r'^altera/situacao/$', views.altera_situacao, name='honorarios_altera_situacao'),
    url(r'^altera/recursogerado/$', views.altera_recurso_gerado, name='honorarios_altera_recurso_gerado'),
    url(r'^movimento/salvar/$', views.salvar_movimento, name='honorarios_salvar_movimento'),
    url(r'^movimento/editar/$', views.editar_movimento, name='honorarios_editar_movimento'),
    url(r'^movimento/documento/salvar/$',
        views.salvar_documento_movimento,
        name='honorarios_salvar_documento_movimento'
        ),
    url(r'^movimento/documento/visibilidade/([0-9.-]+)/$',
        views.visibilidade_documento_movimento,
        name='honorarios_visibilidade_documento_movimento'
        ),
    url(r'^transitados/julgados/$', views.transitados_julgados_list, name='honorarios_transitados_e_julgados_index'),
    url(r'^transitados/julgados/defensor/$',
        views.transitados_julgados_list_defensor,
        name='honorarios_transitados_e_julgados_defensor'
        ),
    url(r'^recursos/$', views.recusos_list, name='honorarios_recursos_index'),
    url(r'^atualizacoes/$', views.atualizacoes_list, name='honorarios_atualizacoes_index'),
    url(r'^atualizacoes/alertas/([0-9.-]+)/$', views.visualiza_alertas, name='confirma_visualizacao_alertas'),
    url(r'^analise/$', views.analise_list, name='honorarios_analise_index'),
    url(r'^suspensos/$', views.suspensos_list, name='honorarios_suspensos_index'),
    url(r'^impossibilidade/$', views.impossibilidade_list, name='honorarios_impossibilidade_index'),
    url(r'^preanalise/$', views.preanalise_list, name='honorarios_preanalise_index'),
    url(r'^fase/possibilidade/$', views.possibilidade_honorarios, name='honorarios_possivel'),
    url(r'^fase/([0-9.-]+)/impossibilidade/$', views.impossibilidade_honorarios, name='honorarios_impossivel'),
    url(r'^fase/impossibilidade/checked/$', views.impossibilidade_honorarios_check, name='honorarios_impossivel_check'),
    url(r'^fase/analise/$', views.criar_analise, name='honorarios_criar_pendencia'),
    url(r'^fase/analise/checked/$', views.analise_honorarios_check, name='honorarios_analise_check'),
    url(r'^relatorios/$', views.relatorios_list, name='honorarios_relatorios_index'),
]
