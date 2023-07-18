# third-party
from rest_framework import routers

# application
from . import viewsets

# defini as rotas da API

router = routers.SimpleRouter()
router.register(r'menus', viewsets.MenuViewSet, basename='menu')
router.register(r'perfil/defensorias', viewsets.PerfilDefensoriaViewSet, basename='perfil')
router.register(r'perfil/supervisores', viewsets.PerfilSupervisoresViewSet, basename='perfil')
router.register(r'permissoes', viewsets.PermissaoViewSet, basename='permissao')
