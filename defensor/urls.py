# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views


urlpatterns = [
    url(r'^listar/plantao/$', views.listar_plantao, name='defensor_listar_plantao'),
    url(r'^([0-9.-]+)/atuacoes/$', views.atuacao_listar, name='defensor_atuacoes'),
    url(r'^([0-9.-]+)/comarcas/$', views.comarcas_listar, name='comarcas_listar'),
    url(r'^([0-9.-]+)/comarcas/([0-9]{4})/$', views.comarcas_listar, name='comarcas_ano_listar'),
    url(r'^([0-9.-]+)/substitutos/$', views.substitutos_listar, name='defensor_substitutos_listar'),
    url(r'^([0-9.-]+)/supervisores/atuacoes/$', views.supervisores_listar_atuacoes,
        name='defensor_supervisores_listar_atuacoes'),
    url(r'^([0-9.-]+)/defensoria/([0-9.-]+)/substitutos/$', views.substitutos_defensoria_listar,
        name='defensor_substitutos_defensoria_listar'),
    url(r'^atuacao/$', views.atuacao_index, name='defensor_atuacao'),
    url(r'^atuacao/supervisores/listar/$', views.atuacao_supervisores_listar, name='defensor_atuacao_supervisores_listar'),  # noqa: E501
    url(r'^atuacao/salvar/$', views.atuacao_salvar, name='defensor_atuacao_salvar'),
    url(r'^atuacao/excluir/$', views.atuacao_excluir, name='defensor_atuacao_excluir'),
    url(r'^atuacao/remanejar-agendamentos/(?P<atuacao_id>[0-9]+)/$',
        views.remanejar_agendamentos,
        name='defensor_atuacao_excluir'
        ),
    url(r'^defensoria/listar/$', views.defensoria_listar, name='defensor_defensoria_listar'),
    url(r'^defensoria/substituido/listar/$', views.defensoria_substituido_listar,
        name='defensor_defensoria_substituido_listar'),
    url(r'^lotacao/salvar/$', views.lotacao_salvar, name='defensor_lotacao_salvar'),
    url(r'^plantao/listar/$', views.listar_editais_plantoes, name='defensor_plantao_listar'),
    url(r'^plantao/([0-9.-]+)/inscricoes/$', views.listar_inscricoes_plantao, name='defensor_inscricao_listar'),
    url(r'^plantao/([0-9.-]+)/vagas/$', views.listar_vagas_plantoes, name='defensor_listar_vagas'),
    url(r'^plantao/inscrever/$', views.inscrever_edital_plantao, name='defensor_plantao_inscrever'),
    url(r'^plantao/cancelar/$', views.cancelar_inscricao_edital_plantao, name='defensor_plantao_cancelar'),
]
