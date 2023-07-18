# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging

# Bibliotecas de terceiros
from django.db import models
from django.db.models import deletion

# Módulos Solar
from contrib.models import Util
from core.models import AuditoriaAbstractMixin
from processo.processo.models import Processo

logger = logging.getLogger(__name__)

# Classe que representa o histórico de consultas das listas de processos.


class HistoricoConsultaProcessos(models.Model):

    inicio_consulta = models.DateTimeField('Data Início da Consulta', null=True, editable=False)
    termino_consulta = models.DateTimeField('Data Término da Consulta', null=True, editable=False)

    data_inicial = models.DateTimeField('Data Inicial', editable=False)
    data_final = models.DateTimeField('Data Final', editable=False, db_index=True)

    paginas = models.IntegerField(null=True)
    registros = models.IntegerField(null=True, db_index=True)
    sucesso = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-data_final']
        verbose_name = u'Histórico Consulta Lista de Processos'
        verbose_name_plural = u'Históricos Consulta Lista de Processos'

# Classe que representa o histórico de consultas de documentos.


class HistoricoConsultaDocumento(AuditoriaAbstractMixin):

    documento = models.CharField('Documento', max_length=50, null=True, blank=True, db_index=True)
    processo = models.CharField('Processo', max_length=50, null=True, blank=True, db_index=True)
    grau = models.SmallIntegerField(choices=Processo.LISTA_GRAU, default=Processo.GRAU_0)
    ip = models.CharField('Endereço IP', max_length=15, null=True, blank=True, db_index=True)

    sucesso = models.BooleanField(default=True)

    class Meta:
        ordering = ['-cadastrado_em']
        verbose_name = u'Histórico Consulta de Documento'
        verbose_name_plural = u'Históricos Consulta de Documentos'

# Classe que representa o histórico de consultas de processos.


class HistoricoConsultaProcesso(AuditoriaAbstractMixin):

    processo = models.CharField('Processo', max_length=50, null=True, blank=True, db_index=True)
    grau = models.SmallIntegerField(choices=Processo.LISTA_GRAU, default=Processo.GRAU_0)
    ip = models.CharField('Endereço IP', max_length=15, null=True, blank=True, db_index=True)

    sucesso = models.BooleanField(default=True)

    class Meta:
        ordering = ['-cadastrado_em']
        verbose_name = u'Histórico Consulta de Processo'
        verbose_name_plural = u'Históricos Consulta de Processos'

# Classe que representa o histórico de consultas da lista de avisos pendentes.


class HistoricoConsultaAvisos(AuditoriaAbstractMixin):

    data_consulta = models.DateTimeField('Data da Consulta', null=True, editable=True)

    class Meta:
        ordering = ['-cadastrado_em']
        verbose_name = u'Histórico Consulta Lista de Avisos Pendentes'
        verbose_name_plural = u'Históricos Consulta Lista de Avisos Pendentes'

# Classe que representa o histórico de consultas de teor de comunicação.


class HistoricoConsultaTeorComunicacao(AuditoriaAbstractMixin):

    aviso = models.CharField('Aviso', max_length=50, null=True, blank=True, db_index=True)
    processo = models.CharField('Processo', max_length=50, null=True, blank=True, db_index=True)
    ip = models.CharField('Endereço IP', max_length=15, null=True, blank=True, db_index=True)

    class Meta:
        ordering = ['-cadastrado_em']
        verbose_name = u'Histórico Consulta de Teor Comunicação'
        verbose_name_plural = u'Históricos Consulta de Teor Comunicação'

#  Classe que representa um sistema de web service.


class SistemaWebService(AuditoriaAbstractMixin):
    nome = models.CharField(verbose_name='Nome', max_length=512, blank=True, null=False)

    class Meta:
        app_label = 'procapi_client'
        verbose_name = u'Sistema Web Service'
        verbose_name_plural = u'Sistemas Web Service'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Competencia(AuditoriaAbstractMixin):
    '''
    Espelho das Competências do ProcAPI, necessário para o relacionamento as Áreas do SOLAR
    '''
    nome = models.CharField(verbose_name='Nome', max_length=512, blank=True, null=False)
    codigo_mni = models.PositiveSmallIntegerField(verbose_name='Código MNI')
    sistema_webservice = models.ForeignKey(
        'SistemaWebService',
        verbose_name='Sistema Web Service',
        on_delete=deletion.PROTECT)
    principal = models.BooleanField(verbose_name='Principal', blank=True, null=False, default=False)
    area = models.ForeignKey(
        'contrib.Area',
        verbose_name='Área da Competência',
        blank=False,
        null=True,
        default=None,
        on_delete=deletion.PROTECT)

    class Meta:
        app_label = 'procapi_client'
        verbose_name = u'Competência ProcAPI'
        verbose_name_plural = u'Competências ProcAPI'
        ordering = ['area__nome', 'sistema_webservice__nome', '-principal', 'nome']
        unique_together = ('codigo_mni', 'sistema_webservice')

    def __str__(self):
        return self.nome


