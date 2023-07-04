# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required

# Modulos locais
from . import views
# Este trecho de código define as URLs (padrões de roteamento) para as views do aplicativo.
# Cada padrão de URL é mapeado para uma view específica e recebe um nome para referência.

urlpatterns = [
    url(r'^get/$', views.get_atividades_extraordinarias, name='get'),
    url(r'^salvar/$', views.salvar_atividade_extraordinaria, name='salvar'),
    url(r'^excluir/$', views.excluir_atividade_extraordinaria, name='excluir'),
    url(r'^buscar/$', login_required(views.AtividadeExtraordinariaListView.as_view()), name='buscar'),
    url(r'^(?P<pk>\d+)/', include([
        url(r'^editar/$', login_required(views.AtividadeExtraordinariaUpdateView.as_view()), name='editar'),
        url(r'^encerrar/$', login_required(views.AtividadeExtraordinariaCloseView.as_view()), name='encerrar'),
        url(r'^preencher-formulario/(?P<formulario_pk>\d+)/$',
            login_required(views.FormularioView.as_view()), name='preencher-formulario'),
    ])),
]
