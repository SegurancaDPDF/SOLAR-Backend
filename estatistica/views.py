# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    return render(request=request, template_name="estatistica/index.html", context=locals())


@login_required
def pendencias(request):
    return render(request=request, template_name="estatistica/pendencias.html", context=locals())
