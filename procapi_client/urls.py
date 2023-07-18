# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

# Modulos locais
from . import views

urlpatterns = [
    url(r'^processo/([0-9.-]+)/consultar/$', views.consultar_processo, name='eproc_consultar_processo'),
    url(r'^processo/([0-9.-]+)/documento/([0-9.-]+)/$', views.consultar_documento, name='eproc_consultar_documento'),
    url(r'^processo/(?P<processo_numero>[0-9]+)/documento/identificar/$',
        login_required(views.IdentificarDocumentoView.as_view()), name='eproc_identificar_documento'),
]
