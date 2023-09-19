# third-party
from rest_framework import routers

# application
from . import viewsets

router = routers.SimpleRouter()
router.register(r'honorarios', viewsets.HonorarioViewSet)
router.register(r'honorarios-alertas-de-movimentacoes', viewsets.AlertaProcessoMovimentoViewSet)
router.register(r'honorarios-analises', viewsets.AnaliseViewSet)
router.register(r'honorarios-documentos', viewsets.DocumentoViewSet)
router.register(r'honorarios-movimentos', viewsets.MovimentoViewSet)
