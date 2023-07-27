
# third-party
from rest_framework.viewsets import ModelViewSet

# application
from . import models
from . import serializers


# define uma ViewSet para o modelo Aprisionamento
class AprisionamentoViewSet(ModelViewSet):
    queryset = models.Aprisionamento.objects.all()
    serializer_class = serializers.AprisionamentoSerializer


# define uma ViewSet para o modelo CalculoExecucaoPenal
class CalculoExecucaoPenalViewSet(ModelViewSet):
    queryset = models.CalculoExecucaoPenal.objects.all()
    serializer_class = serializers.CalculoExecucaoPenalSerializer


# define uma ViewSet para o modelo EstabelecimentoPenal
class EstabelecimentoPenalViewSet(ModelViewSet):
    queryset = models.EstabelecimentoPenal.objects.all()
    serializer_class = serializers.EstabelecimentoPenalSerializer


# define uma ViewSet para o modelo Falta
class FaltaViewSet(ModelViewSet):
    queryset = models.Falta.objects.all()
    serializer_class = serializers.FaltaSerializer


# define uma ViewSet para o modelo Historico
class HistoricoViewSet(ModelViewSet):
    queryset = models.Historico.objects.all()
    serializer_class = serializers.HistoricoSerializer


# define uma ViewSet para o modelo Interrupcao
class InterrupcaoViewSet(ModelViewSet):
    queryset = models.Interrupcao.objects.all()
    serializer_class = serializers.InterrupcaoSerializer


# define uma ViewSet para o modelo MotivoBaixaPrisao
class MotivoBaixaPrisaoViewSet(ModelViewSet):
    queryset = models.MotivoBaixaPrisao.objects.all()
    serializer_class = serializers.MotivoBaixaPrisaoSerializer


# define uma ViewSet para o modelo MudancaRegime
class MudancaRegimeViewSet(ModelViewSet):
    queryset = models.MudancaRegime.objects.all()
    serializer_class = serializers.MudancaRegimeSerializer


# define uma ViewSet para o modelo PenaRestritiva
class PenaRestritivaViewSet(ModelViewSet):
    queryset = models.PenaRestritiva.objects.all()
    serializer_class = serializers.PenaRestritivaSerializer


# define uma ViewSet para o modelo Prisao
class PrisaoViewSet(ModelViewSet):
    queryset = models.Prisao.objects.all()
    serializer_class = serializers.PrisaoSerializer


# define uma ViewSet para o modelo Remissao
class RemissaoViewSet(ModelViewSet):
    queryset = models.Remissao.objects.all()
    serializer_class = serializers.RemissaoSerializer


# define uma ViewSet para o modelo RestricaoPrestacaoServico
class RestricaoPrestacaoServicoViewSet(ModelViewSet):
    queryset = models.RestricaoPrestacaoServico.objects.all()
    serializer_class = serializers.RestricaoPrestacaoServicoSerializer


# define uma ViewSet para o modelo Soltura
class SolturaViewSet(ModelViewSet):
    queryset = models.Soltura.objects.all()
    serializer_class = serializers.SolturaSerializer


# define uma ViewSet para o modelo Tipificacao
class TipificacaoViewSet(ModelViewSet):
    queryset = models.Tipificacao.objects.all()
    serializer_class = serializers.TipificacaoSerializer


# define uma ViewSet para o modelo TipoEstabelecimentoPenal
class TipoEstabelecimentoPenalViewSet(ModelViewSet):
    queryset = models.TipoEstabelecimentoPenal.objects.all()
    serializer_class = serializers.TipoEstabelecimentoPenalSerializer
