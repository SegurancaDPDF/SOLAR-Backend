# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import os

import uuid
import base64

from datetime import datetime

from celery.schedules import crontab_parser
from django.conf import settings
from django.db.models import Q
import six
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from djdocuments.models import Documento as DocumentoGED
from rest_framework import serializers

from atendimento.atendimento.models import Defensor as AtendimentoDefensor, Documento, Pessoa, Procedimento, Tarefa
from atividade_extraordinaria.models import AtividadeExtraordinaria
from contrib.models import Endereco, Estado, Servidor, Telefone
from contrib.services import ImageToPDFService, GedToPDFService
from core.models import Classe as CoreClasse, Processo as CoreProcesso
from core.serializers import GenericSerializer
from indeferimento.models import Indeferimento
from processo.processo.models import Processo, Manifestacao, ManifestacaoDocumento
from .validators import date_is_after_tomorrow
from assistido.models import Documento as DocumentosAssistido


# serializer para o modelo Estado que serializa todos os campos do modelo
class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = '__all__'


# serializer para o modelo Endereco que serializa todos os campos do
#  modelo, exceto os campos de read_only

class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = '__all__'
        read_only_fields = [
            'cadastrado_em',
            'modificado_em',
            'desativado_em',
            'cadastrado_por',
            'modificado_por',
            'desativado_por',
        ]


#  serializer para o modelo Telefone que serializa todos os campos do modelo
#  e adiciona um campo tipo_str usando o método `get_tipo_str`
class TelefoneSerializer(serializers.ModelSerializer):
    tipo_str = serializers.SerializerMethodField()

    class Meta:
        model = Telefone
        fields = '__all__'

    def get_tipo_str(self, obj):
        a = obj.LISTA_TIPO[obj.tipo][1]
        return a


# serializer para o modelo Pessoa que serializa alguns campos específicos do
# # modelo. Ele também adiciona opções extras para personalizar o campo atendimento
class PessoaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pessoa
        fields = (
            'url',
            'id',
            'atendimento',
            'pessoa',
            'tipo',
            'responsavel',
            'ativo'
        )

        extra_kwargs = {
            'atendimento': {
                'lookup_field': 'numero',
                'lookup_url_kwarg': 'numero'
            }
        }


#  serializer para o modelo Procedimento que serializa alguns campos específicos
#  do modelo. Ele também adiciona métodos get_agendamento_numero, get_tipo_str e
#  get_encaminhamento_nome para personalizar a serialização dos campos
class ProcedimentoSerializer(serializers.ModelSerializer):
    tipo_str = serializers.SerializerMethodField()
    agendamento_numero = serializers.SerializerMethodField()
    encaminhamento_nome = serializers.SerializerMethodField()

    class Meta:
        model = Procedimento
        fields = (
            'id',
            'data_cadastro',
            'tipo',
            'tipo_str',
            'agendamento_numero',
            'encaminhamento_nome',
        )

    def get_agendamento_numero(self, obj):
        if obj.agendamento:
            return obj.agendamento.numero

    def get_tipo_str(self, obj):
        return obj.get_tipo_display()

    def get_encaminhamento_nome(self, obj):
        if obj.encaminhamento:
            return obj.encaminhamento.nome


# serializer para o modelo Pessoa usado no contexto de um atendimento.
# Ele adiciona um campo atendimento usando o método get_atendimento.
class AtendimentoPessoaSerializer(serializers.ModelSerializer):
    atendimento = serializers.SerializerMethodField()

    # atendimento = serializers.(view_name='atendimento-detail', read_only=True)
    # atendimento = serializers.RelatedField(read_only=True, source='atendimento.numero')
    class Meta:
        model = Pessoa
        fields = (
            'url',
            'id',
            'atendimento',
            # 'atendimento_url',
            'pessoa',
            'tipo',
            'responsavel',
            'ativo'
        )
        # extra_kwargs = {
        #     'atendimento': {
        #         # 'source': 'atendimento.numero',
        #         # 'lookup_field': 'numero',
        #         'serializer_related_to_field': 'numero',
        #     },
        #
        # }

    def get_atendimento(self, o):
        return o.atendimento.numero


