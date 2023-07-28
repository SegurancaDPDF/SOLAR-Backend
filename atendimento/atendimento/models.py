# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging
from datetime import date, datetime, time
from typing import List

# Bibliotecas de terceiros
import reversion
from constance import config
from django.db.models import deletion
from django.core.exceptions import ObjectDoesNotExist
from django.utils.functional import cached_property
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone

# Solar
from assistido.models import PessoaAssistida
from contrib.models import Util
from contrib.validators import validate_file_size_extension
from core.models import AuditoriaAbstractMixin
from evento.models import Evento
from defensor.models import Atuacao
from processo.processo.models import Parte, Processo

# Modulos locais
from . import managers

logger = logging.getLogger(__name__)


class Acordo(models.Model):
    TIPO_SIM = 0
    TIPO_NAO = 1
    TIPO_REQUERENTE = 2
    TIPO_REQUERIDO = 3
    TIPO_AMBOS = 4
    TIPO_SUBJETIVO = 5

    LISTA_TIPO = (
        (TIPO_SIM, u'Sim - Partes entraram em acordo'),
        (TIPO_SUBJETIVO, u'Sim - Acordo Subjetivo'),
        (TIPO_NAO, u'Não - Partes não entraram em acordo'),
        (TIPO_REQUERENTE, u'Não - Requerente não compareceu'),
        (TIPO_REQUERIDO, u'Não - Requerido não compareceu'),
        (TIPO_AMBOS, u'Não - Ambas partes não compareceram'),
    )

    atendimento = models.OneToOneField('Atendimento', on_delete=models.DO_NOTHING)
    termo = models.ForeignKey('Documento', blank=True, null=True, on_delete=models.DO_NOTHING)
    tipo = models.PositiveSmallIntegerField(choices=LISTA_TIPO, default=TIPO_SIM)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return str(self.atendimento.numero)

    class Meta:
        app_label = 'atendimento'


class Cronometro(models.Model):
    MOTIVO_LIGACAO_FINALIZADA = 0
    MOTIVO_CAIU_LIGACAO = 1
    MOTIVO_ENGANO = 2
    MOTIVO_TROTE = 3
    MOTIVO_TEMPO_EXPIRADO = 4
    MOTIVO_DESISTENCIA = 5

    LISTA_MOTIVO = (
        (MOTIVO_LIGACAO_FINALIZADA, 'Finalizada'),
        (MOTIVO_CAIU_LIGACAO, 'Caiu'),
        (MOTIVO_ENGANO, 'Engano'),
        (MOTIVO_TROTE, 'Trote'),
        (MOTIVO_TEMPO_EXPIRADO, 'Tempo Expirado'),
        (MOTIVO_DESISTENCIA, 'Desistência'),
    )

    atendimento = models.ForeignKey('Atendimento', on_delete=models.DO_NOTHING)
    servidor = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    inicio = models.DateTimeField('Início', null=True, blank=True, default=None)
    termino = models.DateTimeField('Término', auto_now=True)
    duracao = models.IntegerField('Duração', default=0)
    finalizado = models.BooleanField(default=False)
    motivo_finalizou_ligacao = models.PositiveSmallIntegerField(choices=LISTA_MOTIVO, default=MOTIVO_LIGACAO_FINALIZADA)

    class Meta:
        app_label = 'atendimento'
        verbose_name = u'Cronômetro'
        verbose_name_plural = u'Cronometros'
        indexes = [
            models.Index(fields=['atendimento', 'servidor'], condition=Q(finalizado=False), name='atendimento_cronometro_idx_001'),  # noqa: E501
            models.Index(fields=['atendimento', 'termino'], name='atendimento_cronometro_idx_002'),
        ]

    def __str__(self):
        return '{}: {} ({})'.format(self.atendimento, self.inicio, self.servidor)

    @staticmethod
    def expirado():
        return False

    def calcular_duracao(self):

        if self.expirado():
            self.finalizado = True
        else:
            self.termino = datetime.now()
            self.duracao = (self.termino - self.inicio).seconds

    def atualizar(self):

        if not self.atendimento.realizado:
            self.calcular_duracao()
            self.save()

    def finalizar(self, motivo_finalizou_ligacao=None):
        self.calcular_duracao()
        self.motivo_finalizou_ligacao = motivo_finalizou_ligacao
        self.finalizado = True
        self.save()


class Encaminhamento(models.Model):
    nome = models.CharField(max_length=200)
    endereco = models.ForeignKey('contrib.Endereco', null=True, blank=True, on_delete=models.DO_NOTHING)
    telefone = models.ForeignKey('contrib.Telefone', null=True, blank=True, on_delete=models.DO_NOTHING)
    email = models.EmailField(max_length=128, null=True, blank=True, default=None)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        app_label = 'atendimento'
        ordering = ['-ativo', 'nome']


class Informacao(models.Model):
    titulo = models.CharField(max_length=200)
    texto = models.TextField()
    ativo = models.BooleanField(default=True)

    class Meta:
        app_label = 'atendimento'
        ordering = ['-ativo', 'titulo']
        verbose_name = u'Informação'
        verbose_name_plural = u'Informações'

    def __str__(self):
        return self.titulo


class InformacaoAssistido(models.Model):
    data = models.DateTimeField('Data e hora informação', blank=True, null=True, default=None)
    assistido = models.CharField(max_length=200)
    atendente = models.CharField(max_length=200)
    informacao = models.CharField(max_length=1000)

    class Meta:
        app_label = 'atendimento'
        verbose_name = u'Informação'
        verbose_name_plural = u'Informações'
        permissions = (
            ('view_informacao', u'Can view Informação'),
        )


