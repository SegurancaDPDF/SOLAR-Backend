# third-party
from rest_framework import routers

# application
from . import viewsets

# Cria um roteador para gerenciar as rotas da API

router = routers.SimpleRouter()
router.register(r'avisos/distribuir', viewsets.ListDistribuirAvisosViewSet, basename='avisos')
router.register(r'avisos/painel', viewsets.PainelDeAvisosViewSet, basename='avisos')
router.register(r'sistemas-webservice', viewsets.SistemasWebServiceViewSet)
router.register(r'competencias', viewsets.CompentenciaViewSet)
