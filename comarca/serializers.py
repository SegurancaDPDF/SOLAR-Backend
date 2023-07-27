from rest_framework import serializers

from . import models


# padronização das rotas no apiv2
class GuicheSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Guiche
        fields = '__all__'


class PredioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Predio
        fields = '__all__'
