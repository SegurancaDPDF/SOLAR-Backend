

# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
from datetime import date, datetime

# Bibliotecas de terceiros
import reversion
from django.db import models
from django.db.models import Q, Count, deletion

from contrib.models import Util

# Modulos locais
from . import managers


# realiza consultas relacionadas aos defensores
class Defensor(models.Model):

    servidor = models.OneToOneField('contrib.Servidor', on_delete=models.DO_NOTHING)
    supervisor = models.ForeignKey(
        'self',
        related_name='assessores',
        null=True,
        blank=True,
        default=None,
        on_delete=deletion.PROTECT
    )
    usuario_eproc = models.TextField(
        'Usuário(s) MNI',
        blank=True,
        default='',
        help_text='Usuário(s) MNI separados por vígula'
    )
    data_expiracao_credenciais_mni = models.DateTimeField(
        'Data de expiração das credenciais do MNI',
        null=True,
        blank=True,
        default=None
    )
    data_envio_ultimo_email_distribuicao_processos = models.DateTimeField(
        'Data de envio do último e-mail de distribuição de processos',
        null=True,
        blank=True,
        default=None
    )

    posicao_lista_antiguidade = models.IntegerField(null=True, blank=True)

    eh_defensor = models.BooleanField('Defensor Público?', default=False)
    ativo = models.BooleanField(default=True)

    objects = managers.DefensorManager()

    class Meta:
        app_label = 'defensor'
        ordering = ['-ativo', '-eh_defensor', 'servidor__nome']
        verbose_name = u'Defensor/Assessor'
        verbose_name_plural = u'Defensores/Assessores'

    def save(self, *args, **kwargs):

        if self.usuario_eproc:
            # remove excesso de espaços
            self.usuario_eproc = ' '.join(self.usuario_eproc.strip().split())
        if self.supervisor:
            self.eh_defensor = False

        super(Defensor, self).save(*args, **kwargs)

    def ativos(self):
        """Busca os defensores que tem cadastro ativo"""
        return self.objects.filter(ativo=True)

    def atuacoes(self, comarca=None, tipo=None, vigentes=None):

        atuacoes = self.all_atuacoes

        if vigentes:
            atuacoes = atuacoes.vigentes(ajustar_horario=False)
        else:
            atuacoes = atuacoes.ativos()

        if comarca:
            atuacoes = atuacoes.filter(defensoria__comarca=comarca)

        if tipo:
            if isinstance(tipo, (list, dict)):
                atuacoes = atuacoes.filter(tipo__in=tipo)
            else:
                atuacoes = atuacoes.filter(tipo=tipo)

        return atuacoes

    def atuacoes_vigentes(self):
        return self.atuacoes(vigentes=True)

    def comarcas(self, ano=None):
        from contrib.models import Comarca

        comarcas = {}

        if ano is None:
            ano = date.today().year

        # Atendimentos
        atuacoes = Atuacao.objects.filter(
            Q(defensor=self) &
            Q(data_inicial__lte=datetime(int(ano), 12, 31, 23, 59, 59)) &
            (
                Q(data_final__gte=datetime(int(ano), 1, 1)) |
                Q(data_final=None)
            )).values('defensoria__comarca', 'defensoria__comarca__nome')

        atuacoes = atuacoes.annotate(qtd=Count('defensoria__comarca')).order_by('defensoria__comarca')

        for atuacao in atuacoes:
            comarcas[atuacao['defensoria__comarca']] = atuacao['defensoria__comarca__nome']

        # Processos
        comarcas_acao = Comarca.objects.raw(
            "select distinct(ppr.comarca_id) as id "
            "from processo_parte ppa "
            "left join processo_processo ppr ON ppr.id = ppa.processo_id "
            "where (ppa.defensor_id = %s) "
            "and ppr.area_id IS NOT NULL "
            "and ppr.comarca_id IS NOT NULL "
            "and date_part('year', ppa.data_cadastro) = %s "
            "and ppr.tipo != 0 "
            "and ppa.ativo = TRUE "
            "and ppr.ativo = TRUE ", [self.id, int(ano)])

        for comarca in comarcas_acao:
            comarcas[comarca.id] = comarca.nome

        # Movimentações
        comarcas_fases = Comarca.objects.raw(
            "select distinct(cc.id) as id, cc.nome "
            "from processo_fase pf "
            "left join processo_processo pp on pp.id = pf.processo_id "
            "left join contrib_comarca cc on cc.id = pp.comarca_id "
            "where pf.defensor_cadastro_id = %s "
            "and date_part('year',pf.data_cadastro)=%s "
            "and date_part('year',pf.data_cadastro)=date_part('year',pf.data_protocolo) "
            "and date_part('month',pf.data_cadastro)=date_part('month',pf.data_protocolo) "
            "and pf.ativo = true "
            "and pp.ativo = true "
            "order by cc.nome ", [self.id, int(ano)])

        for comarca in comarcas_fases:
            comarcas[comarca.id] = comarca.nome

        # Transforma dicionario em array
        resposta = []
        for key, value in iter(comarcas.items()):
            if key:
                resposta.append({'id': key, 'nome': value})

        return sorted(resposta, key=lambda comarca: comarca['nome'])

    @property
    def defensorias(self):
        # TODO: mover para o manager
        from contrib.models import Defensoria
        return Defensoria.objects.filter(id__in=self.atuacoes_vigentes().values('defensoria_id'))

    @property
    def nucleos_id(self):
        return list(self.defensorias.values_list('nucleo__pk', flat=True))

    def listar_lotados(self, eh_defensor=None, eh_agendamento_online=None):

        defensorias = set(self.atuacoes(vigentes=True).values_list('defensoria_id', flat=True))
        agora = datetime.now()

        q = Q(ativo=True)
        q &= Q(all_atuacoes__ativo=True)
        q &= Q(all_atuacoes__defensoria__in=defensorias)
        q &= Q(all_atuacoes__data_inicial__lte=agora)
        q &= Q(
                Q(all_atuacoes__data_final__gte=agora) |
                Q(all_atuacoes__data_final=None)
            )

        if eh_defensor is not None:
            q &= Q(eh_defensor=eh_defensor)

        if eh_agendamento_online is not None:
            q &= Q(all_atuacoes__defensoria__agendamento_online=eh_agendamento_online)

        return Defensor.objects.select_related('servidor__usuario').filter(q).distinct()

    @property
    def lista_lotados(self):
        return self.listar_lotados()

    @property
    def lista_supervisores(self):
        return self.listar_lotados(eh_defensor=True)

    @property
    def lista_assessores(self):
        return self.listar_lotados(eh_defensor=False)

    @property
    def nome(self):
        return self.servidor.nome

    def validar_eproc(self):
        return True

    def credenciais_expiradas(self):
        if self.data_expiracao_credenciais_mni and self.data_expiracao_credenciais_mni > datetime.now():
            return False
        else:
            return True

    def __str__(self):
        return self.nome


