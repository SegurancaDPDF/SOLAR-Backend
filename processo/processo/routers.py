# third-party
from rest_framework import routers

# application
from . import viewsets

router = routers.SimpleRouter()
router.register(r'audiencias', viewsets.AudienciaViewSet)
router.register(r'historicos-transferencias-partes', viewsets.ParteHistoricoTransferenciaViewSet)
router.register(r'manifestacoes', viewsets.ManifestacaoViewSet)
router.register(r'manifestacoes-avisos', viewsets.ManifestacaoAvisoViewSet)
router.register(r'manifestacoes-documentos', viewsets.ManifestacaoDocumentoViewSet)
router.register(r'prioridades', viewsets.PrioridadeViewSet)
router.register(r'processos', viewsets.ProcessoViewSet)
router.register(r'processos-apensos', viewsets.ProcessoApensoViewSet)
router.register(r'processos-assuntos', viewsets.AssuntoViewSet)
router.register(r'processos-classes', viewsets.AcaoViewSet)
router.register(r'processos-documentos', viewsets.DocumentoFaseViewSet)
router.register(r'processos-eventos', viewsets.FaseViewSet)
router.register(r'processos-outros-parametros', viewsets.OutroParametroViewSet)
router.register(r'processos-partes', viewsets.ParteViewSet)
router.register(r'processos-polo-destinatario', viewsets.ProcessoPoloDestinatarioViewSet)
router.register(r'processos-tipos-documento', viewsets.DocumentoTipoViewSet)
router.register(r'processos-tipos-evento', viewsets.FaseTipoViewSet)
