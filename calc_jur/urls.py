# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views


urlpatterns = [
    url(r'^calcjur/', views.index, name='calc_jur'),
    url(r'^salarios/', views.get_salarios, name='calc_jur_get_salarios'),
    url(r'^inpc/([0-9.-]+)/', views.get_inpc, name='calc_jur_get_inpc'),
    url(r'^calcjur_penal/', views.calcular_penal, name='calcjur_penal_calcular'),
]