#  informações sobre o período do plantão
class EditalConcorrenciaPlantao(models.Model):
    STATUS_ATIVO = 0
    STATUS_CANCELADO = 1
    STATUS_EXAURIO = 2

    LISTA_STATUS = (
        (STATUS_ATIVO, 'Ativo'),
        (STATUS_CANCELADO, 'Cancelado'),
        (STATUS_EXAURIO, 'Exaurido')
    )
    descricao = models.CharField('Descrição', max_length=256, blank=False, null=False)
    data_inicio = models.DateField('Data de início do período do Plantão', null=False, blank=False)
    data_final = models.DateField('Data o final do período do Plantão', null=False, blank=False)
    data_abertura_inscricao = models.DateField('Data de abertura de inscrições ao Plantão', null=False, blank=False)
    data_fechamento_inscricao = models.DateField('Data de fechamento de inscrições ao Plantão', null=False, blank=False)
    status = models.SmallIntegerField('Status', choices=LISTA_STATUS, null=False, blank=False, default=STATUS_ATIVO)
    vagas = models.ManyToManyField('VagaEditalPlantao')

    def __str__(self):
        return self.descricao

    class Meta:
        verbose_name = u'Edital de Concorrência à Plantão'
        verbose_name_plural = u'Editais de Concorrência à Plantão'
        permissions = (
            ('view_inscricao_plantao', u'Pode se inscrever em edital de concorrência de plantão'),
        )


# estabelece uma relação entre um defensor, um edital e uma vaga específica.
class InscricaoEditalPlantao(models.Model):
    defensor = models.ForeignKey(
        'Defensor',
        on_delete=deletion.PROTECT
    )
    edital = models.ForeignKey(
        'EditalConcorrenciaPlantao',
        on_delete=deletion.PROTECT
    )
    ativo = models.BooleanField(default=True)
    vaga = models.ForeignKey(
        'VagaEditalPlantao',
        on_delete=deletion.PROTECT
    )

    def __str__(self):
        return "%s - %s" % (self.defensor.nome, self.edital.descricao)

    class Meta:
        verbose_name = u'Inscrição a Edital de Plantão'
        verbose_name_plural = u'Inscrições a Edital de Plantão'


