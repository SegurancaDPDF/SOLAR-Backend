# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.cache import cache_page
from django_js_reverse import views as django_js_reverse_views
try:
    import debug_toolbar
except ImportError:
    debug_toolbar = None

from djdocuments import djdocuments_urls

# Solar
from contrib import views as contrib_views
from authsolar import authsolar_urls
from core.views import home, index, favicon_view

urlpatterns = [
    # home
    url(r'^$', index, name='index'),
    url(r'^home/', home, name='home'),
    url(r'^favicon\.ico$', cache_page(60 * 60)(favicon_view)),

    url(r'^calcjur/', include('calc_jur.urls')),

    # autenticacao e registro
    url(r'', include(authsolar_urls)),

    # contrib app
    url(r'^busca_rapida/$', contrib_views.busca_rapida, name='busca_rapida'),
    url(r'^endereco/get_by_cep/(\d+)/$', contrib_views.get_endereco_by_cep, name='get_endereco_by_cep'),
    url(r'^estado/listar/$', contrib_views.listar_estado),
    url(r'^estado/([0-9.-]+)/municipios/$', contrib_views.listar_municipio_uf),
    url(r'^defensoria/', include([
        url(r'^buscar/$', login_required(contrib_views.DefensoriaListView.as_view()), name='defensoria_buscar'),
        url(r'^tipo-evento/associar/$',
            permission_required('contrib.change_defensoriatipoevento')(contrib_views.DefensoriaTipoEventoUpdateView.as_view()),
            name='defensoria_tipo_evento_associar'),
        url(r'^listar/$', contrib_views.listar_defensorias),
        url(r'^(?P<defensoria_id>\d+)/', include([
            url(r'^editar/$',
                permission_required('contrib.change_defensoria')(contrib_views.DefensoriaUpdateView.as_view()),
                name='defensoria_editar'),
            url(r'^get/$', contrib_views.get_defensoria),
        ])),
    ])),
    url(r'^diretoria/listar/$', contrib_views.listar_diretoria),
    url(r'^indicador_meritocracia/listar/$', contrib_views.listar_indicadores_meritocracia),
    url(r'^municipio/listar/$', contrib_views.listar_municipio),
    url(r'^municipio/([0-9.-]+)/bairros/$', contrib_views.listar_bairro),
    url(r'^municipio/([0-9.-]+)/logradouros/$', contrib_views.listar_logradouro),
    url(r'^area/listar/$', contrib_views.listar_area, name='listar_area'),
    url(r'^vara/listar/$', contrib_views.listar_vara, name='listar_vara'),
    url(r'^servidor/criar-usuario/$',
        login_required(contrib_views.CadastrarServidorView.as_view()),
        name='criar_usuario_solar'
        ),
    url(r'^servidor/consulta_servidor/$',
        login_required(contrib_views.ConsultarAthenasView.as_view()),
        name='consulta_servidor'
        ),
    url(r'^servidor/autocomplete/supervisor/$',
        login_required(contrib_views.DefensorSupervisorAutocomplete.as_view()),
        name='defensor_supervisor_autocomplete'
        ),
    url(r'^servidor/listar/$',
        login_required(contrib_views.BuscarServidorListView.as_view()),
        name='listar_servidor'
        ),
    url(r'^servidor/listar/json/$', contrib_views.listar_servidor_json, name='listar_servidor_json'),
    url(r'^servidor/lotacao/(?P<defensoria_id>\d+)/listar/json/$', contrib_views.listar_servidor_por_atuacao_json,
        name='listar_servidor_por_atuacao_json'),
    url(r'^servidor/(?P<servidor_id>\d+)/$', contrib_views.perfil_servidor, name='perfil_servidor'),
    url(r'^servidor/(?P<servidor_id>\d+)/editar/$', contrib_views.editar_servidor, name='editar_servidor'),
    url(r'^servidor/(?P<servidor_id>\d+)/lotacao/(?P<lotacao_id>\d+)/excluir/$',
        contrib_views.editar_servidor,
        name='excluir_lotacao_servidor'
        ),
    url(r'^servidor/(?P<username>[a-zA-Z0-9-\._]{1,150})/foto/$',
        contrib_views.foto_servidor_pelo_username,
        name='foto_servidor_pelo_username'
        ),
    # outros apps
    url(r'^aceite/', include('aceite.urls')),
    url(r'^atividade-extraordinaria/',
        include(('atividade_extraordinaria.urls', "atividade_extraordinaria"), namespace='atividade_extraordinaria')),
    url(r'^assistido/', include('assistido.urls')),
    url(r'^atendimento/', include('atendimento.atendimento.urls')),
    url(r'^comarca/', include('comarca.urls')),
    url(r'^contrib/', include(('core.urls', 'contrib'), namespace='contrib')),
    url(r'^core/', include(('core.urls', 'core'), namespace='core')),
    url(r'^defensor/', include('defensor.urls')),
    url(r'^estatistica/', include('estatistica.urls')),
    url(r'^evento/', include('evento.urls')),
    url(r'^ged/', include(('ged.urls', 'ged'), namespace='ged')),
    url(r'^indeferimento/', include(('indeferimento.urls', 'indeferimento'), namespace='indeferimento')),
    url(r'^nucleo/', include('nucleo.urls')),
    url(r'^painel/', include('painel.urls')),
    url(r'^perfil/', include('perfil.urls')),
    url(r'^processo/', include('processo.urls')),
    url(r'^relatorios/', include(('relatorios.urls', 'relatorios'), namespace='relatorios')),

    # Clientes API
    url(r'^procapi/', include('procapi_client.urls')),
    url(r'^livre/seeu/', include(('clients.livre_client.urls', 'livre'), namespace='livre')),

    url(r'^admin/', admin.site.urls),
    url(r'^scrapy_tj/', include('scrapy_tj.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API REST
urlpatterns += [
    url(r'^api/', include('api.urls')),
]

if settings.DEBUG:
    from django.views.defaults import bad_request, permission_denied, page_not_found, server_error
    # Este permite que as páginas de erro a ser depurado durante o desenvolvimento,
    # apenas estas url no navegador para ver como estas páginas de erro parecida.
    urlpatterns += [
        url(r'^400/$', bad_request),
        url(r'^403/$', permission_denied),
        url(r'^404/$', page_not_found),
        url(r'^500/$', server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS and settings.DEBUG_TOOLBAR and debug_toolbar:
        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]


urlpatterns = urlpatterns + [
    url(r'docs/', include((djdocuments_urls, 'documentos'),
                          namespace='documentos')),
    url(r'^captcha/',
        include('captcha.urls'),
        ),
    url(r'^jsreverse/$', django_js_reverse_views.urls_js, name='js_reverse'),
]
