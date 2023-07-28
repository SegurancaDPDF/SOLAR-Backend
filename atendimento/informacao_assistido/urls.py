from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblitecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views

urlpatterns = [
    url(r'^$', views.index, name='informacao_index'),
    url(r'^salvar$', views.salvar, name='informacao_salvar'),
]
