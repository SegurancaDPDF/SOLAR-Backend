# third-party
from rest_framework import serializers

# application
from . import models


# define campos comuns a várias classes de serializers
class GenericSerializer(serializers.Serializer):
    id = serializers.IntegerField()  # define o campo "id" como um IntegerField
    nome = serializers.SerializerMethodField()  # define o campo "nome" como um SerializerMethodField

    def get_nome(self, obj):
        return None if obj is None else obj.__str__()


# serializer para o model classe
class ClasseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Classe
        fields = '__all__'


# serializer para o model documento
class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Documento
        fields = '__all__'
        ref_name = 'CoreDocumento'  # define o nome de referencia para o serializer como CoreDocumento


# serializer para o model evento
class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Evento
        fields = '__all__'
        ref_name = 'CoreEvento'  # define o nome de referencia para o serializer como CoreEvento


# serializer para o model modelodocumento
class ModeloDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModeloDocumento
        fields = '__all__'
        ref_name = 'CoreModeloDocumento'  # define o nome de referencia para o serializer como CoreModeloDocumento


# serializer para o model parte
class ParteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Parte
        fields = '__all__'


# serializer para o model Processo
class ProcessoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Processo
        fields = '__all__'
        ref_name = 'CoreProcesso'  # define o nome de referencia para o serializer como CoreProcesso


# serializer para o model tipodocumento
class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TipoDocumento
        fields = '__all__'


# serializer para o model tipoevento
class TipoEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TipoEvento
        fields = '__all__'
