# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views


urlpatterns = [
    url(r'^(\d+)/termo/json/get/$', views.get_termo_json, name='termo_json_get'),
    url(r'^termo/json/post/$', views.post_termo_json, name='termo_json_post'),
]
