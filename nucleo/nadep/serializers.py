# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from rest_framework import serializers

from . import models


class EstabelecimentoPenalSerializer(serializers.ModelSerializer):  # serializer para o modelo EstabelecimentoPenal
    class Meta:
        model = models.EstabelecimentoPenal
        fields = '__all__'


class AprisionamentoSerializer(serializers.ModelSerializer):  # serializer para o modelo Aprisionamento
    class Meta:
        model = models.Aprisionamento
        fields = '__all__'


class CalculoExecucaoPenalSerializer(serializers.ModelSerializer):  # serializer para o modelo CalculoExecucaoPenal
    class Meta:
        model = models.CalculoExecucaoPenal
        fields = '__all__'


class FaltaSerializer(serializers.ModelSerializer):  # serializer para o modelo Falta
    class Meta:
        model = models.Falta
        fields = '__all__'


class HistoricoSerializer(serializers.ModelSerializer):  # serializer para o modelo Historico
    class Meta:
        model = models.Historico
        fields = '__all__'


class InterrupcaoSerializer(serializers.ModelSerializer):  # serializer para o modelo Interrupcao
    class Meta:
        model = models.Interrupcao
        fields = '__all__'


class MotivoBaixaPrisaoSerializer(serializers.ModelSerializer):  # serializer para o modelo MotivoBaixaPrisao
    class Meta:
        model = models.MotivoBaixaPrisao
        fields = '__all__'


class MudancaRegimeSerializer(serializers.ModelSerializer):  # serializer para o modelo MudancaRegime
    class Meta:
        model = models.MudancaRegime
        fields = '__all__'


class PenaRestritivaSerializer(serializers.ModelSerializer):  # serializer para o modelo PenaRestritiva
    class Meta:
        model = models.PenaRestritiva
        fields = '__all__'


class PrisaoSerializer(serializers.ModelSerializer):  # serializer para o modelo Prisao
    class Meta:
        model = models.Prisao
        fields = '__all__'


class RemissaoSerializer(serializers.ModelSerializer):  # serializer para o modelo Remissao
    class Meta:
        model = models.Remissao
        fields = '__all__'


class RestricaoPrestacaoServicoSerializer(serializers.ModelSerializer):  # serializer para o modelo RestricaoPrestacao
    class Meta:
        model = models.RestricaoPrestacaoServico
        fields = '__all__'


class SolturaSerializer(serializers.ModelSerializer):  # serializer para o modelo Soltura
    class Meta:
        model = models.Soltura
        fields = '__all__'


class TipificacaoSerializer(serializers.ModelSerializer):  # serializer para o modelo Tipificacao
    class Meta:
        model = models.Tipificacao
        fields = '__all__'


class TipoEstabelecimentoPenalSerializer(serializers.ModelSerializer):  # serializer para o modelo TipoEstabelecimentoP
    class Meta:
        model = models.TipoEstabelecimentoPenal
        fields = '__all__'
