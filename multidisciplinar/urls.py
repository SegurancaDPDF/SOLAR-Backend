# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views
# Urls que corresponde à página inicial e do módulo multidisciplinar

urlpatterns = [
    url(r'^$', views.index, name='multidisciplinar_index'),
    url(r'^comarca/(?P<comarca>[0-9]+)/$', views.index_comarca, name='multidisciplinar_index_comarca'),
    url(r'^atendimento/(?P<atendimento>[0-9]+)/distribuir/$',
        views.distribuir_atendimento,
        name='multidisciplinar_distribuir_atendimento'
        ),
    url(r'^cargo/listar/$', views.listar_cargos, name='multidisciplinar_listar_cargos'),
    url(r'^defensoria/listar/$', views.listar_defensorias, name='multidisciplinar_listar_defensorias'),
]