# armazena informações sobre a data de início e final da vaga
class VagaEditalPlantao(models.Model):
    data_inicio = models.DateField('Data de início da vaga', null=False, blank=False)
    data_final = models.DateField('Data do final da vaga', null=False, blank=False)

    def __str__(self):
        return "%s a %s" % (self.data_inicio, self.data_final)

    class Meta:
        verbose_name = u'Vaga para Edital de Plantão'
        verbose_name_plural = u'Vagas para Edital de Plantão'


# subclasse de Defensor
class DefensorAssessor(Defensor):

    objects = managers.DefensorAssessorManager()

    class Meta:
        proxy = True
        verbose_name = u'Defensor (Assessor)'
        verbose_name_plural = u'Defensores (Assessores)'


# subclasse de Defensor
class DefensorSupervisor(Defensor):

    objects = managers.DefensorSupervisorManager()

    class Meta:
        proxy = True
        verbose_name = u'Defensor (Supervisor)'
        verbose_name_plural = u'Defensores (Supervisores)'


# métodos para consultar e manipular atuações.
class Atuacao(models.Model):
    TIPO_SUBSTITUICAO = 0
    TIPO_ACUMULACAO = 1
    TIPO_TITULARIDADE = 2
    TIPO_LOTACAO = 3

    LISTA_TIPO = (
        (TIPO_SUBSTITUICAO, u'Substituição'),
        (TIPO_ACUMULACAO, u'Acumulação'),
        (TIPO_TITULARIDADE, u'Titularidade'),
        (TIPO_LOTACAO, u'Lotação')
    )

    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey(
        'contrib.Servidor',
        related_name='+',
        blank=True,
        null=True,
        default=None,
        editable=False,
        on_delete=deletion.PROTECT
    )
    data_atualizacao = models.DateTimeField('Data da última atualização', null=True, blank=True, default=None)
    data_exclusao = models.DateTimeField('Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey(
        'contrib.Servidor',
        related_name='+',
        blank=True,
        null=True,
        default=None,
        editable=False,
        on_delete=deletion.PROTECT
    )
    defensoria = models.ForeignKey(
        'contrib.Defensoria',
        related_name='all_atuacoes',
        on_delete=deletion.PROTECT
    )
    defensor = models.ForeignKey(
        'Defensor',
        related_name='all_atuacoes',
        on_delete=deletion.PROTECT
    )
    titular = models.ForeignKey(
        'Defensor',
        related_name='+',
        null=True,
        blank=True,
        on_delete=deletion.PROTECT
    )
    tipo = models.SmallIntegerField(choices=LISTA_TIPO, default=TIPO_TITULARIDADE)
    data_inicial = models.DateTimeField()
    data_final = models.DateTimeField(null=True, blank=True, default=None)
    documento = models.ForeignKey(
        'Documento',
        null=True,
        blank=True,
        on_delete=deletion.PROTECT
    )

    observacao = models.TextField('Observação', blank=True, null=True, default=None)
    designacao_extraordinaria = models.BooleanField('É designação extraordinária?', default=False)

    ativo = models.BooleanField(default=True)

    codigo_plantao = models.CharField('Cód. Plantão', max_length=25, blank=True, null=True, default=None)
    codigo_plantao_local = models.CharField('Cód. Plantão Local', max_length=25, blank=True, null=True, default=None)
    foi_enviado_email_plantao = models.BooleanField('Foi enviado e-mail c/ extrato do plantão?', default=False)

    cargo = models.ForeignKey(
        'contrib.Cargo',
        related_name="all_atuacoes",
        null=True,
        blank=True,
        default=None,
        on_delete=deletion.PROTECT
    )

    pode_assinar_ged = models.BooleanField('Pode assinar GED?', default=False)
    # TODO: criar migração para tratar os registros antigos

    habilitado_chat_edefensor = models.BooleanField('Habilitado pra usar chat e-Defensor', default=False)
    visualiza_chat_edefensor = models.BooleanField('Ativada a visualização do chat e-Defensor', default=False)

    objects = managers.AtuacaoManager()

    @property
    def substituicao(self):
        return Atuacao.objects.filter(
            defensoria=self.defensoria,
            titular=self.defensor,
            ativo=True
        ).order_by(
            'data_inicial'
        )

    @staticmethod
    def get_atuacao_em_dia(defensoria, titular, substituto, data):

        if type(data) is datetime:
            data = data.date()

        q = Q(defensoria=defensoria)
        q &= Q(ativo=True)
        q &= Q(data_inicial__date__lte=data)

        if substituto:
            q &= Q(defensor=substituto)
            q &= Q(titular=titular)
            q &= Q(data_final__date__gte=data)
        else:
            q &= Q(defensor=titular)
            q &= Q(titular=None)
            q &= Q(Q(data_final__date__gte=data) | Q(data_final=None))

        return Atuacao.objects.filter(q).first()

    def excluir(self, servidor):
        self.data_exclusao = datetime.now()
        self.excluido_por = servidor
        self.ativo = False
        self.save()

    class Meta:
        app_label = 'defensor'
        ordering = ['defensoria__nome', 'defensor__servidor__nome', '-ativo', '-tipo', 'data_inicial']
        verbose_name = u'Atuação'
        verbose_name_plural = u'Atuações'
        indexes = [
            models.Index(fields=['defensor', 'data_inicial'], name='defensor_atuacao_idx_001'),
            models.Index(fields=['defensoria', 'defensor', 'tipo', 'data_inicial'], name='defensor_atuacao_idx_002'),
        ]

    def save(self, *args, **kwargs):
        if self.data_final and not self.codigo_plantao:
            data_final_formatada = self.data_final.time().replace(second=59, microsecond=999999)
            self.data_final = datetime.combine(self.data_final, data_final_formatada)
        super(Atuacao, self).save(*args, **kwargs)

    def __str__(self):
        return "%s - %s" % (self.defensoria.nome, self.defensor.nome)