# serializer para o modelo AtendimentoDefensor que serializa alguns campos 
# específicos do modelo. Também adiciona métodos para personalizar a serialização
# dos campos
class AtendimentoHyperlinkedModelSerializer(serializers.ModelSerializer):
    partes = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    qualificacao = serializers.SerializerMethodField()
    defensor = serializers.SerializerMethodField()
    substituto = serializers.SerializerMethodField()
    defensoria = serializers.SerializerMethodField()
    predio = serializers.SerializerMethodField()
    endereco = serializers.SerializerMethodField()
    pre_cadastro = serializers.SerializerMethodField()
    pre_cadastro_procedimento = serializers.SerializerMethodField()
    motivo_exclusao = serializers.SerializerMethodField()
    categoria_agenda = serializers.SerializerMethodField()
    forma_atendimento = serializers.SerializerMethodField()
    # ultimos_atendimentos = serializers.SerializerMethodField()

    class Meta:
        model = AtendimentoDefensor
        fields = (
            # 'url',
            'id',
            # 'url_numero',
            'numero',
            'area',
            'qualificacao',
            'inicial',
            'defensor_id',
            'defensor',
            'substituto_id',
            'substituto',
            'defensoria_id',
            'defensoria',
            'predio',
            'endereco',
            'partes',
            'data_agendamento',
            'data_atendimento',
            'pre_cadastro',
            'pre_cadastro_procedimento',
            'motivo_exclusao',
            'ativo',
            'historico_recepcao',
            'categoria_agenda',
            'forma_atendimento'
            # 'ultimos_atendimentos',
        )
        extra_kwargs = {
            # 'url': {'lookup_field': 'numero'},
            # 'inicial': {'lookup_field': 'numero'}
        }
        read_only_fields = (
            'id',
            'numero',
            'inicial'
        )

    def get_partes(self, obj):
        if obj.inicial_id:
            pessoa_queryset = Pessoa.objects.filter(ativo=True, atendimento_id=obj.inicial_id)
        else:
            pessoa_queryset = obj.partes.filter(ativo=True)

        partes = AtendimentoPessoaSerializer(
            instance=pessoa_queryset,
            many=True,
            context={'request': self.context['request']}
        ).data
        return partes

    def get_ultimos_atendimentos(self, obj):

        if obj.inicial_id:
            q_inicial = Q(inicial__numero=obj.inicial.numero)
        else:
            q_inicial = Q(inicial__numero=obj.numero)

        q = Q()
        q &= q_inicial
        q &= Q(ativo=True)
        q &= Q(remarcado=None)
        q &= Q(remarcado_auto=False)
        q &= Q(tipo__in=(
            AtendimentoDefensor.TIPO_INICIAL, AtendimentoDefensor.TIPO_RETORNO,
            AtendimentoDefensor.TIPO_ENCAMINHAMENTO))
        q &= Q(excluido_por=None)
        x = AtendimentoDefensor.objects.select_related(
            'atendimento_ptr'
        ).order_by().order_by(
            '-data_agendamento'
        ).only(
            'defensoria_id'
        ).filter(q).values('numero', 'data_agendamento', 'data_atendimento')

        return x

    def get_area(self, obj):
        n = None
        if obj and obj.qualificacao and obj.qualificacao.area:
            n = obj.qualificacao.area.nome
        return n

    def get_qualificacao(self, obj):
        n = None
        if obj and obj.qualificacao:
            n = obj.qualificacao.titulo
        return n

    def get_defensor(self, obj):
        if obj and obj.defensor:
            return obj.defensor.servidor.nome

    def get_substituto(self, obj):
        if obj and obj.substituto:
            return obj.substituto.servidor.nome

    def get_defensoria(self, obj):
        n = None
        if obj and obj.defensoria:
            n = obj.defensoria.nome
        return n

    def get_predio(self, obj):
        n = None
        if obj and obj.defensoria and obj.defensoria.predio:
            n = obj.defensoria.predio.nome
        return n

    def get_endereco(self, obj):
        n = None
        if obj and obj.defensoria and obj.defensoria.predio and obj.defensoria.predio.endereco:
            n = six.text_type(obj.defensoria.predio.endereco)
        return n

    def get_pre_cadastro(self, obj):
        return (obj.tipo == AtendimentoDefensor.TIPO_LIGACAO)

    def get_pre_cadastro_procedimento(self, obj):
        if obj.tipo == AtendimentoDefensor.TIPO_LIGACAO and obj.ligacao.exists():
            return ProcedimentoSerializer(
                instance=obj.ligacao.first(),
                context={'request': self.context['request']}
            ).data

    def get_motivo_exclusao(self, obj):
        if obj.tipo_motivo_exclusao:
            return obj.tipo_motivo_exclusao.nome
        else:
            return obj.motivo_exclusao

    def get_categoria_agenda(self, obj):
        if obj.agenda:
            return obj.agenda.nome
        else:
            return None

    def get_forma_atendimento(self, obj):
        if obj.forma_atendimento:
            return 'presencial' if obj.forma_atendimento.presencial else 'remoto'
        else:
            return None

    def get_fields(self):
        fields = super(AtendimentoHyperlinkedModelSerializer, self).get_fields()
        if hasattr(fields['partes'], 'child_relation'):
            fields['partes'].child_relation.queryset = fields['partes'].child_relation.queryset.order_by()
        else:
            print("")
            # fields['partes'].queryset = fields['partes'].queryset.order_by()

        return fields


