# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import uuid

from django_currentuser.db.models import CurrentUserField
from django.db import models
from django.db.models import Q
from django.utils import timezone
from jsonfield import JSONField

from . import managers


# define um mixin para adicionar funcionalidades de auditoria a outros modelos
class AuditoriaAbstractMixin(models.Model):
    # rastrear o usuário que cadastrou
    cadastrado_por = CurrentUserField(
        null=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_cadastrado_por'
    )
    # rastrear a data e hora de cadastro
    cadastrado_em = models.DateTimeField(
        auto_now_add=True,
        null=True
    )
    # rastrear quem modificou o objeto
    modificado_por = CurrentUserField(
        null=True,
        on_update=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s%(class)s_modificado_por'
    )
    # data e hora de modificacao do objeto
    modificado_em = models.DateTimeField(
        auto_now=True,
        null=True
    )
    # rastrear o usuário que desativou o objeto
    desativado_por = models.ForeignKey(
        to='auth.User',
        null=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_desativado_por',
        blank=True
    )
    # rastrear a data e hora de desativação do objeto
    desativado_em = models.DateTimeField(
        null=True,
        blank=True
    )

    objects = managers.AuditoriaBaseManager()

    class Meta:
        abstract = True

    def _ativo(self):
        if self.desativado_em:
            return False
        else:
            return True

    _ativo.boolean = True
    ativo = property(_ativo)

    def desativar(self, usuario, data_hora=None):  # método para desativar o objeto
        if not data_hora:
            data_hora = timezone.now()

        self.modificado_por = usuario
        self.modificado_em = data_hora

        self.desativado_por = usuario
        self.desativado_em = data_hora
        self.save()

    def reativar(self, usuario, data_hora=None):  # método para reativar o objeto
        if not data_hora:
            data_hora = timezone.now()

        self.modificado_por = usuario
        self.modificado_em = data_hora

        self.desativado_por = None
        self.desativado_em = None
        self.save()


class AuditoriaAtivoMixin:

    def desativar(self, usuario, data_hora=None):
        if not data_hora:
            data_hora = timezone.now()

        self.ativo = False
        self.save()

    def reativar(self, usuario, data_hora=None):
        if not data_hora:
            data_hora = timezone.now()

        self.ativo = True
        self.save()


