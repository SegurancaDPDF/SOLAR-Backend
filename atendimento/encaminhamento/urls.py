# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

# Modulos locais
from . import views


urlpatterns = [
    # url(r'^([0-9]+)/$', views.index, name='encaminhamento_index'),
    url(r'^$', login_required(views.IndexView.as_view()), name='encaminhamento_index'),
    url(r'^(?P<ligacao_numero>\d+)/$', login_required(views.LigacaoView.as_view()), name='encaminhamento_ligacao'),
    url(r'^(?P<ligacao_numero>\d+)/encaminhar/(?P<encaminhamento_id>\d+)/$', views.encaminhar, name='encaminhamento_encaminhar'),
    url(r'^cadastrar/$', views.cadastrar, name='encaminhamento_cadastrar'),
    url(r'^salvar/$', views.salvar, name='encaminhamento_salvar'),
    url(r'^(\d+)/editar/$', views.editar, name='encaminhamento_editar'),
]
