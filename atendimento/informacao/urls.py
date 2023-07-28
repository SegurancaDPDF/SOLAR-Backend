# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views


urlpatterns = [
    url(r'^([0-9]+)/$', views.index, name='informacao_index'),
    url(r'^buscar/$', views.buscar, name='informacao_buscar'),
    url(r'^informar/([0-9]+)/$', views.informar, name='informacao_informar'),
]
