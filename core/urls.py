# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from contrib.utils import email_info_acesso

# Modulos locais
from . import views

# configura as rotas de URL para diferentes visualizacoes
urlpatterns = [
    url(r'^processo/(?P<processo_uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/', include([
        url(r'^encaminhar/$', views.encaminhar_processo, name='processo_encaminhar'),
        url(r'^evento/', include([
            url(r'^criar/$', views.EventoCreateView.as_view(), name='evento_criar'),
            url(r'^criar/tipo/(?P<tipo>[0-9]+)/$', views.EventoCreateView.as_view(), name='evento_criar_tipo'),
        ])),
    ])),
    url(r'^processo/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/', include([
        url(r'^excluir/$', login_required(views.ProcessoDeleteView.as_view()), name='processo_excluir'),
    ])),
    url(r'^evento/', include([
        url(r'^(?P<pk>\d+)/', include([
            url(r'^editar/$', login_required(views.EventoUpdateView.as_view()), name='evento_editar'),
            url(r'^excluir/$', login_required(views.EventoDeleteView.as_view()), name='evento_excluir'),
            url(r'^registrar/$', login_required(views.EventoUpdateAndCloseView.as_view()), name='evento_encerrar'),
            url(r'^documento/', include([
                url(r'^criar/$', login_required(views.DocumentoCriarParaEvento.as_view()), name='criar_documento'),
                url(r'^upload/$', views.upload_documento, name='upload_documento'),
                url(r'^excluir/$', views.excluir_documento, name='excluir_documento'),
            ])),
        ])),
    ])),
    url(r'^documento/', include([
        url(r'^(?P<pk>\d+)/', include([
            url(r'^renomear/$', login_required(views.DocumentoRenameView.as_view()), name='documento_renomear'),
        ])),
    ])),
    url(r'^classe/listar/$', views.listar_classes, name='listar_classes'),
    url(r'^email_info_acesso/$', email_info_acesso, name='email_info_acesso'),
    url(r'^altera-sigilo-documento/$', views.altera_sigilo_documento, name='altera_sigilo_documento'),
]
