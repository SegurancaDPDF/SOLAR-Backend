# third-party
from rest_framework import routers

# application
from . import viewsets

router = routers.SimpleRouter()
router.register(r'agendas', viewsets.AgendaViewSet)
router.register(r'categorias-de-agenda', viewsets.CategoriaDeAgendaViewSet)
router.register(r'eventos', viewsets.EventoViewSet)
