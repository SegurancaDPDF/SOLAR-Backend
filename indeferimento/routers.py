# third-party
from rest_framework import routers

# application
from . import viewsets

router = routers.SimpleRouter()
router.register(r'indeferimentos', viewsets.IndeferimentoViewSet)
