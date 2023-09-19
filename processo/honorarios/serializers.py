from rest_framework import serializers

from . import models


class AlertaProcessoMovimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AlertaProcessoMovimento
        fields = '__all__'


class AnaliseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Analise
        fields = '__all__'


class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Documento
        fields = '__all__'
        ref_name = 'HonorariosDocumento'


class HonorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Honorario
        fields = '__all__'


class MovimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Movimento
        fields = '__all__'