class Processo(AuditoriaAbstractMixin):

    SITUACAO_PETICIONAMENTO = 10
    SITUACAO_MOVIMENTO = 20
    SITUACAO_BAIXADO = 30

    SITUACOES = (
        (SITUACAO_PETICIONAMENTO, 'Peticionamento'),
        (SITUACAO_MOVIMENTO, 'Movimento'),
        (SITUACAO_BAIXADO, 'Baixado'),
    )

    TIPO_ATENDIMENTO = 10
    TIPO_APOIO = 20  # Núcleos / Multidisciplinar / Diligência
    TIPO_TAREFA = 30
    TIPO_PROCESSO = 40
    TIPO_PROPAC = 50
    TIPO_INDEFERIMENTO = 60  # Impedimento / Suspeição / Negação
    TIPO_ATIVIDADE = 70  # Atividade Extraordinária

    TIPOS = (
        (TIPO_ATENDIMENTO, 'Atendimento'),
        (TIPO_APOIO, 'Apoio'),
        (TIPO_TAREFA, 'Tarefa'),
        (TIPO_PROCESSO, 'Processo'),
        (TIPO_PROPAC, 'PROPAC'),
        (TIPO_INDEFERIMENTO, 'Indeferimento'),
        (TIPO_ATIVIDADE, 'Atividade Extraordinária'),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    numero = models.CharField('Número', max_length=50, null=True, blank=True, unique=True, db_index=True)

    setor_criacao = models.ForeignKey(
        to='contrib.Defensoria',
        on_delete=models.DO_NOTHING,
        related_name='+'
    )

    setor_atual = models.ForeignKey(
        to='contrib.Defensoria',
        on_delete=models.DO_NOTHING,
        related_name='+'
    )

    setor_encaminhado = models.ForeignKey(
        to='contrib.Defensoria',
        on_delete=models.SET_NULL,
        related_name='+',
        null=True,
        blank=True
    )

    setores_notificados = models.ManyToManyField(
        to='contrib.Defensoria',
        related_name='processos_notificados',
        blank=True
    )

    classe = models.ForeignKey(
        to='core.Classe',
        on_delete=models.SET_NULL,
        related_name='+',
        null=True,
        blank=True
    )

    situacao = models.PositiveSmallIntegerField(
        choices=SITUACOES,
        null=False,
        blank=False,
        default=SITUACAO_PETICIONAMENTO,
    )

    tipo = models.PositiveSmallIntegerField(
        choices=TIPOS,
        null=False,
        blank=False
    )

    baixado_por = models.ForeignKey(
        to='auth.User',
        null=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_finalizado_por',
        blank=True
    )

    baixado_em = models.DateTimeField(
        null=True,
        blank=True
    )

    objects = managers.ProcessoManager()

    def __str__(self):
        return '{} ({})'.format(self.uuid, self.numero)

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    #     super(Processo, self).save(force_insert, force_update, using, update_fields)
    #     if not self.numero:
    #         self.numero = self.pk
    #         super(Processo, self).save(force_insert, force_update, using, update_fields)

    def esta_peticionando(self):
        return self.situacao == self.SITUACAO_PETICIONAMENTO

    def esta_movimentando(self):
        return self.situacao == self.SITUACAO_MOVIMENTO

    def esta_baixado(self):
        return self.situacao == self.SITUACAO_BAIXADO

    def encaminhar(self, setor_encaminhado):

        resposta = False
        evento = None

        if not self.setor_encaminhado:

            # cria evento de recebimento
            evento = Evento.objects.create_encaminhamento(processo=self, setor_encaminhado=setor_encaminhado)

            # atualiza dados do processo
            self.setor_encaminhado = setor_encaminhado
            self.save()

        resposta = True

        return resposta, evento

    def confirmar_recebimento(self):

        resposta = False

        if self.setor_encaminhado:

            # cria evento de recebimento
            Evento.objects.create_recebimento(processo=self)

            # atualiza dados do processo
            self.setor_atual = self.setor_encaminhado
            self.setor_encaminhado = None
            self.save()

            resposta = True

        return resposta

    def baixar(self, historico=None):

        resposta = False

        if self.situacao == self.SITUACAO_MOVIMENTO:

            # cria evento de baixa
            evento = Evento.objects.create_baixa(processo=self, historico=historico)

            # atualiza dados do processo
            self.situacao = self.SITUACAO_BAIXADO
            self.baixado_em = evento.cadastrado_em
            self.baixado_por = evento.cadastrado_por
            self.save()

            resposta = True

        return resposta


class Parte(AuditoriaAbstractMixin):

    TIPO_ATIVO = 10  # Requerente/Autor
    TIPO_PASSIVO = 20  # Requerido/Réu
    TIPO_INTERESSADO = 30  # Interessado (ao Preso)

    TIPOS = (
        (TIPO_ATIVO, 'Ativo'),
        (TIPO_PASSIVO, 'Passivo'),
    )

    processo = models.ForeignKey(to='core.Processo', on_delete=models.DO_NOTHING, related_name='partes')
    pessoa = models.ForeignKey(to='assistido.Pessoa', on_delete=models.DO_NOTHING, related_name='+')

    tipo = models.PositiveSmallIntegerField(
        choices=TIPOS,
        null=False,
        blank=False
    )

    class Meta:
        unique_together = ('processo', 'pessoa')

    def __str__(self):
        return '{} - {}'.format(self.processo, self.pessoa)


class Apenso(AuditoriaAbstractMixin):

    TIPO_DEPENDENTE = 10  # Dependente
    TIPO_APENSADO = 20  # Apensado

    TIPOS = (
        (TIPO_DEPENDENTE, 'Dependente'),
        (TIPO_APENSADO, 'Apensado'),
    )

    processo_origem = models.ForeignKey(to='core.Processo', on_delete=models.DO_NOTHING, related_name='dependentes')
    processo_destino = models.ForeignKey(to='core.Processo', on_delete=models.DO_NOTHING, related_name='originarios')

    tipo = models.PositiveSmallIntegerField(
        choices=TIPOS,
        null=True,
        default=None,
        blank=True
    )

    class Meta:
        unique_together = ('processo_origem', 'processo_destino')

    def __str__(self):
        return '{} - {}'.format(self.processo_origem, self.processo_destino)


class Evento(AuditoriaAbstractMixin):

    processo = models.ForeignKey(
        to='core.Processo',
        on_delete=models.DO_NOTHING,
        related_name='eventos',
        null=True,
        blank=True
    )

    parte = models.ForeignKey(
        to='core.Parte',
        on_delete=models.SET_NULL,
        related_name='eventos',
        null=True,
        blank=True
    )

    tipo = models.ForeignKey(
        to='core.TipoEvento',
        on_delete=models.DO_NOTHING,
        related_name='+'
    )

    setor_criacao = models.ForeignKey(
        to='contrib.Defensoria',
        on_delete=models.DO_NOTHING,
        related_name='+'
    )

    setor_encaminhado = models.ForeignKey(
        to='contrib.Defensoria',
        on_delete=models.SET_NULL,
        related_name='+',
        null=True,
        blank=True
    )

    data_referencia = models.DateTimeField(
        null=False,
        blank=True
    )

    encerrado_por = models.ForeignKey(
        to='auth.User',
        null=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_encerrado_por',
        blank=True
    )

    encerrado_em = models.DateTimeField(
        null=True,
        blank=True
    )

    numero = models.SmallIntegerField(blank=True, null=True)

    titulo = models.CharField(max_length=255, blank=True, null=True, default=None)
    historico = models.TextField(blank=True, null=True, default=None)

    participantes = models.ManyToManyField(
        'auth.User',
        through='core.Participante',
        through_fields=('evento', 'usuario')
    )

    complemento = JSONField(blank=True, null=True, default=None)

    em_edicao = models.BooleanField(verbose_name='Em edição?', default=False, editable=False)

    objects = managers.EventoManager()

    area = models.ForeignKey('contrib.Area', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)

    class Meta:
        indexes = [
            models.Index(fields=['processo', 'setor_criacao'], condition=Q(desativado_em=None), name='core_evento_idx_001'),  # noqa: E501
        ]

    def __str__(self):
        if self.processo:
            return '{} - {}'.format(self.processo, self.numero)
        else:
            return '{} - {}'.format(self.id, self.titulo)


def documento_file_name(instance, filename):
    import uuid

    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4(), ext)

    if instance.processo:
        folder_name = instance.processo.uuid
        return '/'.join(['processo', str(folder_name), filename])
    else:
        folder_name = instance.evento.id
        return '/'.join(['core_evento', str(folder_name), filename])


