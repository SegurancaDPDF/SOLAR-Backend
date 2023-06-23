# third-party
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

# django
from django.conf import settings
from django.urls import include, path, re_path

# aplicacão
from aceite.routers import router as aceite_router
from assistido.routers import router as assistido_router
from atendimento.atendimento.routers import router as atendimento_router
from atividade_extraordinaria.routers import router as atividade_extraordinaria_router
from authsolar.viewsets import CustomAuthToken
from comarca.routers import router as comarca_router
from contrib.routers import router as contrib_router
from core.routers import router as core_router
from defensor.routers import router as defensor_router
from evento.routers import router as evento_router
from indeferimento.routers import router as indeferimento_router
from nucleo.itinerante.routers import router as itinerante_router
from nucleo.nadep.routers import router as nadep_router
from nucleo.nucleo.routers import router as nucleo_router
from perfil.routers import router as perfil_router
from procapi_client.routers import router as procapi_router
from processo.honorarios.routers import router as honorarios_router
from processo.processo.routers import router as processos_router
from propac.routers import router as propac_router
from relatorios.routers import router as relatorios_router

# mover router para arquivos routers
router = routers.DefaultRouter()
router.registry.extend(aceite_router.registry)
router.registry.extend(assistido_router.registry)
router.registry.extend(atendimento_router.registry)
router.registry.extend(atividade_extraordinaria_router.registry)
router.registry.extend(comarca_router.registry)
router.registry.extend(contrib_router.registry)
router.registry.extend(core_router.registry)
router.registry.extend(defensor_router.registry)
router.registry.extend(evento_router.registry)
router.registry.extend(honorarios_router.registry)
router.registry.extend(indeferimento_router.registry)
router.registry.extend(itinerante_router.registry)
router.registry.extend(nadep_router.registry)
router.registry.extend(nucleo_router.registry)
router.registry.extend(perfil_router.registry)
router.registry.extend(procapi_router.registry)
router.registry.extend(processos_router.registry)
router.registry.extend(propac_router.registry)
router.registry.extend(relatorios_router.registry)

# cria uma visualização da API usando o swagger (drf_yasg)
schema_view = get_schema_view(
    openapi.Info(
        title="SOLAR API",
        default_version='v2',
        description="Solução Avançada em Atendimento de Refererência (SOLAR)",
        contact=openapi.Contact(email=settings.DEFAULT_FROM_EMAIL),
    ),
    public=False,
    permission_classes=[permissions.AllowAny],
)

# mapeia as Url's da API
urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('get-auth-token/', CustomAuthToken.as_view()),
    path('jwt-token/get/', TokenObtainPairView.as_view()),
    path('jwt-token/refresh/', TokenRefreshView.as_view()),
    path('jwt-token/verify/', TokenVerifyView.as_view()),
    path('', include(router.urls)),
]
