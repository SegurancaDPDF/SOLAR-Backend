# third-party
from rest_framework import routers

# application
from . import viewsets

router = routers.SimpleRouter()
router.register(r'propacs', viewsets.ProcedimentoViewSet)
router.register(r'propacs-documentos', viewsets.DocumentoPropacViewSet)
router.register(r'propacs-eventos', viewsets.MovimentoViewSet)
router.register(r'propacs-situacoes', viewsets.SituacaoProcedimentoViewSet)
router.register(r'propacs-tipos-documento', viewsets.TipoAnexoDocumentoPropacViewSet)
router.register(r'propacs-tipos-evento', viewsets.MovimentoTipoViewSet)
