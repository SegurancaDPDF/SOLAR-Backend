# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging
from datetime import date, datetime, timedelta
from sys import getsizeof

# Bibliotecas de terceiros
import reversion
import re
from constance import config
from django_currentuser.db.models import CurrentUserField
from django.db import models, transaction
from django.db.models import deletion, Q
from django.utils.functional import cached_property
from dateutil.relativedelta import relativedelta

from contrib.models import Util
from core.models import AuditoriaAbstractMixin

from . import managers

logger = logging.getLogger(__name__)


class Assunto(models.Model):
    nome = models.CharField(max_length=512, null=False)
    codigo_eproc = models.CharField(max_length=25, blank=True, null=True, default=None)
    codigo_cnj = models.CharField(max_length=25, blank=True, null=True, default=None)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        app_label = 'processo'
        verbose_name = u'Assunto'
        verbose_name_plural = u'Assuntos'
        ordering = ['-ativo', 'nome']

    def __str__(self):
        return self.nome


class Prioridade(AuditoriaAbstractMixin):
    nome = models.CharField(max_length=512)
    codigo_mni = models.CharField(max_length=256)  # Código MNI (do sistema local)
    disponivel_para_peticionamento = models.BooleanField('Disponível para peticionamento?', default=False)

    class Meta:
        app_label = 'processo'
        verbose_name = u'Prioridade'
        verbose_name_plural = u'Prioridades'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class OutroParametro(AuditoriaAbstractMixin):
    TIPO_TEXTO = 0
    TIPO_NUMERO = 1
    TIPO_DATA = 2
    TIPO_LISTA = 3
    TIPO_BOOLEANO = 4

    LISTA_TIPO = (
        (TIPO_TEXTO, 'Texto'),
        (TIPO_NUMERO, 'Número'),
        (TIPO_DATA, 'Data'),
        (TIPO_LISTA, 'Lista'),
        (TIPO_BOOLEANO, 'Booleano'),
    )

    nome = models.CharField(max_length=512)
    tipo = models.SmallIntegerField(choices=LISTA_TIPO, default=TIPO_TEXTO)
    lista = models.CharField(max_length=255, null=True, blank=True)
    codigo_mni = models.CharField(max_length=512)  # Código MNI (do sistema local)

    class Meta:
        app_label = 'processo'
        ordering = ['nome']
        verbose_name = u'Outro Parâmetro'
        verbose_name_plural = u'Outros Parâmetros'

    def __str__(self):
        return self.nome


class ProcessoOutroParametro(models.Model):
    processo = models.ForeignKey('Processo', on_delete=models.PROTECT)
    outro_parametro = models.ForeignKey('OutroParametro', on_delete=models.PROTECT)
    valor = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'processo_processo_outros_parametros'
        ordering = ['processo', 'outro_parametro']
        unique_together = ('processo', 'outro_parametro')


class ProcessoQuerySet(models.QuerySet):

    def com_nome_defensor_em_parte(self, nome):
        return self.filter(parte__defensor__servidor__nome__icontains=nome)

    def com_defensor_em_parte(self, defensor):
        return self.filter(parte__defensor=defensor)


