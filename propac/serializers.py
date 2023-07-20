from rest_framework import serializers
from atendimento.atendimento.models import Tarefa
from propac.models import DocumentoPropac, Movimento
from api.api_v1.serializers import (
    GenericSerializer, ServidorBasicSerializer, TarefaProcessoSerializer,
    DocumentoGEDSerializer, DocumentoSerializer, ExtraFieldsMixin)
from django.urls import reverse
from . import models


class TarefaListSerializer(serializers.ModelSerializer):  # serializer para listar tarefas com campos especificos
    setor_responsavel = GenericSerializer()
    responsavel = ServidorBasicSerializer()
    finalizado = ServidorBasicSerializer()
    respostas_total = serializers.SerializerMethodField()

    def get_respostas_total(self, obj):
        return obj.respostas.count()

    class Meta:
        fields = ('id', 'finalizado', 'prioridade', 'status', 'respostas_total',
                  'titulo', 'setor_responsavel', 'responsavel', 'data_inicial',
                  'data_final', 'atrasada', 'atendimento', 'eh_alerta',
                  'eh_cooperacao', 'eh_tarefa')
        model = Tarefa


class TarefaCreateSerializer(serializers.ModelSerializer):
    # serializer para criar uma nova tarefa
    id = serializers.ReadOnlyField(required=False)
    movimento = serializers.PrimaryKeyRelatedField(queryset=Movimento.objects.all())

    class Meta:
        fields = ("id", "movimento", "prioridade", "resposta_para", "setor_responsavel", "responsavel",
                  "processo", "titulo", "tipo", "data_inicial", "data_final", "descricao")
        model = Tarefa


class TarefaModelSerializer(ExtraFieldsMixin, serializers.ModelSerializer):
    # serializer para a visualizacao detalhada de uma tarefa
    setor_responsavel = GenericSerializer()
    tipo = GenericSerializer()
    responsavel = ServidorBasicSerializer()
    processo = TarefaProcessoSerializer()
    finalizado = ServidorBasicSerializer()
    resposta_para = GenericSerializer()
    cadastrado_por = ServidorBasicSerializer()
    documento = DocumentoSerializer()
    documentos = DocumentoGEDSerializer(many=True)

    class Meta:
        model = Tarefa
        fields = '__all__'
        extra_fields = ['atrasada', 'eh_alerta', 'eh_cooperacao', 'eh_tarefa']


class TarefaDetailSerializer(TarefaModelSerializer):
    # serializer para a visualizacao detalhada de uma tarefa
    respostas = TarefaModelSerializer(many=True)
    pode_finalizar = serializers.SerializerMethodField()

    def get_pode_finalizar(self, obj):
        return obj.pode_finalizar(self.context['request'].user)

    class Meta:
        model = Tarefa
        fields = '__all__'
        extra_fields = ['atrasada', 'eh_alerta', 'eh_cooperacao', 'eh_tarefa', 'pode_finalizar']


class DocumentoPropacSerializer(serializers.ModelSerializer):
    # serializer para o model documentopropac
    tipo_anexo_nome = serializers.SerializerMethodField()
    cancelar_doc_propac_url = serializers.SerializerMethodField()
    modo = serializers.SerializerMethodField()

    def get_modo(self, instance):
        """
        atributo/MethodField (modo) criado para se adequar ao funcionamento da tela já
        existente que lista documentos de movimento (propac)
        """
        return True if instance.anexo and instance.anexo_original_nome_arquivo else False

    def get_tipo_anexo_nome(self, instance):
        return instance.tipo_anexo.nome

    def get_cancelar_doc_propac_url(self, instance):
        kwargs = {
            'uuid': instance.movimento.procedimento.uuid,
            'pk_movimento': instance.movimento.pk,
            'pk_docpropac': instance.pk
        }

        return reverse('procedimentos:cancelar_documentopropac', kwargs=kwargs)

    class Meta:
        model = DocumentoPropac
        fields = "__all__"


# serializer para varios modelos relacionados ao propac 
class ProcedimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Procedimento
        fields = '__all__'
        ref_name = 'PropacProcedimento'


class MovimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Movimento
        fields = '__all__'
        ref_name = 'PropacMovimento'


class SituacaoProcedimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SituacaoProcedimento
        fields = '__all__'


class TipoAnexoDocumentoPropacSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TipoAnexoDocumentoPropac
        fields = '__all__'


class MovimentoTipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MovimentoTipo
        fields = '__all__'