class AtendimentoDetailSerializer(AtendimentoHyperlinkedModelSerializer):
    class Meta:
        model = AtendimentoDefensor
        fields = '__all__'


# serializer para as anotações de atendimento. Também define um método update para atualizar as anotações
class AnotacaoSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    numero = serializers.IntegerField(read_only=True)
    data_finalizado = serializers.DateTimeField(required=True)

    def update(self, instance, validated_data):
        instance.data_finalizado = validated_data.get('data_finalizado', instance.data_finalizado)
        instance.save()
        return instance


# serializer usado para criar um novo atendimento de retorno
class CadastroAtendimentoRetornoSerializer(serializers.Serializer):
    pessoa_assistida_id = serializers.IntegerField(
        min_value=1,
        help_text='ID da pessoa assistida (requerente)')
    agenda_id = serializers.IntegerField(required=False, min_value=1)
    data_agendamento = serializers.DateTimeField(required=False, validators=())
    categoria_agenda = serializers.IntegerField(required=False, min_value=1)
    anotacao = serializers.CharField(required=False)
    defensor_titular_id = serializers.IntegerField(required=False, min_value=1)
    defensor_substituto_id = serializers.IntegerField(required=False, min_value=1)
    comarca_id = serializers.IntegerField(required=False, min_value=1)
    defensoria_id = serializers.IntegerField(required=False, min_value=1)


# serializer vazio usado para salvar e liberar agendamentos.
class SalvarLiberarAgendamentoSerializer(serializers.Serializer):
    pass


