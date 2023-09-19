# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^atendimento/(?P<atendimento_numero>[0-9]+)/', include([
        url(r'^$',
            login_required(views.AtendimentoProcessoListView.as_view()),
            name='atendimento'),
        url(r'^novo/$',
            login_required(views.IndexView.as_view()),
            name='novo'),
        url(r'^enviar-para-analise/$',
            login_required(views.EnviarParaAnaliseView.as_view()),
            name='enviar-para-analise'),
    ])),
    url(r'^(?P<pk>[0-9]+)/', include([
        url(r'^visualizar/$',
            login_required(views.IndexView.as_view()),
            name='visualizar'),
        url(r'^excluir/$',
            login_required(views.ManifestacaoDeleteView.as_view()),
            name='excluir'),
    ])),
    url(r'^buscar/$',
        login_required(views.BuscarListView.as_view()),
        name='buscar'),
    url(r'^documento/(?P<pk>[0-9]+)/excluir/$',
        login_required(views.DocumentoDeleteView.as_view()),
        name='documento_excluir'),
    url(r'^peticionar/$',
        login_required(views.PeticionarEmMassaView.as_view()),
        name='peticionar'),
]
