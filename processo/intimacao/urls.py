# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^painel/$', login_required(views.PainelView.as_view()), name='painel'),
    url(r'^buscar/$', login_required(views.BuscarView.as_view()), name='buscar'),
    url(r'^abrir-prazo/$', login_required(views.AbrirPrazoView.as_view()), name='abrir-prazo'),
    url(r'^etiquetar-prazo/$', login_required(views.EtiquetarPrazoView.as_view()), name='etiquetar-prazo'),
]
