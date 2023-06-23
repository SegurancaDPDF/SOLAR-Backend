# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views

urlpatterns = [
    url(r'^$',
        views.index,
        name='nucleo_diligencia_index'),
    url(r'^comarca/(?P<comarca>[0-9]+)/$',
        views.index_comarca,
        name='nucleo_diligencia_index_comarca'),
    url(r'^pessoa/(?P<pessoa_id>[0-9]+)/confirmar/(?P<atendimento_numero>[0-9]+)/$',
        views.confirmar_pessoa,
        name='nucleo_diligencia_confirmar_pessoa'
        ),
    url(r'^pessoa/(?P<pessoa>[0-9]+)/distribuir/(?P<atendimento_numero>[0-9]+)/$',
        views.distribuir_pessoa,
        name='nucleo_diligencia_distribuir_pessoa'
        ),
    url(r'^pessoa/(?P<pessoa>[0-9]+)/atender/(?P<atendimento_numero>[0-9]+)/$',
        views.atender_pessoa,
        name='nucleo_diligencia_atender_pessoa'),
]