# serializer usado para criar um novo atendimento inicial
class CadastroAtendimentoInicialSerializer(serializers.Serializer):
    pessoas_assistidas_ids = serializers.ListSerializer(
        child=serializers.IntegerField(min_value=1),
        help_text='IDs das pessoas assistidas (requerentes)')
    agenda_id = serializers.IntegerField(
        min_value=1,
        required=False,
        help_text='ID da agenda (exceto CRC)')
    comarca_id = serializers.IntegerField(
        min_value=1,
        required=False,
        help_text='ID da comarca de preferência de atendimento (somente para CRC)')
    defensoria_id = serializers.IntegerField(
        min_value=1,
        required=False,
        help_text='ID da defensoria (somente para CRC)')
    qualificacao_id = serializers.IntegerField(min_value=1)
    data_agendamento = serializers.DateTimeField(validators=(date_is_after_tomorrow,), required=False)
    categoria_agenda = serializers.IntegerField(
        required=False,
        help_text='ID da categoria de agenda')
    anotacao = serializers.CharField(required=False)
    processo_numero = serializers.CharField(
        required=False,
        help_text='Número do processo judicial')
    defensor_titular_id = serializers.IntegerField(required=False, min_value=1)
    defensor_substituto_id = serializers.IntegerField(required=False, min_value=1)
    atendimento_tipo_ligacao = serializers.BooleanField(required=False)


class ProcessoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Processo
        exclude = (
            'chave',
        )


class ProcessoAtendimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Processo
        exclude = (
            'chave',
        )


class ExtraFieldsMixin(object):

    def get_field_names(self, declared_fields, info):
        expanded_fields = super(ExtraFieldsMixin, self).get_field_names(declared_fields, info)

        if getattr(self.Meta, 'extra_fields', None):
            return expanded_fields + self.Meta.extra_fields
        else:
            return expanded_fields


class ServidorBasicSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    eh_defensor = serializers.SerializerMethodField()

    class Meta:
        model = Servidor
        fields = ('id', 'nome', 'username', 'eh_defensor')

    def get_username(self, obj):
        return obj.usuario.username

    def get_eh_defensor(self, obj):
        if hasattr(obj, 'defensor'):
            return obj.defensor.eh_defensor
        else:
            return False


class ArquivoSerializer(serializers.FileField):
    def to_internal_value(self, urls):
        # recupera número do atendimento da URL
        atendimento_numero = self.context['view'].kwargs.get('parent_lookup_atendimento__numero')
        # obtém dados do atendimento (usa o número do inicial para criar diretório de arquivos)
        atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)

        # diretório de arquivos do atendimento (mesmo formato de Atendimento.Documento)
        relativedir = os.path.join('atendimento', str(atendimento.at_inicial.numero))
        fulldir = os.path.join(settings.MEDIA_ROOT, relativedir)
        filename = '{}.pdf'.format(uuid.uuid4())

        try:
            service = ImageToPDFService()
            service.download_images_and_export(filename, fulldir, urls.split(';'))
        except Exception as e:
            return e
        else:
            return os.path.join(relativedir, filename)


class DocumentoSerializer(serializers.ModelSerializer):
    arquivo = ArquivoSerializer()

    class Meta:
        model = Documento
        fields = ['id', 'nome', 'arquivo', 'documento_online', 'pendente']

    # adiciona comportamento personalizado durante a atualizacao de uma instância do model documento
    def update(self, instance, validated_data):
        instance.analisar = True
        instance.data_enviado = datetime.now()
        instance.enviado_por = self.context['request'].user.servidor
        return super(DocumentoSerializer, self).update(instance, validated_data)

    # validacao do campo arquivo durante a serializacao
    def validate_arquivo(self, value):
        if type(value) is Exception:
            raise serializers.ValidationError(str(value))
        return value


class DocumentoGEDSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoGED
        fields = ['id', 'assunto', 'identificador_versao', 'get_absolute_url']


class TarefaProcessoSerializer(serializers.ModelSerializer):
    acao = serializers.SerializerMethodField()

    class Meta:
        model = Processo
        fields = ('id', 'numero', 'acao')
   
    # obtem o nome da ação relacionada ao objeto Processo
    def get_acao(self, obj):
        return obj.acao.nome


