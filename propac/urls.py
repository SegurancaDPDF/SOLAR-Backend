from django.conf.urls import url
from django.urls import path
from rest_framework import routers


from .views import (
    ProcedimentoHomeView,
    PropacHomeView,
    PropacPerfilHomeView,
    PesquisarPropacProcedimentoHomeView,
    ProcedimentoDetailView,
    CadastraMovimentacaoProcedimentoView,
    CadastraRemocaoMovimentacaoView,
    AlteraSituacaoProcedimentoView,
    AlteraAssuntoProcedimentoView,
    JSONProcedimentoSearchView,
    VinculaProcedimentoAtendimentoView,
    AlteraProcedimentoView,
    DesvinculaProcedimentoAtendimentoView,
    MovimentoUpdateView,
    MovimentoTipoAutocomplete, CriarDocumentoPropac,
    CadastraProcedimentoView,
    CancelarMovimento,
    CancelarDocumentoPropac,
    ProcedimentoNovoMovimentoModalHtml,
    movimento_tarefas_view,
    TarefasPropacViewSet,
    responder_tarefa_view,
    DocumentoPropacViewset
)

# configuração das rotas do Django Rest Framework para as views relacionadas ao propac
router_propac = routers.SimpleRouter()

router_propac.register(
    r'propac-tarefas',
    TarefasPropacViewSet,
    basename='propac-tarefas'
)

router_propac.register(
    r'propac-tarefa-documento',
    DocumentoPropacViewset,
    basename='propac-tarefa-documento'
)


urlpatterns = [
    url(r'^$', ProcedimentoHomeView.as_view(), name='procedimento_index'),
    url(r'^inicio/$', PropacPerfilHomeView.as_view(), name='inicio_index'),
    url(r'^propacs/$', PropacHomeView.as_view(), name='propac_index'),
    url(r'^propacs/buscar/$', JSONProcedimentoSearchView.as_view(), name='buscar_procedimentos'),
    url(r'^propacs/vincular/$', VinculaProcedimentoAtendimentoView.as_view(), name='vincular_procedimento'),
    url(r'^propacs/desvincular/$', DesvinculaProcedimentoAtendimentoView.as_view(), name='desvincular_procedimento'),
    url(r'^pesquisar/$', PesquisarPropacProcedimentoHomeView.as_view(), name='pesquisar_index'),
    url(r'^codigo/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/$',
        ProcedimentoDetailView.as_view(),
        name='procedimento_uuid'
        ),
    url(r'^codigo/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/modal/$',
        ProcedimentoNovoMovimentoModalHtml.as_view(),
        name='procedimento_novo_movimento_modal_html'
        ),
    url(r'^codigo/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/editar/$',
        AlteraProcedimentoView.as_view(),
        name='editar_procedimento'
        ),
    url(r'^codigo/salvar/$', CadastraProcedimentoView.as_view(), name='novo_procedimento'),

    url(r'^codigo/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/movimento/salvar/$',
        CadastraMovimentacaoProcedimentoView.as_view(),
        name='procedimento_cadastrar_movimento'
        ),

    url(r'^codigo/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/movimento/(?P<pk>\d+)/remover/$',  # noqa
        CadastraRemocaoMovimentacaoView.as_view(),
        name='remove_movimento_pk'
        ),

    url(r'^codigo/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/situacao/alterar/$',
        AlteraSituacaoProcedimentoView.as_view(),
        name='procedimento_altera_situacao'
        ),

    url(r'^codigo/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/assunto/alterar/$',
        AlteraAssuntoProcedimentoView.as_view(),
        name='procedimento_altera_assunto'
        ),

    url(r'^codigo/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/movimento/(?P<pk>[0-9]+)/editar_movimento/$',  # noqa
        MovimentoUpdateView.as_view(),
        name='editar_movimento'
        ),
    url(r'^codigo/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/movimento/(?P<pk>[0-9]+)/tarefas/$',  # noqa
        movimento_tarefas_view,
        name='movimento_tarefas'
        ),
    url(r'^codigo/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/movimento/(?P<pk>[0-9]+)/criar_documento_propac/$',  # noqa
        CriarDocumentoPropac.as_view(),
        name='procedimento_criar_documento_propac'
        ),

    url(r'^codigo/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/movimento/(?P<pk>[0-9]+)/cancelar_movimento/$',  # noqa
        CancelarMovimento.as_view(),
        name='cancelar_movimento'
        ),

    url(r'^codigo/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/movimento/(?P<pk_movimento>[0-9]+)/cancelar_documentopropac/(?P<pk_docpropac>[0-9]+)/$',  # noqa
        CancelarDocumentoPropac.as_view(),
        name='cancelar_documentopropac'
        ),

    url(r'^codigo/movimento/tipo_autocomplete/$',
        MovimentoTipoAutocomplete.as_view(),
        name='procedimento_movimento_tipo_autocomplete'
        ),
    path(r'propac/tarefas/responder/',
         responder_tarefa_view,
         name='propac_tarefa_responder'
         ),
]
