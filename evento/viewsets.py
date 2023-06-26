# standard
from datetime import datetime

# third-party
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_extensions.mixins import DetailSerializerMixin

# django
from django.db.models import F, Prefetch

# application
from . import filters
from . import models
from . import serializers


# realiza operacões CRUD para a model agenda
class AgendaViewSet(DetailSerializerMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                    mixins.ListModelMixin, GenericViewSet):

    queryset = models.Agenda.objects.annotate(
        itinerante=F('atuacao__defensoria__nucleo__itinerante')
    ).select_related(
        'atuacao__defensoria__nucleo',
        'cadastrado_por__usuario',
    ).prefetch_related(
        'atuacao__defensoria__categorias_de_agendas',
        Prefetch(
            'filhos',
            queryset=models.Agenda.objects.select_related(
                'atuacao__defensoria',
            ).filter(ativo=True)
        )
    ).filter(
        data_fim__gte=datetime.today(),
        pai=None,
        ativo=True
    )
    serializer_class = serializers.AgendaSerializer
    serializer_detail_class = serializers.AgendaDetailSerializer
    permission_classes = [DjangoModelPermissions]
    filter_class = filters.AgendaFilter

    @swagger_auto_schema(responses={200: serializers.AgendaDetailSerializer()})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.excluir(excluido_por=self.request.user.servidor, excluir_filhos=True)


# remocão de routers duplicados
# operacões CRUD
class CategoriaDeAgendaViewSet(ModelViewSet):
    queryset = models.Categoria.objects.all()
    serializer_class = serializers.CategoriaDeAgendaSerializer
    permission_classes = [DjangoModelPermissions]


class EventoViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                    GenericViewSet):

    queryset = models.Evento.objects.select_related(
        'comarca',
        'defensoria',
        'categoria_de_agenda',
        'cadastrado_por__usuario',
        'autorizado_por__usuario',
    ).prefetch_related(
        Prefetch(
            'filhos',
            queryset=models.Evento.objects.select_related(
                'comarca',
                'defensoria',
                'categoria_de_agenda',
            ).filter(ativo=True)
        )
    ).filter(
        ativo=True,
        agenda=None,
        data_fim__gte=datetime.today()
    ).order_by('-data_ini')
    serializer_class = serializers.EventoSerializer
    permission_classes = [DjangoModelPermissions]
    filter_class = filters.EventoFilter
