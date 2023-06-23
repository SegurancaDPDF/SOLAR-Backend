# standard
import json
from django.db import transaction

# third-party
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

# project
from api.api_v1.serializers import ServidorBasicSerializer
from core.serializers import GenericSerializer

# application
from . import models


class AtuacaoDocumentoSerializer(serializers.ModelSerializer):
    tipo_str = serializers.SerializerMethodField()

    class Meta:
        model = models.Documento
        fields = '__all__'
        ref_name = 'AtuacaoDocumento'
        # https://stackoverflow.com/questions/27858184/nested-field-serializer-data-missing
        # Necessário para atualizar existente em vez de criar novo ao salvar via AtuacaoSerializer
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
        }

    def get_tipo_str(self, obj):
        return obj.get_tipo_display()


class AtuacaoSerializer(serializers.ModelSerializer):
    # Atenção! Por causa dos microsegundos (999999) a formatação AngularJS mostra o dia seguinte, usar máscara abaixo
    data_inicial = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    data_final = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")

    defensoria = GenericSerializer()
    defensor = GenericSerializer()
    usuario = serializers.IntegerField(source='defensor.servidor.usuario_id', read_only=True)
    titular = GenericSerializer()
    cargo = GenericSerializer()
    documento = AtuacaoDocumentoSerializer()
    cadastrado_por = ServidorBasicSerializer()
    excluido_por = ServidorBasicSerializer()

    class Meta:
        model = models.Atuacao
        fields = '__all__'

    def update(self, instance, validated_data):

        # Obtém dados enviados do documento relacionado e cria/atualiza
        try:
            documento_data = validated_data.pop('documento')
        except Exception:
            documento_data = json.loads(self.context['request'].POST.get('documento'))

        documento, _ = models.AtuacaoDocumento.objects.update_or_create(
            id=documento_data.get('id'),
            defaults=documento_data
        )

        # Vincula documento criado/atualizado ao registro
        instance.documento = documento

        return super(AtuacaoSerializer, self).update(instance, validated_data)


class AtuacaoCreateSerializer(serializers.ModelSerializer):
    defensor = GenericSerializer(required=False)

    class Meta:
        model = models.Atuacao
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        validated_data['tipo'] = models.Atuacao.TIPO_LOTACAO
        defensor_id = validated_data['defensor']['id']
        defensoria_id = validated_data['defensoria'].id
        defensor = models.Defensor.objects.get(servidor=defensor_id)
        validated_data['defensor'] = defensor
        verificar_lotacao_cadastrada = models.Atuacao.objects.filter(
            defensoria=defensoria_id,
            defensor__servidor=defensor_id,
            ativo=True,
            tipo=validated_data['tipo']
        ).count()
        if verificar_lotacao_cadastrada >= 1:
            raise serializers.ValidationError({'defensoria': ["Já existe esta defensoria cadastrada"]})
        resultado = models.Atuacao.objects.create(**validated_data)
        return resultado


class DefensorAtuacaoSerializer(serializers.ModelSerializer):
    # Atenção! Por causa dos microsegundos (999999) a formatação AngularJS mostra o dia seguinte, usar máscara abaixo
    data_inicial = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    data_final = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    defensoria = GenericSerializer()
    titular = GenericSerializer()
    documento = AtuacaoDocumentoSerializer()

    class Meta:
        model = models.Atuacao
        fields = ('id', 'tipo', 'data_inicial', 'data_final', 'defensoria', 'titular', 'documento')


class DefensorSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField()
    usuario = serializers.SerializerMethodField()
    atuacoes = serializers.SerializerMethodField()
    cpf = serializers.CharField(source='servidor.cpf')

    class Meta:
        model = models.Defensor
        fields = ('id', 'nome', 'cpf', 'servidor', 'usuario', 'supervisor', 'atuacoes',
                  'data_expiracao_credenciais_mni', 'credenciais_expiradas', 'ativo')

    def get_nome(self, obj):
        return obj.servidor.nome

    def get_usuario(self, obj):
        return obj.servidor.usuario_id

    @swagger_serializer_method(serializer_or_field=DefensorAtuacaoSerializer(many=True))
    def get_atuacoes(self, obj):
        incluir_atuacoes = self.context['request'].query_params.get('incluir_atuacoes')

        if incluir_atuacoes == 'true':
            atuacoes = obj.all_atuacoes.all()  # DefensorViewSet.Prefetch
            return DefensorAtuacaoSerializer(instance=atuacoes, many=True).data
        else:
            return None


class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Documento
        fields = '__all__'
        ref_name = 'DefensorDocumento'


class EditalConcorrenciaPlantaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EditalConcorrenciaPlantao
        fields = '__all__'


class VagaEditalPlantaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.VagaEditalPlantao
        fields = '__all__'