class Documento(AuditoriaAbstractMixin):

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

    processo = models.ForeignKey(
        to='core.Processo',
        on_delete=models.DO_NOTHING,
        related_name='documentos',
        null=True,
        blank=True
    )

    evento = models.ForeignKey(
        to='core.Evento',
        on_delete=models.DO_NOTHING,
        related_name='documentos'
    )

    parte = models.ForeignKey(
        to='core.Parte',
        on_delete=models.SET_NULL,
        related_name='documentos',
        null=True,
        blank=True
    )

    tipo = models.ForeignKey(
        to='core.TipoDocumento',
        on_delete=models.DO_NOTHING,
        related_name='documentos'
    )

    modelo = models.ForeignKey(
        to='core.ModeloDocumento',
        blank=True,
        null=True,
        related_name='documentos',
        on_delete=models.DO_NOTHING
    )

    nome = models.CharField(max_length=255)
    arquivo = models.FileField(null=True, blank=True, upload_to=documento_file_name)

    documento = models.ForeignKey(
        to='djdocuments.Documento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='core_documentos'
    )
    nivel_sigilo = models.SmallIntegerField('Nível de Sigilo', default=SIGILO_0,
                                            choices=LISTA_SIGILO)

    objects = managers.DocumentoManager()

    def __str__(self):
        return '{}'.format(self.nome)

    def pendente(self):
        # verifica se documento está pendente de envio ou pendente de assinatura
        if self.arquivo or (self.documento and self.documento.esta_assinado):
            return False
        else:
            return True


