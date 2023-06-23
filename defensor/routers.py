# third-party
from rest_framework import routers

# application
from . import viewsets

router = routers.SimpleRouter()
router.register(r'atuacoes', viewsets.AtuacaoViewSetV2)
router.register(r'atuacoes-documentos', viewsets.DocumentoViewSet)
router.register(r'defensores', viewsets.DefensorViewSet)
router.register(r'editais-concorrencia-plantao', viewsets.EditalConcorrenciaPlantaoViewSet)
router.register(r'vagas-edital-plantao', viewsets.VagaEditalPlantaoViewSet)
