# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^defensoria-vara/cadastrar/$', login_required(views.DefensoriaVaraCreateView.as_view()),
        name='defensoria_vara_cadastrar'),
    url(r'^defensoria-vara/listar/$', login_required(views.DefensoriaVaraListView.as_view()),
        name='defensoria_vara_listar'),
    url(r'^tipo-de-fase/buscar/$', login_required(views.FaseTipoListView.as_view()), name='fase_tipo_buscar'),
    url(r'^tipo-de-fase/(?P<pk>[0-9]+)/visualizar/$', login_required(views.FaseTipoDetailView.as_view()),
        name='fase_tipo_visualizar'),
]
