# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.urls import re_path

# Modulos locais
from . import views

urlpatterns = [
    re_path('processo/(?P<processo_numero>[0-9]+)/relatorio/(?P<relatorio_tipo>[0-9]{1})/$',
            views.consultar_relatorio, name='consultar_relatorio'),
]
