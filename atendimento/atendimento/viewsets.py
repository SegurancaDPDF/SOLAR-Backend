# third-party
from rest_framework.viewsets import ModelViewSet

# application
from . import models
from . import serializers


class AcordoViewSet(ModelViewSet):
    queryset = models.Acordo.objects.all()
    serializer_class = serializers.AcordoSerializer


class AssuntoViewSet(ModelViewSet):
    queryset = models.Assunto.objects.all()
    serializer_class = serializers.AssuntoSerializer


class QualificacaoAssuntoViewSet(ModelViewSet):
    queryset = models.QualificacaoAssunto.objects.all()
    serializer_class = serializers.QualificacaoAssuntoSerializer


class AtendimentoDefensorViewSet(ModelViewSet):
    queryset = models.Defensor.objects.all()
    serializer_class = serializers.AtendimentoSerializer


class AtendimentoParticipanteViewSet(ModelViewSet):
    queryset = models.AtendimentoParticipante.objects.all()
    serializer_class = serializers.AtendimentoParticipanteSerializer


class ColetivoViewSet(ModelViewSet):
    queryset = models.Coletivo.objects.all()
    serializer_class = serializers.ColetivoSerializer


class AtendimentoViewSet(ModelViewSet):
    queryset = models.Atendimento.objects.all()
    serializer_class = serializers.AtendimentoSerializer


class DocumentoViewSet(ModelViewSet):
    queryset = models.Documento.objects.all()
    serializer_class = serializers.DocumentoSerializer


class EncaminhamentoViewSet(ModelViewSet):
    queryset = models.Encaminhamento.objects.all()
    serializer_class = serializers.EncaminhamentoSerializer


class EspecializadoViewSet(ModelViewSet):
    queryset = models.Especializado.objects.all()
    serializer_class = serializers.EspecializadoSerializer


class FormaAtendimentoViewSet(ModelViewSet):
    queryset = models.FormaAtendimento.objects.all()
    serializer_class = serializers.FormaAtendimentoSerializer


class GrupoDeDefensoriasParaAgendamentoViewSet(ModelViewSet):
    queryset = models.GrupoDeDefensoriasParaAgendamento.objects.all()
    serializer_class = serializers.GrupoDeDefensoriasParaAgendamentoSerializer


class ImpedimentoViewSet(ModelViewSet):
    queryset = models.Impedimento.objects.all()
    serializer_class = serializers.ImpedimentoSerializer


class InformacaoViewSet(ModelViewSet):
    queryset = models.Informacao.objects.all()
    serializer_class = serializers.InformacaoSerializer


class JustificativaViewSet(ModelViewSet):
    queryset = models.Justificativa.objects.all()
    serializer_class = serializers.JustificativaSerializer


class ModeloDocumentoViewSet(ModelViewSet):
    queryset = models.ModeloDocumento.objects.all()
    serializer_class = serializers.ModeloDocumentoSerializer


class MotivoExclusaoViewSet(ModelViewSet):
    queryset = models.MotivoExclusao.objects.all()
    serializer_class = serializers.MotivoExclusaoSerializer


class PastaDocumentoViewSet(ModelViewSet):
    queryset = models.PastaDocumento.objects.all()
    serializer_class = serializers.PastaDocumentoSerializer


class PessoaViewSet(ModelViewSet):
    queryset = models.Pessoa.objects.all()
    serializer_class = serializers.PessoaSerializer


class PerguntaViewSet(ModelViewSet):
    queryset = models.Pergunta.objects.all()
    serializer_class = serializers.PerguntaSerializer


class ProcedimentoViewSet(ModelViewSet):
    queryset = models.Procedimento.objects.all()
    serializer_class = serializers.ProcedimentoSerializer


class QualificacaoViewSet(ModelViewSet):
    queryset = models.Qualificacao.objects.all()
    serializer_class = serializers.QualificacaoSerializer


class TarefaViewSet(ModelViewSet):
    queryset = models.Tarefa.objects.all()
    serializer_class = serializers.TarefaSerializer


class TipoColetividadeViewSet(ModelViewSet):
    queryset = models.TipoColetividade.objects.all()
    serializer_class = serializers.TipoColetividadeSerializer


class TipoVulnerabilidadeViewSet(ModelViewSet):
    queryset = models.TipoVulnerabilidade.objects.all()
    serializer_class = serializers.TipoVulnerabilidadeSerializer
