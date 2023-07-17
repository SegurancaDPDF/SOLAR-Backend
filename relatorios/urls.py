# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

# Modulos locais
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^listar/$', views.listar, name='listar'),
    url(r'^buscar/$', login_required(views.RelatorioListView.as_view()), name='buscar'),
    url(r'^jasper/novo/$', login_required(views.RelatorioCreateView.as_view()), name='novo'),
    url(r'^jasper/novo-parametrizavel/$',
        login_required(views.RelatorioParametrizavelCreateView.as_view()),
        name='novo-parametrizavel'),
    url(r'^metabase/novo/$', login_required(views.RelatorioMetabaseCreateView.as_view()), name='metabase-novo'),
    url(r'^(?P<pk>\d+)/', include([
        url(r'^editar/$', login_required(views.RelatorioUpdateView.as_view()), name='editar'),
        url(r'^excluir/$', login_required(views.RelatorioDeleteView.as_view()), name='excluir'),
        url(r'^parametrizar/$', login_required(views.RelatorioParametrosUpdateView.as_view()), name='parametrizar'),
        url(r'^visualizar/$', login_required(views.RelatorioVisualizarView.as_view()), name='visualizar'),
    ])),
]
