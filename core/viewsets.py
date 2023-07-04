# third-party
from rest_framework.viewsets import ModelViewSet

# application
from . import models
from . import serializers
from . import filters


class AuditoriaModelViewSet(ModelViewSet):
    def perform_destroy(self, instance):
        instance.desativar(self.request.user)


class ClasseViewSet(ModelViewSet):  # define a visualizacao de conjuntos de dados para o model classe
    queryset = models.Classe.objects.all()
    serializer_class = serializers.ClasseSerializer


class DocumentoViewSet(ModelViewSet):  # define a visualizacao de conjuntos de dados para o model documento
    queryset = models.Documento.objects.all()
    serializer_class = serializers.DocumentoSerializer


class EventoViewSet(ModelViewSet):  # define a visualizacao de conjunto de dados para o model evento
    queryset = models.Evento.objects.all()
    serializer_class = serializers.EventoSerializer


class ModeloDocumentoViewSet(ModelViewSet):  # define a visualizacao de conjunto de dados para o modelo ModeloDocumento
    queryset = models.ModeloDocumento.objects.all()
    serializer_class = serializers.ModeloDocumentoSerializer


class ParteViewSet(ModelViewSet):
    queryset = models.Parte.objects.all()
    serializer_class = serializers.ParteSerializer


class ProcessoViewSet(ModelViewSet):
    queryset = models.Processo.objects.all()
    serializer_class = serializers.ProcessoSerializer


class TipoDocumentoViewSet(ModelViewSet):
    queryset = models.TipoDocumento.objects.all()
    serializer_class = serializers.TipoDocumentoSerializer


class TipoEventoViewSet(ModelViewSet):
    queryset = models.TipoEvento.objects.all()
    serializer_class = serializers.TipoEventoSerializer
    filter_class = filters.TipoEventoFilter
