# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views


urlpatterns = [
    url(r'^$', views.index, name='qualificacao_index'),
    url(r'^buscar/$', views.buscar, name='qualificacao_buscar'),
    url(r'^([0-9]+)/$', views.index, name='qualificacao_index'),
    url(r'^([0-9]+)/buscar/$', views.buscar, name='qualificacao_buscar'),
    url(r'^qualificar/([0-9]+)/$', views.qualificar, name='qualificacao_encaminhar'),
    url(r'^listar/$', views.listar, name='qualificacao_listar'),
    url(r'^listar/nucleo/([0-9]+)/$', views.listar_nucleo, name='qualificacao_listar_nucleo'),
    url(r'^visualizar/$', views.visualizar, name='qualificacao_visualizar'),
]
