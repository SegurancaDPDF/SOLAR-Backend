# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from django.conf import settings
from django.conf.urls import url
from rest_framework import permissions
from rest_framework.routers import Route, SimpleRouter
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_extensions.routers import ExtendedSimpleRouter
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from procapi_client.views import (
    ProcapiCompetenciaViewSet,
    ProcapiAvisoViewSet,
    ProcapiAssuntoViewSet,
    ProcapiClasseViewSet,
    ProcapiSignalAvisoViewSet,
    ProcapiSignalProcessoViewSet,
    ProcapiSignalManifestacaoViewSet
)

from atendimento.atendimento.urls import router_atendimento
from atendimento.atendimento.views import DocumentoAtendimentoGedViewSet
from authsolar.viewsets import CustomAuthToken
from contrib import viewsets as views_contrib
from defensor import viewsets as views_defensor
from propac.urls import router_propac

from . import views

# gera a visualização da documentação da API usando Swagger e Redoc
schema_view = get_schema_view(
    openapi.Info(
        title="SOLAR API",
        default_version='v1',
        description="Solução Avançada em Atendimento de Refererência (SOLAR)",
        contact=openapi.Contact(email=settings.DEFAULT_FROM_EMAIL),
    ),
    public=False,
    permission_classes=[permissions.AllowAny],
)


# adicionar uma rota personalizada ao roteador, especificando um URL e um
# mapeamento para um método de visualização.
class CustomExtendedSimpleRouter(SimpleRouter):
    routes = [
        Route(
            url=r'^atendimentos/{lookup}/{prefix}/$',
            mapping={
                'get': 'list',
            },
            name='{basename}-list',
            detail=True,
            initkwargs={'suffix': 'List'}
        ),
    ]


custom_router = CustomExtendedSimpleRouter()

router = ExtendedSimpleRouter()
# Cada registro especifica um URL, uma classe de visualização correspondente e,
# opcionalmente, um nome de base para a rota
router.register(r'anotacoes', views.AnotacaoViewSet, 'atendimento')
router.register(r'areas', views.AreaViewSet, 'area')
router.register(r'atividades-extraordinarias', views.AtividadeExtraordinariaViewSet)
router.register(r'atuacoes', views_defensor.AtuacaoViewSetV1)
router.register(r'bairros', views.BairroViewSet)
router.register(r'cartorios', views.CartorioViewSet)
router.register(r'categorias-de-agendas', views.CategoriaDeAgendaViewSet)
router.register(r'defensorias-etiquetas', views.DefensoriaEtiquetaViewSet)
router.register(r'comarcas', views.ComarcaViewSet)
router.register(r'estados', views.EstadoViewSet)
router.register(r'etiquetas', views.EtiquetaViewSet)
router.register(r'formas-atendimento', views.FormaAtendimentoViewSet)
router.register(r'tipos-documento', views.ContribDocumentoViewSet)
router.register(r'defensores', views_defensor.DefensorViewSet)
router.register(r'defensorias', views_contrib.DefensoriaViewSet)
router.register(r'periodic-tasks', views.PeriodicTaskViewSet, basename='periodic-tasks')
router.register(r'qualificacoes', views.QualificacaoViewSet)
router.register(r'servidores', views.ServidorViewSet)
router.register(r'settings', views.SettingViewSet, basename='settings')

router.register(r'estabelecimentos-penais', views.EstabelecimentoPenalViewSet)
router.register(r'formularios-respostas', views.FormularioRespostaViewSet)

router.register(r'telefones', views.TelefoneViewSet)

router.register(r'perguntas', views.PerguntaViewSet)
router.register(r'encaminhamentos', views.EncaminhamentoViewSet)
router.register(r'situacoes', views.SituacaoViewSet)
router.register(r'tipos-renda', views.TipoRendaViewSet)

