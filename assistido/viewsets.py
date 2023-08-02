# third-party
from rest_framework.viewsets import ModelViewSet

# application
from . import models
from . import serializers


# fornece operações CRUD para o modelo Dependente
class DependenteViewSet(ModelViewSet):
    queryset = models.Dependente.objects.all()
    serializer_class = serializers.DependenteSerializer


# fornece operações CRUD para o modelo Documento
class DocumentoViewSet(ModelViewSet):
    queryset = models.Documento.objects.all()
    serializer_class = serializers.DocumentoSerializer


# fornece operações CRUD para o modelo EstruturaMoradia
class EstruturaMoradiaViewSet(ModelViewSet):
    queryset = models.EstruturaMoradia.objects.all()
    serializer_class = serializers.EstruturaMoradiaSerializer


# fornece operações CRUD para o modelo Filiacao
class FiliacaoViewSet(ModelViewSet):
    queryset = models.Filiacao.objects.all()
    serializer_class = serializers.FiliacaoSerializer


# fornece operações CRUD para o modelo Imovel
class ImovelViewSet(ModelViewSet):
    queryset = models.Imovel.objects.all()
    serializer_class = serializers.ImovelSerializer


# fornece operações CRUD para o modelo Movel
class MovelViewSet(ModelViewSet):
    queryset = models.Movel.objects.all()
    serializer_class = serializers.MovelSerializer


# fornece operações CRUD para o modelo Patrimonial.
class PatrimonialViewSet(ModelViewSet):
    queryset = models.Patrimonial.objects.all()
    serializer_class = serializers.PatrimonialSerializer


# fornece operações CRUD para o modelo PatrimonialTipo
class PatrimonialTipoViewSet(ModelViewSet):
    queryset = models.PatrimonialTipo.objects.all()
    serializer_class = serializers.PatrimonialTipoSerializer


# fornece operações CRUD para o modelo Patrimonio
class PatrimonioViewSet(ModelViewSet):
    queryset = models.Patrimonio.objects.all()
    serializer_class = serializers.PatrimonioSerializer


# fornece operações CRUD para o modelo PerfilCamposObrigatorios
class PerfilCamposObrigatoriosViewSet(ModelViewSet):
    queryset = models.PerfilCamposObrigatorios.objects.all()
    serializer_class = serializers.PerfilCamposObrigatoriosSerializer


# fornece operações CRUD para o modelo PessoaAssistida
class PessoaAssistidaViewSet(ModelViewSet):
    queryset = models.PessoaAssistida.objects.all()
    serializer_class = serializers.PessoaAssistidaSerializer


# fornece operações CRUD para o modelo Profissao
class ProfissaoViewSet(ModelViewSet):
    queryset = models.Profissao.objects.all()
    serializer_class = serializers.ProfissaoSerializer


# fornece operações CURD para o modelo Renda
class RendaViewSet(ModelViewSet):
    queryset = models.Renda.objects.all()
    serializer_class = serializers.RendaSerializer


# fornece operações CRUD para o modelo Semovente
class SemoventeViewSet(ModelViewSet):
    queryset = models.Semovente.objects.all()
    serializer_class = serializers.SemoventeSerializer


# fornece operações CRUD para o modelo Situacao
class SituacaoViewSet(ModelViewSet):
    queryset = models.Situacao.objects.all()
    serializer_class = serializers.SituacaoSerializer


# fornecendo operações CRUD para o modelo TipoRenda
class TipoRendaViewSet(ModelViewSet):
    queryset = models.TipoRenda.objects.all()
    serializer_class = serializers.TipoRendaSerializer