class ModeloDocumento(AuditoriaAbstractMixin):

    TIPO_GED = 0
    TIPO_JASPER = 1
    TIPO_FORMULARIO = 2

    LISTA_TIPO = (
        (TIPO_GED, u'GED'),
        (TIPO_JASPER, u'Jasper'),
        (TIPO_FORMULARIO, u'Formulário'),
    )

    nome = models.CharField(max_length=255, blank=False, null=False)
    tipo = models.PositiveSmallIntegerField(choices=LISTA_TIPO, blank=False, null=False, default=TIPO_GED)

    tipo_documento = models.ForeignKey(
        to='core.TipoDocumento',
        on_delete=models.PROTECT,
        related_name='modelos'
    )

    ged_modelo = models.ForeignKey(
        to='djdocuments.Documento',
        verbose_name='Modelo GED',
        related_name='core_modelos_documentos',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    jasper_resource = models.CharField(max_length=255, blank=True, null=True, default=None)
    jasper_name = models.CharField(max_length=255, blank=True, null=True, default=None)
    jasper_params = models.CharField(max_length=255, blank=True, null=True, default=None)

    formulario_modelo = models.ForeignKey(
        to='nucleo.Formulario',
        verbose_name='Modelo Formulário',
        related_name='core_modelos_documentos',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nome


class TipoDocumento(AuditoriaAbstractMixin):

    nome = models.CharField(max_length=255)
    nome_norm = models.CharField(max_length=255)

    def __str__(self):
        return '{}'.format(self.nome)

    def save(self, *args, **kwargs):
        from contrib.models import Util
        self.nome_norm = Util.normalize(self.nome)
        super(TipoDocumento, self).save(*args, **kwargs)


class TipoEvento(AuditoriaAbstractMixin):

    # Tipos genéricos (**)
    TIPO_PETICAO = 10
    TIPO_RECURSO = 11
    TIPO_ENCAMINHAMENTO = 12
    TIPO_RECEBIMENTO = 13
    TIPO_DECISAO = 14
    TIPO_BAIXA = 15
    TIPO_ANOTACAO = 20
    TIPO_ATIVIDADE = 30
    # Tipos específicos para Atividade Extraordinária (70**)
    TIPO_BRINQUEDOTECA = 7010

    TIPOS = (
        (TIPO_PETICAO, u'Petição'),
        (TIPO_RECURSO, u'Recurso'),
        (TIPO_ENCAMINHAMENTO, u'Encaminhamento'),
        (TIPO_RECEBIMENTO, u'Recebimento'),
        (TIPO_DECISAO, u'Decisão'),
        (TIPO_BAIXA, u'Baixa'),
        (TIPO_ANOTACAO, u'Anotação'),
        (TIPO_ATIVIDADE, u'Atividade'),
        (TIPO_BRINQUEDOTECA, u'Brinquedoteca'),
    )

    tipo = models.PositiveSmallIntegerField(
        choices=TIPOS,
        null=False,
        blank=False,
        default=TIPO_PETICAO
    )

    tipo_processo = models.PositiveSmallIntegerField(
        choices=Processo.TIPOS,
        null=True,
        default=None,
        blank=True
    )

    nome = models.CharField(max_length=255)
    nome_norm = models.CharField(max_length=255)

    objects = managers.TipoEventoManager()

    def __str__(self):
        return '{}'.format(self.nome)

    def save(self, *args, **kwargs):
        from contrib.models import Util
        self.nome_norm = Util.normalize(self.nome)
        super(TipoEvento, self).save(*args, **kwargs)

    @property
    def eh_brinquedoteca(self):
        return self.tipo == self.TIPO_BRINQUEDOTECA


class Classe(AuditoriaAbstractMixin):

    # Tipos genéricos (00**)
    TIPO_PEDIDO = 10  # TODO: o tipo 0010 apresenta erro de sintaxe no python3
    # Tipos específicos para Processo de Indeferimento (60**)
    TIPO_IMPEDIMENTO = 6030
    TIPO_SUSPEICAO = 6040
    TIPO_NEGACAO = 6050
    TIPO_NEGACAO_HIPOSSUFICIENCIA = 6051
    TIPO_NEGACAO_PROCEDIMENTO = 6052

    TIPOS = (
        (TIPO_PEDIDO, u'Pedido'),
        (TIPO_IMPEDIMENTO, u'Impedimento'),
        (TIPO_SUSPEICAO, u'Suspeição'),
        (TIPO_NEGACAO, u'Negação'),
        (TIPO_NEGACAO_HIPOSSUFICIENCIA, u'Negação por Hipossuficiência'),
        (TIPO_NEGACAO_PROCEDIMENTO, u'Denegação de Procedimento'),
    )

    tipo = models.PositiveSmallIntegerField(
        choices=TIPOS,
        null=False,
        blank=False,
        default=TIPO_PEDIDO
    )

    tipo_processo = models.PositiveSmallIntegerField(
        choices=Processo.TIPOS,
        null=True,
        default=None,
        blank=True
    )

    nome = models.CharField(max_length=255)
    nome_norm = models.CharField(max_length=255)

    modelos_documentos = models.ManyToManyField('ModeloDocumento', related_name='classes', blank=True)

    #
    # Parametrização de Indeferimentos
    #

    INDEFERIMENTO_NAO_PODE_REGISTRAR_RECURSO = 0
    INDEFERIMENTO_REGISTRAR_RECURSO_NO_INICIO = 10
    INDEFERIMENTO_REGISTRAR_RECURSO_NO_MEIO = 20

    LISTA_INDEFERIMENTO_PODE_REGISTRAR_RECURSO = (
        (INDEFERIMENTO_NAO_PODE_REGISTRAR_RECURSO, u'Não pode registrar recurso'),
        (INDEFERIMENTO_REGISTRAR_RECURSO_NO_INICIO, u'O recurso deve ser registrado no início da movimentação do processo (status inicial: Peticionamento)'),  # noqa: E501
        (INDEFERIMENTO_REGISTRAR_RECURSO_NO_MEIO, u'O recurso pode ser registrado a qualquer momento da movimentação do processo (status inicial: Movimento)'),  # noqa: E501
    )

    indeferimento_pode_registrar_recurso = models.PositiveSmallIntegerField(
        verbose_name='Indeferimento: Pode registrar recurso?',
        choices=LISTA_INDEFERIMENTO_PODE_REGISTRAR_RECURSO,
        null=False,
        blank=False,
        default=INDEFERIMENTO_NAO_PODE_REGISTRAR_RECURSO
    )

    objects = managers.ClasseManager()

    def __str__(self):
        return '{}'.format(self.nome)

    def save(self, *args, **kwargs):

        # Indeferimentos do tipo impedimento, suspeição e negação de procedimento deve ter recurso registrado no início
        if self.tipo_processo == Processo.TIPO_INDEFERIMENTO:
            if self.tipo in [Classe.TIPO_IMPEDIMENTO, Classe.TIPO_SUSPEICAO, Classe.TIPO_NEGACAO_PROCEDIMENTO]:
                self.indeferimento_pode_registrar_recurso = Classe.INDEFERIMENTO_REGISTRAR_RECURSO_NO_INICIO
        # Outros tipos de processo assumem o valor padrão (desativado)
        else:
            self.indeferimento_pode_registrar_recurso = Classe.INDEFERIMENTO_NAO_PODE_REGISTRAR_RECURSO

        # Guarda nome do registro normalizado
        from contrib.models import Util
        self.nome_norm = Util.normalize(self.nome)

        super(Classe, self).save(*args, **kwargs)

    def eh_tipo_impedimento(self):
        return self.tipo == self.TIPO_IMPEDIMENTO


class Participante(AuditoriaAbstractMixin):

    evento = models.ForeignKey(
        to='core.Evento',
        on_delete=models.DO_NOTHING
    )

    usuario = models.ForeignKey(
        to='auth.User',
        on_delete=models.DO_NOTHING,
        related_name='+'
    )

    papel = models.ForeignKey(
        to='contrib.Papel',
        on_delete=models.DO_NOTHING,
        related_name='+'
    )

    objects = managers.AuditoriaBaseManager()

    def __str__(self):
        return self.usuario.get_full_name()
