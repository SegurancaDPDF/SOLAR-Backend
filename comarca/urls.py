# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views


urlpatterns = [
    url(r'^([0-9.-]+)/$', views.index, name='comarca_index'),
    url(r'^atuacoes/$', views.status_comarca, name='status_comarca'),
    url(r'^guiches/$', views.guiches, name='comarca_guiches'),
    url(r'^predio/guiche/get/$', views.get_guiche, name='get_guiche'),
    url(r'^guiches/salvar/$', views.salvar_guiche, name='comarca_salvar_guiche'),
    url(r'^listar/$', views.listar, name='comarca_listar'),
    url(r'^predio/buscar/$', views.buscar_predio, name='comarca_buscar_predio'),
    url(r'^predio/cadastrar/$', views.cadastrar_predio, name='comarca_cadastrar_predio'),
    url(r'^predio/salvar/$', views.salvar_predio, name='comarca_salvar_predio'),
    url(r'^predio/(\d+)/editar/$', views.editar_predio, name='comarca_editar_predio'),
    url(r'^predio/get/$', views.get_predios, name='comarca_get_predios'),

]
