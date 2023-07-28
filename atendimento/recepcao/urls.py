# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views


urlpatterns = [

    url(r'^$', views.index, name='recepcao_index'),
    url(r'^chamar/$', views.chamar, name='painel_chamar'),

    url(r'^marcados/comarca/([0-9]+)/$', views.marcados_comarca, name='recepcao_marcados_comarca'),
    url(r'^marcados/comarca/([0-9]+)/get/$', views.marcados_comarca_get, name='recepcao_marcados_comarca_get'),
    url(r'^marcados/comarca/([0-9]+)/predio/([0-9]+)/$', views.marcados_comarca, name='recepcao_marcados_predio'),
    url(r'^marcados/comarca/([0-9]+)/predio/([0-9]+)/get/$', views.marcados_comarca_get,
        name='recepcao_marcados_predio_get'),
    url(r'^marcados/([0-9]+)/$', views.atendimento, name='recepcao_atendimento'),
    url(r'^marcados/([0-9]+)/json/get/liberacao/$', views.get_json_atendimento_liberar,
        name='get_json_atendimento_liberacao'),
    url(r'^marcados/([0-9]+)/tipo/([0-2])/$', views.atendimento, name='recepcao_atendimento'),
    url(r'^marcados/([0-9]+)/tipo/([0-1])/responsavel/([0-1])/cadastrado/([0-1])/$', views.atendimento,
        name='recepcao_atendimento'),
    url(r'^marcados/([0-9]+)/tipo/([0-1])/responsavel/([0-1])/cadastrado/([0-1])/pessoa/$', views.atendimento,
        name='recepcao_atendimento'),
    url(r'^marcados/([0-9]+)/tipo/([0-1])/responsavel/([0-1])/cadastrado/([0-1])/pessoa/([0-9]+)/$', views.atendimento,
        name='recepcao_atendimento'),
    url(r'^publico/$', views.publico, name='recepcao_publico'),
    url(r'^buscar_pessoa/$', views.buscar_pessoa, name='recepcao_buscar_pessoa'),
    url(r'^adicionar_pessoa/$', views.atendimento_adicionar_pessoa,
        name='recepcao_adicionar_pessoa'),
    url(r'^remover_pessoa/$', views.remover_pessoa, name='recepcao_remover_pessoa'),
    url(r'^alterar_interessado/$', views.alterar_interessado, name='recepcao_alterar_interessado'),
    url(r'^alterar_responsavel/$', views.alterar_responsavel, name='recepcao_alterar_responsavel'),
    url(r'^alterar_tipo_pessoa_envolvida/$', views.alterar_tipo_pessoa_envolvida,
        name='recepcao_alterar_tipo_pessoa_envolvida'),
    url(r'^alterar_defensoria/$', views.alterar_defensoria, name='recepcao_alterar_defensoria'),
    url(r'^salvar_atendimento/$', views.salvar_atendimento, name='recepcao_salvar_atendimento'),

    url(r'^predio/alterar/$', views.alterar_predio, name='recepcao_predio_alterar'),

    url(r'^predio/$', views.index_predio, name='recepcao_index_predio'),
    url(r'^predio/([0-9]+)/$', views.predio_set, name='recepcao_predio_set'),

]
