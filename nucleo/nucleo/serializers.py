# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from rest_framework import serializers

from . import models


# classe de serialização para o modelo Resposta do Formulário
class FormularioRespostaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Resposta
        fields = '__all__'


# classe de serialização para o modelo Formulário
class FormularioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Formulario
        fields = '__all__'


# classe de serialização para o modelo Núcleo
class NucleoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Nucleo
        fields = '__all__'


# classe de serialização para o modelo Pergunta
class PerguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pergunta
        fields = '__all__'
        ref_name = 'FormularioPergunta'


# classe de serialização para o modelo Resposta
class RespostaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Resposta
        fields = '__all__'