# definição de URL'S para várias funcionalidades
processos_pendentes_router = router.register(
    r'processos_atualizacao_pendentes',
    views.ProcessoComAtualizacaoPendentesReadOnlyViewSet,
    'processo_pentente'
)

atendimento_router = router.register(
    r'atendimentos',
    views.AtendimentoViewSet,
    basename='atendimento'
)
atendimento_router.register(
    r'documento-online',
    DocumentoAtendimentoGedViewSet,
    basename='documento-online',
    parents_query_lookups=['atendimento__numero']
)

atendimento_router.register(
    r'documentos',
    views.DocumentosAtendimentoViewSet,
    basename='atendimentos-documento',
    parents_query_lookups=['atendimento__numero']
)

atendimento_router.register(
    r'tarefas',
    views.TarefasAtendimentoViewSet,
    basename='atendimentos-tarefa',
    parents_query_lookups=['atendimento__numero']
)

atendimento_router.register(
    r'assistidos',
    views.PessoaAssistidaViewSet,
    basename='atendimentos-assistido',
    parents_query_lookups=['atendimentos__atendimento__numero']
)

assistido_router = router.register(
    r'pessoasassistidas',
    views.PessoaAssistidaViewSet,
    basename='pessoaassistida'
)

assistido_router.register(
    r'atendimentos',
    views.ReadOnlyAtendimentosPessoaAssistida,
    basename='pessoaassistida-atendimento',
    parents_query_lookups=['partes__pessoa']
)

processos_atendimento_router = custom_router.register(
    r'processos',
    views.ProcessosAtendimentoViewSet,
    basename='processos-atendimento'
)

manifestacao_processual_router = router.register(
    r'manifestacao_processual',
    views.ManifestacaoProcessualViewSet,
    basename='manifestacao-processual'
)

manifestacao_processual_router.register(
    r'documentos',
    views.ManifestacaoProcessualDocumentosViewSet,
    basename='manifestacao-processual-documentos',
    parents_query_lookups=['manifestacao_id']

)

procapi_competencias = router.register(
    r'procapi/competencias',
    ProcapiCompetenciaViewSet,
    basename='procapi-competencias'
)

procapi_classes = router.register(
    r'procapi/classes',
    ProcapiClasseViewSet,
    basename='procapi-classes'
)

procapi_assuntos = router.register(
    r'procapi/assuntos',
    ProcapiAssuntoViewSet,
    basename='procapi-assuntos'
)

procapi_assuntos = router.register(
    r'procapi/avisos',
    ProcapiAvisoViewSet,
    basename='procapi-avisos'
)

procapi_signal_processo = router.register(
    'procapi/notificar_processo_criado_ou_atualizado',
    ProcapiSignalProcessoViewSet,
    basename='procapi_signal_processo'
)

procapi_signal_manifestacao = router.register(
    'procapi/notificar_manifestacao_protocolada',
    ProcapiSignalManifestacaoViewSet,
    basename='procapi_signal_manifestacao'
)

procapi_signal_aviso = router.register(
    'procapi/notificar_aviso_criado',
    ProcapiSignalAvisoViewSet,
    basename='procapi_signal_aviso'
)


