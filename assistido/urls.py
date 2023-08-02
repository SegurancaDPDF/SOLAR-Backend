# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views


urlpatterns = [
    url(r'^avaliar/$', views.avaliar, name='assistido_avaliar'),
    url(r'^buscar/$', views.buscar, name='assistido_buscar'),
    url(r'^comunidade/listar/$', views.listar_comunidade, name='assistido_listar_comunidade'),
    url(r'^cpf/existe/$', views.cpf_existe, name='assistido_cpf_existe'),
    url(r'^cadastrar/$', views.editar, name='assistido_editar'),
    url(r'^cadastrar/(?P<pessoa_id>[0-9]+)/(?P<tipo_pessoa>[0-9]+)/$', views.editar, name='assistido_editar'),
    url(r'^editar/(\d+)/$', views.editar, name='assistido_editar'),
    url(r'^editar/(?P<pessoa_id>[0-9]+)/(?P<tipo_pessoa>[0-9]+)/$', views.editar, name='assistido_editar'),
    url(r'^excluir/(\d+)/$', views.excluir, name='assistido_excluir'),
    url(r'^filiacao/excluir/$', views.excluir_filiacao, name='assistido_excluir_filiacao'),
    url(r'^endereco/excluir/$', views.excluir_endereco, name='assistido_excluir_endereco'),
    url(r'^foto/salvar/$', views.salvar_foto, name='assistido_salvar_foto'),
    url(r'^json/get/$', views.get_json, name='assistido_json_get'),
    url(r'^(\d+)/endereco/json/get/$', views.get_json_enderecos_pessoa_assistida, name='assistido_endereco_json_get'),
    url(r'^(?P<pessoa_id>[0-9]+)/documento/(?P<documento_id>[0-9]+)/excluir/$',
        views.excluir_documento,
        name='assistido_excluir_documento'),
    url(r'^(?P<pessoa_id>[0-9]+)/documento/listar/$', views.listar_documento, name='assistido_documento_listar'),
    url(r'^(?P<pessoa_id>[0-9]+)/documento/adicionar/$', views.salvar_documento, name='assistido_documento_adicionar'),
    url(r'^(?P<pessoa_id>[0-9]+)/foto/salvar-agora/$', views.salvar_foto_agora, name='assistido_salvar_foto_agora'),
    url(
        r'^(\d+)/endereco/historico/json/get/$',
        views.get_json_enderecos_historico_pessoa_assistida,
        name='assistido_endereco_historico_json_get'
    ),
    url(r'^(\d+)/json/get/$', views.get_json, name='assistido_json_get'),
    url(r'^cpf/(\d+)/json/get/$', views.get_json_by_cpf, name='assistido_json_get_by_cpf'),
    url(r'^salvar/$', views.salvar, name='assistido_salvar'),
    url(r'^profissao/listar/$', views.listar_profissao, name='assistido_listar_profissao'),
    url(r'^(\d+)/telefone/excluir/$', views.excluir_telefone, name='assistido_excluir_telefone'),
    url(r'^campos-obrigatorios/$',
        views.index_campos_obrigatorios,
        name='campos_obrigatorios_index'),
    url(r'^campos-obrigatorios/perfil/(?P<perfil_id>[0-9]+)/$',
        views.configurar_campos_obrigatorios,
        name='campos_obrigatorios_configurar_perfil'),
    url(r'^campos-obrigatorios/perfil/(?P<perfil_id>[0-9]+)/salvar/$',
        views.salvar_campos_obrigatorios,
        name='campos_obrigatorios_salvar_perfil'),
    url(r'^unificar/$', views.unificar, name='assistido_unificar'),
    url(r'^patrimonio/(?P<patrimonio_id>[0-9]+)/$', views.excluir_patrimonio_assistido_por_id),
    url(r'^editar/([0-9.-]+)/acesso/$', views.listar_acesso, name='assistido_acesso_listar'),
    url(r'^editar/([0-9.-]+)/acesso/conceder/$', views.conceder_acesso, name='assistido_acesso_conceder'),
    url(r'^editar/([0-9.-]+)/acesso/revogar/$', views.revogar_acesso, name='assistido_acesso_revogar'),
    url(r'^editar/([0-9.-]+)/acesso/solicitar/$', views.solicitar_acesso, name='assistido_acesso_solicitar'),
]
