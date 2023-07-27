# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import include, url

# Modulos locais
from .nucleo import views


urlpatterns = [
    url(r'^multidisciplinar/', include('multidisciplinar.urls')),
    url(r'^diligencia/', include('nucleo_diligencia.urls')),
    url(r'^nadep/', include('nucleo.nadep.urls')),
    url(r'^itinerante/', include('nucleo.itinerante.urls')),
    url(r'^procedimento/', include(('propac.urls', 'procedimentos'), namespace='procedimentos')),
    url(r'^([0-9.-]+)/$', views.index, name='nucleo_index'),
    url(r'^([0-9.-]+)/formulario/listar/$', views.listar_formularios, name='nucleo_formularios_listar'),
    url(r'^defensoria/listar/$', views.listar_defensorias, name='nucleo_defensorias_listar'),
    url(r'^listar/$', views.listar, name='nucleo_listar'),
]