class TarefaAtendimentoSerializer(ExtraFieldsMixin, serializers.ModelSerializer):
    setor_responsavel = GenericSerializer()
    tipo = GenericSerializer()
    responsavel = ServidorBasicSerializer()
    processo = TarefaProcessoSerializer()
    finalizado = ServidorBasicSerializer()
    resposta_para = GenericSerializer()
    cadastrado_por = ServidorBasicSerializer()
    documento = DocumentoSerializer()
    documentos = DocumentoGEDSerializer(many=True)

    class Meta:
        model = Tarefa
        fields = '__all__'
        extra_fields = ['atrasada', 'eh_alerta', 'eh_cooperacao', 'eh_tarefa']


class TarefaAtendimentoDetailSerializer(TarefaAtendimentoSerializer):
    respostas = TarefaAtendimentoSerializer(many=True)
    pode_finalizar = serializers.SerializerMethodField()

    def get_pode_finalizar(self, obj):
        return obj.pode_finalizar(self.context['request'].user)

    class Meta:
        model = Tarefa
        fields = '__all__'
        extra_fields = ['atrasada', 'eh_alerta', 'eh_cooperacao', 'eh_tarefa', 'pode_finalizar']


class CoreClasseSerializer(serializers.ModelSerializer):
    tipo = serializers.CharField(source='get_tipo_display')

    #  O campo tipo utiliza o source para obter o valor do método get_tipo_display do modelo
    class Meta:
        model = CoreClasse
        fields = ('id', 'nome', 'tipo')


class CoreProcessoSerializer(serializers.ModelSerializer):
    classe = CoreClasseSerializer()
    setor_criacao = GenericSerializer()
    setor_atual = GenericSerializer()
    setor_encaminhado = GenericSerializer()

    class Meta:
        model = CoreProcesso
        fields = ('id', 'uuid', 'numero', 'classe', 'setor_criacao', 'setor_atual', 'setor_encaminhado', 'cadastrado_em')  # noqa: E501


class IndeferimentoSerializer(serializers.ModelSerializer):
    processo = CoreProcessoSerializer()
    defensor = GenericSerializer()
    pessoa = GenericSerializer()
    tipo_baixa = serializers.CharField(source='get_tipo_baixa_display')

    class Meta:
        model = Indeferimento
        fields = ('id', 'processo', 'defensor', 'pessoa', 'tipo_baixa')


class IndeferimentoPrateleiraSerializer(serializers.Serializer):

    PRATELEIRA_RECEBIDOS = 1
    PRATELEIRA_EM_ANALISE = 2
    PRATELEIRA_ENCAMINHADOS = 3
    PRATELEIRA_BAIXADOS = 4

    LISTA_PRATELEIRA = (
        (PRATELEIRA_RECEBIDOS, 'Recebidos'),
        (PRATELEIRA_EM_ANALISE, 'Em análise'),
        (PRATELEIRA_ENCAMINHADOS, 'Encaminhados'),
        (PRATELEIRA_BAIXADOS, 'Baixados'),
    )

    prateleira = serializers.IntegerField()
    nome = serializers.SerializerMethodField()
    classe = serializers.IntegerField()
    classe_nome = serializers.CharField()
    total = serializers.IntegerField()

    # obtem o nome correspondente ao valor do campo prateleira
    def get_nome(self, obj):
        return dict(self.LISTA_PRATELEIRA).get(obj['prateleira'])


class AtividadeExtraordinariaSerializer(serializers.ModelSerializer):
    complemento = serializers.SerializerMethodField()
    participantes = serializers.SerializerMethodField()

    class Meta:
        model = AtividadeExtraordinaria
        fields = '__all__'

    def get_complemento(self, obj):
        return obj.complemento

    def get_participantes(self, obj):
        return obj.participante_set.ativos().values_list('usuario_id', flat=True)


class CrontabScheduleSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    minutes = serializers.SerializerMethodField()
    hours = serializers.SerializerMethodField()
    days_of_week = serializers.SerializerMethodField()
    days_of_month = serializers.SerializerMethodField()
    months_of_year = serializers.SerializerMethodField()

    class Meta:
        model = CrontabSchedule
        exclude = (
            'timezone',
        )

    def get_name(self, obj):
        return str(obj)

    def get_minutes(self, obj):
        return crontab_parser(60).parse(obj.minute)

    def get_hours(self, obj):
        return crontab_parser(24).parse(obj.hour)

    def get_days_of_week(self, obj):
        return crontab_parser(7).parse(obj.day_of_week)

    def get_days_of_month(self, obj):
        return crontab_parser(31, 1).parse(obj.day_of_month)

    def get_months_of_year(self, obj):
        return crontab_parser(12, 1).parse(obj.month_of_year)


class PeriodicTaskSerializer(serializers.ModelSerializer):
    crontab = CrontabScheduleSerializer()

    class Meta:
        model = PeriodicTask
        fields = '__all__'

    def create_or_update_crontab(self, validated_data, instance=None):
        crontab = CrontabScheduleSerializer()

        # preenche timezone
        validated_data['timezone'] = settings.TIME_ZONE

        # Se crontab só utilizado pela task atual, atualiza dados
        if instance and instance.periodictask_set.count() == 1:
            instance = crontab.update(instance, validated_data)
        # Senão, verifica se existe algum crontab com os mesmos dados ou cria um novo
        else:
            instance = CrontabSchedule.objects.filter(**validated_data).first()
            if not instance:
                instance = crontab.create(validated_data)
        return instance

    def create(self, validated_data):
        validated_data['crontab'] = self.create_or_update_crontab(validated_data['crontab'])
        return super(PeriodicTaskSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        validated_data['crontab'] = self.create_or_update_crontab(validated_data['crontab'], instance.crontab)
        return super(PeriodicTaskSerializer, self).update(instance, validated_data)


class ManifestacaoProcessualSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manifestacao
        fields = '__all__'


class ManifestacaoProcessualDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManifestacaoDocumento
        fields = '__all__'

    def create(self, validated_data):
        validated_data['posicao'] = validated_data['manifestacao'].documentos.count()
        return super().create(validated_data)


class ManifestacaoProcessualDocumentoBase64Serializer(serializers.ModelSerializer):
    conteudo_em_base64 = serializers.SerializerMethodField('get_base_64')
    ja_foi_assinado = serializers.SerializerMethodField('verificar_se_ja_foi_assinado')

    def create(self, validated_data):
        validated_data['posicao'] = validated_data['manifestacao'].documentos.count()
        return super().create(validated_data)

    def get_base_64(self, manifestacao_documento_model):

        documento = None

        if manifestacao_documento_model.origem == ManifestacaoDocumento.ORIGEM_ATENDIMENTO:
            documento = Documento.objects.get(id=manifestacao_documento_model.origem_id)
        else:
            documento = DocumentosAssistido.objects.get(id=manifestacao_documento_model.origem_id)

        if hasattr(documento, 'documento_online_id') and documento.documento_online_id:
            documento_ged = DocumentoGED.objects.get(id=documento.documento_online_id)
            servico_ged = GedToPDFService(documento_ged)
            conteudo_ged_em_pdf = servico_ged.export()
            return base64.b64encode(conteudo_ged_em_pdf)
        elif documento.arquivo.path:
            with open(documento.arquivo.path, 'rb') as file:
                content = file.read()
                return base64.b64encode(content)

    def verificar_se_ja_foi_assinado(self, manifestacao_documento_model):

        documento = None

        if manifestacao_documento_model.origem == ManifestacaoDocumento.ORIGEM_ATENDIMENTO:
            documento = Documento.objects.get(id=manifestacao_documento_model.origem_id)
        else:
            documento = DocumentosAssistido.objects.get(id=manifestacao_documento_model.origem_id)

        if hasattr(documento.documento_assinado, 'arquivo') and os.path.exists(documento.documento_assinado.arquivo.path):  # noqa: E501
            return True
        else:
            return False

    class Meta:
        model = ManifestacaoDocumento
        fields = '__all__'
