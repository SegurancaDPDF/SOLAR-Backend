# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views

urlpatterns = [

    url(r'^$', views.index, name='itinerante_index'),
    url(r'^distribuir/$', views.distribuir, name='itinerante_distribuir'),
    url(r'^distribuir/salvar/$', views.distribuir_salvar, name='itinerante_distribuir_salvar'),
    url(r'^autorizar/$', views.autorizar, name='itinerante_autorizar'),
    url(r'^excluir/$', views.excluir, name='itinerante_excluir'),
    url(r'^listar/$', views.listar, name='itinerante_listar'),
    url(r'^salvar/$', views.salvar, name='itinerante_salvar'),

]
