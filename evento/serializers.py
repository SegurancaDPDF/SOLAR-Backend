# third-party
from rest_framework import serializers

# project
from authsolar.serializers import UsuarioSerializer
from contrib.models import Comarca, Defensoria
from core.serializers import GenericSerializer

# application
from . import models


# serializador para a classe AgendaFilho.
class AgendaFilhoSerializer(serializers.ModelSerializer):
    defensoria = GenericSerializer(source='atuacao.defensoria')

    class Meta:
        model = models.Agenda
        fields = ('id', 'defensoria')


# serializador para a classe Agenda
class AgendaSerializer(serializers.ModelSerializer):
    defensoria = GenericSerializer(source='atuacao.defensoria')
    data_inicial = serializers.DateField(source='data_ini')
    data_final = serializers.DateField(source='data_fim')
    cadastrado_em = serializers.DateTimeField(source='data_cadastro')
    cadastrado_por = UsuarioSerializer(source='cadastrado_por.usuario')
    filhos = AgendaFilhoSerializer(many=True)

    class Meta:
        model = models.Agenda
        fields = ('id', 'titulo', 'defensoria', 'data_inicial', 'data_final', 'cadastrado_em', 'cadastrado_por',
                  'filhos')


# adiciona um campo adicional chamado horarios à serialização.
class AgendaFilhoDetailSerializer(AgendaFilhoSerializer):
    horarios = serializers.ListField(source='get_horarios_por_categoria')

    class Meta:
        model = models.Agenda
        fields = ('id', 'defensoria', 'horarios')


# adiciona um campo adicional chamado horarios
class AgendaDetailSerializer(AgendaSerializer):
    horarios = serializers.ListField(source='get_horarios_por_categoria')
    filhos = AgendaFilhoDetailSerializer(many=True)

    class Meta:
        model = models.Agenda
        fields = ('id', 'titulo', 'defensoria', 'data_inicial', 'data_final', 'cadastrado_em', 'cadastrado_por',
                  'filhos', 'horarios')


# serializador para a classe Categoria
class CategoriaDeAgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Categoria
        fields = ('id', 'nome', 'sigla', 'eh_categoria_crc')


# serializador para validar as relações entre uma defensoria e uma categoria de agenda em um evento
class EventoFilhoSerializer(serializers.ModelSerializer):
    comarca = GenericSerializer()
    defensoria = GenericSerializer()
    categoria_de_agenda = GenericSerializer()

    class Meta:
        model = models.Evento
        fields = ('id', 'comarca', 'defensoria', 'categoria_de_agenda')


class EventoDefensoriaCategoriaSerializer(serializers.Serializer):
    defensoria = serializers.PrimaryKeyRelatedField(queryset=Defensoria.objects.ativos(), write_only=True)
    categoria = serializers.PrimaryKeyRelatedField(queryset=models.Categoria.objects.ativos(), write_only=True)

    def validate(self, attrs):
        if not attrs['defensoria'].categorias_de_agendas.filter(id=attrs['categoria'].id).exists():
            raise serializers.ValidationError({'categoria': 'A categoria não está vinculada à defensoria'})
        return attrs


# define a representação da instância do modelo Evento em formato JSON
class EventoSerializer(serializers.ModelSerializer):
    comarca = GenericSerializer(read_only=True)
    comarcas = serializers.PrimaryKeyRelatedField(queryset=Comarca.objects.ativos(), many=True, write_only=True,
                                                  required=False)
    defensoria = GenericSerializer(read_only=True)
    defensorias = serializers.PrimaryKeyRelatedField(queryset=Defensoria.objects.ativos(), many=True, write_only=True,
                                                     required=False)
    categoria_de_agenda = GenericSerializer(read_only=True)
    categorias_de_agenda = EventoDefensoriaCategoriaSerializer(many=True, write_only=True, required=False)
    data_inicial = serializers.DateField(source='data_ini')
    data_final = serializers.DateField(source='data_fim')
    cadastrado_em = serializers.DateTimeField(source='data_cadastro', read_only=True)
    cadastrado_por = UsuarioSerializer(source='cadastrado_por.usuario', read_only=True)
    filhos = EventoFilhoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Evento
        exclude = ('data_ini', 'data_fim', 'data_cadastro')
        ref_name = 'EventoEvento'

    # criar uma instância do modelo Evento com base nos dados validados
    def create(self, validated_data):

        validated_data['cadastrado_por'] = self.context['request'].user.servidor

        extra_data = self.extract_non_model_fields(validated_data)
        comarcas = extra_data['comarcas']
        defensorias = extra_data['defensorias']
        categorias_de_agenda = extra_data['categorias_de_agenda']

        if len(comarcas) > 0:
            return self.bulk_create_categoria_de_agenda(validated_data, comarcas)

        if len(defensorias) > 0:
            return self.bulk_create_defensoria(validated_data, defensorias)

        if len(categorias_de_agenda) > 0:
            return self.bulk_create_categoria_de_agenda(validated_data, categorias_de_agenda)

        return super().create(validated_data)

    # responsável por criar uma instância do modelo Evento para cada comarca fornecida
    def bulk_create_comarca(self, validated_data: dict, comarcas: dict) -> models.Evento:

        instance = None

        for comarca in comarcas[:1]:
            validated_data['comarca'] = comarca
            instance = super().create(validated_data)

        for comarca in comarcas[1:]:
            validated_data['pai'] = instance
            validated_data['comarca'] = comarca
            super().create(validated_data)

        return instance

    # itera sobre a lista de categorias de agenda e cria uma instância do modelo Evento para a primeira categoria
    def bulk_create_categoria_de_agenda(self, validated_data: dict, categorias_de_agenda: dict) -> models.Evento:

        instance = None

        for categoria in categorias_de_agenda[:1]:
            validated_data['defensoria'] = categoria['defensoria']
            validated_data['categoria_de_agenda'] = categoria['categoria']
            instance = super().create(validated_data)

        for categoria in categorias_de_agenda[1:]:
            validated_data['pai'] = instance
            validated_data['defensoria'] = categoria['defensoria']
            validated_data['categoria_de_agenda'] = categoria['categoria']
            super().create(validated_data)

        return instance

    def bulk_create_defensoria(self, validated_data: dict, defensorias: dict) -> models.Evento:

        instance = None

        for defensoria in defensorias[:1]:
            validated_data['defensoria'] = defensoria
            instance = super().create(validated_data)

        for defensoria in defensorias[1:]:
            validated_data['pai'] = instance
            validated_data['defensoria'] = defensoria
            super().create(validated_data)

        return instance

    # retorna um dicionário contendo esses campos extraídos
    def extract_non_model_fields(self, validated_data: dict) -> dict:
        return {
            'comarcas': validated_data.pop('comarcas', []),
            'defensorias': validated_data.pop('defensorias', []),
            'categorias_de_agenda': validated_data.pop('categorias_de_agenda', []),
        }
