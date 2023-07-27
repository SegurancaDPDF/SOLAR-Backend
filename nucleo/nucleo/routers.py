# third-party
from rest_framework import routers

# application
from . import viewsets

router = routers.SimpleRouter()
router.register(r'formularios', viewsets.FormularioViewSet)
router.register(r'formularios-perguntas', viewsets.PerguntaViewSet)
router.register(r'formularios-respostas', viewsets.RespostaViewSet)
router.register(r'nucleos', viewsets.NucleoViewSet)
