# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

# Modulos locais
from . import views


urlpatterns = [
    url(r'^$', views.index, name='precadastro_index'),
    url(r'^iniciar/$', views.iniciar, name='precadastro_iniciar'),
    url(r'^continuar/([0-9]+)/$', views.continuar, name='precadastro_continuar'),
    url(r'^encerrar/$', views.encerrar, name='precadastro_encerrar'),
    url(r'^encerrar/([0-9]+)/([0-9]+)/$', views.encerrar, name='precadastro_encerrar'),
    url(r'^atendimento/([0-9]+)/$', views.atendimento, name='precadastro_atendimento'),
    url(r'^pessoa/get/$', views.get_pessoa, name='precadastro_get_pessoa'),
    url(r'^pessoa/set/([0-9]+)/$', views.set_pessoa, name='precadastro_set_pessoa'),
    url(r'^painel/$', login_required(views.PainelView.as_view()), name='precadastro_painel'),
    url(r'^painel/(?P<slug>\d+)/alterar-comarca/$',
        login_required(views.PainelAlterarComarcaView.as_view()), name='precadastro_painel_alterar_comarca'),
]

# DPE-AM
urlpatterns += [
    url(r'^enviar_lembrete_email/$', views.enviar_lembrete_email, name='precadastro_lembrete'),
    url(r'^enviar_reclamacao_email/$', views.enviar_reclamacao_email, name='reclamacao_lembrete'),
    url(r'^reclamacao/painel/(?P<painel>(comercial|industrial|residencial|todos))/$',
        login_required(views.ReclamacaoPainel.as_view()), name='painel_acompanhar_reclamacao'),
]