class Processo(models.Model):
    TIPO_EXTRA = 0
    TIPO_FISICO = 1
    TIPO_EPROC = 2
    TIPO_PAD = 3

    GRAU_0 = 0  # Usado como valor padrão e para tipo extrajudicial
    GRAU_1 = 1
    GRAU_2 = 2
    GRAU_3 = 3

    LISTA_TIPO = (
        (TIPO_EXTRA, 'Extrajudicial'),
        (TIPO_FISICO, 'Físico'),
        (TIPO_EPROC, 'Eletrônico'),
        (TIPO_PAD, 'Processo Administrativo Disciplinar (PAD)'),
    )

    LISTA_GRAU = (
        (GRAU_1, '1º Grau'),
        (GRAU_2, '2º Grau'),
        (GRAU_3, 'STF/STJ'),
    )

    SIGILO_0 = 0
    SIGILO_1 = 1
    SIGILO_2 = 2
    SIGILO_3 = 3
    SIGILO_4 = 4
    SIGILO_5 = 5

    LISTA_SIGILO = (
        (SIGILO_0, 'Público'),
        (SIGILO_1, 'Segredo de Justiça'),
        (SIGILO_2, 'Sigilo mínimo'),
        (SIGILO_3, 'Sigilo médio'),
        (SIGILO_4, 'Sigilo intenso'),
        (SIGILO_5, 'Sigilo absoluto'),
    )

    SITUACAO_MOVIMENTO = 0
    SITUACAO_BAIXADO = 1

    LISTA_SITUACAO = (
        (SITUACAO_MOVIMENTO, 'Movimento'),
        (SITUACAO_BAIXADO, 'Baixado'),
    )

    objects = ProcessoQuerySet.as_manager()

    numero = models.CharField('Número', max_length=50, null=True, blank=True)
    numero_puro = models.CharField('Número puro', max_length=50, null=False, blank=False, db_index=True)
    chave = models.CharField('Chave', max_length=50, null=True, blank=True)
    grau = models.SmallIntegerField(choices=LISTA_GRAU, default=GRAU_0)
    credencial_mni_cadastro = models.CharField(u'Credencial MNI de Cadastro', max_length=50, null=True, blank=True, default=None)

    tipo = models.SmallIntegerField(choices=LISTA_TIPO, default=TIPO_EPROC)
    nivel_sigilo = models.SmallIntegerField('Nível de Sigilo', choices=LISTA_SIGILO, default=SIGILO_0)
    intervencao_mp = models.BooleanField('Intervenção do Ministério Público', default=False, help_text='Intervenção do Ministério Público?')  # noqa: E501

    valor_causa = models.FloatField('Valor da Causa', default=0)
    calculo_judicial = models.CharField('Código do Cálculo Judicial', max_length=50, blank=True, null=True)

    competencia_mni = models.CharField('Competência Judicial', max_length=50, blank=True, null=True)

    comarca = models.ForeignKey('contrib.Comarca', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    area = models.ForeignKey('contrib.Area', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    vara = models.ForeignKey('contrib.Vara', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    acao = models.ForeignKey('Acao', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    acao_cnj = models.CharField(max_length=50, null=True, blank=True)
    assuntos = models.ManyToManyField('Assunto', through='ProcessoAssunto', through_fields=('processo', 'assunto'))
    prioridades = models.ManyToManyField('Prioridade', blank=True)
    outros_parametros = models.ManyToManyField('OutroParametro', through='ProcessoOutroParametro',
                                               through_fields=('processo', 'outro_parametro'),
                                               verbose_name='Outros Parâmetros')

    originario = models.ForeignKey('Processo', related_name='+', blank=True, null=True, default=None,
                                   verbose_name='Processo Originário', on_delete=models.DO_NOTHING)
    peticao_inicial = models.ForeignKey('Fase', related_name='+', blank=True, null=True, default=None,
                                        on_delete=models.DO_NOTHING)

    pre_cadastro = models.BooleanField(default=False)
    parte_pre_cadastro = models.CharField(max_length=250, null=True, blank=True)

    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                       on_delete=models.DO_NOTHING)

    # TODO: Migrar para AuditoriaAbstractMixin
    modificado_em = models.DateTimeField(
        auto_now=True,
        null=True
    )

    modificado_por = CurrentUserField(
        null=True,
        on_update=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_modificado_por'
    )

    data_exclusao = models.DateTimeField('Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)

    # Controle atualização processos pelo ProcAPI
    ultima_modificacao = models.DateTimeField('Data da Última Modificação no ProcAPI', null=True, blank=True)
    ultima_consulta = models.DateTimeField('Data da Última Consulta para Atualização no ProcAPI', null=True, blank=True)
    atualizando = models.BooleanField('Atualizando via ProcAPI', default=False)
    atualizado = models.BooleanField('Atualizado via ProcAPI', default=False)

    situacao = models.SmallIntegerField(choices=LISTA_SITUACAO, default=SITUACAO_MOVIMENTO)
    ativo = models.BooleanField(default=True)

    # Varíavel de controle
    atendimento = None

    @property
    def autores(self):
        return Parte.objects.filter(processo=self, parte=Parte.TIPO_AUTOR, atendimento__ativo=True, ativo=True)

    @property
    def autor(self):
        autores = self.autores()
        if autores:
            return autores[0]

    @property
    def reus(self):
        return Parte.objects.filter(processo=self, parte=Parte.TIPO_REU, atendimento__ativo=True, ativo=True)

    @property
    def reu(self):
        reus = self.reus()
        if reus:
            return reus[0]

    @property
    def parte_atual(self):
        if self.atendimento:
            return self.parte(self.atendimento)

    def lista_fases(self, fase_id=None):
        if fase_id is None:
            return Fase.objects.filter(processo=self, ativo=True)
        else:
            return Fase.objects.get(processo=self, ativo=True, id=fase_id)

    def lista_audiencias(self):
        return Fase.objects.filter(processo=self, tipo__audiencia=True, ativo=True)

    def get_tipo(self):
        if self.tipo in [Processo.TIPO_EXTRA, Processo.TIPO_PAD]:
            return self.tipo
        else:
            if len(self.numero_inteiro) == 20:
                return Processo.TIPO_EPROC
            else:
                return Processo.TIPO_FISICO

    def get_grau(self):
        """Método que identifica o grau do processo
        Códigos dos Tribunais Estaduais (TJ) e Turmas Recursais (https://www.cnj.jus.br/tribunais-estaduais/)
        TJ-AC: 9XXX/0000
        TJ-AL: 0000
        TJ-AM: ????
        TJ-AP: 0000
        TJ-BA: 0000/9XXX
        TJ-CE: 0000/9XXX
        TJ-DF: 0000
        TJ-ES: ????
        TJ-GO: ????
        TJ-MA: 0000
        TJ-MG: 0000
        TJ-MS: 0000/9XXX
        TJ-MT: ????
        TJ-PA: ????
        TJ-PB: 0000/9XXX
        TJ-PE: ????
        TJ-PI: 0000
        TJ-PR: ????
        TJ-RJ: 0000/9XXX
        TJ-RN: ????
        TJ-RO: 0000/9XXX
        TJ-RR: 9XXX
        TJ-RS: ????
        TJ-SC: ????
        TJ-SE: ????
        TJ-SP: ????
        TJ-TO: 0000/9XXX/2700
        """
        numero = self.numero_inteiro
        if str(numero)[-4:] == '0000' or str(numero)[-4:-3] == '9' or str(numero)[-7:] == '8272700':
            grau = Processo.GRAU_2
        else:
            grau = Processo.GRAU_1

        return grau

    def criar_fases_eproc(self):
        from .services import ProcessoService
        if self.tipo == self.TIPO_EPROC:
            service = ProcessoService(self)
            service.atualizar()

    def gerar_numero(self, parte):

        ano = self.data_cadastro.year

        # Até 2020:
        # defensorias com núcleo: XXXXX.NNN/AAAA = sequencia anual + id do núcleo + ano corrente
        # defensorias sem núcleo: XXXX.DDCC/AAAA = sequencia anual + nº da defensoria + nº da comarca + ano corrente
        # Obs: essa numeração foi descontinuada porque precisa dos dados do atendimento que são mutáveis
        # A partir de 2021:
        # XXXXX.CCC/AAAA = número sequencial anual + id da comarca + ano corrente

        posicao = Processo.objects.filter(
            tipo=Processo.TIPO_EXTRA,
            comarca=self.comarca,
            data_cadastro__year=ano,
            id__lte=self.id
        ).count()

        numero = "{:05d}.{:03d}/{:04d}".format(
            posicao,
            self.comarca.id,
            ano
        )

        return numero

    @property
    def numero_inteiro(self):
        return self.gerar_numero_inteiro(self.numero)

    def gerar_numero_inteiro(self, numero, zfill=None):
        import re
        from uuid import UUID

        if not numero:
            return None

        try:
            UUID(numero, version=4)
        except ValueError:
            numero = re.sub('[^0-9]', '', numero)
            # Se informado, adiciona x zeros à esquerda
            if zfill:
                numero = numero.zfill(zfill)

        return numero

    @property
    def numero_formatado(self):
        return Processo.formatar_numero(self.numero)

    @property
    def numero_procapi(self):
        numero = self.numero_inteiro
        if self.grau and numero and len(numero) == 20:
            numero = '{}{}'.format(self.numero_inteiro, self.grau)
        return numero

    @staticmethod
    def formatar_numero(numero):
        if numero and len(numero) == 20:
            return '{}{}{}{}{}{}{}-{}{}.{}{}{}{}.{}.{}{}.{}{}{}{}'.format(*numero)
        else:
            return numero

    def __str__(self):
        return f'{self.numero} - {self.grau}º Grau' if self.numero and self.grau else f'{self.numero} - Extra Judicial' if self.numero and self.grau == 0 else ''

    def save(self, *args, **kwargs):

        # Se não tem area, descobre a partir da ação
        if not self.area and self.acao and self.acao.area:
            self.area = self.acao.area

        # pré-cadastros não podem ter área (gera inconsistência nos relatórios)
        if self.pre_cadastro:
            self.area = None

        super(Processo, self).save(*args, **kwargs)

    class Meta:
        app_label = 'processo'
        unique_together = ('numero_puro', 'grau')
        ordering = ['numero_puro', '-ativo', 'id']
        permissions = (
            ('view_distribuicao', u'Pode ver Painel de Distribuição de Processos'),
        )


class ParteHistoricoSituacao(AuditoriaAbstractMixin):

    STATUS_EM_ANDAMENTO = 10
    STATUS_SOBRESTADO = 20
    STATUS_FINALIZADO = 30

    LISTA_STATUS_ACOMPANHAMENTO = (
        (STATUS_EM_ANDAMENTO, 'Em andamento'),
        (STATUS_SOBRESTADO, 'Sobrestado'),
        (STATUS_FINALIZADO, 'Finalizado'),
    )

    status = models.PositiveSmallIntegerField(
        choices=LISTA_STATUS_ACOMPANHAMENTO,
        default=STATUS_EM_ANDAMENTO,
        null=True,
        blank=True
    )
    parte = models.ForeignKey(
        'Parte',
        related_name='historico_situacao',
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING
    )

    motivo = models.TextField(max_length=255, blank=True, null=True, default=None)

    inicio_sobrestamento = models.DateTimeField(
        verbose_name="Data de início do sobrestamento",
        blank=True,
        null=True,
        default=None
    )

    fim_sobrestamento = models.DateTimeField(
        verbose_name='Data final do sobrestamento',
        blank=True,
        null=True,
        default=None
    )

    class Meta:
        verbose_name = 'Histórico de Situação de Parte'
        verbose_name_plural = 'Histórico de Situações de Partes'

    def __str__(self):
        return 'Processo: {} - Parte: {} - Status: {}'.format(
            self.parte.processo.numero,
            self.parte.get_parte_display(),
            self.get_status_display()
        )


class Parte(models.Model):
    TIPO_AUTOR = 0
    TIPO_REU = 1
    TIPO_TERCEIRO = 2
    TIPO_VITIMA = 3
    TIPO_ASSISTENTE = 4

    LISTA_TIPO = (
        (TIPO_AUTOR, 'Ativa (autora)'),
        (TIPO_REU, 'Passiva (ré)'),
        (TIPO_TERCEIRO, 'Terceira'),
        (TIPO_VITIMA, 'Vítima'),
        (TIPO_ASSISTENTE, 'Assistente simples desinteressado (amicus curiae e vulnerabilis)'),
    )

    situacao_atual = models.IntegerField(
        choices=ParteHistoricoSituacao.LISTA_STATUS_ACOMPANHAMENTO,
        default=ParteHistoricoSituacao.STATUS_EM_ANDAMENTO
    )

    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                       on_delete=models.DO_NOTHING)

    # TODO: Migrar para AuditoriaAbstractMixin
    modificado_em = models.DateTimeField(
        auto_now=True,
        null=True
    )

    modificado_por = CurrentUserField(
        null=True,
        on_update=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_modificado_por'
    )

    data_exclusao = models.DateTimeField('Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)

    parte = models.SmallIntegerField(choices=LISTA_TIPO, default=TIPO_AUTOR)
    processo = models.ForeignKey('Processo', related_name='parte', verbose_name='Processo', on_delete=models.DO_NOTHING)
    atendimento = models.ForeignKey('atendimento.Defensor', blank=True, null=True, default=None,
                                    on_delete=models.DO_NOTHING)
    data_vista = models.DateTimeField('Data da Vista', blank=True, null=True, default=None)
    defensor = models.ForeignKey('defensor.Defensor', related_name='+', blank=True, null=True, default=None,
                                 verbose_name='Defensor Responsável', on_delete=models.DO_NOTHING)
    defensor_cadastro = models.ForeignKey('defensor.Defensor', related_name='+', blank=True, null=True, default=None,
                                          verbose_name='Defensor Cadastro', on_delete=models.DO_NOTHING)
    defensoria = models.ForeignKey('contrib.Defensoria', related_name='+', blank=True, null=True, default=None,
                                   verbose_name='Defensoria Responsável', on_delete=models.DO_NOTHING)
    defensoria_cadastro = models.ForeignKey('contrib.Defensoria', related_name='+', blank=True, null=True, default=None,
                                            verbose_name='Defensoria Cadastro', on_delete=models.DO_NOTHING)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return u'{} - {} - {}'.format(self.processo, self.atendimento, self.parte)

    class Meta:
        app_label = 'processo'
        ordering = ['-ativo', 'processo']
        verbose_name = u'Parte do Processo'
        verbose_name_plural = u'Partes dos Processos'
        indexes = [
            models.Index(fields=['processo', 'defensoria'], name='processo_parte_idx_001'),
            models.Index(fields=['processo', 'ativo'], name='processo_parte_idx_002'),
        ]

    def excluir(self, excluido_por):
        with transaction.atomic():

            data_exclusao = datetime.now()

            # Exclui todas as fases vinculadas diretamente a parte (cadastro manual via usuario)
            self.fase_set.update(
                ativo=False,
                excluido_por=excluido_por,
                data_exclusao=data_exclusao
            )

            # Exclui registro
            self.data_exclusao = data_exclusao
            self.excluido_por = excluido_por
            self.ativo = False
            self.save()

            if not self.processo.parte.filter(ativo=True).exists():
                # Exclui todas as fases sem vinculos com parte (cadastro automatico via PROCAPI)
                self.processo.fases.update(
                    excluido_por=excluido_por,
                    data_exclusao=data_exclusao,
                    ativo=False
                )

                self.processo.data_exclusao = data_exclusao
                self.processo.excluido_por = excluido_por
                self.processo.ativo = False
                self.processo.save()

            # Exclui atendimento foi criado para o processo
            if self.atendimento and self.atendimento.tipo == self.atendimento.TIPO_PROCESSO:
                if not self.atendimento.parte_set.filter(ativo=True).exclude(id=self.id).exists():

                    # TODO alterar para atendimento.excluir()
                    self.atendimento.excluido_por = excluido_por
                    self.atendimento.data_exclusao = data_exclusao
                    self.atendimento.ativo = False
                    self.atendimento.save()

    def transferir_atendimento(self, atendimento_novo_id, usuario):
        """Utilizado para transferir a Parte para outro atendimento"""

        sucesso = False

        if atendimento_novo_id and usuario:
            with transaction.atomic():

                # Exclui o atendimento que foi criado para processo e não tem outras Partes (processos) vinculados
                if self.atendimento and self.atendimento.tipo == self.atendimento.TIPO_PROCESSO:
                    if not self.atendimento.parte_set.filter(ativo=True).exclude(id=self.id).exists():
                        self.atendimento.excluir(excluido_por=usuario.servidor)

                atendimento_antigo_id = self.atendimento_id
                self.atendimento_id = atendimento_novo_id
                self.save()

                ParteHistoricoTransferencia(
                    parte=self,
                    atendimento_antigo_id=atendimento_antigo_id,
                    atendimento_novo_id=atendimento_novo_id,
                    cadastrado_por=usuario,
                    modificado_por=usuario
                ).save()

                sucesso = True

        return sucesso

    def permissao_transferir(self, usuario):
        tem_permissao = False

        # Pode acessar se superuser
        if usuario.is_superuser:
            tem_permissao = True

        # Pode acessar se tem permissão de alterar parte
        elif usuario.has_perm(perm='processo.change_parte'):
            tem_permissao = True

        return tem_permissao

    @property
    def sigla_parte(self):
        siglas = [
            "AT",  # Ativa (Autora)
            "PA",  # Passiva (re)
            "TC",  # Terceira
            "VI",  # Vítima
            "AD",  # Assistente simples e desinteressado (amicus curiae e vulnerabilis)
        ]
        return siglas[self.parte]


class ParteHistoricoTransferencia(AuditoriaAbstractMixin):
    """Utilizado para salvar o histórico de transferências de Parte entre os atendimentos com dados de Auditoria"""

    parte = models.ForeignKey(
        'Parte',
        related_name='historicos_transferencias',
        blank=False,
        null=False,
        on_delete=deletion.PROTECT
    )
    atendimento_antigo = models.ForeignKey(
        to='atendimento.Defensor',
        related_name='+',
        blank=False,
        null=False,
        on_delete=deletion.PROTECT
    )
    atendimento_novo = models.ForeignKey(
        to='atendimento.Defensor',
        related_name='+',
        blank=False,
        null=False,
        on_delete=deletion.PROTECT
    )

    class Meta:
        app_label = 'processo'
        verbose_name = u'Historico de Transferencia de Parte'
        verbose_name_plural = u'Historico de Transferencias de Partes'
        ordering = ['parte', 'cadastrado_em']

    def __str__(self):
        return u'id {} --- parte_id {}'.format(self.id, self.parte_id)


class Acao(models.Model):
    nome = models.CharField(max_length=512, null=False)
    descricao = models.CharField(max_length=512, blank=True, null=True, default=None)
    area = models.ForeignKey('contrib.Area', blank=False, null=True, default=None, on_delete=models.DO_NOTHING)
    codigo_eproc = models.CharField(max_length=25, blank=True, null=True, default=None)
    codigo_cnj = models.CharField(max_length=25, blank=True, null=True, default=None)
    judicial = models.BooleanField(default=True)
    extrajudicial = models.BooleanField(default=False)
    penal = models.BooleanField('Penal', default=False)
    inquerito = models.BooleanField('Inquérito Policial', default=False)
    acao_penal = models.BooleanField('Ação Penal', default=False)
    execucao_penal = models.BooleanField('Execução Penal', default=False)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        app_label = 'processo'
        verbose_name = u'Tipo de Ação'
        verbose_name_plural = u'Tipos de Ações'
        ordering = ['-ativo', 'nome']

    def __str__(self):
        return self.nome

    @property
    def nome_norm(self):
        return Util.normalize(self.nome.strip())


class ProcessoAssunto(models.Model):
    processo = models.ForeignKey('Processo', on_delete=models.CASCADE)
    assunto = models.ForeignKey('Assunto', on_delete=models.CASCADE)
    principal = models.BooleanField(default=False)

    class Meta:
        db_table = 'processo_processo_assuntos'
        ordering = ['processo', '-principal', 'assunto']
        unique_together = ('processo', 'assunto')


class ProcessoApenso(models.Model):
    pai = models.ForeignKey('Processo', related_name='+', blank=True, null=False, default=None,
                            on_delete=models.DO_NOTHING)
    apensado = models.ForeignKey('Processo', related_name='+', blank=True, null=False, default=None,
                                 on_delete=models.DO_NOTHING)
    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    apensado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     on_delete=models.DO_NOTHING)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        app_label = 'processo'
        verbose_name = u'Apenso de Processo'
        verbose_name_plural = u'Apensos de Processos'
        ordering = ['pai', 'apensado', 'data_cadastro']

    def __str__(self):
        return "%s - %s - %s" % (self.pai, self.apensado, self.data_cadastro)


class ProcessoPoloDestinatario(AuditoriaAbstractMixin):
    nome = models.CharField(max_length=256)
    sigla_sistema_webservice = models.CharField(null=False, max_length=3)

    class Meta:
        app_label = 'processo'
        verbose_name = u'Processo Polo Destinatário'
        verbose_name_plural = u'Processo Polos Destinatário'

    def __str__(self):
        return self.nome


class Fase(models.Model):
    ATIVIDADE_OUTRA = 0
    ATIVIDADE_AUDIENCIA = 1
    ATIVIDADE_JURI = 2
    ATIVIDADE_SENTENCA = 3
    ATIVIDADE_RECURSO = 4

    LISTA_ATIVIDADE = (
        (ATIVIDADE_OUTRA, 'Outra'),
        (ATIVIDADE_AUDIENCIA, 'Audiência'),
        (ATIVIDADE_JURI, 'Júri'),
        (ATIVIDADE_SENTENCA, 'Sentença'),
        (ATIVIDADE_RECURSO, 'Recurso'),
    )

    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                       on_delete=models.DO_NOTHING)

    # TODO: Migrar para AuditoriaAbstractMixin
    modificado_em = models.DateTimeField(
        auto_now=True,
        null=True
    )

    modificado_por = CurrentUserField(
        null=True,
        on_update=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_modificado_por'
    )

    data_exclusao = models.DateTimeField('Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)

    tipo = models.ForeignKey('FaseTipo', blank=True, null=False, default=None, on_delete=models.DO_NOTHING)
    processo = models.ForeignKey('Processo', related_name='fases', on_delete=models.DO_NOTHING)
    parte = models.ForeignKey('Parte', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    defensoria = models.ForeignKey('contrib.Defensoria', related_name='+', blank=True, null=True, default=None,
                                   on_delete=models.DO_NOTHING)
    defensor_cadastro = models.ForeignKey('defensor.Defensor', related_name='+', blank=True, null=True, default=None,
                                          on_delete=models.DO_NOTHING)
    defensor_substituto = models.ForeignKey('defensor.Defensor', related_name='+', blank=True, null=True, default=None,
                                            on_delete=models.DO_NOTHING)
    descricao = models.TextField(null=True, blank=True)
    data_protocolo = models.DateTimeField('Data de Protocolo', null=True, blank=False, default=None)
    data_termino_protocolo = models.DateTimeField('Data Término do Protocolo', null=True, blank=True, default=None)
    ativo = models.BooleanField('Ativo', default=True)
    automatico = models.BooleanField('Automático', default=False)
    atividade = models.SmallIntegerField(choices=LISTA_ATIVIDADE, default=ATIVIDADE_OUTRA)

    plantao = models.BooleanField('Plantão', default=False)

    evento_eproc = models.IntegerField(blank=True, null=True, default=None)
    usuario_eproc = models.CharField(max_length=100, blank=True, null=True, default=None)

    class Meta:
        app_label = 'processo'
        ordering = ['-ativo', '-data_cadastro', 'tipo__nome']
        verbose_name = u'Fase Processual'
        verbose_name_plural = u'Fases Processuais'
        indexes = [
            models.Index(fields=['processo', 'ativo'], name='processo_fase_idx_001'),
            models.Index(fields=['processo', 'tipo', 'data_protocolo'], name='processo_fase_idx_002'),
        ]

    def __str__(self):
        return u'%s - %s' % (self.processo, self.tipo)

    def documentos(self):
        return DocumentoFase.objects.filter(fase=self, ativo=True)

    def excluir(self, excluido_por):
        self.data_exclusao = datetime.now()
        self.excluido_por = excluido_por
        self.ativo = False
        self.save()

    @property
    def bloqueado(self):

        pode_editar = False

        if not self.automatico:

            hoje = date.today()
            dia_um = date(hoje.year, hoje.month, 1)

            # se dia menor ou igual ao limite, permite editar registros do mês passado
            if hoje.day <= config.DIA_LIMITE_CADASTRO_FASE:
                dia_um -= relativedelta(months=1)

            # pode editar se data_protocolo maior ou igual o primeiro dia do mês (por causa das audiências agendadas)
            if self.data_protocolo.date() >= dia_um:
                pode_editar = True
            # ou então se a data_cadastro maior ou igual ao primeiro dia do mês
            elif self.data_cadastro.date() >= dia_um:
                pode_editar = True

        return not pode_editar

    @property
    def modificar_mes(self):
        if self.data_protocolo.month == date.today().month and self.data_protocolo.year == date.today().year:
            return True
        else:
            return False


class Audiencia(Fase):

    AUDIENCIA_MARCADA = 0
    AUDIENCIA_REALIZADA = 1
    AUDIENCIA_CANCELADA = 2
    AUDIENCIA_NAO_REALIZADA = 3 

    LISTA_AUDIENCIA_STATUS = (
        (AUDIENCIA_MARCADA, 'Audiência marcada'),
        (AUDIENCIA_REALIZADA, 'Audiência realizada'),
        (AUDIENCIA_CANCELADA, 'Audiência cancelada'),
        (AUDIENCIA_NAO_REALIZADA, 'Audiência não realizada/Advogado constituído'),
    )

    CUSTODIA_NAO_APLICA = 0
    CUSTODIA_RELAX_FLAG = 10
    CUSTODIA_LIB_PROV_COM_FIANCA = 21
    CUSTODIA_LIB_PROV_SEM_FIANCA = 22
    CUSTODIA_LIB_PROV_COM_MED_CAUT = 23
    CUSTODIA_LIB_PROV_SEM_MED_CAUT = 24
    CUSTODIA_MANTEVE_PRISAO = 30

    LISTA_CUSTODIA = (
        (CUSTODIA_NAO_APLICA, 'Não se aplica'),
        (CUSTODIA_RELAX_FLAG, '1. Relaxamento de Flagrante'),
        (CUSTODIA_LIB_PROV_COM_FIANCA, '2.1. Liberdade Provisória - com fiança'),
        (CUSTODIA_LIB_PROV_SEM_FIANCA, '2.2. Liberdade Provisória - sem fiança'),
        (CUSTODIA_LIB_PROV_COM_MED_CAUT, '2.3. Liberdade Provisória - com medida cautelar'),
        (CUSTODIA_LIB_PROV_SEM_MED_CAUT, '2.4. Liberdade Provisória - sem medida cautelar'),
        (CUSTODIA_MANTEVE_PRISAO, '3. Manteve a prisão'),
    )

    audiencia_status = models.SmallIntegerField(choices=LISTA_AUDIENCIA_STATUS, default=AUDIENCIA_MARCADA)
    audiencia_realizada = models.BooleanField('Audiência Realizada', default=False)

    custodia = models.SmallIntegerField(choices=LISTA_CUSTODIA, default=CUSTODIA_NAO_APLICA)

    data_baixa = models.DateTimeField('Data de Baixa', null=True, blank=False, editable=False)
    baixado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                    editable=False, on_delete=models.DO_NOTHING)

    def realizar(self, descricao=None, baixado_por=None, custodia=CUSTODIA_NAO_APLICA):
        if descricao:
            self.descricao = descricao

        self.baixado_por = baixado_por
        self.data_baixa = datetime.now()
        self.audiencia_status = self.AUDIENCIA_REALIZADA
        self.audiencia_realizada = True
        self.custodia = custodia
        self.save()

    @property
    def atrasada(self):
        esta_atrasada = self.audiencia_status == self.AUDIENCIA_MARCADA and self.data_protocolo < datetime.now()
        return esta_atrasada

    class Meta:
        app_label = 'processo'


class Aviso(AuditoriaAbstractMixin):

    SITUACAO_PENDENTE = 10
    SITUACAO_ABERTO = 20
    SITUACAO_FECHADO = 30
    SITUACAO_EXPIRADO = 40

    LISTA_SITUACAO = (
        (SITUACAO_PENDENTE, 'Pendentes de Abertura'),
        (SITUACAO_ABERTO, 'Prazos em aberto'),
        (SITUACAO_FECHADO, 'Fechados'),
        (SITUACAO_EXPIRADO, 'Expirados (Decurso de Prazo)'),
    )

    LISTA_TIPO = (
        ('URG', 'Urgente'),
        ('INT', 'Intimação'),
        ('CIT', 'Citação'),
        ('NOT', 'Notificação'),
        ('VIS', 'Vista para manifestação'),
        ('PTA', 'Pauta de julgamento/audiência'),
        ('FCO', 'Fórum de conciliação'),
    )

    class Meta:
        abstract = True


class FaseTipo(AuditoriaAbstractMixin):
    nome = models.CharField(max_length=512, null=False)
    nome_norm = models.CharField(max_length=512, blank=True, null=True, default=None)
    descricao = models.CharField(max_length=512, blank=True, null=True, default=None)
    codigo_eproc = models.CharField('Código MNI (depreciado)', max_length=25, blank=True, null=True, default=None)
    codigo_cnj = models.CharField('Código CNJ', max_length=25, blank=True, null=True, default=None,
                                  help_text="Código Nacional do Movimento (para mais detalhes, acesse o SGT/CNJ)")
    audiencia = models.BooleanField('Audiência', default=False)
    juri = models.BooleanField('Júri', default=False)
    sentenca = models.BooleanField('Sentença', default=False)
    recurso = models.BooleanField('Recurso', default=False)
    judicial = models.BooleanField(default=True)
    extrajudicial = models.BooleanField(default=False)

    class Meta:
        app_label = 'processo'
        verbose_name = u'Tipo de Fase do Processo'
        verbose_name_plural = u'Tipos de Fases dos Processos'
        ordering = ['-desativado_em', 'nome']

    def __str__(self):
        return u'{}'.format(self.nome)

    def save(self, *args, **kwargs):
        self.nome_norm = Util.normalize(self.nome)
        super(FaseTipo, self).save(*args, **kwargs)


def documento_fase_file_name(instance, filename):
    import uuid

    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)

    return '/'.join(['processo', str(instance.fase.processo.numero_inteiro), filename])


class DocumentoFase(models.Model):
    fase = models.ForeignKey('Fase', on_delete=models.DO_NOTHING)
    tipo = models.ForeignKey(to='DocumentoTipo',
                             help_text='Tipo de Documento',
                             related_name='documentos',
                             null=True,
                             blank=False,
                             default=None,
                             on_delete=models.DO_NOTHING)
    arquivo = models.FileField(upload_to=documento_fase_file_name, null=True, blank=True, default=None)
    documento_atendimento = models.ForeignKey('atendimento.Documento', verbose_name='Documento', on_delete=models.SET_NULL, null=True, blank=True)  # noqa: E501
    nome = models.CharField(max_length=255, db_index=True)
    eproc = models.CharField(max_length=100, null=True, blank=True, default=None)
    ativo = models.BooleanField(default=True)
    data_enviado = models.DateTimeField(null=True, blank=False, auto_now_add=True, editable=False)
    enviado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                    on_delete=models.DO_NOTHING)

    def __str__(self):
        return "%s " % (self.nome)

    def excluir(self):
        self.ativo = False
        self.save()

    class Meta:
        app_label = 'processo'
        ordering = ['-ativo', 'fase', 'nome']
        indexes = [
            models.Index(fields=['fase', 'eproc'], name='processo_doc_fase_idx_001'),
            models.Index(fields=['fase', 'nome'], name='processo_doc_fase_idx_002'),
        ]


class DocumentoTipo(models.Model):

    GRAU_TODOS = 0
    GRAU_1 = 1
    GRAU_2 = 2

    LISTA_GRAU = (
        (GRAU_TODOS, 'Todos'),
        (GRAU_1, u'1º Grau'),
        (GRAU_2, u'2º Grau'),
    )

    nome = models.CharField(max_length=255, db_index=True)
    grau = models.SmallIntegerField(choices=LISTA_GRAU, default=GRAU_TODOS)
    eproc = models.CharField(max_length=100, null=True, blank=True, default=None)
    recurso = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    conta_estatistica = models.BooleanField(help_text='Conta Estatísticas?', default=True)

    def __str__(self):
        return '{0} ({1})'.format(self.nome, self.get_grau_display())

    class Meta:
        app_label = 'processo'
        ordering = ['-ativo', 'nome', 'grau']
        verbose_name = u'Tipo de Documento'
        verbose_name_plural = u'Tipos de Documento'


class ProcessoDashboard(Processo):
    class Meta:
        proxy = True
        verbose_name = 'Processos - Dashboard'
        verbose_name_plural = 'Processos - Dashboard'


class Manifestacao(AuditoriaAbstractMixin):

    TIPO_PETICAO_INICIAL = 10
    TIPO_PETICAO = 20

    SITUACAO_ANALISE = 10
    SITUACAO_NAFILA = 20
    SITUACAO_PROTOCOLADO = 30
    SITUACAO_ERRO = 90

    LISTA_TIPO = (
        (TIPO_PETICAO_INICIAL, 'Petição Inicial'),
        (TIPO_PETICAO, u'Petição'),
    )

    LISTA_SITUACAO = (
        (SITUACAO_ANALISE, 'Em Análise'),
        (SITUACAO_NAFILA, u'Na Fila'),
        (SITUACAO_PROTOCOLADO, u'Protocolado'),
        (SITUACAO_ERRO, u'Falha do protocolo'),
    )

    parte = models.ForeignKey('Parte', on_delete=models.DO_NOTHING)

    defensoria = models.ForeignKey(
        to='contrib.Defensoria',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True
    )

    defensor = models.ForeignKey(
        to='auth.User',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True
    )

    manifestante = models.ForeignKey(
        to='auth.User',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True
    )

    enviado_por = models.ForeignKey(
        to='auth.User',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True
    )

    enviado_em = models.DateTimeField(
        null=True,
        blank=True
    )

    respondido_em = models.DateTimeField(
        null=True,
        blank=True
    )

    protocolo_resposta = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )

    mensagem_resposta = models.TextField(
        null=True,
        blank=True,
        default=None
    )

    codigo_procapi = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None,
        help_text='Código Identificador da Manifestação no ProcAPI'
    )

    sistema_webservice = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None,
        help_text='Identificador do Sistema Webservice no ProcAPI'
    )

    usuario_webservice = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None,
        help_text='Identificador do Usuário Webservice no ProcAPI'
    )

    # TODO: mover todos campos repetidos para a fase processual
    # Fase processual relacionada à manifestação
    fase = models.OneToOneField('Fase', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)

    tipo = models.SmallIntegerField(choices=LISTA_TIPO, default=TIPO_PETICAO)
    tipo_evento = models.SmallIntegerField(null=True, blank=True, default=None, help_text='Tipo do Evento no MNI')

    situacao = models.SmallIntegerField(choices=LISTA_SITUACAO, default=SITUACAO_ANALISE)

    enviando = models.BooleanField('Enviando para ProcAPI', default=False)
    enviado = models.BooleanField('Enviado para ProcAPI', default=False)

    objects = managers.ManifestacaoManager()

    class Meta:
        app_label = 'processo'
        verbose_name = u'Manifestação'
        verbose_name_plural = u'Manifestações'
        indexes = [
            models.Index(fields=['cadastrado_por'], condition=Q(desativado_em=None), name='processo_manifestacao_idx_001'),  # noqa: E501
            models.Index(fields=['parte', 'defensoria', 'situacao'], condition=Q(desativado_em=None), name='processo_manifestacao_idx_002'),  # noqa: E501
        ]

    def __str__(self):
        return u'Manifestação nº {}'.format(self.id)

    def save(self, *args, **kwargs):

        super(Manifestacao, self).save(*args, **kwargs)

        # Se existe fase processual relacionada, atualiza seus dados de acordo com a manifestação
        if self.fase:

            if self.ativo and self.situacao == self.SITUACAO_PROTOCOLADO:
                self.fase.data_protocolo = self.respondido_em
                self.fase.ativo = True
            else:
                self.fase.data_protocolo = None
                self.fase.ativo = False

            self.fase.defensoria = self.defensoria
            self.fase.defensor_cadastro = self.defensor.servidor.defensor if self.defensor else None

            self.fase.data_exclusao = self.desativado_em
            self.fase.excluido_por = self.desativado_por.servidor if self.desativado_por else None

            self.fase.save()

    def pode_excluir(self):
        if self.situacao in [Manifestacao.SITUACAO_ANALISE, Manifestacao.SITUACAO_ERRO]:
            return True
        else:
            return False

    def pode_reenviar(self):
        if self.situacao == Manifestacao.SITUACAO_ERRO or self.envio_expirado:
            return True
        else:
            return False

    @property
    def envio_expirado(self):
        return self.situacao == Manifestacao.SITUACAO_NAFILA and self.enviado_em + timedelta(minutes=10) < datetime.now()  # noqa: E501

    @property
    def mensagem_amigavel(self):
        """Retorna uma mensagem amigável conforme o regex da resposta técnica"""

        mensagem_amigavel = None
        if self.mensagem_resposta:
            from procapi_client.models import RespostaTecnica
            # busca as RespostaTecnica
            respostas_tecnicas = RespostaTecnica.objects.filter(
                sistema_webservices__nome=self.sistema_webservice,
                desativado_em=None)

            # verifica cada regex
            for resposta_tecnica in respostas_tecnicas:
                p = re.compile(resposta_tecnica.regex)

                # se o regex der match preenche a resposta amigável
                if p.match(self.mensagem_resposta):
                    mensagem_amigavel = resposta_tecnica.resposta_amigavel
                    break

        return mensagem_amigavel

    @property
    def mensagem_amigavel_tecnica(self):
        """Retorna a descrição do erro para o admin saber o motivo do erro e o que pode ser feito"""

        mensagem_amigavel = None
        if self.mensagem_resposta:
            from procapi_client.models import RespostaTecnica
            respostas_tecnicas = RespostaTecnica.objects.filter(
                sistema_webservices__nome=self.sistema_webservice,
                desativado_em=None)

            # verifica cada regex
            for resposta_tecnica in respostas_tecnicas:
                p = re.compile(resposta_tecnica.regex)

                # se o regex der match preenche a resposta amigável para o admin
                if p.match(self.mensagem_resposta):
                    mensagem_amigavel = resposta_tecnica.descricao
                    break

        return mensagem_amigavel

    @property
    def mensagem_whatsapp(self):
        """Retorna mensagem a ser enviada para o assistido ao ter uma petição protocolada"""

        whatsapp_template = config.WHATSAPP_PROCESSO_MANIFESTACAO_PROTOCOLO.format(manifestacao=self)

        return whatsapp_template

    @property
    def vara(self):
        """Retorna a vara de acordo com as informações da manifestação"""

        # Se não tem parte e processo, não exibe
        if self.parte is None and self.parte.processo is None:
            return None
        # Se intermediária ou inicial protocolada, retorna vara do processo
        if self.tipo == Manifestacao.TIPO_PETICAO or self.situacao == Manifestacao.SITUACAO_PROTOCOLADO:
            return self.parte.processo.vara
        # Se inicial com processo originário, retorna vara do processo originário (distribuição por dependência)
        elif self.parte.processo.originario:
            return self.parte.processo.originario.vara
        # Senão, não exibe (distribuição automática)
        else:
            return None


