# standard
import re

# django
from django.db.models import (
    Case,
    Count,
    F,
    IntegerField,
    Min,
    OuterRef,
    Q,
    Subquery,
    Sum,
    Value,
    When
)
from django.db.models.fields import CharField

from django_filters import (
    BaseInFilter,
    BooleanFilter,
    CharFilter,
    DateTimeFilter,
    FilterSet,
    ModelChoiceFilter,
    NumberFilter
)

# project
from contrib.models import Defensoria, Util
from contrib.utils import validar_cnpj, validar_cpf
from defensor.models import Defensor

# application
from . import models


class ManifestacaoFilter(FilterSet):
    data_inicial = DateTimeFilter(field_name='cadastrado_em', lookup_expr='gte')
    data_final = DateTimeFilter(field_name='cadastrado_em', lookup_expr='lte')
    ativo = BooleanFilter(field_name='desativado_em', lookup_expr='isnull')

    class Meta:
        model = models.Manifestacao
        fields = ('data_inicial', 'data_final', 'cadastrado_por', 'defensoria', 'situacao', 'ativo')


class ProcessoFilter(FilterSet):
    data_inicial = DateTimeFilter(field_name='fases__data_protocolo', lookup_expr='gte')
    data_final = DateTimeFilter(field_name='fases__data_protocolo', lookup_expr='lte')
    defensor = ModelChoiceFilter(method='get_defensor', label="Defensor", queryset=Defensor.objects.ativos())
    defensoria = ModelChoiceFilter(method='get_defensoria', label="Defensoria", queryset=Defensoria.objects.ativos())
    incluir_partes = BooleanFilter(method='get_incluir_partes', label='Incluir partes?')
    filtro = CharFilter(method='get_filtro', label='Nº do processo, nome ou CPF/CNPJ do assistido')

    class Meta:
        model = models.Processo
        fields = ('data_inicial', 'data_final', 'defensor', 'defensoria', 'ativo')

    def get_defensor(self, queryset, name, value: Defensor):
        return queryset.filter(parte__defensoria__in=value.defensorias)

    def get_defensoria(self, queryset, name, value: Defensoria):
        return queryset.filter(parte__defensoria=value)

    def get_incluir_partes(self, queryset, name, value):
        return queryset

    def get_filtro(self, queryset, name, value):

        filtro_texto = Util.normalize(value)
        filtro_numero = re.sub('[^0-9]', '', value)
        filtro_cpf = False

        # Verifica se número é um CPF/CNPJ válido
        if len(filtro_numero) == 11 and validar_cpf(filtro_numero):
            filtro_cpf = True
        elif len(filtro_numero) == 14 and validar_cnpj(filtro_numero):
            filtro_cpf = True

        if filtro_cpf:
            return queryset.filter(
                Q(parte__atendimento__partes__pessoa__cpf=filtro_numero) |
                Q(parte__atendimento__inicial__partes__pessoa__cpf=filtro_numero)
            )

        if filtro_numero:
            return queryset.filter(numero_puro=filtro_numero)

        # TODO: Refatorar, pesquisa muita lenta por causa do excesso de JOINs e ORs
        if len(filtro_texto) > 0:
            return queryset.filter(
                Q(parte__atendimento__partes__pessoa__nome_norm__istartswith=filtro_texto) |
                Q(parte__atendimento__partes__pessoa__nome_social__istartswith=filtro_texto) |
                Q(parte__atendimento__partes__pessoa__apelido__istartswith=filtro_texto) |
                Q(parte__atendimento__inicial__partes__pessoa__nome_norm__istartswith=filtro_texto) |
                Q(parte__atendimento__inicial__partes__pessoa__nome_social__istartswith=filtro_texto) |
                Q(parte__atendimento__inicial__partes__pessoa__apelido__istartswith=filtro_texto)
            )

        return queryset


class AudienciaFilter(FilterSet):
    data_inicial = DateTimeFilter(field_name='data_protocolo', lookup_expr='gte')
    data_final = DateTimeFilter(field_name='data_protocolo', lookup_expr='lte')
    processo = CharFilter('processo__numero_puro', lookup_expr='icontains')

    class Meta:
        model = models.Audiencia
        fields = ('data_inicial', 'data_final', 'defensor_cadastro', 'defensoria', 'processo', 'ativo')


class AcaoFilter(FilterSet):
    class Meta:
        model = models.Acao
        fields = ('judicial', 'extrajudicial', 'penal', 'inquerito', 'acao_penal', 'execucao_penal')


