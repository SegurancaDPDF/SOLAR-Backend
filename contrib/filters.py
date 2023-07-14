# third-party
import coreapi  
from django_filters import FilterSet, BooleanFilter, CharFilter, ModelChoiceFilter, BaseInFilter, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend

# project
from defensor.models import Defensor

# application
from . import models


class BairroFilterBackend(DjangoFilterBackend):  # adiciona recursos de filtragem para os campos nome e municipio
    class Meta:
        model = models.Bairro

    def get_schema_fields(self, view):
        fields = super(BairroFilterBackend, self).get_schema_fields(view)
        f = [
            coreapi.Field(
                name="nome",
                description='Nome',
                required=False,
                location='query',
                type='string'),
            coreapi.Field(
                name="municipio",
                description='Código IBGE do Município',
                required=False,
                location='query',
                type='integer'
            ),
        ]

        fields.extend(f)
        return fields


class ComarcaFilter(FilterSet):  # inclui filtros para os campos eh_coordenadoria e incluir_filhos 
    eh_coordenadoria = BooleanFilter(field_name='coordenadoria', lookup_expr='isnull', label='É coordenadoria?')
    incluir_filhos = BooleanFilter(method='get_incluir_filhos', label='Incluir filhos?')

    class Meta:
        model = models.Comarca
        fields = ('eh_coordenadoria', 'ativo',)

    def get_incluir_filhos(self, queryset, name, value):  
        return queryset


class DefensoriaFilter(FilterSet):  # conjunto de filtros para o model defensoria
    defensor = ModelChoiceFilter(method='get_defensor', label="Defensor", queryset=Defensor.objects.ativos())
    eh_itinerante = BooleanFilter(field_name='nucleo__itinerante', label='É itinerante?')
    incluir_atuacoes = BooleanFilter(method='get_incluir_atuacoes', label='Incluir atuações vigentes?')
    incluir_categorias = BooleanFilter(method='get_incluir_categorias', label='Incluir categorias de agendas?')
    nome = CharFilter(field_name='nome', lookup_expr='icontains')
    serializer = BooleanFilter(method='get_serializer')

    class Meta:
        model = models.Defensoria
        fields = ('nome', 'numero', 'comarca', 'eh_itinerante', 'incluir_atuacoes', 'incluir_categorias', 'ativo')

    def get_defensor(self, queryset, name, value):
        defensorias = set(value.all_atuacoes.ativos().defensorias())
        return queryset.filter(id__in=defensorias)

    def get_incluir_atuacoes(self, queryset, name, value):
        return queryset

    def get_incluir_categorias(self, queryset, name, value):
        return queryset

    def get_serializer(self, queryset, name, value):
        return queryset


class DefensoriaEtiquetaFilter(FilterSet):  # conjunto de filtros para o modelo DefensoriaEtiqueta
    defensorias = CharFilter(method='get_defensorias', label="IDs das Defensorias separados por vírgula")

    class Meta:
        model = models.DefensoriaEtiqueta
        fields = ('defensorias',)

    def get_defensorias(self, queryset, name, value):
        ids = value.split(',')
        return queryset.filter(defensoria__in=ids)


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class DefensoriaTiposEventoFilter(FilterSet):  # conjunto de filtros para o modelo DefensoriaTipoEvent
    defensoria = NumberInFilter(field_name='defensoria__id', lookup_expr='in')

    class Meta:
        model = models.DefensoriaTipoEvento
        fields = ('defensoria', 'tipo_evento')


class DefensoriaVaraFilter(FilterSet):  # conjunto de filtros para o modelo DefensoriaVara

    class Meta:
        model = models.DefensoriaVara
        fields = ('defensoria', 'vara', 'paridade')


class DocumentoFilterBackend(DjangoFilterBackend):  # adiciona recursos de filtragem para os campos
    class Meta:
        model = models.Documento

    def get_schema_fields(self, view):
        fields = super(DocumentoFilterBackend, self).get_schema_fields(view)
        f = [
            coreapi.Field(
                name="exibir_em_documento_assistido",
                description='Exibir em Documento do Assistido?',
                required=False, location='query', type='boolean'
            ),
            coreapi.Field(
                name="exibir_em_documento_atendimento",
                description='Exibir em Documento do Atendimento?',
                required=False, location='query', type='boolean'
            ),
            coreapi.Field(
                name="ativo",
                description='Ativo?',
                required=False, location='query', type='boolean'
            ),
        ]

        fields.extend(f)
        return fields


class MunicipioFilterBackend(DjangoFilterBackend):  # adiciona recursos de filtragem para os campos nome e estado
    class Meta:
        model = models.Municipio

    def get_schema_fields(self, view):
        fields = super(MunicipioFilterBackend, self).get_schema_fields(view)
        f = [
            coreapi.Field(
                name="nome",
                description='Nome',
                required=False,
                location='query',
                type='string'),
            coreapi.Field(
                name="estado",
                description='Código IBGE do Estado',
                required=False,
                location='query',
                type='integer'
            ),
        ]

        fields.extend(f)
        return fields


class ServidorFilterBackend(FilterSet):  # conjunto de filtros para o model Servidor
    cpf = CharFilter(lookup_expr='icontains')
    comarca = CharFilter(field_name='comarca__id')
    papel = CharFilter(field_name='papel__id')
    nome = CharFilter(lookup_expr='icontains')
    matricula = CharFilter(lookup_expr='iexact')

    class Meta:
        model = models.Servidor
        fields = ['id', 'cpf', 'comarca', 'nome', 'papel', 'matricula']


class DefensoriaFilterBackend(DjangoFilterBackend):  # adiciona recursos de filtragem para o campo apenas_itinerante
    class Meta:
        model = models.Defensoria

    def get_schema_fields(self, view):
        fields = super(DefensoriaFilterBackend, self).get_schema_fields(view)
        f = [
            coreapi.Field(
                name="apenas_itinerante",
                description='(opcional) true: apenas defensorias itinerante; false: retorna todos os registros',
                required=False,
                location='query',
                type='boolean'
            ),
        ]

        fields.extend(f)
        return fields


class ServidorFilter(FilterSet):  # conjunto de filtros para o model Servidor
    class Meta:
        model = models.Servidor
        fields = ('papel', 'comarca', 'cpf', 'uso_interno', 'ativo')