class ManifestacaoDocumento(AuditoriaAbstractMixin):

    ORIGEM_ATENDIMENTO = 10
    ORIGEM_PESSOA = 20

    LISTA_ORIGEM = (
        (ORIGEM_ATENDIMENTO, 'Atendimento'),
        (ORIGEM_PESSOA, 'Pessoa'),
    )

    manifestacao = models.ForeignKey('Manifestacao', related_name='documentos', on_delete=models.DO_NOTHING)

    # Documento original
    origem = models.SmallIntegerField(choices=LISTA_ORIGEM, default=ORIGEM_ATENDIMENTO)
    # TODO: criar relacionamento com AtendimentoDocumento
    origem_id = models.IntegerField()

    # Posição na lista
    posicao = models.IntegerField(blank=False, null=False, default=0)

    # Tipo do documento mni
    tipo_mni = models.IntegerField(blank=True, null=True, default=None)
    # Nível de sigilo
    nivel_sigilo = models.SmallIntegerField(choices=Processo.LISTA_SIGILO, default=Processo.SIGILO_0)

    objects = managers.ManifestacaoDocumentoManager()

    class Meta:
        app_label = 'processo'
        verbose_name = u'Documento de Manifestação'
        verbose_name_plural = u'Documentos de Manifestações'
        indexes = [
            models.Index(fields=['manifestacao', 'origem'], name='processo_manifest_doc_idx_001'),
            models.Index(fields=['manifestacao'], condition=Q(desativado_em=None), name='processo_manifest_doc_idx_002'),  # noqa: E501
        ]

    def __str__(self):
        return self.get_origem.nome

    @cached_property
    def get_origem(self):
        from assistido.models import Documento as DocumentoAssistido
        from atendimento.atendimento.models import Documento as DocumentoAtendimento

        if self.origem == ManifestacaoDocumento.ORIGEM_ATENDIMENTO:
            documento = DocumentoAtendimento.objects.get(id=self.origem_id)
        else:
            documento = DocumentoAssistido.objects.get(id=self.origem_id)

        return documento

    @cached_property
    def get_size(self):

        documento = self.get_origem
        tamanho = 0

        # Se arquivo, obtém tamanho em bytes
        if documento.arquivo:
            try:
                tamanho = documento.arquivo.size
            except FileNotFoundError:
                pass
        # Se GED, calcula tamanho estimado em bytes
        elif hasattr(documento, 'documento_online') and documento.documento_online:
            ged = documento.documento_online
            tamanho = getsizeof(ged.cabecalho) + getsizeof(ged.conteudo) + getsizeof(ged.rodape)

        return tamanho