class AudienciaTotalFilter(FilterSet):
    ano = NumberFilter(
        field_name='data_protocolo__year',
        lookup_expr='exact',
        label="Ano das audiências",
        required=True
    )
    mes = NumberFilter(
        field_name='data_protocolo__month',
        method='get_mes',
        label="Mês das audiências",
        required=True
    )
    area_id = NumberFilter(
        field_name='processo__area_id',
        lookup_expr='exact',
        label="Área do proceso da audiência"
    )
    vara_id = BaseInFilter(
        field_name='processo__vara_id',
        lookup_expr='in',
        label="Varas do proceso da audiência"
    )
    usuario_defensor_id = NumberFilter(
        field_name='processo__parte__defensor__servidor__usuario_id'
    )

    class Meta:
        model = models.Audiencia
        fields = ['ano', 'mes', 'area_id', 'vara_id', "usuario_defensor_id"]

    def get_mes(self, queryset, name, value):
        params = {
            name: value,
        }
        return queryset.filter(**params).values('audiencia_status').annotate(
            quantidade=Sum(
                Case(
                    When(data_protocolo__month=value, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            )
        ).order_by()


class PeticaoTotalMensalFilter(FilterSet):
    usuario_defensor_id = NumberFilter(
        field_name='processo__peticao_inicial__defensor_cadastro__servidor__usuario_id',
        required=True
    )
    area_id = NumberFilter(
        field_name='processo__area_id',
        required=True
    )
    vara_id = BaseInFilter(
        field_name='processo__vara_id',
        lookup_expr='in'
    )
    ano = NumberFilter(
        field_name='processo__peticao_inicial__data_cadastro',
        lookup_expr='year',
        required=True
    )
    mes = NumberFilter(
        field_name='processo__peticao_inicial__data_cadastro',
        lookup_expr='month',
        required=True
    )

    class Meta:
        model = models.Parte
        fields = ['usuario_defensor_id', 'area_id', 'vara_id', 'ano', 'mes']

    @property
    def qs(self):
        queryset = super().qs
        area_id = self.form.cleaned_data.get('area_id')
        vara_id = self.form.cleaned_data.get('vara_id')
        usuario_id = self.form.cleaned_data.get('usuario_defensor_id')
        ano = self.form.cleaned_data.get('ano')
        mes = self.form.cleaned_data.get('mes')

        # BUG: Essa solução foi desenvolvida para obter um array da query string de multiplos parâmetros repetidos
        # Porém apresentou que muda o resultado da query quando alterna os parâmetros
        # vara_id = self.request.GET.getlist('vara_id')
        # Se a query string for separado por vírgula obter áreas pelo form.cleaned_data
        # if (len(vara_id) <= 1):
        #     vara_id = self.form.cleaned_data.get('vara_id')

        if (area_id is not None and usuario_id is not None and ano is not None and mes is not None):

            queryset_filtered = self.realizar_filtro(
                usuario_id=usuario_id,
                queryset=queryset,
                area_id=area_id,
                vara_id=vara_id,
                ano=ano,
                mes=mes
            )

            return queryset_filtered

        return queryset

    def realizar_filtro(self, queryset, area_id, vara_id, usuario_id, ano, mes):

        optional_params = {}
        if (vara_id):
            optional_params["processo__vara_id__in"] = vara_id

        queryset = queryset.filter(
            Q(
                Q(
                    processo__ativo=True,
                    processo__area_id__isnull=False,
                    processo__vara_id__isnull=False,
                    ativo=True,
                    processo__area_id=area_id,
                    processo__peticao_inicial__ativo=True,
                    processo__peticao_inicial__defensor_cadastro_id=usuario_id,
                ) &
                Q(
                    processo__peticao_inicial__data_cadastro__year=ano,
                    processo__peticao_inicial__data_cadastro__month=mes
                ) &
                Q(
                    processo__peticao_inicial__data_cadastro__year=F(
                        'processo__peticao_inicial__data_protocolo__year'
                    ),
                    processo__peticao_inicial__data_cadastro__month=F(
                        'processo__peticao_inicial__data_protocolo__month'
                    )
                )
            )
        ).filter(
            **optional_params
        ).exclude(processo__tipo=0).distinct().values(
            'id',
            'processo__id',
            'processo__area_id'
        )

        cte_primeira_parte = queryset.values('processo_id').annotate(
            parte_id_min=Min('id')
        ).values('processo_id', 'parte_id_min')

        pet_inicial = queryset.filter(
            id=Subquery(cte_primeira_parte.filter(
                processo_id=OuterRef('processo_id')).values('parte_id_min')[:area_id]
            )
        ).values(
            area_id=F('processo__area_id')
        ).annotate(
            tipo=Value('PETIÇÕES INICIAIS', output_field=CharField()),
            quantidade=Count('processo_id')
        ).order_by()

        pet_intermediaria = models.Parte.objects.filter(
            processo__area_id=area_id,
            processo__area_id__isnull=False,
            processo__vara_id__isnull=False,
            ativo=True,
            processo__ativo=True,
            data_cadastro__year=ano,
            data_cadastro__month=mes
        ).filter(
            **optional_params
        ).exclude(processo__tipo=0).filter(
            Q(
                Q(
                    Q(data_cadastro__lt='2015-04-01 00:00:00') &
                    Q(defensor_id__isnull=False) &
                    Q(defensor__servidor__usuario_id=usuario_id)
                ) |
                Q(
                    Q(data_cadastro__gte='2015-04-01 00:00:00') &
                    Q(defensor_cadastro_id__isnull=False) &
                    Q(defensor_cadastro__servidor__usuario_id=usuario_id)
                )
            ) &
            Q(
                Q(processo__peticao_inicial_id__isnull=True) |
                Q(
                    ~Q(defensor_cadastro__id=F('processo__peticao_inicial__defensor_cadastro__id')) &
                    Q(processo__peticao_inicial__defensor_cadastro_id__isnull=False)
                )
            )
        ).values(
            area_id=F('processo__area_id')
        ).annotate(
            tipo=Value('PETIÇÕES INTERMEDIÁRIAS E PARTE CONTRÁRIA', output_field=CharField()),
            quantidade=Count('id')
        ).order_by()

        return pet_inicial.union(pet_intermediaria.all())