class OrgaoJulgador(AuditoriaAbstractMixin):
    '''
    Espelho dos Órgãos Julgadores do ProcAPI, necessário para o relacionamento as Varas do SOLAR
    '''
    nome = models.CharField(verbose_name='Nome', max_length=512, blank=True, null=False)
    codigo_mni = models.CharField(verbose_name='Código MNI', max_length=25)
    sistema_webservice = models.ForeignKey(
        'SistemaWebService',
        verbose_name='Sistema Web Service',
        on_delete=deletion.PROTECT)
    vara = models.ForeignKey(
        'contrib.Vara',
        verbose_name='Vara',
        blank=False,
        null=True,
        default=None,
        on_delete=deletion.PROTECT)

    class Meta:
        app_label = 'procapi_client'
        verbose_name = u'Órgão Julgador ProcAPI'
        verbose_name_plural = u'Órgãos Julgadores ProcAPI'
        ordering = ['vara__comarca', 'vara__nome', 'sistema_webservice__nome', 'nome']
        unique_together = ('codigo_mni', 'sistema_webservice')

    def __str__(self):
        return self.nome


class TipoArquivo(AuditoriaAbstractMixin):
    extensao = models.CharField(max_length=10, verbose_name='Extensão', help_text='Ex: PDF, JPG, MP3')
    tamanho_maximo = models.IntegerField(verbose_name='Tamanho máximo (MB)', help_text='Em Megabytes (MB)')
    sistema_webservice = models.ForeignKey(
        'SistemaWebService',
        verbose_name='Sistema Web Service',
        on_delete=deletion.PROTECT)

    class Meta:
        app_label = 'procapi_client'
        verbose_name = 'Tipo de Arquivo ProcAPI'
        verbose_name_plural = 'Tipos de Arquivo ProcAPI'
        ordering = ['extensao', 'sistema_webservice__nome']
        unique_together = ('sistema_webservice', 'extensao')

    def __str__(self):
        return u'{} ({})'.format(self.extensao, self.sistema_webservice.nome)

    @property
    def tamanho_maximo_em_bytes(self):
        return self.tamanho_maximo * 1024 * 1024


class TipoEvento(AuditoriaAbstractMixin):
    '''
    Espelho dos Tipos de Eventos do ProcAPI, necessário para o relacionamento com os Tipos de Fases do SOLAR
    '''
    nome = models.CharField(
        verbose_name='Nome',
        max_length=512)
    nome_norm = models.CharField(
        verbose_name='Nome (Normalizado)',
        max_length=512)
    codigo_mni = models.CharField(verbose_name='Código MNI', max_length=25)
    sistema_webservice = models.ForeignKey(
        'SistemaWebService',
        verbose_name='Sistema Web Service',
        on_delete=deletion.PROTECT)
    tipos_de_fase = models.ManyToManyField(
        to='processo.FaseTipo',
        related_name='tipos_de_evento',
        db_table='procapi_client_tipoevento_fasestipo'
    )
    disponivel_em_peticao_avulsa = models.BooleanField(
        verbose_name='Disponível em Petição Avulsa?',
        default=False)
    disponivel_em_peticao_com_aviso = models.BooleanField(
        verbose_name='Disponível em Petição com Aviso?',
        default=False)

    class Meta:
        app_label = 'procapi_client'
        verbose_name = u'Tipo de Evento ProcAPI'
        verbose_name_plural = u'Tipos de Evento ProcAPI'
        ordering = ['sistema_webservice__nome', 'nome']
        unique_together = ('codigo_mni', 'sistema_webservice')

    def __str__(self):
        return u'{} ({})'.format(self.nome, self.codigo_mni)

    @property
    def disponivel_em_peticao(self):
        return (self.disponivel_em_peticao_avulsa or self.disponivel_em_peticao_com_aviso)

    def save(self, *args, **kwargs):
        self.nome_norm = Util.normalize(self.nome)
        super(TipoEvento, self).save(*args, **kwargs)


class RespostaTecnica(AuditoriaAbstractMixin):
    """Resposta técnica e sua resposta amigável para cada sistema"""

    descricao = models.CharField(verbose_name='Descrição', max_length=512, blank=True, null=False)
    regex = models.CharField(verbose_name='Regex', max_length=512, blank=True, null=False, unique=True)
    resposta_amigavel = models.ForeignKey(
        'RespostaAmigavel',
        verbose_name='Resposta Amigável',
        on_delete=deletion.PROTECT)
    sistema_webservices = models.ManyToManyField(
        to='SistemaWebService',
        related_name='respostas_tecnicas',
        db_table='procapi_client_respostatecnica_sistemawebservice',
        blank=False
    )

    class Meta:
        app_label = 'procapi_client'
        verbose_name = u'Resposta Técnica'
        verbose_name_plural = u'Respostas Técnicas'
        ordering = ['descricao']

    def __str__(self):
        return self.regex


class RespostaAmigavel(AuditoriaAbstractMixin):
    """Resposta amigável para as respostas técnicas"""

    descricao = models.CharField(verbose_name='Descrição', max_length=512, blank=True, null=False, unique=True)

    class Meta:
        app_label = 'procapi_client'
        verbose_name = u'Resposta Amigável'
        verbose_name_plural = u'Respostas Amigáveis'
        ordering = ['descricao']

    def __str__(self):
        return self.descricao
