from rest_framework import serializers

from . import models


class TermoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Termo
        fields = '__all__'


class TermoRespostaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TermoResposta
        fields = '__all__'
