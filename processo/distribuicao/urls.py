# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^distribuir/$', login_required(views.DistribuirListView.as_view()),
        name='distribuir'),
    url(r'^redistribuir/$', login_required(views.RedistribuirAvisoView.as_view()),
        name='redistribuir'),
]
