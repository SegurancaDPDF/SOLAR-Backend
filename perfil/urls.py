# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url

# Modulos locais
from . import views

# função para definir padrões de URL em Django.

urlpatterns = [
    url(r'^admin/$', views.perfil_admin, name='perfil_admin'),
    url(r'^comarcas/$', views.perfil_comarcas, name='perfil_comarcas'),
    url(r'^atualizacoes/$', views.atualizacoes, name='atualizacoes_perfil'),
    url(r'^editar/$', views.editar_perfil, name='editar_perfil'),
    url(r'^editar/senha/$', views.editar_senha, name='editar_senha'),
    url(r'^editar/email/$', views.editar_email, name='editar_email'),
    url(r'^editar/configurar-visualizacao-chat-por-atuacao/$', views.configurar_visualizacao_chat_por_atuacao,
        name='configurar_visualizacao_chat_por_atuacao'),
    url(r'^editar/foto/$', views.editar_foto, name='editar_foto'),
    url(r'^editar/senha-eproc/$', views.editar_senha_eproc, name='editar_senha_eproc'),
    url(r'^editar/usuario-projudi/$', views.editar_usuario_projudi, name='editar_usuario_projudi'),
    url(r'^editar/#tab-eproc', views.editar_perfil, name='editar_perfil_defensor'),
    url(r'^config/$', views.get_config_situacoes_sigilosas, name='get_config_situacoes_sigilosas'),
    # url(r'^salvar/$', views.salvar_perfil, name='salvar_perfil'),
]
