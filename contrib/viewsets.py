# third-party
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import DetailSerializerMixin

# django
from django.db.models import Prefetch

# project
from core.viewsets import AuditoriaModelViewSet
from defensor.models import Atuacao

# application
from . import filters
from . import models
from . import serializers
from .mixins import (
    QuerysetSerializerMixin,
    QueryParameterSerializerMixin
)


class AreaViewSet(ModelViewSet):
    # define as operacoes CRUD para o model area / criar endpoints restantes do app contrib
    queryset = models.Area.objects.all()
    serializer_class = serializers.AreaSerializer
    permission_classes = [DjangoModelPermissions]


class AtualizacaoViewSet(ModelViewSet):
    # define as operacoes CRUD para o model atualizacao / mover viewsets para arquivos viewsets.py
    queryset = models.Atualizacao.objects.all()
    serializer_class = serializers.AtualizacaoSerializer
    permission_classes = [DjangoModelPermissions]


class BairroViewSet(ModelViewSet):
    # define as operacoes CRUD para o model bairro / criar endpoints restantes do app Contrib
    queryset = models.Bairro.objects.all()
    serializer_class = serializers.BairroSerializer
    permission_classes = [DjangoModelPermissions]


class CargoViewSet(ModelViewSet):
    # define as operacoes CRUD para o model cargo / mover viewsets para arquivos viewsets.py
    queryset = models.Cargo.objects.all()
    serializer_class = serializers.CargoSerializer
    permission_classes = [DjangoModelPermissions]


class CEPViewSet(ModelViewSet):
    # define as operacoes CRUD para o model  cep / mover viewsets para arquivos viewsets.py
    queryset = models.CEP.objects.all()
    serializer_class = serializers.CEPSerializer
    permission_classes = [DjangoModelPermissions]


class ComarcaViewSet(ModelViewSet):
    # define as operações CRUD para o model comarca
    # realiza prefetch das comarcas ativas relacionadas
    queryset = models.Comarca.objects.prefetch_related(
        Prefetch(
            'comarca_set',
            queryset=models.Comarca.objects.filter(
                ativo=True
            )
        )
    )
    serializer_class = serializers.ComarcaSerializer
    permission_classes = [DjangoModelPermissions]
    filter_class = filters.ComarcaFilter


class DefensoriaViewSet(QuerysetSerializerMixin,
                        QueryParameterSerializerMixin,
                        DetailSerializerMixin,
                        ModelViewSet):
    # define as operações CRUD para o model defensoria
    # realiza prefetch de modelos relacionados e define ordem de classificacao
    queryset = models.Defensoria.objects.select_related(
        'comarca'
    ).prefetch_related(
        'categorias_de_agendas',
        Prefetch(
            'all_atuacoes',
            queryset=Atuacao.objects.select_related(
                'titular__servidor',
                'documento'
            ).vigentes(
                ajustar_horario=False
            )
        )
    ).order_by(
        'comarca__nome', 'numero', 'nome'
    )
    serializer_class = serializers.DefensoriaSerializer
    serializer_detail_class = serializers.DefensoriaDetailSerializer
    serializer_classes = {"basico": serializers.DefensoriaBasicoSerializer}
    queryset_serializer = {
        "basico": models.Defensoria.objects.select_related(
                    "comarca"
                  ).all().order_by(
                    'comarca__nome', 'numero', 'nome'
                  )
    }
    permission_classes = [DjangoModelPermissions]
    filter_class = filters.DefensoriaFilter


class DefensoriaTipoEventoViewSet(ModelViewSet):
    # define as operações CRUD para o modelo defensoriatipoviewset
    queryset = models.DefensoriaTipoEvento.objects.all()
    serializer_class = serializers.DefensoriaTipoEventoSerializer
    permission_classes = [DjangoModelPermissions]
    filter_class = filters.DefensoriaTiposEventoFilter


class DefensoriaVaraViewSet(AuditoriaModelViewSet):
    # define as operacoes CRUD para o model defensoriavara
    # realiza prefetch de defensoriavarafilter e define serializers especificos
    queryset = models.DefensoriaVara.objects.ativos()
    serializer_class = serializers.DefensoriaVaraSerializer
    permission_classes = [DjangoModelPermissions]
    filter_class = filters.DefensoriaVaraFilter

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return serializers.DefensoriaVaraCreateSerializer
        return self.serializer_class

    @swagger_auto_schema(responses={200: serializers.DefensoriaVaraCreateSerializer()})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: serializers.DefensoriaVaraCreateSerializer()})
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: serializers.DefensoriaVaraCreateSerializer()})
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: serializers.DefensoriaVaraCreateSerializer()})
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class DeficienciaViewSet(ModelViewSet):
    # define as operacoes CRUD para o model deficiencia
    queryset = models.Deficiencia.objects.all()
    serializer_class = serializers.DeficienciaSerializer
    permission_classes = [DjangoModelPermissions]


