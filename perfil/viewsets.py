# third-party
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# project
from contrib.models import Defensoria
from core.serializers import GenericSerializer
from defensor.models import Defensor

# application
from . import serializers
from . import services

# retorna uma lista de menus do usuário autenticado


class MenuViewSet(ViewSet):

    @swagger_auto_schema(responses={200: serializers.UsuarioMenusSerializer(many=True)})
    def list(self, request):

        serializer = serializers.UsuarioMenusSerializer({
            'usuario': request.user,
            'menus': services.MenuService(request.user).gerar()
        })

        return Response(serializer.data)

# retorna as permissões do usuário autenticado


class PermissaoViewSet(ViewSet):

    @swagger_auto_schema(responses={200: serializers.UsuarioPermissoesSerializer})
    def list(self, request):

        serializer = serializers.UsuarioPermissoesSerializer({
            'usuario': request.user,
            'permissoes': sorted(request.user.get_all_permissions())
        })

        return Response(serializer.data)

# retornar o queryset adequado com base no tipo de usuário autenticado


class PerfilDefensoriaViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = GenericSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Defensoria.objects.all()
        else:
            return self.request.user.servidor.defensor.defensorias


class PerfilSupervisoresViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = GenericSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Defensor.objects.filter(eh_defensor=True)
        else:
            return self.request.user.servidor.defensor.lista_supervisores
