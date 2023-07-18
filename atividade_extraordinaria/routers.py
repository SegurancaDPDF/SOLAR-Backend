# third-party
from rest_framework import routers

# application
# Cria um roteador para as APIs
from . import viewsets

router = routers.SimpleRouter()
router.register(r'tipos-atividade-extraordinaria', viewsets.AtividadeExtraordinariaTipoViewSet)
router.register(r'atividades-extraordinaria', viewsets.AtividadeExtraordinariaViewSet)