class Acesso(models.Model):
    NIVEL_CONSULTA = 0
    NIVEL_EDICAO = 1
    NIVEL_ADMINISTRACAO = 2

    LISTA_NIVEL = (
        (NIVEL_CONSULTA, 'Consulta'),
        (NIVEL_EDICAO, 'Edição'),
        (NIVEL_ADMINISTRACAO, 'Administração'),
    )

    atendimento = models.ForeignKey('Atendimento', on_delete=models.DO_NOTHING)
    defensor = models.ForeignKey('defensor.Defensor', blank=True, null=True, default=None, related_name='+', on_delete=models.DO_NOTHING)  # noqa: E501
    solicitado_por = models.ForeignKey('defensor.Defensor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    data_solicitacao = models.DateTimeField(blank=True, null=True, default=None)
    concedido_por = models.ForeignKey('defensor.Defensor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    data_concessao = models.DateTimeField(blank=True, null=True, default=None)
    revogado_por = models.ForeignKey('defensor.Defensor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    data_revogacao = models.DateTimeField(blank=True, null=True, default=None)
    nivel = models.SmallIntegerField(choices=LISTA_NIVEL, default=NIVEL_CONSULTA)
    ativo = models.BooleanField(default=True)

    @staticmethod
    def conceder(atendimento, defensor, concedido_por):

        existe = Acesso.objects.filter(
            atendimento=atendimento.at_inicial,
            defensor_id=defensor,
            data_revogacao=None,
            data_concessao__isnull=False
        ).exists()

        if not existe:
            Acesso.objects.update_or_create(
                atendimento=atendimento.at_inicial,
                defensor_id=defensor,
                data_concessao=None,
                data_revogacao=None,
                defaults={
                    'data_concessao': datetime.now(),
                    'concedido_por': concedido_por
                }
            )

    @staticmethod
    def conceder_publico(atendimento, concedido_por):
        Acesso.objects.create(
            atendimento=atendimento.at_inicial,
            defensor=None,
            data_concessao=datetime.now(),
            concedido_por=concedido_por
        )

    @staticmethod
    def revogar(atendimento, defensor, revogado_por):
        Acesso.objects.filter(
            atendimento=atendimento.at_inicial,
            defensor=defensor,
            data_revogacao=None
        ).update(
            data_revogacao=datetime.now(),
            revogado_por=revogado_por
        )

    @staticmethod
    def revogar_publico(atendimento, revogado_por):
        Acesso.objects.filter(
            atendimento=atendimento.at_inicial,
            defensor=None,
            data_revogacao=None
        ).update(
            data_revogacao=datetime.now(),
            revogado_por=revogado_por
        )


class AtendimentoParticipante(models.Model):
    atendimento = models.ForeignKey('Atendimento', related_name='participantes_atendimentos', on_delete=models.DO_NOTHING)  # noqa: E501
    servidor = models.ForeignKey('contrib.Servidor', related_name='participantes_atendimentos', on_delete=models.DO_NOTHING)  # noqa: E501
    cargo = models.ForeignKey('contrib.Cargo', related_name='participantes_atendimentos', null=True, blank=True, on_delete=models.DO_NOTHING)  # noqa: E501

    class Meta:
        unique_together = ('atendimento', 'servidor')
        db_table = 'atendimento_atendimento_participantes'


class Atendimento(models.Model):

    # ATENÇÃO!
    # - Futura numeração de tipos para migração para core.Processo:
    # - Prefixo do módulo Atendimento: 10XX
    # - Ao criar novos tipos, usar nova lógica para facilitar a migração

    # TIPOS PRÉ-ATENDIMENTO
    TIPO_LIGACAO = 0  # 1011: futura numeração para migração core.Processo
    TIPO_RECEPCAO = 3  # 1012: futura numeração para migração core.Processo

    # TIPOS ATENDIMENTO (DEFENSOR)
    TIPO_INICIAL = 1  # 1021: futura numeração para migração core.Processo
    TIPO_RETORNO = 2  # 1022: futura numeração para migração core.Processo
    TIPO_ENCAMINHAMENTO = 9  # 1023: futura numeração para migração core.Processo

    # TIPOS ATENDIMENTO (APOIO)
    TIPO_NUCLEO_PEDIDO = 1031
    TIPO_NUCLEO = 4  # 1032 (resposta): futura numeração para migração core.Processo
    TIPO_ATIVIDADE = 10  # 1033: futura numeração para migração core.Processo

    TIPO_PROCESSO = 6  # 1040: futura numeração para migração core.Processo (10: atendimento + 40: processo)

    # TIPOS ATENDIMENTO (LIVRE)
    TIPO_VISITA = 7  # 1041: futura numeração para migração core.Processo)
    TIPO_INTERESSADO = 8  # 1042: futura numeração para migração core.Processo)

    # TIPOS DIVERSOS
    TIPO_ANOTACAO = 5  # 1091: futura numeração para migração core.Processo)
    TIPO_NOTIFICACAO = 1092

    # TIPOS DPE-AM
    TIPO_RECLAMACAO = 11
    TIPO_INFORMACAO = 12
    TIPO_OFICIO = 13
    TIPO_OFICIO_FINALIZADO = 14

    # TIPOs ARQUIVAMENTO
    TIPO_DESARQUIVAMENTO = 998
    TIPO_ARQUIVAMENTO = 999

    LISTA_TIPO = (
        (TIPO_LIGACAO, u'Ligação'),
        (TIPO_INICIAL, u'Inicial'),
        (TIPO_RETORNO, u'Retorno'),
        (TIPO_RECEPCAO, u'Recepção'),
        (TIPO_NUCLEO_PEDIDO, u'Solicitação de Apoio de Núcleo Especializado'),
        (TIPO_NUCLEO, u'Apoio de Núcleo Especializado'),
        (TIPO_ANOTACAO, u'Anotação'),
        (TIPO_PROCESSO, u'Processo'),
        (TIPO_VISITA, u'Visita ao Preso'),
        (TIPO_INTERESSADO, u'Atendimento ao Interessado'),
        (TIPO_ENCAMINHAMENTO, u'Encaminhamento'),
        (TIPO_ATIVIDADE, u'Atividade'),
        (TIPO_NOTIFICACAO, u'Notificação'),
        # DPE-AM
        (TIPO_RECLAMACAO, u'Reclamacao pelo disk'),
        (TIPO_INFORMACAO, u'Informacao pelo disk'),
        (TIPO_OFICIO, u'Ofício encaminhado'),
        (TIPO_OFICIO_FINALIZADO, u'Ofício finalizado'),
        (TIPO_ARQUIVAMENTO, u'Atendimento arquivado'),
        (TIPO_DESARQUIVAMENTO, u'Atendimento desarquivado'),
    )

    PRIORIDADE_0 = 0
    PRIORIDADE_1 = 10
    PRIORIDADE_2 = 20

    LISTA_PRIORIDADE = (
        (PRIORIDADE_0, u'Sem prioridade'),
        (PRIORIDADE_1, u'Prioridade'),
        (PRIORIDADE_2, u'Prioridade +80'),
    )

    numero = models.BigIntegerField(blank=True, null=True, db_index=True)
    tipo = models.PositiveSmallIntegerField(choices=LISTA_TIPO, default=TIPO_LIGACAO, db_index=True)
    agenda = models.ForeignKey('evento.Categoria', default=1, on_delete=models.DO_NOTHING)
    data_agendamento = models.DateTimeField('Data do agendamento', blank=True, null=True, default=None, db_index=True)
    data_atendimento = models.DateTimeField('Data do atendimento', blank=True, null=True, default=None, db_index=True)
    agendado_por = models.ForeignKey(
        'contrib.Servidor',
        related_name='+',
        blank=True,
        null=True,
        default=None,
        on_delete=deletion.PROTECT
    )
    atendido_por = models.ForeignKey(
        'contrib.Servidor',
        related_name='+',
        blank=True,
        null=True,
        default=None,
        on_delete=deletion.PROTECT
    )
    historico = models.TextField('Histórico Atendimento', blank=True, null=True, default=None)
    historico_recepcao = models.TextField('Histórico Agendamento', blank=True, null=True, default=None)
    inicial = models.ForeignKey(
        'self',
        related_name='retorno',
        blank=True,
        null=True,
        default=None,
        on_delete=deletion.PROTECT
    )
    origem = models.ForeignKey(
        'self',
        related_name='filhos',
        blank=True,
        null=True,
        default=None,
        on_delete=deletion.PROTECT
    )
    remarcado = models.ForeignKey(
        'self',
        related_name='atendimento_remarcado',
        blank=True,
        null=True,
        default=None,
        on_delete=deletion.PROTECT
    )
    remarcado_auto = models.BooleanField(default=False)
    nucleo = models.ForeignKey(
        'nucleo.Nucleo',
        related_name='+',
        blank=True,
        null=True,
        default=None,
        on_delete=deletion.PROTECT
    )
    assuntos = models.ManyToManyField('Assunto', related_name='atendimentos', blank=True)

    participantes = models.ManyToManyField('contrib.Servidor', related_name='atendimentos',
                                           through='AtendimentoParticipante',
                                           through_fields=('atendimento', 'servidor'), blank=True)

    prazo = models.BooleanField(default=False)

    exibir_no_painel_de_acompanhamento = models.BooleanField(
        'Exibir no Painel de Acompanhamento?',
        default=True
    )

    prioridade = models.PositiveSmallIntegerField(choices=LISTA_PRIORIDADE, default=PRIORIDADE_0, null=False)

    qualificacao = models.ForeignKey(
        to='Qualificacao',
        verbose_name='Qualificação',
        blank=True,
        null=True,
        default=None,
        on_delete=deletion.PROTECT
    )

    # Usado somente quando TIPO_ATIVIDADE para multiplicar o nº atividades nos relatórios dos núcleos especializados
    multiplicador = models.PositiveSmallIntegerField(default=1)

    forma_atendimento = models.ForeignKey(
        to='FormaAtendimento',
        verbose_name='Forma de atendimento',
        blank=True,
        null=True,
        default=None,
        on_delete=deletion.PROTECT
    )

    tipo_coletividade = models.ForeignKey(
        to='TipoColetividade',
        verbose_name='Atendimento Coletivo',
        blank=True,
        null=True,
        default=None,
        on_delete=deletion.PROTECT
    )

    INTERESSE_CONCILIACAO_DEFENSORIA = 10
    INTERESSE_CONCILIACAO_JUSTICA = 20

    LISTA_INTERESSE_CONCILIACAO = (
        (INTERESSE_CONCILIACAO_DEFENSORIA, u'Na Defensoria'),
        (INTERESSE_CONCILIACAO_JUSTICA, u'Perante a justiça'),
    )
    interesse_conciliacao = models.PositiveSmallIntegerField(choices=LISTA_INTERESSE_CONCILIACAO, blank=True, null=True)
    justificativa_nao_interesse = models.TextField(blank=True, null=True, default="")

    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    data_modificacao = models.DateTimeField('Data de Modificação', null=True, blank=False, auto_now=True, editable=False)  # noqa: E501
    modificado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    tipo_motivo_exclusao = models.ForeignKey('MotivoExclusao', related_name='+', blank=True, null=True, default=None,
                                             editable=False, on_delete=models.PROTECT)
    motivo_exclusao = models.CharField(max_length=255, blank=True, null=True, default=None)
    data_exclusao = models.DateTimeField('Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)

    # TODO: remover (depreciado)
    ativo = models.BooleanField(default=True)

    # Informações do Ofício (DPE-AM)
    oficio = models.BooleanField(default=False)
    detalhes = models.TextField('Detalhes do Ofício', blank=True, null=True, default=None)

    objects = managers.AtendimentoManager()

    def __str__(self):
        return str(self.numero)

    def to_dict(self):
        return {'agendado_por': self.agendado_por,
                'atendido_por': self.atendido_por,
                'data_agendamento': self.data_agendamento_formatada,
                'data_atendimento': self.data_atendimento_formatada,
                'data_cadastro': self.data_cadastro_formatada,
                'numero': self.numero,
                'tipo': self.status_to_s()}

    def status_to_s(self):
        status_dict = dict(self.LISTA_TIPO)
        return status_dict[self.ativo]

    @property
    def data_atendimento_formatada(self):
        if self.data_atendimento:
            return self.data_atendimento.strftime("%d/%m/%Y")
        else:
            return "data indefinida"

    @property
    def data_agendamento_formatada(self):
        data_formatada = 'data indefinida'

        if self.data_agendamento:
            if self.extra:
                data_formatada = "%s Extra-Pauta" % (self.data_agendamento.strftime("%d/%m/%Y"))
            else:
                data_formatada = self.data_agendamento.strftime("%d/%m/%Y %H:%M")

        return data_formatada

    @property
    def data_cadastro_formatada(self):
        if self.data_cadastro:
            return self.data_cadastro.strftime("%d/%m/%Y")
        else:
            return "data indefinida"

    def text_mail(self):

        email_msg = ""
        agendamento_msg = ""
        unidade_msg = ""
        telefone_msg = ""
        endereco_msg = ""
        area_msg = ""
        documento_msg = ""
        email_msg += "<br><strong>Atendimento número: </strong>" + str(self.numero)
        # Data agendamento
        if self.extra:
            agendamento_msg = "<br><strong>Agendado para: </strong>" + \
                self.data_agendamento.strftime("%d/%m/%y")
        else:
            agendamento_msg = "<br><strong>Agendado para: </strong>" + \
                self.data_agendamento.strftime("%d/%m/%y %H:%M")
        # Unidade agendamento
        if hasattr(self, 'defensoria'):
            defensoria = self.defensoria
        else:
            defensoria = Defensor.objects.get(atendimento_ptr_id=self.id).defensoria
        if defensoria.nucleo:
            unidade_msg = "<br><strong>Núcleo: </strong>" + defensoria.nucleo.nome
        else:
            unidade_msg = "<br><strong>Defensoria:</strong>" + defensoria.nome

        # Endereço agendamento
        if defensoria.predio.endereco:
            endereco_msg = "<br><strong>Endereço: </strong>" + str(defensoria.predio.endereco)

        # Telefone agendamento
        if defensoria.telefone:
            telefone_msg = "<br><strong>Telefone da Unidade: </strong>" + defensoria.telefone

        # Qualificação agendamento
        area_msg = "<br><strong>Área/Pedido: </strong>" + self.qualificacao.area.nome + "/" + self.qualificacao.titulo

        # Documentos agendamento
        if self.tipo == self.TIPO_INICIAL:
            if self.qualificacao.documentos:
                documento_msg = "<br><strong>ATENÇÃO: DOCUMENTOS SÃO NECESSÁRIOS SOMENTE CÓPIAS (NÃO ACEITAM ORIGINAIS).</strong>"  # noqa: E501
                documentos = "<br><strong>Documentos: </strong><br>"
                documentos += self.qualificacao.documentos + "<br>"
                documentos = documentos.replace(";", "<br>&#09;")
                documento_msg += documentos
        email_msg += agendamento_msg
        email_msg += unidade_msg
        email_msg += telefone_msg
        email_msg += endereco_msg
        email_msg += area_msg
        email_msg += documento_msg
        email_msg += "<br> <br>"
        return email_msg

    def get_procedimentos(self):
        return Procedimento.objects.filter(ligacao=self).order_by('data_cadastro')

    def get_processos(self):
        return Processo.objects.select_related(
            'acao', 'area', 'vara'
        ).filter(
            (
                Q(ativo=True) &
                Q(parte__ativo=True) &
                Q(parte__atendimento__ativo=True) &
                Q(parte__atendimento__in=self.ids_todos_atendimentos)
            ) &
            Q(ativo=True) &
            Q(parte__atendimento__ativo=True) &
            Q(parte__ativo=True)
        ).order_by('-tipo', 'parte__data_cadastro')

    processos = cached_property(get_processos, name='processos')

    @cached_property
    def processo(self):
        return self.get_processos().first()

    def get_processo_partes(self):
        if not hasattr(self, '_partes'):
            self._partes = Parte.objects.select_related(
                'processo'
            ).filter(
                (
                    Q(atendimento=self) |
                    Q(atendimento=self.at_inicial_id) |
                    Q(atendimento__inicial=self.at_inicial_id)
                ) &
                Q(ativo=True) &
                Q(atendimento__ativo=True) &
                Q(processo__ativo=True)
            ).order_by('-processo__tipo', 'data_cadastro')

        return self._partes

    processo_partes = cached_property(get_processo_partes, name='processo_partes')

    @cached_property
    def processo_partes_judiciais(self):
        return self.get_processo_partes().exclude(processo__tipo=Processo.TIPO_EXTRA)

    @cached_property
    def processo_partes_extrajudiciais(self):
        return self.get_processo_partes().filter(processo__tipo=Processo.TIPO_EXTRA)

    @cached_property
    def processo_parte(self):
        return self.get_processo_partes().first()

    @cached_property
    def at_inicial(self):
        """Método que retorna o atendimento inicial de um atendimento"""

        try:
            return Defensor.objects.get(id=self.at_inicial_id)
        except ObjectDoesNotExist:
            if self.inicial_id:
                return self.inicial
            else:
                return self

    @cached_property
    def at_inicial_id(self):
        """Método que retorna o id do atendimento inicial de um atendimento"""

        if self.inicial_id:
            return self.inicial_id
        else:
            return self.id

    @cached_property
    def at_final(self):
        """Método que retorna o ultimo atendimento realizado da arvore"""

        ultimo = Defensor.objects.ultimos_validos().filter(inicial=self.at_inicial_id).first()

        if ultimo:
            return ultimo
        else:
            return self.at_inicial

    @cached_property
    def arquivado(self):
        return self.at_final.tipo == self.TIPO_ARQUIVAMENTO

    @cached_property
    def at_defensor(self):
        return Defensor.objects.filter(id=self.id).first()

    @cached_property
    def at_origem(self):
        return Defensor.objects.filter(id=self.origem_id).first()

    @cached_property
    def ids_todos_atendimentos(self) -> List[int]:
        """
        Retorna lista com os ids de todos atendimentos da árvore
        """
        ids_atendimentos = list(Atendimento.objects.filter(inicial_id=self.at_inicial_id).values_list('id', flat=True))
        ids_atendimentos.append(self.at_inicial_id)
        return ids_atendimentos

    @cached_property
    def ids_todas_pessoas(self):
        return Pessoa.objects.ativos().filter(
            atendimento__in=self.ids_todos_atendimentos
        ).values_list(
            'pessoa_id', flat=True
        )

    @property
    def documentos(self):
        """
        Lista todos os documentos da árvore de atendimentos
        """
        q = (
                Q(documento_online=None) |
                Q(documento_online__esta_ativo=True)
            ) & Q(ativo=True)

        if self.tipo == Atendimento.TIPO_ANOTACAO:
            q &= Q(atendimento=self)
        else:
            q &= Q(atendimento__in=self.ids_todos_atendimentos)
            q &= ~Q(atendimento__filhos__tipo=Atendimento.TIPO_NUCLEO)

        return Documento.objects.filter(q).order_by('documento')

    @property
    def documentos_pendentes(self):
        return self.documentos.filter(data_enviado=None)

    def get_atividades(self):
        return self.filhos.filter(ativo=True, tipo=self.TIPO_ATIVIDADE).order_by('data_atendimento')

    atividades = cached_property(get_atividades, name='atividades')

    def get_requerentes(self):
        return self.pessoas.filter(tipo=Pessoa.TIPO_REQUERENTE)

    requerentes = cached_property(get_requerentes, name='requerentes')

    @property
    def telefone_para_sms(self):
        """Retorna um dicionácio contendo informações sobre
        telefone para SMS que pode ser utilizado neste
        atendimento, o seu assistido, se nenhum assistido
        tem telefone válido e se o serviço está indisponível.

        O objeto a ser retornado poderá conter:

        'telefone' : o telefone do assistido,
        'assistido' : o assistido do telefone,
        'no_valid_cell' : True se nenhum assistido do atendimento tem telefone válido,
        'unavaliable_service' : True se o serviço não está disponível,

        """

        # Cria o objeto de retorno
        retorno = {
            'telefone': None,
            'assistido': None,
            'no_valid_cell': None,
            'unavaliable_service': None,
            'validos': 0
        }

        # Se a Defensoria utiliza serviço de SMS
        if config.USAR_SMS:

            # Se o serviço está disponível no momento
            if config.SERVICO_SMS_DISPONIVEL:

                retorno['unavaliable_service'] = False

                telefone = None

                if isinstance(self.requerente, Pessoa):
                    # Obtém um telefone válido do assistido principal
                    telefone = self.requerente.pessoa.telefone_para_sms

                # Se o assistido principal tem um telefone válido e aceita receber SMS
                if (telefone and isinstance(self.requerente, Pessoa) and self.requerente.pessoa.aderiu_sms):

                    logger.error("o assistido principal tem um telefone válido e aceita receber SMS")

                    # Usa este telefone
                    retorno['telefone'] = telefone
                    retorno['assistido'] = self.requerente
                    return retorno

                # Se o assistido principal não tem um telefone válido OU não aceita receber SMS
                else:

                    logger.error("o assistido principal não tem um telefone válido OU não aceita receber SMS")

                    # Inicia os contadores
                    validos_que_nao_aderiram = 0
                    retorno['validos'] = 0

                    # Itera sobre os assistidos secundários
                    for r in self.requerentes_secundarios:

                        logger.error("iterando sobre o assistido secundário X")

                        # Obtém um telefone válido do assistido secundário
                        telefone_sec = r.pessoa.telefone_para_sms

                        # Se o secundário tem um telefone válido e aceita receber SMS
                        if telefone_sec and r.pessoa.aderiu_sms:

                            # Usa este telefone
                            retorno['telefone'] = telefone_sec
                            retorno['assistido'] = r
                            return retorno

                        # Conta a quantidade de telefones válidos de secundários
                        if telefone_sec:
                            retorno['validos'] += 1

                        # Conta a quantidade de telefones válidos de secundários que aceitam receber SMS
                        if telefone_sec and not r.pessoa.aderiu_sms:
                            validos_que_nao_aderiram += 1

                    # Se nenhum dos que tinha telefone válido aceita receber SMS
                    if retorno['validos'] > 0 and validos_que_nao_aderiram == 0:

                        logger.error("nenhum dos que tinha telefone válido aceita receber SMS")

                        # Não retornar mensagem (MENS_D)
                        return retorno

                    # Se nenhum secundário tinha telefone válido
                    if retorno['validos'] == 0:

                        logger.error("nenhum secundário tinha telefone válido")

                        # Se o principal não aceitou receber SMS
                        if (isinstance(self.requerente, Pessoa) and not self.requerente.pessoa.aderiu_sms):

                            logger.error("o principal não aceitou receber SMS")

                            # Não retornar mensagem (MENS_D)
                            return retorno

                        # Se o principal também não tinha telefone válido
                        if not telefone:

                            logger.error("o principal também não tinha telefone válido")

                            # Informa que não tem telefone válido (MENS_A)
                            retorno['no_valid_cell'] = True
                            return retorno

                        # Se o principal tinha telefone válido, só não aceitou receber SMS
                        else:

                            logger.error("o principal tinha telefone válido, só não aceitou receber SMS")

                            # Não retornar mensagem (MENS_D)
                            return retorno

                    # Em todos os outros casos
                    else:

                        # Não retornar mensagem (MENS_D)
                        return retorno

            # Se o serviço NÃO está disponível no momento
            else:

                # Mostra mensagem de não disponível (MENS_C)
                retorno['unavaliable_service'] = True
                return retorno

        else:
            # Não retornar mensagem (MENS_D)
            return retorno

    @property
    def requerentes_secundarios(self):
        return self.requerentes.filter(responsavel=False)

    @property
    def requerentes_secundarios_nomes(self):
        requerentes = self.requerentes_secundarios
        return ', '.join(requerente.nome for requerente in requerentes)

    def get_requerente(self):
        return self.get_requerentes().first()

    requerente = cached_property(get_requerente, name='requerente')

    @property
    def requerentes_secundarios_data_nascimento(self):
        nascimentos = []
        for requerente in self.requerentes_secundarios:
            try:
                nascimento = requerente.pessoa.data_nascimento
            except Exception:
                nascimento = None
            if nascimento:
                nascimentos.append(nascimento)
        return nascimentos

    @property
    def requerentes_data_nascimento_to_s(self):
        datas_nascimento = self.requerentes_secundarios_data_nascimento
        return ', '.join(data.strftime("%d/%m/%Y") for data in datas_nascimento)

    def set_requerente(self, pessoa_id):
        return self.add_pessoa(pessoa_id, Pessoa.TIPO_REQUERENTE, True)

    def add_requerente(self, pessoa_id):
        return self.add_pessoa(pessoa_id, Pessoa.TIPO_REQUERENTE)

    def add_requerido(self, pessoa_id):
        return self.add_pessoa(pessoa_id, Pessoa.TIPO_REQUERIDO)

    def get_requeridos(self):
        return self.pessoas.filter(tipo=Pessoa.TIPO_REQUERIDO)

    requeridos = cached_property(get_requeridos, name='requeridos')

    def get_requerido(self):
        return self.get_requeridos().first()

    requerido = cached_property(get_requerido, name='requerido')

    def set_requerido(self, pessoa_id):
        return self.add_pessoa(pessoa_id, Pessoa.TIPO_REQUERIDO, True)

    def add_pessoa(self, pessoa_id, tipo, responsavel=False, vincular_ao_inicial=True):
        """Utilizado para adicionar pessoa no atendimento/processo"""

        if responsavel:
            if tipo == Pessoa.TIPO_REQUERENTE:
                self.get_requerentes().update(responsavel=False)
            elif tipo == Pessoa.TIPO_REQUERIDO:
                self.get_requeridos().update(responsavel=False)

        if vincular_ao_inicial:
            atendimento = self.at_inicial
        else:
            atendimento = self

        # o primeiro requerente sempre é o responsável. O mesmo se aplica ao requerido
        if tipo == Pessoa.TIPO_REQUERENTE:
            if not self.get_requerentes():
                responsavel = True
        elif tipo == Pessoa.TIPO_REQUERIDO:
            if not self.get_requeridos():
                responsavel = True

        pessoa, novo = Pessoa.objects.update_or_create(
            atendimento=atendimento,
            pessoa_id=pessoa_id,
            defaults={
                'tipo': tipo,
                'responsavel': responsavel,
                'ativo': True
            })

        return pessoa, novo

    @property
    def pessoas(self):
        """ Retorna todas as pessoas (ativas) vinculadas ao atendimento """

        if not hasattr(self, '_pessoas'):
            self._pessoas = self.todas_pessoas.filter(ativo=True)

        return self._pessoas

    @property
    def todas_pessoas(self):
        """ Retorna todas as pessoas (ativas e inativas) vinculadas ao atendimento """

        if not hasattr(self, '_todas_pessoas'):
            self._todas_pessoas = Pessoa.objects.select_related(
                'pessoa'
            ).filter(
                atendimento=self.at_inicial_id,
            ).order_by('tipo', '-responsavel', 'pessoa__nome')

        return self._todas_pessoas

    @property
    def retornos(self):
        return Defensor.objects.filter(
            inicial=self.at_inicial_id,
            remarcado=None,
            ativo=True,
            tipo__in=[self.TIPO_RETORNO, self.TIPO_NUCLEO, self.TIPO_VISITA, self.TIPO_ENCAMINHAMENTO]
        ).order_by('numero')

    @property
    def retornos_pendentes(self):
        return self.retornos.filter(
            data_atendimento=None
        ).exclude(
            tipo=self.TIPO_NUCLEO
        )

    @cached_property
    def retornos_pendentes_hoje(self):
        # Desconsidera atendimentos do tipo núcleo (resposta pedido de apoio)
        if self.tipo == self.TIPO_NUCLEO:
            return False
        else:
            hoje = date.today()
            return self.retornos.filter(
                data_agendamento__year=hoje.year,
                data_agendamento__month=hoje.month,
                data_agendamento__day=hoje.day,
                id__gt=self.id,
            ).exclude(
                filhos__tipo=Atendimento.TIPO_NUCLEO
            ).exists()

    @property
    def proximos(self):
        return self.retornos.filter(Q(numero__gt=self.numero) & ~Q(tipo__in=[self.TIPO_NUCLEO, self.TIPO_ANOTACAO]))

    @property
    def anotacoes(self):
        return Defensor.objects.filter(origem=self, tipo__in=[self.TIPO_ANOTACAO, self.TIPO_VISITA],
                                       ativo=True).order_by('data_atendimento')

    @property
    def atrasado(self):
        if not self.extra and self.tipo != Atendimento.TIPO_NUCLEO and self.data_agendamento and self.data_agendamento < datetime.now():  # noqa: E501
            return True
        return False

    @property
    def realizado(self):
        return (self.data_atendimento is not None)

    @property
    def realizado_hoje(self):
        return self.realizado and self.data_atendimento.date() == date.today()

    @property
    def agendado_hoje(self):
        return self.data_agendamento is not None and self.data_agendamento.date() == date.today()

    @property
    def agendado_futuro(self):
        if self.data_agendamento and self.data_agendamento.date() > date.today():
            return True
        else:
            return False

    @property
    def apoio(self):
        return Defensor.objects.filter(origem=self, tipo=self.TIPO_NUCLEO, ativo=True).first()

    @cached_property
    def recepcao(self):
        return Atendimento.objects.select_related('atendido_por').filter(origem=self, tipo=self.TIPO_RECEPCAO, ativo=True).first()  # noqa: E501

    @property
    def extra(self):
        return self.data_agendamento and self.data_agendamento.time() == time()

    @cached_property
    def cronometro(self):
        cronometro, msg = Cronometro.objects.get_or_create(atendimento=self)
        cronometro.calcular_duracao()
        return cronometro

    @property
    def testemunhas_rol(self):
        return u"NOME, NACIONALIDADE, ESTADO CIVIL, PROFISSÃO, RG, CPF, ENDEREÇO "

    @property
    def comarca(self):
        return self.defensoria.comarca

    @property
    def qtd_remarcado(self):
        return self.atendimento_remarcado.filter(ativo=True).count()

    def permissao_acessar(self, usuario):

        # Pode acessar se superuser
        if usuario.is_superuser:
            return True

        # Pode acessar se tem permissão para ver todos atendimentos
        if usuario.has_perm(perm='atendimento.view_all_atendimentos'):
            return True

        if hasattr(usuario.servidor, 'defensor'):

            defensor = usuario.servidor.defensor
            defensorias = list(defensor.defensorias.values_list('id', flat=True))

            # Pode acessar se é um defensores ou defensorias que já atenderam o atendimento
            if Defensor.objects.filter(
                (
                    Q(id=self.at_inicial_id) |
                    Q(inicial=self.at_inicial_id)
                ) &
                (
                    Q(defensor=defensor) |
                    Q(substituto=defensor) |
                    Q(defensoria__in=defensorias)
                ) &
                Q(remarcado=None) &
                Q(ativo=True)
            ).exists():
                return True

            # Pode acessar se é responsável por uma das tarefas vinculadas ao atendimento
            if self.tarefa_set.filter(responsavel=defensor.servidor).exists():
                return True

            # Pode acessar se defensor/defensoria cadastrou ou é responsável por um dos processos vinculados
            if self.get_processo_partes().filter(
                (
                    Q(defensor=defensor) |
                    Q(defensor_cadastro=defensor) |
                    Q(defensoria__in=defensorias) |
                    Q(defensoria_cadastro__in=defensorias)
                ) &
                Q(ativo=True)
            ).exists():
                return True

        itinerante = usuario.servidor.proximo_itinerante

        if itinerante and itinerante.defensoria == self.defensoria:
            return True

        return False

    def permissao_modificar(self):
        if not self.realizado or self.data_atendimento.date() >= date(datetime.today().year, date.today().month, 1):
            return True
        else:
            return False

    def acesso_publico(self):
        return Acesso.objects.filter(
            atendimento=self.at_inicial_id,
            defensor=None,
            data_revogacao=None,
            ativo=True
        ).exclude(
            data_concessao=None
        ).exists()

    def acesso_solicitado(self, defensor):
        return Acesso.objects.filter(
            atendimento=self.at_inicial_id,
            defensor=defensor,
            data_revogacao=None,
            data_concessao=None,
            ativo=True
        ).exists()

    def acesso_concedido(self, defensor=None):
        if defensor:
            return Acesso.objects.filter(
                (
                    Q(defensor=defensor) | Q(defensor=None)
                ),
                atendimento=self.at_inicial_id,
                data_revogacao=None,
                ativo=True
            ).exclude(
                data_concessao=None
            ).exists()
        else:
            return Acesso.objects.filter(
                atendimento=self.at_inicial_id,
                defensor=None,
                data_revogacao=None,
                ativo=True
            ).exclude(
                data_concessao=None
            ).exists()

    def pode_excluir(self, usuario=None):

        resposta = False

        # Se o atendimento tem atividades ou anotações vinculadas diretamente a ele, não permite a exclusão
        if self.filhos.ativos().filter(tipo__in=[Atendimento.TIPO_ANOTACAO, Atendimento.TIPO_ATIVIDADE]).exists():
            resposta = False

        # Senão, se o atendimento foi realizado, verifica outros critérios de exclusão
        elif self.data_atendimento:

            hoje = date.today()
            dia_um = datetime(hoje.year, hoje.month, 1)

            # O atendimento está dentro do prazo pra exclusão ou é um superusuário?
            if self.data_atendimento > dia_um or (usuario and usuario.is_superuser):

                # Se for anotação, visita ou atividade pode excluir se não tiver atendimentos vinculados
                if self.tipo in [Atendimento.TIPO_ANOTACAO, Atendimento.TIPO_VISITA, Atendimento.TIPO_ATIVIDADE]:

                    resposta = not self.filhos.ativos().exists()

                # Para outros tipos, só exclui se não é pedido de apoio ou pedido não foi respondido e não tem atividades vinculadas  # noqa: E501
                else:

                    tem_pedido = self.filhos.ativos().filter(
                        tipo=Atendimento.TIPO_NUCLEO,
                    ).exists()

                    if tem_pedido:

                        tem_pedido_nao_respondido = self.filhos.ativos().filter(
                            tipo=Atendimento.TIPO_NUCLEO,
                            data_atendimento=None
                        ).exists()

                        tem_atividades_vinculadas = Atendimento.objects.ativos().filter(
                            origem__origem=self,
                            origem__tipo=Atendimento.TIPO_NUCLEO,
                            tipo=Atendimento.TIPO_ATIVIDADE
                        ).exists()

                        if tem_pedido_nao_respondido and not tem_atividades_vinculadas:
                            resposta = True

                    else:

                        resposta = True

        # Se atendimento não tem atividades e não foi realizado, pode excluir a qualquer momento
        else:
            resposta = True

        return resposta

    def excluir(self, excluido_por, data_exclusao=datetime.now(), motivo_exclusao=None, tipo_motivo_exclusao_id=None):

        resposta = False

        if self.pode_excluir(usuario=excluido_por.usuario):

            for filho in self.filhos.ativos().filter(tipo=Atendimento.TIPO_NUCLEO):
                filho.excluir(
                    excluido_por=excluido_por,
                    data_exclusao=data_exclusao,
                    motivo_exclusao=motivo_exclusao,
                    tipo_motivo_exclusao_id=tipo_motivo_exclusao_id
                )

            self.excluido_por = excluido_por
            self.data_exclusao = data_exclusao
            self.motivo_exclusao = motivo_exclusao
            self.tipo_motivo_exclusao_id = tipo_motivo_exclusao_id
            self.ativo = False
            self.save()

            resposta = True

        return resposta

    class Meta:
        app_label = 'atendimento'
        ordering = ['-ativo', '-numero', ]
        permissions = (
            ('delete_anotacao', u'Pode excluir anotação'),
            ('agendar_com_bloqueio', u'Pode agendar em dia com bloqueio (feriado)'),
            ('change_all_agendamentos', u'Pode alterar agendamentos de qualquer comarca'),
            ('view_all_atendimentos', u'Pode ver teor de atendimentos públicos e privados'),
            ('view_129', u'Pode ver Painel 129'),
            ('view_recepcao', u'Pode ver Painel da Recepção'),
            ('view_defensor', u'Pode ver Painel do Defensor'),
            ('view_distribuicao', u'Pode ver Painel de Distribuição de Atendimentos'),
            ('view_painel', u'Pode ver Painel de Senhas'),
            ('unificar_atendimento', u'Pode unificar atendimentos'),
            ('requalificar_atendimento_retroativo', u'Pode requalificar atendimento retroativo'),
            ('encaminhar_atendimento_para_qualquer_area', u'Pode encaminhar atendimento p/ qualquer área'),
            ('atender_retroativo', u'Pode atender retroativo'),
            ('atender_sem_liberar', u'Pode atender sem liberar na recepção'),
            ('remeter_atendimento', u'Pode remeter atendimento para outra Defensoria'),
            ('arquivar_atendimento', u'Pode arquivar um atendimento'),
            ('desarquivar_atendimento', u'Pode desarquivar um atendimento'),
            # Novas permissões DPE-AM
            # ('view_triagem', u'Can view Triagem'),
            # ('view_buscar', u'Can view botão buscar (LUPA)'),
            # ('view_botao_recepcao', u'Can view botão recepcao'),
            ('view_encaminhar_oficio', u'Can view botão encaminhar oficio'),
            # ('view_carta_convite', u'Can view botão carta convite'),
            # ('view_recepcao_atendimentos_do_dia', u'Can view aba atendimentos do dia'),
            # ('view_recepcao_audiencias_retornos', u'Can view aba atendimentos retorno e audiências'),
            # ('view_recepcao_aguardando', u'Can view aba atendimentos aguardando'),
            # ('view_recepcao_atrasados', u'Can view aba atendimentos atrasados'),
            # ('view_recepcao_liberados', u'Can view aba atendimentos liberados'),
            # ('view_recepcao_em_atendimento', u'Can view aba em atendimento'),
            # ('view_recepcao_atendidos', u'Can view aba atendidos'),
            # ('view_recepcao_atendimentos_arquivados', u'Can view aba atendimentos arquivados'),
            # ('view_recepcao_pre_atendimento', u'Can view botão atender na Recepção'),
            # ('view_recepcao_chamar', u'Can view botão chamar na Recepção'),
        )
        verbose_name = u'Atendimento Geral'
        verbose_name_plural = u'Atendimentos Gerais'
        indexes = [
            models.Index(fields=['origem', 'tipo'], name='atendimento_atend_idx_001'),
        ]


class AtendimentoVisualizacao(models.Model):
    atendimento = models.ForeignKey(Atendimento, related_name='visualizacoes', on_delete=models.DO_NOTHING)
    evento = models.ForeignKey(Atendimento, related_name='+', on_delete=models.DO_NOTHING)
    visualizado_por = models.ForeignKey('auth.User', related_name='+', on_delete=models.DO_NOTHING)
    visualizado_em = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)

    class Meta:
        db_table = 'atendimento_atendimento_visualizacao'
        ordering = ['atendimento', '-visualizado_em']
        indexes = [
            models.Index(fields=['atendimento', 'visualizado_por'], name='atendimento_atend_vis_idx_001'),
        ]


class Pessoa(models.Model):
    TIPO_REQUERENTE = 0
    TIPO_REQUERIDO = 1
    # TIPO_REPRESENTANTE = 2
    # TIPO_INTERESSADO = 3
    TIPO_DILIGENCIA = 4
    TIPO_NOTIFICACAO = 5

    LISTA_TIPO = (
        (TIPO_REQUERENTE, 'Requerente'),
        (TIPO_REQUERIDO, 'Requerido'),
        (TIPO_DILIGENCIA, 'Diligencia'),
        (TIPO_NOTIFICACAO, 'Notificação'),
    )

    LISTA_REPRESENTACAO = (
        ('P', 'Representação legal de ascendente (pais)'),
        ('AP', 'Assistência dos pais'),
        ('SP', 'Substituição ou representação processual nos caos de ações coletivas'),
        ('T', 'Tutoria'),
        ('C', 'Curadoria'),
    )

    atendimento = models.ForeignKey('Atendimento', related_name='partes', on_delete=deletion.PROTECT)
    pessoa = models.ForeignKey(PessoaAssistida, related_name='atendimentos', on_delete=deletion.PROTECT)

    representante = models.ForeignKey(
        to='Pessoa',
        related_name='representados',
        on_delete=deletion.PROTECT,
        blank=True,
        null=True,
        default=None)

    representante_modalidade = models.CharField(
        max_length=2,
        choices=LISTA_REPRESENTACAO,
        blank=True,
        null=True,
        default=None)

    tipo = models.SmallIntegerField(choices=LISTA_TIPO)
    responsavel = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)

    objects = managers.BaseManager()

    class Meta:
        app_label = 'atendimento'
        ordering = ['-ativo', '-atendimento__numero', 'tipo', '-responsavel', 'pessoa__nome']
        verbose_name = u'Parte'
        verbose_name_plural = u'Partes'
        unique_together = ('atendimento', 'pessoa')
        indexes = [
            models.Index(fields=['atendimento', 'pessoa', 'tipo'], name='atendimento_pessoa_idx_001'),
        ]

    @property
    def nome(self):
        if self.pessoa.nome_social:
            return self.pessoa.nome_social
        else:
            return self.pessoa.nome

    def __str__(self):
        if self.pessoa.nome_social:
            return self.pessoa.nome_social
        else:
            return self.pessoa.nome


class Defensor(Atendimento):
    # necessario para migracao futura para django 1.11
    # necessario conferir todas as queries
    # atendimento_ptr = models.OneToOneField('atendimento.Atendimento',
    #                                        on_delete=models.DO_NOTHING,
    #                                        primary_key=True,
    #                                        db_index=True,
    #                                        related_name='atendimentodefensor'
    #                                        )
    defensoria = models.ForeignKey(
        'contrib.Defensoria',
        blank=True,
        null=True,
        default=None,
        on_delete=deletion.PROTECT
    )
    comarca = models.ForeignKey(
        'contrib.Comarca',
        blank=True,
        null=True,
        default=None,
        on_delete=deletion.PROTECT
    )
    defensor = models.ForeignKey(
        'defensor.Defensor',
        blank=True,
        null=True,
        default=None,
        related_name='+',
        on_delete=deletion.PROTECT
    )
    substituto = models.ForeignKey(
        'defensor.Defensor',
        blank=True,
        null=True,
        default=None,
        related_name='+',
        on_delete=deletion.PROTECT
    )

    # campos de distribuição entre servidores da Defensoria
    responsavel = models.ForeignKey(
        'defensor.Defensor',
        blank=True,
        null=True,
        default=None,
        related_name='+',
        on_delete=deletion.PROTECT
    )
    data_distribuido = models.DateTimeField(blank=True, null=True, default=None)
    distribuido_por = models.ForeignKey(
        'contrib.Servidor',
        related_name='+',
        blank=True,
        null=True,
        default=None,
        on_delete=deletion.PROTECT
    )

    # campos para distribuição automática
    encaminhado_para = models.ForeignKey(
        'contrib.Defensoria',
        blank=True,
        null=True,
        default=None,
        related_name='+',
        on_delete=deletion.PROTECT
    )
    data_encaminhado = models.DateTimeField(blank=True, null=True, default=None)

    impedimento = models.ForeignKey(
        'Impedimento',
        related_name='+',
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_DEFAULT
    )

    data_finalizado = models.DateTimeField(blank=True, null=True, default=None)
    finalizado_por = models.ForeignKey(
        'defensor.Defensor',
        related_name='+',
        blank=True,
        null=True,
        default=None,
        on_delete=deletion.PROTECT
    )

    objects = managers.AtendimentoManager()

    class Meta:
        app_label = 'atendimento'
        ordering = ['-ativo', '-numero', ]
        verbose_name = u'Atendimento'
        verbose_name_plural = u'Atendimentos'

    def has_marcados(self):
        return self.retornos.filter(data_atendimento=None)

    def marcar(self, atuacao_id, data_agendamento, agendado_por, justificativa=None, categoria_de_agenda=None,
               forma_atendimento=None, anotacao=None, original=None, oficio=False, detalhes=''):

        atuacao = Atuacao.objects.get(id=atuacao_id)

        self.defensoria = atuacao.defensoria

        if atuacao.evento_set.count():
            self.comarca = atuacao.evento_set.first().municipio.comarca
        else:
            self.comarca = atuacao.defensoria.comarca

        # Se agendando a partir da substituição, obtem dados a partir da atuação
        if atuacao.tipo == Atuacao.TIPO_SUBSTITUICAO:

            self.defensor = atuacao.titular
            self.substituto = atuacao.defensor

        else:  # Senão, obtem dados a partir da atuação e verifica se há substituto para o dia do atendimento

            self.defensor = atuacao.defensor
            self.defensoria = atuacao.defensoria

        # no AM utilizado para as defensorias do interior, onde há vários defensores atuando em uma mesma defensoria e não há substituição  # noqa: E501
        if not self.defensoria.eh_mutirao:
            for substituicao in atuacao.substituicao:
                if substituicao.data_inicial.date() <= data_agendamento.date() <= substituicao.data_final.date():
                    self.substituto = substituicao.defensor

        # se remarcar para uma defensoria diferente, reavalia novo tipo
        if original and self.tipo in [Atendimento.TIPO_RETORNO, Atendimento.TIPO_ENCAMINHAMENTO]:

            # procura por ultimo retorno realizado sem ser o atual
            ultimo = Defensor.objects.ultimos_validos().filter(inicial=self.at_inicial_id).exclude(id=original.id).first()  # noqa: E501

            # se não existe ultimo retorno, assume o atendimento inicial
            if ultimo is None:
                ultimo = self.at_inicial

            if ultimo.defensoria_id != atuacao.defensoria_id:
                self.tipo = Atendimento.TIPO_ENCAMINHAMENTO
            else:
                self.tipo = Atendimento.TIPO_RETORNO

        self.agenda_id = categoria_de_agenda
        self.historico_recepcao = anotacao
        self.cadastrado_por = agendado_por
        self.agendado_por = agendado_por
        self.data_agendamento = data_agendamento
        self.forma_atendimento = forma_atendimento

        self.oficio = oficio
        self.detalhes = detalhes

        self.save()

        if justificativa and not hasattr(self, 'justificativa'):
            justificativa = Justificativa(atendimento=self, justificativa=justificativa)
            justificativa.save()

    def marcar_nucleo(self, data_agendamento, agendado_por, categoria_de_agenda=None, anotacao=None,
                      oficio=False, detalhes=''):

        self.agenda_id = categoria_de_agenda
        self.historico_recepcao = anotacao
        self.cadastrado_por = agendado_por
        self.agendado_por = agendado_por
        self.data_agendamento = data_agendamento
        self.save()

    def marcar_retorno(self, origem, atuacao_id, data_agendamento, agendado_por, categoria_de_agenda=None,
                       forma_atendimento=None, prazo=False, prioridade=Atendimento.PRIORIDADE_0, anotacao=None,
                       tipo=Atendimento.TIPO_RETORNO, oficio=False, detalhes=''):

        retorno = Defensor(
            inicial=self,
            qualificacao=self.qualificacao,
            tipo=tipo,
            origem=origem,
            prazo=prazo,
            prioridade=prioridade)

        retorno.marcar(
            atuacao_id=atuacao_id,
            data_agendamento=data_agendamento,
            agendado_por=agendado_por,
            categoria_de_agenda=categoria_de_agenda,
            forma_atendimento=forma_atendimento,
            anotacao=anotacao,
            oficio=oficio,
            detalhes=detalhes
        )

        # define o requerente principal para o atendimento
        retorno.set_requerente(self.requerente.pessoa)

        return retorno

    def remarcar(self, origem, atuacao_id, data_agendamento, agendado_por, justificativa=None, categoria_de_agenda=None,
                 forma_atendimento=None, automatico=False, prazo=False, prioridade=Atendimento.PRIORIDADE_0,
                 anotacao=None, oficio=False, detalhes=''):

        novo = Defensor(
            inicial=self.inicial,
            qualificacao=self.qualificacao,
            tipo=self.tipo,
            prazo=prazo,
            prioridade=prioridade)

        novo.origem = origem

        novo.marcar(
            atuacao_id=atuacao_id,
            data_agendamento=data_agendamento,
            agendado_por=agendado_por,
            categoria_de_agenda=categoria_de_agenda,
            forma_atendimento=forma_atendimento,
            anotacao=anotacao,
            original=self,
            oficio=oficio,
            detalhes=detalhes
        )

        # Move relacionamentos dependentes para novo agendamento
        from .services import AtendimentoService
        service = AtendimentoService(self)
        service.transferir_relacionamentos(
            atendimento_destino=novo
        )

        self.remarcado_auto = automatico
        self.remarcado = novo
        self.save()

        if justificativa and not hasattr(novo, 'justificativa'):
            justificativa = Justificativa(atendimento=novo, justificativa=justificativa)
            justificativa.save()

        return novo

    def get_atuacao(self):

        data_referencia = self.data_cadastro

        if self.data_atendimento:
            data_referencia = self.data_atendimento
        elif self.data_agendamento:
            data_referencia = self.data_agendamento

        return Atuacao.get_atuacao_em_dia(self.defensoria, self.defensor, self.substituto, data_referencia)

    def eh_diligencia(self):
        if self.qualificacao.tipo == Qualificacao.TIPO_PEDIDO and self.qualificacao.nucleo.diligencia:
            return True
        else:
            return False

    def pode_atender_retroativo(self, usuario):

        if self.data_agendamento:
            data_base = self.data_agendamento.date()
        elif self.data_atendimento:
            data_base = self.data_atendimento.date()
        else:
            return False

        # Só verifica a permissão se a data do agendamento é menor ou igual a hoje
        if data_base <= date.today() and usuario.has_perm('atendimento.atender_retroativo'):
            return True

        return Evento.objects.filter(
            Q(ativo=True) &
            Q(tipo=Evento.TIPO_PERMISSAO) &
            Q(data_validade__gte=date.today()) &
            Q(data_ini__lte=data_base) &
            Q(data_fim__gte=data_base) &
            ~Q(data_autorizacao=None) &
            (
                Q(comarca=None) |
                Q(defensoria=self.defensoria) |
                (
                    Q(comarca=self.defensoria.comarca) &
                    Q(defensoria=None)
                )
            )
        ).exists()

    def pode_ver_atendimento(self, usuario):
        # Pode ver atendimento (caixa verde) se atende as condições:
        # 1. Não realizado ou
        # 2. Agendado para hoje ou
        # 3. Realizado hoje ou
        # 4. Permissão para atender retroativo
        # 5. Não é atendimento para processo ou para multidisciplinar
        return (
            not self.realizado or
            self.agendado_hoje or
            self.realizado_hoje or
            self.pode_atender_retroativo(usuario)
        ) and not (
            self.tipo == Atendimento.TIPO_PROCESSO or
            (
                self.defensoria.nucleo and
                self.defensoria.nucleo.multidisciplinar
            )
        )

    def pode_ver_detalhes_do_atendimento(self, usuario):
        # Pode ver detalhes do atendimento (dentro da caixa verde) se atende a uma das condições:
        # 1. Agendado para hoje e passou pela recepção
        # 2. Pedido de apoio a núcleo especializado
        # 3. Agendado para defensoria de plantão ou itinerante
        # 4. Permissão para atender retroativo

        pode_atender_sem_liberar = usuario.has_perm('atendimento.atender_sem_liberar')

        return (
            self.pode_atender_retroativo(usuario) or
            (self.agendado_hoje and (self.recepcao or pode_atender_sem_liberar)) or
            (self.defensoria and self.defensoria.nucleo and (
                self.tipo == self.TIPO_NUCLEO or
                self.defensoria.nucleo.plantao or
                self.defensoria.nucleo.itinerante
            ))
        )


class ViewAtendimentoDefensor(models.Model):
    """View SQL public.vw_atendimentos_defensor utilizada no Painel do Defensor"""

    id = models.IntegerField('ID', db_column='atendimento_ptr_id', primary_key=True)
    numero = models.CharField('Número', max_length=256)
    tipo = models.SmallIntegerField('Tipo', choices=Atendimento.LISTA_TIPO)
    data_agendamento = models.DateTimeField('Data do agendamento')
    data_atendimento = models.DateTimeField('Data do atendimento')

    requerente_nome = models.CharField('Requerente nome', max_length=256)
    requerente_nome_social = models.CharField('Requerente nome social', max_length=256)

    requerido_nome = models.CharField('Requerido nome', max_length=256)
    requerido_nome_social = models.CharField('Requerido nome social', max_length=256)

    agenda_id = models.IntegerField('Agenda ID')
    forma_atendimento_id = models.IntegerField('Forma de atendimento ID')

    inicial_id = models.IntegerField('Inicial ID')
    inicial_numero = models.CharField('Inicial Número', max_length=256)

    origem_id = models.IntegerField('Origem ID')
    origem_tipo = models.SmallIntegerField('Tipo Origem')

    recepcao_id = models.IntegerField('Atendimento Recepção ID')
    data_atendimento_recepcao = models.DateTimeField('Data do atendimento da Recepção')

    defensor_id = models.IntegerField('Defensor ID')
    defensor_nome = models.CharField('Defensor nome', max_length=256)

    substituto_id = models.IntegerField('Substituto ID')
    substituto_nome = models.CharField('Substituto nome', max_length=256)

    responsavel_id = models.IntegerField('Responsável ID')
    responsavel_nome = models.CharField('Responsável nome', max_length=256)

    defensoria_id = models.IntegerField('Defensoria ID')
    defensoria_nome = models.CharField('Defensoria nome', max_length=256)

    comarca_id = models.IntegerField('Comarca ID')

    nucleo_id = models.IntegerField('Núcleo ID')
    nucleo_nome = models.CharField('Núcleo nome', max_length=256)

    area_nome = models.CharField('Área nome', max_length=256)
    qualificacao_nome = models.CharField('Qualificação nome', max_length=256)

    especializado_id = models.IntegerField('Especializado ID')

    ativo = models.BooleanField('Ativo')
    prazo = models.BooleanField('Prazo')
    prioridade = models.SmallIntegerField('Prioridade')
    extra = models.BooleanField('Extra-Pauta')

    cadastrado_por_nome = models.CharField('Cadastrado por nome', max_length=256)
    liberado_por_nome = models.CharField('Liberado por nome', max_length=256)
    atendido_por_nome = models.CharField('Atendido por nome', max_length=256)

    defensoria_origem_id = models.IntegerField('Defensoria Origem ID')
    defensoria_origem_nome = models.CharField('Defensoria Origem nome', max_length=256)

    historico_agendamento = models.TextField('Histórico Agendamento')

    class Meta:
        managed = False
        db_table = 'vw_atendimentos_defensor'


class TipoVulnerabilidade(AuditoriaAbstractMixin):
    nome = models.CharField(verbose_name='Tipo de atendimento', null=False, blank=False, max_length=100)
    descricao = models.TextField(verbose_name='Descrição da vulnerabilidade', null=True, blank=True, max_length=500)

    class Meta:
        verbose_name = 'Tipo de Vulnerabilidade Digital'
        verbose_name_plural = 'Tipos de Vulnerabilidades Digitais'

    def __str__(self):
        return '{} - {}'.format(self.id, self.nome)


class AtendimentoVulnerabilidade(models.Model):
    atendimento = models.ForeignKey(
        Atendimento,
        verbose_name='Atendimento',
        null=False, blank=False,
        on_delete=models.DO_NOTHING)

    vulnerabilidade = models.ForeignKey(
        TipoVulnerabilidade,
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'atendimento_atendimento_vulnerabilidade'
        verbose_name = 'Atendimento/Vulnerabilidade'
        verbose_name_plural = 'Atendimentos/Vulnerabilidades'


class Coletivo(models.Model):
    atendimento = models.OneToOneField('Atendimento', on_delete=models.DO_NOTHING)
    comunidade = models.ForeignKey('assistido.Pessoa', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    propac = models.CharField(max_length=25)

    def __str__(self):
        return self.comunidade.nome

    class Meta:
        app_label = 'atendimento'
        verbose_name = u'Atendimento Coletivo'
        verbose_name_plural = u'Atendimentos Coletivos'


class Qualificacao(models.Model):

    TIPO_PEDIDO = 10
    TIPO_ATIVIDADE = 20
    TIPO_ANOTACAO = 30
    TIPO_NOTIFICACAO = 31
    TIPO_TAREFA = 40
    TIPO_REMETIMENTO = 50
    TIPO_ARQUIVAMENTO_COM_RESOLUCAO = 60
    TIPO_ARQUIVAMENTO_SEM_RESOLUCAO = 61
    TIPO_DESARQUIVAMENTO = 62

    LISTA_TIPO = (
        (TIPO_PEDIDO, u'Pedido'),
        (TIPO_ATIVIDADE, u'Atividade'),
        (TIPO_ANOTACAO, u'Anotação'),
        (TIPO_NOTIFICACAO, u'Notificação (chatbot)'),
        (TIPO_TAREFA, u'Tarefa'),
        (TIPO_REMETIMENTO, u'Remetimento atendimento'),
        (TIPO_ARQUIVAMENTO_COM_RESOLUCAO, u'Arquivamento com resolução'),
        (TIPO_ARQUIVAMENTO_SEM_RESOLUCAO, u'Arquivamento sem resolução'),
        (TIPO_DESARQUIVAMENTO, u'Desarquivamento'),
    )

    tipo = models.PositiveSmallIntegerField(choices=LISTA_TIPO, default=TIPO_PEDIDO)
    area = models.ForeignKey('contrib.Area', on_delete=models.DO_NOTHING)
    nucleo = models.ForeignKey('nucleo.Nucleo', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    defensorias = models.ManyToManyField('contrib.Defensoria', related_name='qualificacoes', blank=True)
    especializado = models.ForeignKey('Especializado', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    numero = models.SmallIntegerField(null=False, blank=False, default=0)
    titulo = models.CharField(max_length=255)
    titulo_norm = models.CharField(max_length=255, default='', db_index=True)
    texto = models.TextField(blank=True, null=True, default=None)
    perguntas = models.TextField(blank=True, null=True, default=None)
    documentos = models.TextField(blank=True, null=True, default=None)
    conta_estatistica = models.BooleanField(help_text='Conta Estatísticas?', default=True)
    multiplica_estatistica = models.BooleanField(
        help_text='Permite informar valor do campo Atendimento.multiplicador para multiplicar o valor nos relatórios?',
        default=False)
    disponivel_para_agendamento_via_app = models.BooleanField(
        verbose_name='Disponível para agendamento via apps (Luna, eDefensor, etc)?',
        default=False)
    exibir_em_atendimentos = models.BooleanField(
        verbose_name='Indica se deve ser exibido ao usuário final na tela de seleção de qualificações de atendimento',
        default=True)
    peso = models.DecimalField(
        null=True,
        blank=True,
        max_digits=16,
        decimal_places=1,
        default=0,
        help_text=u'Campo opcional para ser utilizado em relatórios que computam peso na qualificação de atendimento'
    )

    ativo = models.BooleanField(default=True)

    modelos_documentos = models.ManyToManyField('ModeloDocumento', related_name='qualificacoes', blank=True)

    acao = models.ForeignKey('processo.Acao', verbose_name='Processo Ação', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    orgao_encaminhamento = models.ForeignKey('Encaminhamento', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    assuntos = models.ManyToManyField(
        to='processo.Assunto',
        through='QualificacaoAssunto',
        through_fields=('qualificacao', 'assunto'))

    objects = managers.QualificacaoManager()

    def get_eh_qualificacao_sms(self):
        return self.titulo.encode('ascii', 'replace').strip().lower() == "sms"

    eh_qualificacao_sms = cached_property(get_eh_qualificacao_sms, name='eh_qualificacao_sms')

    class Meta:
        app_label = 'atendimento'
        ordering = ['-ativo', 'titulo']
        verbose_name = u'Qualficação'
        verbose_name_plural = u'Qualificações'

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        self.titulo_norm = Util.normalize(self.titulo)
        super(Qualificacao, self).save(*args, **kwargs)


class QualificacaoAssunto(AuditoriaAbstractMixin):
    qualificacao = models.ForeignKey('Qualificacao', verbose_name=u'Qualificação', blank=False, null=False, on_delete=models.DO_NOTHING)  # noqa: E501
    assunto = models.ForeignKey('processo.Assunto', verbose_name=u'Assunto Processual', blank=False, null=False, on_delete=models.DO_NOTHING)  # noqa: E501
    principal = models.BooleanField(verbose_name='Principal', blank=False, null=False, default=False)

    class Meta:
        app_label = 'atendimento'
        db_table = 'atendimento_qualificacao_assunto'
        ordering = ['qualificacao', '-principal', 'assunto']
        verbose_name = u'Assunto de Qualificação'
        verbose_name_plural = u'Assuntos das Qualificações'
        unique_together = ('assunto', 'qualificacao')

    # def __str__(self):
    #     return u'{} - {}'.format(self.qualificacao.nome, self.assunto.nome)


class Pergunta(models.Model):
    qualificacao = models.ForeignKey('Qualificacao', on_delete=models.DO_NOTHING)
    slug = models.CharField(max_length=64, unique=True)
    texto = models.CharField(max_length=255, default="")
    dica = models.CharField(max_length=255, blank=True, null=True)
    obrigatorio = models.BooleanField(verbose_name='Pergunta obrigatória?', blank=False, null=False, default=False)

    class Meta:
        app_label = 'atendimento'
        verbose_name = u'Pergunta'
        verbose_name_plural = u'Perguntas'

    def __str__(self):
        return self.texto


class Procedimento(models.Model):
    TIPO_AGENDAMENTO_INICIAL = 1
    TIPO_AGENDAMENTO_RETORNO = 2
    TIPO_ENCAMINHAMENTO = 3
    TIPO_INFORMACAO = 4
    TIPO_REAGENDAMENTO = 5
    # DPE-AM
    TIPO_INFORMACAO_ASSISTIDO = 6
    TIPO_RECLAMACAO = 7

    LISTA_TIPO = (
        (TIPO_AGENDAMENTO_INICIAL, 'Agendamento Inicial'),
        (TIPO_AGENDAMENTO_RETORNO, 'Agendamento Retorno'),
        (TIPO_ENCAMINHAMENTO, 'Encaminhamento'),
        (TIPO_INFORMACAO, 'Informação'),
        (TIPO_REAGENDAMENTO, 'Reagendamento'),
        # DPE-AM
        (TIPO_INFORMACAO_ASSISTIDO, 'Informação ao Assistido'),
        (TIPO_RECLAMACAO, 'Reclamação')
    )

    data_cadastro = models.DateTimeField('Data de cadastro', auto_now_add=True, editable=False)
    tipo = models.SmallIntegerField(choices=LISTA_TIPO)
    ligacao = models.ForeignKey('Atendimento', related_name='ligacao', on_delete=models.DO_NOTHING, db_index=True)
    agendamento = models.ForeignKey('Defensor', related_name='agendamento', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    informacao = models.ForeignKey('Informacao', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    encaminhamento = models.ForeignKey('Encaminhamento', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    # DPE-AM
    attprocedimento = models.ForeignKey('Atendimento', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # aponta atendimento que ocorreu o procedimento  # noqa: E501
    atendente = models.ForeignKey('auth.User', blank=False, null=True, default=None, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'atendimento'
        ordering = ['-data_cadastro', ]


def documento_file_name(instance, filename):
    import uuid

    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)

    if instance.atendimento:
        return '/'.join(['atendimento', str(instance.atendimento.at_inicial.numero), filename])

    return '/'.join(['propac-tarefas', filename])


class Documento(models.Model):

    STATUS_RESPOSTA_PENDENTE = 0
    STATUS_RESPOSTA_SIM = 1
    STATUS_RESPOSTA_NAO = 2

    LISTA_STATUS_RESPOSTA = (
        (STATUS_RESPOSTA_PENDENTE, u'Pendente'),
        (STATUS_RESPOSTA_SIM, u'Respondido'),
        (STATUS_RESPOSTA_NAO, u'Não Respondido'),
    )

    atendimento = models.ForeignKey('Atendimento', blank=True, null=True, on_delete=models.DO_NOTHING)
    defensoria = models.ForeignKey('contrib.Defensoria', blank=True, null=True, related_name='documentos_atendimento', on_delete=models.DO_NOTHING)  # noqa: E501
    impedimento = models.ForeignKey('Impedimento', blank=True, null=True, related_name='documentos_avaliacao', on_delete=models.DO_NOTHING)  # noqa: E501
    pessoa = models.ForeignKey('assistido.PessoaAssistida', blank=True, null=True, related_name='+', on_delete=models.DO_NOTHING)  # noqa: E501

    modelo = models.ForeignKey('ModeloDocumento', blank=True, null=True, related_name='modelo', on_delete=models.DO_NOTHING)  # noqa: E501
    documento = models.ForeignKey('contrib.Documento', verbose_name='Tipo', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    documento_online = models.ForeignKey('djdocuments.Documento', verbose_name='Documento', on_delete=models.SET_NULL, null=True, blank=True)  # noqa: E501
    arquivo = models.FileField(verbose_name='Anexo', upload_to=documento_file_name, null=True, blank=True, default=None, validators=[validate_file_size_extension])  # noqa: E501
    nome = models.CharField(max_length=255, blank=True, null=True, default=None)
    ativo = models.BooleanField(default=True)

    data_enviado = models.DateTimeField(blank=True, null=True)
    enviado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    data_exclusao = models.DateTimeField('Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)

    prazo_resposta = models.DateTimeField(blank=True, null=True, default=None)
    status_resposta = models.PositiveSmallIntegerField(choices=LISTA_STATUS_RESPOSTA, blank=True, null=True, default=None)  # noqa: E501
    documento_resposta = models.OneToOneField('self', related_name='origem_resposta', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    # campos para controle de avaliação de documentos enviados via API
    analisar = models.BooleanField(default=False)
    data_analise = models.DateTimeField(blank=True, null=True)
    analisado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    documento_assinado = models.ForeignKey(
        to='atendimento.DocumentoAssinado',
        related_name='+',
        blank=True,
        null=True,
        default=None,
        on_delete=models.DO_NOTHING
    )
    pasta = models.ForeignKey("PastaDocumento", on_delete=models.PROTECT,
                              related_name="documentos", null=True, blank=True)

    objects = managers.DocumentoManager()

    @property
    def nome_norm(self):
        return Util.normalize(self.nome)

    @property
    def pendente(self):
        if not self.documento_online_id and not self.arquivo:
            return True
        else:
            return False

    @property
    def tarefa(self):
        return Tarefa.objects.get(documento=self)

    def excluir(self, excluido_por, agora=datetime.now()):
        """
        Excluir Documento(Atendimento), GED (com Revogar Assinaturas)
        :param excluido_por: Servidor do Solar
        :param agora: timestamp do momento de exclusão
        :param excluido_por_usuario: User para exclusão do GED
        :return:
        """
        with transaction.atomic():
            pode_excluir = True

            # Só exclui GED caso tenha apenas 1 vínculo com Documento(Atendimento).
            # Exemplo: diligência gera 2 vínculos de GED com Documento(Atendimento)
            if self.documento_online and self.documento_online.documento_set.ativos().count() == 1:
                from djdocuments_solar_backend.backend import SolarDefensoriaBackend
                pode_excluir = SolarDefensoriaBackend().excluir_documento(
                    document=self.documento_online,
                    usuario=excluido_por.usuario,
                    agora=agora
                )

            if pode_excluir:
                self.data_exclusao = agora
                self.excluido_por = excluido_por
                self.ativo = False
                self.save()

    def __str__(self):
        return self.nome

    class Meta:
        app_label = 'atendimento'
        ordering = ['-ativo', '-atendimento__numero', 'nome']
        indexes = [
            models.Index(fields=['atendimento', 'documento_online'], name='atendimento_documento_idx_001'),
        ]


class DocumentoAssinado(AuditoriaAbstractMixin):
    atendimento = models.ForeignKey('Atendimento', blank=True, null=True, on_delete=models.DO_NOTHING)
    arquivo = models.FileField("Arquivo", upload_to=documento_file_name)
    data_enviado = models.DateTimeField('Data de Envio', null=True, blank=False, auto_now_add=True, editable=False)


class ModeloDocumento(models.Model):

    TIPO_GED = 0
    TIPO_JASPER = 1

    LISTA_TIPO = (
        (TIPO_GED, u'GED'),
        (TIPO_JASPER, u'Jasper'),
    )

    nome = models.CharField(max_length=255, blank=False, null=False)
    tipo = models.PositiveSmallIntegerField(choices=LISTA_TIPO, blank=False, null=False, default=TIPO_GED)

    ged_modelo = models.ForeignKey('djdocuments.Documento', verbose_name='Documento', on_delete=models.SET_NULL, null=True, blank=True)  # noqa: E501

    jasper_resource = models.CharField(max_length=255, blank=True, null=True, default=None)
    jasper_name = models.CharField(max_length=255, blank=True, null=True, default=None)
    jasper_params = models.CharField(max_length=255, blank=True, null=True, default=None)

    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Tarefa(models.Model):
    PRIORIDADE_URGENTE = 0
    PRIORIDADE_ALTA = 1
    PRIORIDADE_NORMAL = 2
    PRIORIDADE_BAIXA = 3
    PRIORIDADE_ALERTA = 4
    PRIORIDADE_COOPERACAO = 5

    LISTA_PRIORIDADE = (
        (PRIORIDADE_URGENTE, 'Urgente'),
        (PRIORIDADE_ALTA, 'Alta'),
        (PRIORIDADE_NORMAL, 'Normal'),
        (PRIORIDADE_BAIXA, 'Baixa'),
        (PRIORIDADE_ALERTA, 'Alerta'),
        (PRIORIDADE_COOPERACAO, 'Cooperação'),
    )

    STATUS_CADASTRO = 0
    STATUS_PENDENTE = 1
    STATUS_CUMPRIDO = 2

    TAREFA_AGUARDANDO = 0
    TAREFA_ATRASADA = 1
    TAREFA_PENDENCIA = 2
    TAREFA_CUMPRIDA = 3
    TAREFA_FINALIZADA = 4
    TAREFA_EXCLUIDA = 999

    LISTA_STATUS = (
        (STATUS_CADASTRO, 'Cadastrado'),
        (STATUS_PENDENTE, 'Pendente'),
        (STATUS_CUMPRIDO, 'Cumprido'),
    )

    LISTA_STATUS_BUSCA = (
        (TAREFA_AGUARDANDO, 'Aguardando'),
        (TAREFA_ATRASADA, 'Atrasada'),
        (TAREFA_PENDENCIA, 'C/ Pendência'),
        (TAREFA_CUMPRIDA, 'Cumprida'),
        (TAREFA_FINALIZADA, 'Finalizada'),
        (TAREFA_EXCLUIDA, 'Excluída'),
    )

    documentos = models.ManyToManyField('djdocuments.Documento',
                                        related_name='%(app_label)s_%(class)s_tarefas',
                                        blank=True)

    tipo = models.ForeignKey('Qualificacao', blank=True, null=True, default=None, related_name='+', on_delete=models.DO_NOTHING)  # noqa: E501
    tarefa_oficio = models.BooleanField('É do tipo ofício?', default=False)

    origem = models.ForeignKey('self', related_name='all_respostas', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    documento = models.ForeignKey('Documento', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    atendimento = models.ForeignKey('Atendimento', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    movimento = models.ForeignKey("propac.Movimento", null=True, blank=True, on_delete=models.DO_NOTHING,
                                  related_name="tarefas",
                                  verbose_name="movimento (propac/procedimento)",
                                  help_text="Movimento de Propac ou Procedimento.")
    processo = models.ForeignKey('processo.Processo', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    resposta_para = models.ForeignKey('contrib.Defensoria', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    setor_responsavel = models.ForeignKey('contrib.Defensoria', related_name='+', blank=False, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    responsavel = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    finalizado = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    prioridade = models.SmallIntegerField(choices=LISTA_PRIORIDADE, blank=True, null=True, default=None)
    titulo = models.CharField(max_length=255, blank=True, null=True, default=None)
    descricao = models.TextField(blank=True, null=True, default=None)
    data_inicial = models.DateField(blank=True, null=True)
    data_final = models.DateField(blank=True, null=True)
    data_finalizado = models.DateTimeField(blank=True, null=True)
    status = models.SmallIntegerField(choices=LISTA_STATUS, blank=True, null=True, default=STATUS_CADASTRO)
    ativo = models.BooleanField(default=True)

    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    data_exclusao = models.DateTimeField('Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)

    objects = managers.BaseManager()

    @property
    def eh_alerta(self):
        return self.prioridade == self.PRIORIDADE_ALERTA

    @property
    def eh_cooperacao(self):
        return self.prioridade == self.PRIORIDADE_COOPERACAO

    @property
    def eh_tarefa(self):
        return self.prioridade not in (Tarefa.PRIORIDADE_ALERTA, Tarefa.PRIORIDADE_COOPERACAO)

    def pode_finalizar(self, usuario):

        pode = False

        if self.finalizado is None:
            if usuario.is_superuser:  # pode finalizar se é superusuario
                pode = True
            elif self.cadastrado_por == usuario.servidor:  # pode finalizar se for quem cadastrou
                pode = True
            elif hasattr(usuario.servidor, 'defensor'):
                # cooperação pode ser finalizada pelo defensor do setor solicitante
                if self.prioridade == Tarefa.PRIORIDADE_COOPERACAO:
                    pode = usuario.servidor.defensor.all_atuacoes.vigentes().nao_lotacoes().filter(
                        defensoria=self.resposta_para
                    ).exists()
                # alerta pode ser finalizado por um servidor do setor solicitante ou do setor responsável
                elif self.prioridade == Tarefa.PRIORIDADE_ALERTA:
                    pode = usuario.servidor.defensor.all_atuacoes.vigentes().filter(
                        defensoria__in=[self.resposta_para, self.setor_responsavel]
                    ).exists()
                # tarefa pode ser finalizado pelo defensor do setor responsável
                else:
                    pode = usuario.servidor.defensor.all_atuacoes.vigentes().nao_lotacoes().filter(
                        defensoria=self.setor_responsavel
                    ).exists()

                    # tarefa pode ser finalizada se o defensor foi o responsável pelo atendimento itinerante
                    if not pode:
                        if (self.atendimento.defensor.defensor == usuario.servidor.defensor and
                                self.atendimento.defensor.defensoria.nucleo and
                                self.atendimento.defensor.defensoria.nucleo.itinerante):
                            pode = True

        return pode

    @property
    def finalizada(self):
        return self.finalizado_id is not None

    @property
    def cumprida(self):
        return self.status == self.STATUS_CUMPRIDO

    @property
    def com_pendencia(self):
        return self.status == self.STATUS_PENDENTE

    @property
    def atrasada(self):
        if self.data_final and self.data_final < date.today() and self.status == self.STATUS_CADASTRO and \
           not self.finalizada and self.ativo:
            return True
        else:
            return False

    def dias_atrasada(self):
        if self.atrasada:
            delta = date.today() - self.data_final
            return delta.days
        else:
            return 0

    def excluir(self, excluido_por):
        self.data_exclusao = datetime.now()
        self.excluido_por = excluido_por
        self.ativo = False
        self.save()

    def finalizar(self, servidor, data_finalizado=None):

        if data_finalizado:
            self.data_finalizado = data_finalizado
        else:
            self.data_finalizado = timezone.now()

        self.finalizado = servidor
        self.save()

    @property
    def respostas(self):
        return Tarefa.objects.filter(origem=self, ativo=True).order_by('data_finalizado')

    def responder(self, resposta, respondido_por, status=STATUS_PENDENTE):

        setor_responsavel = None

        if self.resposta_para:
            if status == self.STATUS_CADASTRO:
                setor_responsavel = self.resposta_para
            else:
                setor_responsavel = self.setor_responsavel

        resposta = Tarefa.objects.create(
            origem=self,
            descricao=resposta,
            finalizado=respondido_por,
            data_finalizado=datetime.now(),
            setor_responsavel=setor_responsavel,
            status=status
        )

        return resposta

    def __str__(self):
        if self.origem:
            return "{titulo} [resposta]".format(titulo=self.origem.titulo)
        else:
            return self.titulo

    class Meta:
        app_label = 'atendimento'
        ordering = ['-ativo', '-atendimento__numero', 'titulo']
        permissions = (
            ('view_all_tarefas', u'Pode ver todas tarefas do gabinete'),
        )
        indexes = [
            models.Index(fields=['atendimento', 'responsavel', 'data_final'], name='atendimento_tarefa_idx_001'),
            models.Index(fields=['data_finalizado'], condition=Q(origem=None), name='atendimento_tarefa_idx_002'),
            models.Index(fields=['data_final', 'status'], condition=Q(origem=None, data_finalizado=None), name='atendimento_tarefa_idx_003'),
            models.Index(fields=['status'], condition=Q(origem=None, data_finalizado=None), name='atendimento_tarefa_idx_004'),
        ]


class TarefaVisualizacao(models.Model):
    tarefa = models.ForeignKey(Tarefa, related_name='visualizacoes', on_delete=models.DO_NOTHING)
    visualizada_por = models.ForeignKey('contrib.Servidor', related_name='+', on_delete=models.DO_NOTHING)
    visualizada_em = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)

    class Meta:
        db_table = 'atendimento_tarefa_visualizacao'
        indexes = [
            models.Index(fields=['tarefa', 'visualizada_por'], name='atendimento_tarefa_vis_idx_001'),
        ]


class Especializado(models.Model):
    nome = models.CharField(max_length=255)
    nucleo = models.ForeignKey('nucleo.Nucleo', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        app_label = 'atendimento'


class Impedimento(models.Model):

    RESULTADO_NAO_AVALIADO = 0
    RESULTADO_DEFERIDO = 10
    RESULTADO_INDEFERIDO = 20

    LISTA_RESULTADO = (
        (RESULTADO_NAO_AVALIADO, 'Não Avaliado'),
        (RESULTADO_DEFERIDO, 'Deferido'),
        (RESULTADO_INDEFERIDO, 'Indeferido'),
    )

    BAIXA_NAO_REALIZADA = 0
    BAIXA_REMARCADO = 10
    BAIXA_ENCAMINHADO = 20
    BAIXA_NEGADO = 30

    LISTA_BAIXA = (
        (BAIXA_NAO_REALIZADA, 'Não Realizada'),
        (BAIXA_REMARCADO, 'Retorno Marcado'),
        (BAIXA_ENCAMINHADO, 'Encaminhamento Marcado'),
        (BAIXA_NEGADO, 'Atendimento Negado'),
    )

    defensor = models.ForeignKey('defensor.Defensor', on_delete=models.DO_NOTHING)
    pessoa = models.ForeignKey(PessoaAssistida, related_name='impedimentos', on_delete=models.DO_NOTHING)
    atendimento = models.ForeignKey(Defensor, related_name='impedimentos', blank=False, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    razao = models.ForeignKey(Qualificacao, blank=False, null=True, default=None, related_name='+', on_delete=models.DO_NOTHING)  # noqa: E501
    medida_pretendida = models.TextField(blank=True, null=True)
    justificativa = models.TextField(blank=False, null=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    # Dados do recurso do Assistido
    data_recurso = models.DateTimeField(blank=True, null=True, default=None)
    recorrido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    # Dados do recebimento pelo DPG
    data_recebimento = models.DateTimeField(blank=True, null=True, default=None)
    recebido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    # Dados da comunicação para Corregedoria
    anotacao_comunicacao = models.TextField(blank=False, null=True)
    data_comunicacao = models.DateTimeField(blank=True, null=True, default=None)
    comunicado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    # Dados da verificação (parecer) da Corregedoria
    anotacao_verificacao = models.TextField(blank=False, null=True)
    data_verificacao = models.DateTimeField(blank=True, null=True, default=None)
    verificado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    # Dados da avaliação do DPG
    anotacao_avaliacao = models.TextField(blank=False, null=True)
    data_avaliacao = models.DateTimeField(blank=True, null=True, default=None)
    avaliado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    resultado = models.SmallIntegerField(choices=LISTA_RESULTADO, blank=True, null=True, default=RESULTADO_NAO_AVALIADO)

    # Dados da baixa da Diretoria Regional
    anotacao_baixa = models.TextField(null=True)
    tipo_baixa = models.SmallIntegerField(choices=LISTA_BAIXA, blank=True, null=True, default=BAIXA_NAO_REALIZADA)
    data_baixa = models.DateTimeField(blank=True, null=True, default=None)
    baixado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    ativo = models.BooleanField(default=True)

    objects = managers.ImpedimentoManager()

    def __str__(self):
        return '{} - {}'.format(self.pessoa, self.defensor).upper()

    class Meta:
        app_label = 'atendimento'
        ordering = ['-ativo', 'data_cadastro', 'pessoa__nome', 'defensor']

    @property
    def avaliado(self):
        return self.data_avaliacao is not None

    @property
    def recorrido(self):
        return self.data_recurso is not None

    @property
    def verificado(self):
        return self.data_verificacao is not None


class Justificativa(models.Model):
    atendimento = models.OneToOneField('atendimento.Atendimento', on_delete=models.DO_NOTHING)
    justificativa = models.TextField(blank=True, null=True, default=None)

    class Meta:
        app_label = 'atendimento'


class Assunto(models.Model):
    titulo = models.CharField(verbose_name='Título', max_length=256, null=False, blank=False)
    codigo = models.CharField(verbose_name='Código', max_length=256, null=True, blank=True)
    pai = models.ForeignKey('self', related_name='filhos', null=True, blank=True, on_delete=models.DO_NOTHING)
    ordem = models.IntegerField(null=False, blank=False)
    data_cadastro = models.DateTimeField('Data de cadastro', auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    data_exclusao = models.DateTimeField('Data de Exclusao', blank=True, null=True)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    descricao = models.CharField(verbose_name='Descição Completa (Caminho)', max_length=256, null=True, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return '{0}'.format(self.titulo)

    class Meta:
        app_label = 'atendimento'
        ordering = ['-ativo', 'pai__ordem', 'ordem']


class Arvore(models.Model):

    atendimento = models.OneToOneField('atendimento.Atendimento', db_index=True, on_delete=models.DO_NOTHING)
    conteudo = models.TextField('Conteúdo', blank=True, null=True, default=None)
    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    data_modificacao = models.DateTimeField(u'Data de Modificação', null=True, blank=False, editable=False)
    data_exclusao = models.DateTimeField(u'Data de Exclusão', null=True, blank=False, editable=False)
    ativo = models.BooleanField(default=True)

    def excluir(self):
        self.data_exclusao = datetime.now()
        self.ativo = False
        self.save()


class FormaAtendimento(AuditoriaAbstractMixin):

    TIPO_PRESENCIAL = 'P'  # presencial = True
    TIPO_REMOTO = 'R'  # presencial = False

    LISTA_TIPO = (
        (TIPO_PRESENCIAL, 'Presencial'),
        (TIPO_REMOTO, 'Remoto'),
    )

    nome = models.CharField(max_length=512, null=False, db_index=True)
    data_inicial = models.DateTimeField(verbose_name='Data inicial', null=False, blank=False)
    data_final = models.DateTimeField(verbose_name='Data final', null=True, blank=True, default=None)
    conta_estatistica = models.BooleanField(
        verbose_name='Conta estatísticas',
        help_text='Conta Estatística?',
        default=True
    )
    aparece_defensor = models.BooleanField(
        verbose_name='Aparece para o defensor?',
        help_text='Aparece para o defensor?',
        default=True
    )
    aparece_recepcao = models.BooleanField(
        verbose_name='Aparece para a recepção?',
        help_text='Aparece para a recepção?',
        default=True
    )
    por_email = models.BooleanField(
        verbose_name='Atendido por e-mail?',
        help_text='O atendimento foi por e-mail?',
        default=False
    )
    por_app_mensagem = models.BooleanField(
        verbose_name='Atendido por mensagem?',
        help_text='O atendimento foi por WhatsApp/Telegram?',
        default=False
    )
    por_ligacao = models.BooleanField(
        verbose_name='Atendido por ligação?',
        help_text='O atendimento foi por ligação?',
        default=False
    )
    presencial = models.BooleanField(
        verbose_name='Atendido presencialmente?',
        help_text='O atendimento foi presencial?',
        default=False
    )

    objects = managers.FormaAtendimentoManager()

    class Meta:
        db_table = 'atendimento_forma_atendimento'
        verbose_name = u'Forma de atendimento'
        verbose_name_plural = u'Formas de atendimento'
        ordering = ['nome']
        unique_together = ('nome', 'data_inicial', 'data_final')

    def __str__(self):
        return '{0}'.format(self.nome)


class TipoColetividade(AuditoriaAbstractMixin):
    nome = models.CharField(max_length=512, null=False, db_index=True)
    data_inicial = models.DateTimeField(verbose_name='Data inicial', null=False, blank=False)
    data_final = models.DateTimeField(verbose_name='Data final', null=True, blank=True, default=None)
    conta_estatistica = models.BooleanField(
        verbose_name='Conta estatísticas',
        help_text='Conta Estatística?',
        default=True
    )
    individual = models.BooleanField(
        verbose_name='Atendimento individual?',
        help_text='O atendimento é para caso individual?',
        default=False
    )
    coletivo = models.BooleanField(
        verbose_name='Atendimento coletivo?',
        help_text='O atendimento é para caso coletivo?',
        default=False
    )
    difuso = models.BooleanField(
        verbose_name='Atendimento coletivo difuso?',
        help_text='O atendimento é para caso de coletividade difusa?',
        default=False
    )

    objects = managers.TipoColetividadeManager()

    class Meta:
        verbose_name = u'Tipo de Coletividade'
        verbose_name_plural = u'Tipos de Coletividade'
        ordering = ['nome']
        unique_together = ('nome', 'data_inicial', 'data_final')

    def __str__(self):
        return '{0}'.format(self.nome)


class MotivoExclusao(AuditoriaAbstractMixin):
    nome = models.CharField(max_length=512, null=False, db_index=True)

    class Meta:
        verbose_name = u'Motivo de Exclusão'
        verbose_name_plural = u'Motivos de Exclusão'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Reclamacao(models.Model):
    ESTABELECIMENTO_COMERCIAL = 1
    ESTABELECIMENTO_INDUSTRIAL = 2
    ESTABELECIMENTO_RESIDENCIAL = 3

    LISTA_TIPO_ESTABELECIMENTO = (
        (ESTABELECIMENTO_COMERCIAL, 'Comercial'),
        (ESTABELECIMENTO_INDUSTRIAL, 'Industrial'),
        (ESTABELECIMENTO_RESIDENCIAL, 'Residencial'),
    )

    data = models.DateTimeField('Data e hora reclamacao', blank=True, null=True, default=None)
    assistido = models.CharField(max_length=200)
    atendente = models.CharField(max_length=200)
    reclamacao = models.CharField(max_length=1000)

    nome_estabelecimento = models.CharField(max_length=255, null=True)
    tipo_estabelecimento = models.SmallIntegerField(choices=LISTA_TIPO_ESTABELECIMENTO, null=True)
    endereco_estabelecimento = models.ForeignKey('contrib.Endereco', null=True, on_delete=models.DO_NOTHING)

    ativo = models.BooleanField(default=True)

    class Meta:
        app_label = 'atendimento'
        verbose_name = u'Reclamação'
        verbose_name_plural = u'Reclamações'


class GrupoDeDefensoriasParaAgendamento(models.Model):

    nome = models.CharField(verbose_name='Nome', max_length=256)
    defensorias = models.ManyToManyField(
        to='contrib.Defensoria',
        related_name='grupos_de_agendamento',
        blank=True,
        default=None
    )

    aceitar_agend_pauta = models.BooleanField(
        verbose_name='Aceitar agendamento na pauta',
        default=True,
        help_text='Permitir que as defensorias do grupo e o disk 129 agendem na pauta',
    )

    aceitar_agend_extrapauta = models.BooleanField(
        verbose_name='Aceitar agendamento extra-pauta',
        default=False,
        help_text='Permitir que as defensorias do grupo e o disk 129 agendem extra-pauta',
    )

    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Grupo de Agendamento'
        verbose_name_plural = 'Grupos de Agendamento'
        ordering = ['-ativo', 'nome']


class PastaDocumento(AuditoriaAbstractMixin):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    atendimento = models.ForeignKey("Atendimento", on_delete=models.PROTECT, related_name="pastas")

    class Meta:
        unique_together = ("atendimento", "nome")
        verbose_name = "Pastas doc. atendimento"
        verbose_name_plural = "Pastas doc. atendimentos"

    def __str__(self):
        return f"{self.nome}"


reversion.register(Acordo)
reversion.register(Encaminhamento)
reversion.register(Informacao)
reversion.register(Atendimento)
reversion.register(Defensor)
reversion.register(Coletivo)
reversion.register(Qualificacao)
reversion.register(Pergunta)
reversion.register(Procedimento)
reversion.register(Tarefa)
reversion.register(Especializado)
reversion.register(Impedimento)
reversion.register(GrupoDeDefensoriasParaAgendamento)
reversion.register(PastaDocumento)