# Armazena informações sobre o defensor
#  possui campos relacionados a plantões, como códigos de plantão e códigos de plantão local.
class Supervisor(models.Model):
    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey(
        'contrib.Servidor',
        related_name='+',
        blank=True,
        null=True,
        default=None,
        editable=False,
        on_delete=deletion.PROTECT
    )
    data_atualizacao = models.DateTimeField('Data da última atualização', null=True, blank=True, default=None)
    data_exclusao = models.DateTimeField('Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey(
        'contrib.Servidor',
        related_name='+',
        blank=True,
        null=True,
        default=None,
        editable=False,
        on_delete=deletion.PROTECT
    )

    defensor = models.ForeignKey(
        'Defensor',
        related_name='supervisionados',
        on_delete=deletion.PROTECT
    )
    supervisor = models.ForeignKey(
        'Defensor',
        related_name='supervisores',
        null=True,
        blank=True,
        on_delete=deletion.PROTECT
    )

    data_inicial = models.DateTimeField(null=True, blank=False)
    data_final = models.DateTimeField(null=True, blank=True, default=None)

    ativo = models.BooleanField(default=True)

    codigo_plantao = models.CharField('Cód. Plantão', max_length=25, blank=True, null=True, default=None)
    codigo_plantao_local = models.CharField('Cód. Plantão Local', max_length=25, blank=True, null=True, default=None)

    class Meta:
        app_label = 'defensor'


# Add. documento (portaria/ato) vinculado à atuação do defensor
class Documento(models.Model):
    TIPO_PORTARIA = 0
    TIPO_ATO = 1
    TIPO_EDITAL = 2
    TIPO_RESOLUCAO = 3

    LISTA_TIPO = (
        (TIPO_PORTARIA, u'Portaria'),
        (TIPO_ATO, u'Ato'),
        (TIPO_EDITAL, u'Edital'),
        (TIPO_RESOLUCAO, u'Resolução'),
    )

    numero = models.CharField(max_length=50)
    data = models.DateTimeField()
    tipo = models.SmallIntegerField(choices=LISTA_TIPO, default=TIPO_PORTARIA)
    doe_numero = models.SmallIntegerField(null=True, blank=True, default=None)
    doe_data = models.DateTimeField(null=True, blank=True, default=None)
    ativo = models.BooleanField(default=True)

    @property
    def nome(self):
        return "%s %s" % (self.LISTA_TIPO[self.tipo][1], self.numero)

    class Meta:
        app_label = 'defensor'
        ordering = ['-ativo', 'tipo', 'data', 'numero']

    def __str__(self):
        return self.nome


reversion.register(Defensor)
reversion.register(DefensorAssessor)
reversion.register(DefensorSupervisor)
reversion.register(Atuacao)
reversion.register(Documento)