urlpatterns = [
    url(r'^$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    url(r'^get_auth_token/$', CustomAuthToken.as_view(), name='get_auth_token'),

    url(r'^partesatendimentos/$', views.PessoaList.as_view(), name='pessoa-list'),
    url(r'^partesatendimentos/(?P<pk>[0-9]+)/$', views.PessoaDetail.as_view(), name='pessoa-detail'),

    url(r'^enderecos/$', views.EnderecoList.as_view(), name='endereco-list'),
    url(r'^enderecos/(?P<pk>[0-9]+)/$', views.EnderecoDetail.as_view(), name='endereco-detail'),

    url(r'^municipios/$', views.MunicipioList.as_view(), name='municipio-list'),
    url(r'^municipios/(?P<pk>[0-9]+)/$', views.MunicipioDetail.as_view(), name='municipio-detail'),

    url(r'^defensorias/(?P<id>[0-9]+)/horarios/$', views.HorarioDisponivelParaAgendamentoDefensoriaAPIView.as_view({'get': 'retrieve'}), name='defensoria-horarios'),  # noqa: E501

    url(r'^agendamentos/(?P<numero>[0-9]+)/horarios/$', views.HorarioDisponivelParaAgendamentoAoAtendimentoAPIView.as_view({'get': 'retrieve'}), name='agendamento-horario'),  # noqa: E501
    url(r'^agendamentos/(?P<numero_inicial>[0-9]+)/arvore/$', views.AgendamentoArvoreAPIView.as_view(), name='agendamento-arvore'),  # noqa: E501

    url(r'^agendamentos/(?P<numero>[0-9]+)/marcarretorno/$', views.NovoAgendamentoRetornoViewSet.as_view({'post': 'create'}), name='agendamento-marcarretorno'),  # noqa: E501
    url(r'agendamentos/(?P<numero>[0-9]+)/salvareliberaratendimento/$', views.SalvarLiberarAgendamentoViewSet.as_view({'post': 'update'}), name='agendamento-salvar-liberar'),  # noqa: E501
    url(r'^agendamentos/marcarinicial/$', views.NovoAgendamentoInicialViewSet.as_view({'post': 'create'}), name='agendamento-marcarinicial'),  # noqa: E501

    url(r'^indeferimentos/$', views.IndeferimentoList.as_view(), name='indeferimento'),
    url(r'^indeferimentos/prateleiras/$', views.IndeferimentoPrateleiraList.as_view(), name='indeferimento-prateleira'),

    url(r'^edefensor/gera-token/$', views.GeraTokenChatEdefensor.as_view(), name='gera-token-edefensor'),
    url(r'^edefensor/renova-token/$', views.RenovaTokenChatEdefensor.as_view(), name='renova-token-edefensor'),
    url(r'^edefensor/possiveis-conversas-chat/$', views.PossiveisConversasChat.as_view({'get': 'retrieve'}), name='possiveis-conversas'),  # noqa: E501

    url(r'^atendimentos/tipos-coletividade/$', views.AtendimentoTipoColetividadeList.as_view(), name='atendimentos-tipos-coletividade'),  # noqa: E501
    url(r'^atendimentos/com-documento-pendente/(?P<defensor_id>[0-9]+)/$', views.AtendimentosComDocumentoPendente.as_view({'get': 'retrieve'}), name='atendimentos-com-documento-pendente'),  # noqa: E501

    url(r'^pessoasassistidas/por-ids/$', views.PessoasAssistidasPorListaIdsList.as_view(), name='assistidos-por-ids'),
    url(r'^pessoasassistidas/patrimonios-tipos/$', views.PessoaAssistidaPatrimonioTipoList.as_view(), name='assistidos-patrimonios-tipos'),  # noqa: E501
    url(r'^pessoasassistidas/(?P<pk>[0-9]+)/patrimonios/$', views.PessoaAssistidaPatrimonioList.as_view(), name='assistidos-patrimonios'),  # noqa: E501

    url(r'^adesao-luna-chatbot/(?P<pk>[0-9]+)/cadastrar/$', views.AderirLunaChatBotViewSet.as_view({'post': 'subscribe'}), name='adesao-luna-chatbot-cadastrar'),  # noqa: E501
    url(r'^adesao-luna-chatbot/(?P<pk>[0-9]+)/descadastrar/$', views.AderirLunaChatBotViewSet.as_view({'post': 'unsubscribe'}), name='adesao-luna-chatbot-descadastrar'),  # noqa: E501
]

urlpatterns += router.urls
urlpatterns += router_propac.urls
urlpatterns += router_atendimento.urls
urlpatterns += custom_router.urls
urlpatterns = format_suffix_patterns(urlpatterns)
