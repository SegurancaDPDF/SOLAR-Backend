# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views


urlpatterns = [
    url(r'^$', views.index, name='estatistica_index'),
    url(r'^pendencias/$', views.pendencias, name='estatistica_pendencias'),
]
