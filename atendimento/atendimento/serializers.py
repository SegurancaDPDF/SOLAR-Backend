# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from rest_framework import serializers

from . import models
from contrib.models import Servidor


TIPOS_ARQUIVAMENTO = (
    models.Qualificacao.TIPO_ARQUIVAMENTO_COM_RESOLUCAO,
    models.Qualificacao.TIPO_ARQUIVAMENTO_SEM_RESOLUCAO
)

TIPOS_DESARQUIVAMENTO = (
    models.Qualificacao.TIPO_DESARQUIVAMENTO,
)


class FormaAtendimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FormaAtendimento
        fields = '__all__'


class QualificacaoSerializer(serializers.ModelSerializer):
    from api.api_v1.serializers import GenericSerializer

    area = GenericSerializer()
    nucleo = GenericSerializer()
    especializado = GenericSerializer()
    tipo_nome = serializers.CharField(source="get_tipo_display", required=False)

    class Meta:
        model = models.Qualificacao
        fields = ('id', 'tipo', 'tipo_nome', 'titulo', 'area', 'nucleo', 'especializado',
                  'numero', 'disponivel_para_agendamento_via_app', 'orgao_encaminhamento', 'defensorias')


class QualificacaoDetailSerializer(QualificacaoSerializer):

    class Meta:
        model = models.Qualificacao
        fields = '__all__'


class TipoColetividadeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.TipoColetividade
        fields = ('id', 'nome')


class PerguntaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Pergunta
        fields = '__all__'
        ref_name = 'PerguntaAtendimento'


class EncaminhamentoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Encaminhamento
        fields = '__all__'


class DocumentoAtendimentoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Documento
        fields = '__all__'


class QualificacaoArquivamentoSerializer(serializers.ModelSerializer):
    tipo = serializers.ChoiceField(choices=models.Qualificacao.LISTA_TIPO)
    tipo_nome = serializers.CharField(source="get_tipo_display")

    class Meta:
        model = models.Qualificacao
        fields = ("id", "titulo", "tipo", "tipo_nome")


class CurrentServidorDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.servidor

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class DocumentoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Documento
        fields = ("nome", "arquivo", "atendimento", "enviado_por")
        extra_kwargs = {"nome": {"required": False}}
        ref_name = 'AtendimentoDocumento'


class ArquivarAtendimentoSerializer(serializers.ModelSerializer):
    qualificacao = serializers.PrimaryKeyRelatedField(
        queryset=models.Qualificacao.objects.filter(tipo__in=TIPOS_ARQUIVAMENTO)
    )
    cadastrado_por = serializers.PrimaryKeyRelatedField(queryset=Servidor.objects.all(), default=CurrentServidorDefault())
    atendido_por = serializers.PrimaryKeyRelatedField(queryset=Servidor.objects.all(), default=CurrentServidorDefault())
    # Não descomentar esta linha, pois há algum bug com o timezone / index_db=True quando utilizados no serializer
    # data_atendimento = serializers.DateTimeField(default=timezone.now())
    documento_arquivo = serializers.FileField(required=False, write_only=True)
    documento_nome = serializers.CharField(max_length=255, required=False, write_only=True)
    historico = serializers.CharField(required=True)

    class Meta:
        model = models.Defensor
        fields = ("tipo", "qualificacao", "historico", "defensoria",
                  "defensor", "cadastrado_por", "atendido_por", "inicial",
                  "documento_arquivo", "documento_nome")


class DesarquivarAtendimentoSerializer(serializers.ModelSerializer):
    cadastrado_por = serializers.PrimaryKeyRelatedField(queryset=Servidor.objects.all(), default=CurrentServidorDefault())
    atendido_por = serializers.PrimaryKeyRelatedField(queryset=Servidor.objects.all(), default=CurrentServidorDefault())
    # Não descomentar esta linha, pois há algum bug com o timezone / index_db=True quando utilizados no serializer
    # data_atendimento = serializers.DateTimeField(default=timezone.now())
    documento_arquivo = serializers.FileField(required=False, write_only=True)
    documento_nome = serializers.CharField(max_length=255, required=False, write_only=True)
    qualificacao = serializers.PrimaryKeyRelatedField(
        queryset=models.Qualificacao.objects.filter(tipo__in=TIPOS_DESARQUIVAMENTO)
    )
    historico = serializers.CharField(required=True)

    class Meta:
        model = models.Defensor
        fields = ("tipo", "qualificacao", "historico", "defensoria",
                  "defensor", "cadastrado_por", "atendido_por", "inicial",
                  "documento_arquivo", "documento_nome")


class PastaDocumentoSerializer(serializers.ModelSerializer):
    atendimento = serializers.PrimaryKeyRelatedField(queryset=models.Atendimento.objects.all())

    def update(self, instance, validated_data):
        """
            Previne atualização do campo atendimento durante a atualização de uma pasta, talvez permitir essa
            atualização seja interessante no futuro em uma eventual refatoração da tela de criação/edição de pastas.
        """
        validated_data.pop('atendimento', None)
        return super().update(instance, validated_data)

    class Meta:
        model = models.PastaDocumento
        fields = ("id", "nome", "descricao", "atendimento")


class AcordoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Acordo
        fields = '__all__'


class AssuntoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Assunto
        fields = '__all__'


class QualificacaoAssuntoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QualificacaoAssunto
        fields = '__all__'


class AtendimentoParticipanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AtendimentoParticipante
        fields = '__all__'


class ColetivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Coletivo
        fields = '__all__'


class AtendimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Atendimento
        fields = '__all__'


class EspecializadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Especializado
        fields = '__all__'


class GrupoDeDefensoriasParaAgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GrupoDeDefensoriasParaAgendamento
        fields = '__all__'


class ImpedimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Impedimento
        fields = '__all__'


class InformacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Informacao
        fields = '__all__'


class JustificativaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Justificativa
        fields = '__all__'


class ModeloDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModeloDocumento
        fields = '__all__'
        ref_name = 'AtendimentoModeloDocumento'


class MotivoExclusaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MotivoExclusao
        fields = '__all__'


class PessoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pessoa
        fields = '__all__'


class ProcedimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Procedimento
        fields = '__all__'


class TarefaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tarefa
        fields = '__all__'


class TipoVulnerabilidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TipoVulnerabilidade
        fields = '__all__'
