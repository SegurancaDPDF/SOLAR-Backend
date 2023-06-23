# third-party
from rest_framework import routers

# application
from . import viewsets

router = routers.SimpleRouter()
router.register(r'termos', viewsets.TermoViewSet)
router.register(r'termos-respostas', viewsets.TermoRespostaViewSet)
