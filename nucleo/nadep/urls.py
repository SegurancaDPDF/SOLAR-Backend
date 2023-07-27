# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views
from nucleo.nadep.views import Presos

urlpatterns = [

    url(r'^$', views.views.index, name='nadep_index'),
    url(r'^comarca/(\d+)/$', views.views.index_comarca, name='nadep_index_comarca'),

    url(r'^pessoa/buscar/$', views.views.buscar_pessoa, name='nadep_buscar_pessoa'),
    url(r'^pessoa/visualizar/(\d+)/$', views.views.visualizar_pessoa, name='nadep_visualizar_pessoa'),
    url(r'^pessoa/visualizar/$', views.views.visualizar_pessoa, name='nadep_visualizar_pessoa'),

    url(r'^pessoa/(\d+)/prisao/get/$',
        views.Prisoes.buscar_prisao_pessoa_json,
        name='nadep_buscar_prisao_pessoa__json'
        ),

    url(r'^estabelecimento/buscar/$', views.EstabelecimentosPenais.buscar_estabelecimento,
        name='nadep_buscar_estabelecimento'),
    url(r'^estabelecimento/cadastrar/$', views.EstabelecimentosPenais.cadastrar_estabelecimento,
        name='nadep_cadastrar_estabelecimento'),
    url(r'^estabelecimento/editar/(\d+)/$', views.EstabelecimentosPenais.editar_estabelecimento,
        name='nadep_editar_estabelecimento'),
    url(r'^estabelecimento/excluir/(\d+)/$', views.EstabelecimentosPenais.excluir_estabelecimento,
        name='nadep_excluir_estabelecimento'),
    url(r'^estabelecimento/salvar/$', views.EstabelecimentosPenais.salvar_estabelecimento,
        name='nadep_salvar_estabelecimento'),
    url(r'^estabelecimento/get/$', views.EstabelecimentosPenais.buscar_estabelecimento_json,
        name='nadep_buscar_estabelecimento_json'),
    url(r'^estabelecimento/municipio/(\d+)/get/$', views.EstabelecimentosPenais.buscar_estabelecimento_json,
        name='nadep_buscar_estabelecimento_municipio_json'),
    url(r'^estabelecimento/municipio/get/$', views.EstabelecimentosPenais.buscar_municipio_json,
        name='nadep_buscar_municipio_json'),

    url(r'^preso/buscar/$', Presos.buscar, name='nadep_buscar_preso'),
    url(r'^preso/(\d+)/historico/$', views.Prisoes.get_historico, name='nadep_historico_preso'),
    url(r'^preso/(\d+)/transferir/$', views.Prisoes.cadastrar_transferencia, name='nadep_transferir_preso'),
    url(r'^preso/(\d+)/soltar/$', views.Prisoes.cadastrar_soltura, name='nadep_soltar_preso'),
    url(r'^preso/(\d+)/baixar/$', views.Prisoes.baixar_preso, name='nadep_baixar_preso'),

    url(r'^preso/(\d+)/aprisionamento/get/$', views.Prisoes.get_aprisionamento, name='nadep_listar_aprisionamento'),
    url(r'^preso/(\d+)/aprisionamento/salvar/$',
        views.Prisoes.cadastrar_aprisionamento,
        name='nadep_cadastrar_aprisionamento'
        ),
    url(r'^preso/(\d+)/aprisionamento/excluir/$',
        views.Prisoes.excluir_aprisionamento,
        name='nadep_excluir_aprisionamento'
        ),

    url(r'^preso/(\d+)/interrupcao/get/$', views.Prisoes.get_interrupcao, name='nadep_listar_interrupcao'),
    url(r'^preso/(\d+)/interrupcao/salvar/$', views.Prisoes.cadastrar_interrupcao, name='nadep_cadastrar_interrupcao'),
    url(r'^preso/(\d+)/interrupcao/excluir/$', views.Prisoes.excluir_interrupcao, name='nadep_excluir_interrupcao'),

    url(r'^preso/(\d+)/falta/get/$', views.Prisoes.get_falta, name='nadep_listar_falta'),
    url(r'^preso/(\d+)/falta/salvar/$', views.Prisoes.cadastrar_falta, name='nadep_cadastrar_falta'),
    url(r'^preso/(\d+)/falta/excluir/$', views.Prisoes.excluir_falta, name='nadep_excluir_falta'),

    url(r'^preso/(\d+)/remissao/get/$', views.Prisoes.get_remissao, name='nadep_listar_remissao'),
    url(r'^preso/(\d+)/remissao/salvar/$', views.Prisoes.cadastrar_remissao, name='nadep_cadastrar_remissao'),
    url(r'^preso/(\d+)/remissao/excluir/$', views.Prisoes.excluir_remissao, name='nadep_excluir_remissao'),
    url(r'^preso/(\d+)/remissao/total/get/$',
        views.Prisoes.get_total_remissao_periodo,
        name='nadep_total_remissao_periodo'
        ),

    url(r'^preso/(\d+)/calculo/get/$', views.Prisoes.get_calculo, name='nadep_get_calculo'),
    url(r'^preso/(\d+)/guia/get/$', views.Prisoes.get_guia, name='nadep_get_guia'),
    url(r'^preso/(\d+)/prisao/get/$', views.Prisoes.get_prisao, name='nadep_get_prisao'),
    url(r'^preso/(\d+)/processo/get/$', views.Prisoes.get_processo, name='nadep_get_processo'),

    url(r'^prisao/buscar/$', views.Prisoes.buscar_prisao, name='nadep_buscar_prisao'),
    url(r'^prisao/buscar/(\d+)/(\d+)/(\d+)/$',
        views.Prisoes.buscar_prisao_por_data,
        name='nadep_buscar_prisao_por_data'
        ),
    url(r'^prisao/cadastrar/(\d+)/$', views.Prisoes.cadastrar_prisao, name='nadep_cadastrar_prisao'),
    url(r'^prisao/editar/(\d+)/$', views.Prisoes.editar_prisao, name='nadep_editar_prisao'),
    url(r'^prisao/excluir/(\d+)/$', views.Prisoes.excluir_prisao, name='nadep_excluir_prisao'),
    url(r'^prisao/converter/(\d+)/$', views.Prisoes.converter_prisao, name='nadep_converter_prisao'),

    url(r'^prisao/([0-9]+)/$', views.Prisoes.visualizar_prisao, name='nadep_visualizar_prisao'),
    url(r'^prisao/([0-9]+)/atendimento/salvar/$', views.Atendimentos.salvar, name='nadep_atendimento_salvar'),
    url(r'^prisao/([0-9]+)/atendimento/listar/$', views.Atendimentos.listar, name='nadep_atendimento_listar'),
    url(r'^prisao/([0-9]+)/visita/salvar/$', views.Atendimentos.salvar_visita, name='nadep_visita_salvar'),
    url(r'^prisao/([0-9]+)/visita/listar/$', views.Atendimentos.listar_visita, name='nadep_visita_listar'),
    url(r'^prisao/([0-9]+)/horas/get/$', views.Prisoes.get_horas, name='nadep_horas_get'),
    url(r'^prisao/([0-9]+)/horas/salvar/$', views.Prisoes.salvar_horas, name='nadep_horas_salvar'),
    url(r'^prisao/([0-9]+)/horas/excluir/$', views.Prisoes.excluir_horas, name='nadep_horas_excluir'),
    url(r'^prisao/([0-9]+)/regime/alterar/$', views.Prisoes.alterar_regime, name='nadep_alterar_regime'),
    url(r'^prisao/([0-9]+)/regime/liquidar/$', views.Prisoes.liquidar_pena, name='nadep_liquidar_pena'),

    url(r'^prisao/atendimento/buscar/$', views.Atendimentos.buscar, name='nadep_buscar_atendimento'),
    url(r'^prisao/atendimento/excluir/([0-9]+)/$', views.Atendimentos.excluir, name='nadep_excluir_atendimento'),
    url(r'^prisao/atendimento/visualizar/([0-9]+)/$',
        views.Atendimentos.visualizar,
        name='nadep_visualizar_atendimento_prisao'
        ),

]
