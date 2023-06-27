# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required

# Modulos locais
from . import views

# definicao das URLs da aplicacao. Cada URL é associada a uma funcao da view correspondente
# são usadas para mapear as requisicoes recebidas para as funcoes apropriadas

urlpatterns = [
    url(r'^buscar/$', login_required(views.IndeferimentoListView.as_view()), name='buscar'),
    url(r'^nucleo/(?P<nucleo_id>[0-9]+)/', include([
        url(r'^$', views.index, name='index'),
        url(r'^setor/(?P<setor_id>[0-9]+)/$', views.index, name='index_setor'),
    ])),
    url(r'^solicitacao/', include([
        url(r'^impedimento/novo/$', views.novo_impedimento, name='novo_impedimento'),
        url(r'^negacao/nova/$', views.nova_negacao, name='nova_negacao'),
        url(r'^suspeicao/nova/$', views.nova_suspeicao, name='nova_suspeicao'),
        url(r'^negacao-procedimento/nova/$', views.nova_negacao_procedimento, name='nova_negacao_procedimento'),
        url(r'^(?P<processo_uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/', include([
            url(r'^editar/$', views.editar_solicitacao, name='editar_solicitacao'),
            url(r'^salvar/$', views.salvar_solicitacao, name='salvar_solicitacao'),
            url(r'^recurso/', include([
                url(r'^novo/$', views.novo_recurso, name='novo_recurso'),
                url(r'^novo/form/$', views.novo_recurso_form, name='novo_recurso_form'),
                url(r'^salvar/$', views.salvar_recurso, name='salvar_recurso'),
            ])),
            url(r'^evento/', include([
                url(r'^criar/tipo/(?P<tipo>[0-9]+)/$', views.EventoIndeferimentoCreateView.as_view(), name='evento_criar_tipo'),  # noqa: E501
                url(r'^(?P<pk>\d+)/', include([
                    url(r'^editar/$', login_required(views.EventoIndeferimentoUpdateView.as_view()), name='evento_editar'),  # noqa: E501
                ])),
            ])),
            url(r'^nucleo/(?P<nucleo_id>[0-9]+)/', include([
                url(r'^setor/(?P<setor_id>[0-9]+)/ver/$', views.ver_solicitacao, name='ver_solicitacao'),
                url(r'^avaliar/resultado/(?P<resultado>[0-9]+)$',
                    views.avaliar_solicitacao,
                    name='avaliar_solicitacao'),
                url(r'^baixar/tipo/(?P<tipo>[0-9]+)$',
                    views.baixar_solicitacao,
                    name='baixar_solicitacao'),
                url(r'^evento/', include([
                    url(r'^novo/anotacao/$',
                        views.novo_evento_anotacao_form,
                        name='novo_evento_anotacao_form'),
                    url(r'^novo/encaminhamento/$',
                        views.novo_evento_encaminhamento_form,
                        name='novo_evento_encaminhamento_form'),
                    url(r'^novo/decisao/$',
                        views.novo_evento_decisao_form,
                        name='novo_evento_decisao_form'),
                ])),
                url(r'^diligencia/', include([
                    url(r'^nova/$',
                        views.nova_diligencia_form,
                        name='nova_diligencia_form'),
                    url(r'^salvar/$',
                        views.salvar_diligencia,
                        name='salvar_diligencia'),
                ])),
            ])),
        ])),
    ])),
]
