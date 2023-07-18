# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblitecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views

urlpatterns = [

    url(r'^$', views.index, name='painel_index'),
    url(r'^senhas/predio/([0-9]+)/$', views.get_senhas, name='get_senhas'),
    url(r'^predios/$', views.index_get_predios, name='painel_index_predios'),
    url(r'^predios/([0-9]+)/$', views.predio_set, name='painel_predio_set'),

]
