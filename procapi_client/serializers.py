
# third-party
from rest_framework import serializers

# application
from . import models


class CompetenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Competencia
        fields = '__all__'


class DestinatarioDistribuicaoAvisoField(serializers.Serializer):
    aviso_numero = serializers.CharField()
    defensor = serializers.CharField()
    defensoria = serializers.CharField()


class DistribuicaoAvisoSerializer(serializers.Serializer):
    objects = serializers.ListSerializer(child=DestinatarioDistribuicaoAvisoField())


class SistemaWebServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SistemaWebService
        fields = '__all__'


class PainelDeAvisoItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nome = serializers.CharField()
    total = serializers.IntegerField()


class PainelDeAvisoGrupoSerializer(serializers.Serializer):
    id = serializers.CharField()
    nome = serializers.CharField()
    total = serializers.IntegerField()
    itens = serializers.ListSerializer(child=PainelDeAvisoItemSerializer())


class PainelDeAvisoSerializer(serializers.Serializer):
    total_geral = serializers.IntegerField()
    prateleiras = serializers.ListSerializer(child=PainelDeAvisoGrupoSerializer())
