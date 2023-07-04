# third-party
from rest_framework import routers

# application
from . import viewsets

router = routers.SimpleRouter()

router.register(r'core-classes', viewsets.ClasseViewSet)
router.register(r'core-documentos', viewsets.DocumentoViewSet)
router.register(r'core-eventos', viewsets.EventoViewSet)
router.register(r'core-modelos-documento', viewsets.ModeloDocumentoViewSet)
router.register(r'core-partes', viewsets.ParteViewSet)
router.register(r'core-processos', viewsets.ProcessoViewSet)
router.register(r'core-tipos-documento', viewsets.TipoDocumentoViewSet)
router.register(r'core-tipos-evento', viewsets.TipoEventoViewSet)
