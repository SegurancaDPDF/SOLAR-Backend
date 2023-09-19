# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

# Bibliotecas de terceiros
from django_currentuser.db.models import CurrentUserField

from contrib.models import Defensoria, Servidor
# Solar
from defensor.models import Defensor

logger = logging.getLogger(__name__)


class Honorario(models.Model):

    TIPO_NOVO = 0
    TIPO_RECURSO = 1
    TIPO_TRANSITADO_JULGADO = 2

    LISTA_SITUACAO = (
        (TIPO_NOVO, u'Novo'),
        (TIPO_RECURSO, u'Recurso'),
        (TIPO_TRANSITADO_JULGADO, u'Transitado em Julgado'),
    )

    # if for recurso, gerar numero de recurso
    numero_recurso_gerado = models.CharField(u'Número Puro Recurso', max_length=50, null=True, blank=True, default=None)

    # if era um recurso e agora entrar no transito e julgado
    honorario_origem = models.ForeignKey('self', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)

    # ForeignKey do recurso que existir no sistema baseado no field numero_recurso_gerado
    recurso_vinculado = models.ForeignKey('processo.Processo', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    # Quando o recurso transitou em julgado e continua o fluxo de movimentos.
    recurso_finalizado = models.BooleanField(default=False, help_text=u'Ao finalizar o Recurso, deve ser marcado como True para liberar as movimentacoes.')  # noqa: E501

    fase = models.OneToOneField('processo.Fase', related_name='honorario', null=False, on_delete=models.DO_NOTHING)
    possivel = models.BooleanField(default=False)
    situacao = models.PositiveSmallIntegerField(choices=LISTA_SITUACAO, default=TIPO_NOVO)
    defensor = models.ForeignKey(Defensor, null=True, default=None, related_name='honorarios_defensor', blank=True, on_delete=models.DO_NOTHING)  # noqa: E501
    defensoria = models.ForeignKey(Defensoria, null=True, default=None, related_name='honorarios_defensoria', blank=True, on_delete=models.DO_NOTHING)  # noqa: E501

    data_cadastro = models.DateTimeField('Data de cadastro', auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey(Servidor, related_name='honorarios_cadastro', blank=False, null=False, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    data_exclusao = models.DateTimeField('Data de Exclusão', blank=True, null=True, default=None)
    excluido_por = models.ForeignKey(Servidor, related_name='honorarios_excluido', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    modificado_por = CurrentUserField(
        null=True,
        on_update=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_modificado_por'
    )

    modificado_em = models.DateTimeField(
        auto_now=True,
        null=True
    )

    valor_estimado = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=None)
    valor_efetivo = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=None)

    suspenso = models.BooleanField(verbose_name='Suspenso?', default=False)
    suspenso_ate = models.DateField(verbose_name='Suspenso até', blank=True, null=True, default=None)

    atendimento = models.ForeignKey('atendimento.Defensor', null=True, blank=True, default=None, related_name='honorarios', on_delete=models.DO_NOTHING)  # noqa: E501

    baixado = models.BooleanField(u'Honorario baixado/finalizado', default=False)
    ativo = models.BooleanField(default=True)

    class Meta:
        app_label = 'honorarios'
        verbose_name = u'Honoráio'
        verbose_name_plural = u'Honoráios'

    def __str__(self):
        return u'Id:{0} - Processo: {1}'.format(self.id, self.fase)

    @property
    def lista_movimentos(self):
        return Movimento.objects.filter(honorario=self, ativo=True).exclude(tipo=Movimento.TIPO_ANOTACAO).order_by('data_cadastro')  # noqa: E501

    @property
    def lista_movimentos_geral(self):
        return Movimento.objects.filter(honorario=self, ativo=True).order_by('data_cadastro')

    @property
    def has_anotacao(self):
        if self.lista_movimentos_geral.filter(tipo=Movimento.TIPO_ANOTACAO).count():
            return True

    @property
    def has_aguard_peti(self):
        if self.lista_movimentos.filter(tipo=Movimento.TIPO_AGUARDANDO_PET).count():
            return True

    @property
    def has_peticao(self):
        if self.lista_movimentos.filter(tipo=Movimento.TIPO_PETICAO).count():
            return True

    @property
    def has_encaminhado_def(self):
        if self.lista_movimentos.filter(tipo=Movimento.TIPO_ENCAMINHADO_DEF).count():
            return True

    @property
    def has_protocolo(self):
        if self.lista_movimentos.filter(tipo=Movimento.TIPO_PROTOCOLO).count():
            return True

    @property
    def has_baixa(self):
        if self.lista_movimentos.filter(tipo=Movimento.TIPO_BAIXA).count():
            return True

    @property
    def verifica_recurso_solar(self):
        from processo.processo.models import Processo
        if self.situacao == 1:
            try:
                recurso = Processo.objects.get(numero_puro=self.numero_recurso_gerado, ativo=True)
            except ObjectDoesNotExist:
                recurso = None

            if recurso:
                return True
        return False

    @property
    def verifica_recurso_honorario(self):
        if self.verifica_recurso_solar:
            try:
                recurso = Honorario.objects.filter(fase__processo__numero_puro=self.numero_recurso_gerado, ativo=True)
            except Exception:
                recurso = None

            if recurso:
                return True
        return False

    @property
    def get_encaminhado_movimento(self):
        if self.lista_movimentos.filter(tipo=Movimento.TIPO_ENCAMINHADO_DEF):
            return self.lista_movimentos.filter(tipo=Movimento.TIPO_ENCAMINHADO_DEF).first()

    @property
    def getid_recurso_honorario(self):
        if self.verifica_recurso_honorario:
            try:
                recurso = Honorario.objects.filter(fase__processo__numero_puro=self.numero_recurso_gerado, ativo=True)
            except ObjectDoesNotExist:
                recurso = None

            if recurso.count():
                return recurso[0].id

    @property
    def get_recurso_honorario(self):
        if self.getid_recurso_honorario:
            try:
                return Honorario.objects.get(pk=self.getid_recurso_honorario)
            except ObjectDoesNotExist:
                return None


def documento_file_name(instance, filename):
    import uuid

    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    ref = instance.honorario.id if hasattr(instance, 'honorario') else instance.movimento.honorario.id
    return '/'.join(['honorario', '{0}'.format(ref), filename])


class Movimento(models.Model):

    TIPO_ANOTACAO = 0
    TIPO_AGUARDANDO_PET = 1
    TIPO_PETICAO = 2
    TIPO_ENCAMINHADO_DEF = 3
    TIPO_PROTOCOLO = 4
    TIPO_BAIXA = 5
    TIPO_SUSPENSAO = 6

    LISTA_TIPO = (
        (TIPO_ANOTACAO, u'Anotação'),
        (TIPO_AGUARDANDO_PET, u'Aguardando Peticionamento'),
        (TIPO_PETICAO, u'Petição'),
        (TIPO_ENCAMINHADO_DEF, u'Encaminhado ao Defensor'),
        (TIPO_PROTOCOLO, u'Protocolo'),
        (TIPO_BAIXA, u'Baixa'),
        (TIPO_SUSPENSAO, u'Suspensão'),
    )

    honorario = models.ForeignKey(Honorario, blank=False, null=False, default=None, related_name='movimentos_honorario', on_delete=models.DO_NOTHING)  # noqa: E501
    tipo = models.PositiveSmallIntegerField(choices=LISTA_TIPO, default=TIPO_ANOTACAO)
    anotacao = models.CharField(max_length=255, blank=False, null=True, default=None,)
    anexo = models.FileField(upload_to=documento_file_name, blank=True, null=True, default=None)

    defensor = models.ForeignKey(Defensor, related_name='movimento_defensor', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    defensoria = models.ForeignKey(Defensoria, related_name='movimento_defensoria', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501

    valor_estimado = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=None)
    valor_efetivo = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=None)
    valor_atualizado = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=None)
    data_atualizacao_valor = models.DateTimeField(u'Data Atualização Valor', blank=True, null=True, default=None)

    data_cadastro = models.DateTimeField(u'Data de cadastro', auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey(Servidor, related_name='movimentos_cadastro', blank=False, null=False, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    data_exclusao = models.DateTimeField(u'Data de Exclusão', blank=True, null=True, default=None)
    excluido_por = models.ForeignKey(Servidor, related_name='movimento_excluido', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    ativo = models.BooleanField(default=True)

    class Meta:
        app_label = 'honorarios'
        verbose_name = u'Movimento Honoráio'
        verbose_name_plural = u'Movimentos Honoráios'

    def __str__(self):
        return u'{0} - Honorario: {1}'.format(self.tipo, self.honorario.id)

    @property
    def lista_documentos_movimento(self):
        return self.documentos_movimento.filter(ativo=True).order_by('-visivel')

    @property
    def lista_documentos_visiveis_movimento(self):
        return self.lista_documentos_movimento.filter(visivel=True)


class Documento(models.Model):
    movimento = models.ForeignKey(Movimento, blank=False, null=False, default=None, related_name='documentos_movimento', on_delete=models.DO_NOTHING)  # noqa: E501
    anexo = models.FileField(upload_to=documento_file_name, blank=False, null=False, default=None)
    nome = models.CharField(max_length=256)
    visivel = models.BooleanField('Visivel', default=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = u'Documento'
        verbose_name_plural = u'Documentos'
        ordering = ['movimento', 'nome']

    def __str__(self):
        return self.nome


class Analise(models.Model):

    fase = models.OneToOneField('processo.Fase', related_name='analises', null=False, on_delete=models.DO_NOTHING)
    motivo = models.CharField(u'Motivo pendência', max_length=255, blank=True, null=True, default=None)
    cadastrado_por = models.ForeignKey(Servidor, related_name='analise_cadastro', blank=False, null=False, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    data_cadastro = models.DateTimeField('Data de cadastro', auto_now_add=True, editable=False)
    ativo = models.BooleanField(default=True)

    class Meta:
        app_label = 'honorarios'
        verbose_name = u'Análise de Honorário'
        verbose_name_plural = u'Análise de Honorários'

    def __str__(self):
        return u'Pendência:{0} - Processo: {1}'.format(self.motivo, self.fase)


class AlertaProcessoMovimento(models.Model):
    honorario = models.ForeignKey(Honorario, related_name='alertas', null=False, on_delete=models.DO_NOTHING)
    mensagem = models.CharField(u'Mensagem alerta', max_length=255, blank=True, null=True, default=None)
    visualizado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    visualizado_por_nome = models.CharField(u'Nome de quem visualizou', max_length=255, blank=True, null=True, default=None)  # noqa: E501
    data_visualizado = models.DateTimeField('Data de visualizacao', blank=True, null=True)
    visualizado = models.BooleanField(default=False)
    data_cadastro = models.DateTimeField('Data de cadastro', auto_now_add=True, editable=False)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = u'Alerta de Movimentacao Honorario'
        ordering = ['-ativo', '-data_cadastro']
        verbose_name_plural = u'Alertas de Movimentações Honorarios'
