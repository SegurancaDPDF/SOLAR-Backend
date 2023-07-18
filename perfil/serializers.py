# third-party
from rest_framework import serializers

from authsolar.serializers import UsuarioSerializer

# função para definir os serializadores relacionados à funcionalidade de menus e permissões de usuário


class SubMenuSerializer(serializers.Serializer):
    nome = serializers.CharField()
    url = serializers.URLField()
    icon = serializers.CharField()


class MenuSerializer(SubMenuSerializer):
    submenus = SubMenuSerializer(many=True, required=False)


class UsuarioMenusSerializer(serializers.Serializer):
    usuario = UsuarioSerializer()
    menus = MenuSerializer(many=True)


class UsuarioPermissoesSerializer(serializers.Serializer):
    usuario = UsuarioSerializer()
    permissoes = serializers.ListField(child=serializers.CharField())