class DocumentoViewSet(ModelViewSet):
    # define as operacoes CRUD para o model documento
    queryset = models.Documento.objects.all()
    serializer_class = serializers.DocumentoSerializer
    permission_classes = [DjangoModelPermissions]


class EnderecoViewSet(ModelViewSet):
    # define as operacoes CRUD para o model endereco
    queryset = models.Endereco.objects.all()
    serializer_class = serializers.EnderecoSerializer
    permission_classes = [DjangoModelPermissions]


class EnderecoHistoricoViewSet(ModelViewSet):
    # define as operacoes CRUD para o model enderecohistorico
    queryset = models.EnderecoHistorico.objects.all()
    serializer_class = serializers.EnderecoHistoricoSerializer
    permission_classes = [DjangoModelPermissions]


class EstadoViewSet(ModelViewSet):
    # define as operacoes CRUD para o model estado
    queryset = models.Estado.objects.all()
    serializer_class = serializers.EstadoSerializer
    permission_classes = [DjangoModelPermissions]


class EtiquetaViewSet(ModelViewSet):
    # define as operacoes CRUD para o model etiqueta
    queryset = models.Etiqueta.objects.all()
    serializer_class = serializers.EtiquetaSerializer
    permission_classes = [DjangoModelPermissions]


class HistoricoLoginViewSet(ModelViewSet):
    # define as operacoes CRUD para o model historicologin
    queryset = models.HistoricoLogin.objects.all()
    serializer_class = serializers.HistoricoLoginSerializer
    permission_classes = [DjangoModelPermissions]


class IdentidadeGeneroViewSet(ModelViewSet):
    # define as operacoes CRUD para o model identidadegenero
    queryset = models.IdentidadeGenero.objects.all()
    serializer_class = serializers.IdentidadeGeneroSerializer
    permission_classes = [DjangoModelPermissions]


class MenuExtraViewSet(ModelViewSet):
    # define as operacoes CRUD para o model menuextra
    queryset = models.MenuExtra.objects.all()
    serializer_class = serializers.MenuExtraSerializer
    permission_classes = [DjangoModelPermissions]


class MunicipioViewSet(ModelViewSet):
    # define as operacoes CRUD para o model municipio
    queryset = models.Municipio.objects.all()
    serializer_class = serializers.MunicipioSerializer
    permission_classes = [DjangoModelPermissions]


class OrientacaoSexualViewSet(ModelViewSet):
    # define as operacoes CRUD para o model orientacaosexual
    queryset = models.OrientacaoSexual.objects.all()
    serializer_class = serializers.OrientacaoSexualSerializer
    permission_classes = [DjangoModelPermissions]


class PaisViewSet(ModelViewSet):
    # define as operacoes CRUD para o model pais
    queryset = models.Pais.objects.all()
    serializer_class = serializers.PaisSerializer
    permission_classes = [DjangoModelPermissions]


class PapelViewSet(ModelViewSet):
    # define as operacoes CRUD para o model papel
    queryset = models.Papel.objects.all()
    serializer_class = serializers.PapelSerializer
    permission_classes = [DjangoModelPermissions]


class SalarioViewSet(ModelViewSet):
    # define as operacoes CRUD para o model salario
    queryset = models.Salario.objects.all()
    serializer_class = serializers.SalarioSerializer
    permission_classes = [DjangoModelPermissions]


class TelefoneViewSet(ModelViewSet):
    # define as operacoes CRUD para o model telefone
    queryset = models.Telefone.objects.all()
    serializer_class = serializers.TelefoneSerializer
    permission_classes = [DjangoModelPermissions]


class VaraViewSet(ModelViewSet):
    # define as operacoes CRUD para o model vara
    queryset = models.Vara.objects.all()
    serializer_class = serializers.VaraSerializer
    permission_classes = [DjangoModelPermissions]


class ServidorViewSet(ModelViewSet):
    # define as operacoes CRUD para o model servidor
    queryset = models.Servidor.objects.all().order_by('-ativo', '-usuario__is_superuser', 'nome')
    serializer_class = serializers.ServidorSerializer
    permission_classes = [DjangoModelPermissions]
    filter_class = filters.ServidorFilterBackend
