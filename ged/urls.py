# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

# Modulos locais
from . import views


urlpatterns = [
    url(r'^painel/$',
        login_required(views.GEDPainelGeralView.as_view()),
        name='painel_geral'
        ),
    url(r'^painel/assinaturas-pendentes/$',
        login_required(views.GEDPainelAssinaturasPendentesView.as_view()),
        name='painel_geral_assinaturas_pendentes'
        ),
    url(r'^painel/assinaturas-realizadas/$',
        login_required(views.GEDAssinaturasRealizadasView.as_view()),
        name='painel_geral_assinaturas_realizadas'
        ),
    url(r'^painel/documentos/$',
        login_required(views.GEDDocumentoListView.as_view()),
        name='painel_geral_documentos'
        ),
    url(r'^painel/documentos-nao-finalizados/$',
        login_required(views.GEDPainelDocumentosNaoFinalizadosView.as_view()),
        name='painel_geral_documentos_nao_finalizados'
        ),
    url(r'^painel/documentos-finalizados/$',
        login_required(views.GEDPainelDocumentosFinalizadosView.as_view()),
        name='painel_geral_documentos_finalizados'
        ),
    url(r'^painel/documentos-em-edicao/$',
        login_required(views.GEDPainelDocumentosEmEdicaoView.as_view()),
        name='painel_geral_documentos_em_edicao'
        ),
    url(r'^painel/modelos/$',
        login_required(views.GEDPainelModelos.as_view()),
        name='painel_geral_modelos'
        ),
    url(r'^painel/modelos-publicos/$',
        login_required(views.GEDPainelModelosPublicos.as_view()),
        name='painel_geral_modelos_publicos'
        ),
    url(r'^painel/modelos-publicos/comarca/(?P<comarca_id>\d+)/$',
        login_required(views.GEDPainelModelosPublicos.as_view()),
        name='painel_geral_modelos_publicos_comarca'
        ),
    url(r'^painel/modelos-publicos/defensoria/(?P<defensoria_id>\d+)/$',
        login_required(views.GEDPainelModelosPublicos.as_view()),
        name='painel_geral_modelos_publicos_defensoria'
        ),
    url(r'^painel/documento/excluir/$',
        login_required(views.GEDPainelExcluirDocumento.as_view()),
        name='painel_geral_excluir_ged'
        ),

]
