# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from rest_framework import serializers

from . import models


# classe de serializador para o modelo ProcessoApenso
class ProcessoApensoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProcessoApenso
        fields = '__all__'


# classe de serializador para o modelo Acao
class AcaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Acao
        fields = '__all__'


# classe de serializador para o modelo Assunto
class AssuntoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Assunto
        fields = '__all__'
        ref_name = 'ProcessosAssuntos'


# classe de serializador para o modelo Audiencia
class AudienciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Audiencia
        fields = '__all__'


# classe de serializador para o modelo ManifestacaoAviso
class ManifestacaoAvisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ManifestacaoAviso
        fields = '__all__'


# classe de serializador para o modelo DocumentoFase
class DocumentoFaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocumentoFase
        fields = '__all__'


# classe de serializador para o modelo ManifestacaoDocumento
class ManifestacaoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ManifestacaoDocumento
        fields = '__all__'


# classe de serializador para o modelo Fase
class FaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Fase
        fields = '__all__'


# classe de serializador para o modelo ParteHistoricoTransferencia
class ParteHistoricoTransferenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ParteHistoricoTransferencia
        fields = '__all__'


# classe de serializador para o modelo Manifestacao
class ManifestacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Manifestacao
        fields = '__all__'


# classe de serializador para o modelo OutroParametro
class OutroParametroSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OutroParametro
        fields = '__all__'


# classe de serializador para o modelo Parte
class ParteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Parte
        fields = '__all__'
        ref_name = 'ParteProcesso'


# classe de serializador para o modelo Prioridade
class PrioridadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Prioridade
        fields = '__all__'
        ref_name = 'ParteProcesso'


# classe de serializador para o modelo ProcessoPoloDestinatario
class ProcessoPoloDestinatarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProcessoPoloDestinatario
        fields = '__all__'


# classe de serializador para o modelo Processo
class ProcessoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Processo
        fields = '__all__'
        ref_name = 'Processo'


# classe de serializador para o modelo DocumentoTipo
class DocumentoTipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocumentoTipo
        fields = '__all__'


# classe de serializador para o modelo FaseTipo.
class FaseTipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FaseTipo
        fields = '__all__'