class ManifestacaoAviso(AuditoriaAbstractMixin):
    manifestacao = models.ForeignKey('Manifestacao', related_name='avisos', on_delete=models.DO_NOTHING)
    numero = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None,
        help_text='Número do Aviso no Tribunal de Justiça'
    )

    class Meta:
        app_label = 'processo'
        verbose_name = u'Aviso de Manifestação'
        verbose_name_plural = u'Avisos de Manifestações'


class ManifestacaoParte(AuditoriaAbstractMixin):
    manifestacao = models.ForeignKey('Manifestacao', related_name='partes', on_delete=models.DO_NOTHING)
    parte = models.ForeignKey('atendimento.Pessoa', related_name='+', on_delete=models.DO_NOTHING)


class Distribuicao(AuditoriaAbstractMixin):
    processo = models.ForeignKey('Processo', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)

    distribuido_defensor = models.ForeignKey('defensor.Defensor', related_name='+', blank=True, null=True, default=None,
                                             editable=False, on_delete=models.DO_NOTHING)
    distribuido_defensoria = models.ForeignKey('contrib.Defensoria', related_name='+', blank=True, null=True, default=None,
                                               editable=False, on_delete=models.DO_NOTHING)
    foi_redistribuido = models.BooleanField('Foi Redistribuido?', default=False)
    numero_aviso = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None,
        help_text='Número do Aviso no Tribunal de Justiça'
    )
    numero_processo = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None,
        help_text='Número do Processo Judicial'
    )

    class Meta:
        app_label = 'processo'
        verbose_name = u'Registro de Distribuição'
        verbose_name_plural = u'Registros de Distribuições'


class Redistribuicao(AuditoriaAbstractMixin):

    distribuicao_origem = models.ForeignKey('Distribuicao', related_name='+', blank=True, null=True, default=None,
                                            editable=False, on_delete=models.DO_NOTHING)

    redistribuido_defensor = models.ForeignKey('defensor.Defensor', related_name='+', blank=True, null=True,
                                               default=None, editable=False, on_delete=models.DO_NOTHING)
    redistribuido_defensoria = models.ForeignKey('contrib.Defensoria', related_name='+', blank=True, null=True,
                                                 default=None, editable=False, on_delete=models.DO_NOTHING)

    foi_redistribuido = models.BooleanField('Foi Redistribuido?', default=False)

    class Meta:
        app_label = 'processo'
        verbose_name = u'Registro de Redistribuição'
        verbose_name_plural = u'Registros de Redistribuições'


reversion.register(Processo)
reversion.register(Fase)
reversion.register(Audiencia)
reversion.register(FaseTipo)
reversion.register(Acao)
reversion.register(ProcessoApenso)
reversion.register(DocumentoFase)
