# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import uuid
import reversion
from django.conf import settings
from django.db import models
from django.utils import timezone

from contrib.models import Util, Area


# classe do modelo procedimento que representa procedimentos e propacs
class Procedimento(models.Model):
    # constantes para as diferentes situacoes do procedimento
    SITUACAO_MOVIMENTO = 10
    SITUACAO_ENCERRADO = 20
    SITUACAO_ARQUIVADO = 30
    SITUACAO_DESARQUIVADO = 40

    LISTA_SITUACAO = (
        (SITUACAO_MOVIMENTO, 'Movimento'),
        (SITUACAO_ENCERRADO, 'Encerrado'),
        (SITUACAO_ARQUIVADO, 'Arquivado'),
        (SITUACAO_DESARQUIVADO, 'Desarquivado'),
    )

    # constantes para os diferentes tipos de procedimento
    TIPO_PROCEDIMENTO = 10
    TIPO_PROPAC = 20

    LISTA_TIPO = (
        (TIPO_PROCEDIMENTO, 'Procedimento Preparatorio'),
        (TIPO_PROPAC, 'Propac'),
    )

    NIVEL_PUBLICO = 10
    NIVEL_RESTRITO = 20
    NIVEL_PRIVADO = 30

    LISTA_ACESSO = (
        (NIVEL_PUBLICO, 'Acesso Público'),
        (NIVEL_RESTRITO, 'Acesso Restrito'),
        (NIVEL_PRIVADO, 'Acesso Privado'),
    )

    # campos do modelo procedimento
    atendimentos = models.ManyToManyField('atendimento.Atendimento', related_name='procedimentos', blank=True)
    defensor_responsavel = models.ForeignKey('defensor.Defensor', related_name='procedimentos', blank=True, null=True,
                                             default=None, on_delete=models.DO_NOTHING)
    defensor_responsavel_nome = models.CharField(max_length=256, null=True, blank=True, default=None)
    defensoria_responsavel = models.ForeignKey('contrib.Defensoria', related_name='procedimentos', blank=True,
                                               null=True, default=None, on_delete=models.DO_NOTHING)
    defensoria_responsavel_nome = models.CharField(max_length=256, null=True, blank=True, default=None)
    defensorias_acesso = models.ManyToManyField('contrib.Defensoria', related_name='procedimentos_vinculados',
                                                blank=True)

    representante = models.CharField(max_length=1024, null=True, blank=True, default=None)
    representado = models.CharField(max_length=1024, null=True, blank=True, default=None)
    acesso = models.SmallIntegerField(choices=LISTA_ACESSO, default=NIVEL_PRIVADO)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    numero = models.CharField('Número', max_length=50, null=True, blank=True, unique=True, db_index=True)
    assunto = models.CharField(verbose_name="Objeto", max_length=256, null=True, blank=True, default=None,
                               db_index=True)
    tipo = models.SmallIntegerField(choices=LISTA_TIPO, default=TIPO_PROCEDIMENTO)
    situacao = models.SmallIntegerField(choices=LISTA_SITUACAO, default=SITUACAO_MOVIMENTO)
    data_ultima_movimentacao = models.DateTimeField('Data da Ultima Movimentação', null=True, blank=True)
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)

    area = models.ForeignKey('contrib.Area', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = " Procedimento e Propac"
        verbose_name_plural = " Procedimentos e Propacs"
        ordering = ['-data_ultima_movimentacao']

    def __str__(self):
        return '{} - {}'.format(self.numero, self.get_tipo_display())

    def movimentos_ativos(self):  # obtem movimentos ativos relacionados ao procedimento
        return self.movimentos.filter(ativo=True).order_by('volume', 'ordem_volume')

    def movimentos_ativos_cadastrados(self):  # obtem movimentos ativos cadastrados relacionados ao procedimento
        return self.movimentos_ativos().filter(eh_precadastro=False)

    def movimentos_ativos_sem_instauracao(self):  # obtem movimentos ativos cadastados sem instauracao no procedimento
        return self.movimentos_ativos_cadastrados().exclude(tipo__instauracao=True)

    def movimentos_ativos_nao_removidos(self):  # obtem movimentos ativos cadastrados nao removidos no procediment
        return self.movimentos_ativos_cadastrados().filter(data_remocao=None)

    def situacoes_ativas(self):  # obtem situacoes ativas relacionadas ao procedimento
        return self.situacoes.filter(ativo=True)

    def atendimentos_vinculados(self):  # obtem atendimentos vinculados ao procedimento
        return self.atendimentos.all()

    def listar_defensorias_acesso(self):  # lista defensorias com acesso ao procedimento
        return self.defensorias_acesso.all()

    def listar_defensorias_acesso_ids(self):  # listar IDs das defensorias com acesso ao procedimento
        return self.defensorias_acesso.all().filter().values_list('id', flat=True)

    def listar_defensorias_acesso_e_responsavel_ids(self):  # listar IDs das defensorias com acesso a defensoria
        defensorias = list(self.listar_defensorias_acesso_ids())
        defensorias.append(self.defensoria_responsavel.id)
        return defensorias

    def remover_defensorias_acesso(self):  # remover defensorias com acesso ao procedimento
        return self.defensorias_acesso.clear()


class SituacaoProcedimento(models.Model):  # representa as situacoes do procedimento
    procedimento = models.ForeignKey('Procedimento', related_name='situacoes', blank=False, null=False, default=None, on_delete=models.DO_NOTHING)
    situacao = models.SmallIntegerField(choices=Procedimento.LISTA_SITUACAO, default=Procedimento.SITUACAO_MOVIMENTO)
    motivo = models.CharField('Motivo remoção(256 letras)', max_length=256, null=True, blank=True, default=None)
    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Situação do procedimento"
        verbose_name_plural = "Situações dos procedimentos"
        ordering = ['-pk']

    def __str__(self):
        return '{} - {}'.format(self.procedimento, self.get_situacao_display())


class Movimento(models.Model):  # representa os movimentos do procedimento
    procedimento = models.ForeignKey('Procedimento', related_name='movimentos', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    eh_precadastro = models.BooleanField(verbose_name='É precadastro', default=True, editable=False)

    # relacionamento com o modelo movimentotipo
    tipo = models.ForeignKey('MovimentoTipo', related_name='+', blank=False, null=False, default=None, on_delete=models.DO_NOTHING)
    data_movimento = models.DateTimeField('Data de Movimento', null=True, blank=False)
    volume = models.SmallIntegerField()
    ordem_volume = models.SmallIntegerField()
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)

    data_remocao = models.DateTimeField('Data de Remocao', null=True, blank=True)
    motivo_remocao = models.CharField('Motivo remoção(256 letras)', max_length=256, null=True, blank=True, default=None)
    removido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)

    data_exclusao = models.DateTimeField('Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)
    historico = models.TextField('Histórico', blank=True, null=True, default=None)
    
    class Meta:
        verbose_name = "Movimento"
        verbose_name_plural = "Movimentos"
        ordering = ['-data_cadastro']

    def __str__(self):
        return '{}-{}-{}'.format(self.id, self.volume, self.ordem_volume)

    def maximo_movimentos_por_volume(self):
        """
            Define o nuumero máximo de movimentacoes ativas por volume
            Valor definido em settings.PROCEDIMENTO_NUMERO_MAXIMO_POR_VOLUME
            :return: integer
        """
        return settings.PROCEDIMENTO_NUMERO_MAXIMO_POR_VOLUME

    def numero_ultimo_volume(self):
        """
            Define o numero do volume atual e disponível para adicionar novos movimentos.
            :return: integer
        """
        return (self.procedimento.movimentos_ativos_cadastrados().count() // self.maximo_movimentos_por_volume()) + 1

    def ordem_ultimo_volume(self):
        """
            Define o numero de ordenação para o movimento dentro do volume corrente.
            :return: integer
        """
        ordem = self.procedimento.movimentos_ativos_cadastrados().filter(
            volume=self.numero_ultimo_volume()
        ).count()

        return ordem + 1

    def documentos_movimento(self):  # obtem documentos relacionados ao movimento
        return self.documentos.all().filter(ativo=True)

    def cancelar_movimentacao(self, motivo, user):  # cancela a movimentacao do movimento
        self.motivo_remocao = 'movimentacao cancelada'
        self.data_remocao = timezone.now()
        self.removido_por = user.servidor
        for documento in self.documentos.all():
            documento.delete()
        self.ativo = False
        with reversion.create_revision(atomic=False):
            reversion.set_user(user)
            reversion.set_comment('Remoção ' + Util.get_comment_delete(user, self))
            self.save()
        return self


class MovimentoTipo(models.Model):  # representa os tipos de movimento
    nome = models.CharField(max_length=128, null=False, blank=True, default=None)
    codigo = models.SlugField(max_length=128, unique=True, null=False, blank=True, default=None)
    instauracao = models.BooleanField('Instauracao', default=False)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Movimento"
        verbose_name_plural = "Tipos de Movimentos"
        ordering = ['nome']

    def __str__(self):
        return '{}'.format(self.nome)


# define o nome do arquivo para os documentos de movimento de procedimento
def documento_movimento_procedimento_file_name(instance, filename):
    raise Exception('Lembra de apagar isso aqui das migracoes')


def documento_file_name(instance, filename):  # define o nome do arquivo para os documentos
    import uuid

    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    folder_name = instance.movimento.procedimento.uuid

    return '/'.join(['procedimento', str(folder_name), filename])


class TipoAnexoDocumentoPropac(models.Model):  # representa os tipos de anexo de documento propac
    nome = models.CharField(max_length=255, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class DocumentoPropac(models.Model):  # representa os documentos de movimento propac

    movimento = models.ForeignKey('Movimento', related_name='documentos', on_delete=models.DO_NOTHING)
    tipo_anexo = models.ForeignKey('TipoAnexoDocumentoPropac', related_name='documentos', on_delete=models.SET_NULL,
                                   null=True, blank=True)
    nome = models.CharField(max_length=255, default='', blank=True)
    anexo = models.FileField(null=True, blank=True, upload_to=documento_file_name)
    anexo_original_nome_arquivo = models.CharField(max_length=128, default="", blank=True)
    # anexo = FilerFileField(null=True, blank=True,
    #                        related_name="documentopropac_anexo")

    documento = models.ForeignKey('djdocuments.Documento', on_delete=models.SET_NULL, null=True, blank=True)

    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)

    data_remocao = models.DateTimeField('Data de Remocao', null=True, blank=True)
    motivo_remocao = models.CharField('Motivo remoção(256 letras)', max_length=256, null=True, blank=True, default=None)
    removido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)

    data_exclusao = models.DateTimeField('Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)

    def delete(self, using=None):
        if self.documento:
            self.documento.esta_ativo = False
            self.documento.save()
        if self.anexo:
            self.anexo.delete()
        self.ativo = False
        super(DocumentoPropac, self).delete(using)

    def save(self, *args, **kwargs):
        if self.anexo:
            self.anexo_original_nome_arquivo = self.anexo.name.replace('./', '')
        super(DocumentoPropac, self).save(*args, **kwargs)

    def __str__(self):
        return 'Nome: {}, tipo_anexo: {}, documento: {}'.format(self.nome, self.tipo_anexo, self.documento)
