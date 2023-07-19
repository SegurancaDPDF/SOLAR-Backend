# third-party
from rest_framework import routers

# application
from . import viewsets

router = routers.SimpleRouter()
router.register(r'locais', viewsets.LocalViewSet)
router.register(r'relatorios', viewsets.RelatorioViewSet)
