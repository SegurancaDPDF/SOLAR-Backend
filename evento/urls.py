# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views


urlpatterns = [
    url(r'^$', views.index, name='evento_index'),
    url(r'^agenda/$', views.agenda_index, name='agenda_index'),
    url(r'^agenda/salvar/$', views.agenda_salvar, name='evento_salvar'),
    url(r'^agenda/atualizar/$', views.agenda_atualizar, name='evento_atualizar'),
    url(r'^bloqueio/$', views.bloqueio_index, name='evento_bloqueio_index'),
    url(r'^desbloqueio/listar/$', views.desbloqueio_listar, name='evento_desbloqueio_listar'),
    url(r'^defensor/([0-9.-]+)/listar/$', views.agenda_listar, name='evento_defensor_listar'),
    url(r'^atuacao/([0-9.-]+)/listar/$', views.agenda_listar_por_atuacao, name='evento_defensor_listar_por_atuacao'),
    url(r'^excluir/$', views.excluir, name='evento_excluir'),
    url(r'^excluir-parcial/$', views.excluir_parcial, name='evento_excluir_parcial'),
    url(r'^listar/$', views.listar, name='evento_listar'),
    url(r'^salvar/$', views.salvar, name='evento_salvar'),
    url(r'^autorizar/$', views.autorizar, name='evento_autorizar'),
]
