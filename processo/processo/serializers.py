from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# django
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

# project
from atendimento.atendimento.models import Atendimento
from core.serializers import GenericSerializer

# application
from . import models


class ProcessoApensoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProcessoApenso
        fields = '__all__'


class AcaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Acao
        fields = '__all__'


class AssuntoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Assunto
        fields = '__all__'
        ref_name = 'ProcessosAssuntos'


class AudienciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Audiencia
        fields = '__all__'


class AudienciaTotalSerializer(serializers.Serializer):
    tipo = serializers.SerializerMethodField()
    quantidade = serializers.IntegerField()

    tipo_audiencia = {
        models.Audiencia.AUDIENCIA_MARCADA: "Audiência Marcada",
        models.Audiencia.AUDIENCIA_REALIZADA: "Audiência Realizada",
        models.Audiencia.AUDIENCIA_NAO_REALIZADA: "Audiência Não Realizada",
        models.Audiencia.AUDIENCIA_CANCELADA: "Audiência Cancelada"
    }

    def get_tipo(self, obj):
        return self.tipo_audiencia[obj['audiencia_status']]


class ManifestacaoAvisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ManifestacaoAviso
        fields = '__all__'


class DocumentoFaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocumentoFase
        fields = '__all__'


class ManifestacaoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ManifestacaoDocumento
        fields = '__all__'


class FaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Fase
        fields = '__all__'


class ParteHistoricoTransferenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ParteHistoricoTransferencia
        fields = '__all__'


class ManifestacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Manifestacao
        fields = '__all__'


class OutroParametroSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OutroParametro
        fields = '__all__'


class ParteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Parte
        fields = '__all__'
        ref_name = 'ParteProcesso'


class PrioridadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Prioridade
        fields = '__all__'
        ref_name = 'ParteProcesso'


class ProcessoPoloDestinatarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProcessoPoloDestinatario
        fields = '__all__'


class ProcessoParteAtendimentoSerializer(serializers.ModelSerializer):
    requerente = GenericSerializer()

    class Meta:
        model = Atendimento
        fields = ('id', 'numero', 'requerente')


class ProcessoParteSerializer(serializers.ModelSerializer):
    defensoria = GenericSerializer()
    atendimento = ProcessoParteAtendimentoSerializer()

    class Meta:
        model = models.Parte
        fields = ('id', 'parte', 'defensoria', 'atendimento')
        ref_name = 'ParteProcesso'


class ProcessoSerializer(serializers.ModelSerializer):
    comarca = GenericSerializer()
    area = GenericSerializer()
    vara = GenericSerializer()
    acao = GenericSerializer()
    partes = serializers.SerializerMethodField()

    class Meta:
        model = models.Processo
        fields = '__all__'
        ref_name = 'Processo'

    @swagger_serializer_method(serializer_or_field=ProcessoParteSerializer(many=True))
    def get_partes(self, obj):
        incluir_partes = self.context['request'].query_params.get('incluir_partes')

        if incluir_partes == 'true':
            partes = obj.parte.filter(ativo=True)
            return ProcessoParteSerializer(instance=partes, many=True).data

        return None


class PeticaoTotalMensalSerializar(serializers.Serializer):
    tipo = serializers.CharField()
    area_id = serializers.IntegerField()
    quantidade = serializers.IntegerField()


class DocumentoTipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocumentoTipo
        fields = '__all__'


class FaseTipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FaseTipo
        fields = '__all__'


class GenericSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    nome = serializers.CharField(read_only=True)
    descricao = serializers.CharField(read_only=True)
