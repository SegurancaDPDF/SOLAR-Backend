# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
import json
import jwt
import time
from constance import config
from django.db import models
from jsonfield import JSONField

# Solar
from core.models import AuditoriaAbstractMixin
from core.managers import AuditoriaBaseManager

from .managers import LocalManager


class Relatorio(AuditoriaAbstractMixin):

    TIPO_JASPER = 1
    TIPO_METABASE = 2

    LISTA_TIPO = (
        (TIPO_JASPER, 'Jasper'),
        (TIPO_METABASE, 'Metabase'),
    )

    tipo = models.PositiveSmallIntegerField(choices=LISTA_TIPO, blank=False, null=False, default=TIPO_JASPER)
    titulo = models.CharField('Título', max_length=255)

    # Jasper
    caminho = models.CharField('Caminho no JasperServer', max_length=255)
    parametros = JSONField(default={})

    # Metabase
    metabase_dashboard_id = models.PositiveSmallIntegerField(
        'ID do Dashboard (Painel) do Metabase',
        blank=True,
        null=True)

    locais = models.ManyToManyField('relatorios.Local', related_name='relatorios')
    papeis = models.ManyToManyField('contrib.Papel', related_name='relatorios')

    objects = AuditoriaBaseManager()

    @property
    def resource(self):
        arr = self.caminho.split('/')
        return '/'.join(arr[:-1])

    @property
    def name(self):
        arr = self.caminho.split('/')
        return arr[-1]

    def get_aliases(self):
        return self.parametros.get('aliases', {})

    def get_defaults(self):
        return self.parametros.get('defaults', {})

    def get_metabase_url(self):

        if self.tipo == self.TIPO_METABASE:

            payload = {
                "resource": {"dashboard": self.metabase_dashboard_id},
                "params": {
                },
                "exp": round(time.time()) + (60 * config.METABASE_EXPIRATION_IN_MINUTES)
            }

            token = jwt.encode(payload, config.METABASE_SECRET_KEY, algorithm="HS256")
            url = config.METABASE_SITE_URL + "/embed/dashboard/" + token + "#bordered=true&titled=true"

            return url

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'titulo': self.titulo,
            'perm': True,
            'metabase_url': self.get_metabase_url(),
            'resource': self.resource,
            'name': self.name,
            'fields': self.parametros,
            'extra': self.parametros.get('extra'),
            'defaults': self.get_defaults(),
            'aliases': self.get_aliases(),
            'format': 'pdf'
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = u'Relatório'
        verbose_name_plural = u'Relatórios'
        ordering = ['titulo']


class Local(AuditoriaAbstractMixin):

    PAGINA_RELATORIO_LISTAR = 'relatorio_listar'
    PAGINA_AGENDAMENTO_CONFIRMAR = 'agendamento_confirmar'
    PAG_ASSISTIDO_CADASTRAR = 'assistido_cadastrar'
    PAG_RECEPCAO_DETALHES_BTN_CARTA_CONVITE = 'recepcao_detalhes_btn_carta_convite'
    PAG_RECEPCAO_DETALHES_BTN_REQUERENTE = 'recepcao_detalhes_btn_requerente'
    PAG_RECEPCAO_DETALHES_BTN_REQUERIDO = 'recepcao_detalhes_btn_requerido'
    PAG_ATENDIMENTO_ATENDER = 'atendimento_atender'
    PAG_ATENDIMENTO_ATENDER_BTN_REQUERENTE = 'atendimento_atender_btn_requerente'
    PAG_ATENDIMENTO_ATENDER_BTN_REQUERIDO = 'atendimento_atender_btn_requerido'
    PAG_ATENDIMENTO_CONFLITOS_CORRIGIDOS = 'atendimento_conflitos_corrigidos'
    PAG_DILIGENCIA_INDEX = 'diligencia_index'
    PAG_ITINERANTE_INDEX = 'itinerante_index'
    PAG_LIVRE_DETALHES_BTN_CALCULO_HORAS = 'livre_detalhes_btn_calculo_horas'
    PAG_MULTIDISCIPLINAR_INDEX = 'multidisciplinar_index'
    PAG_PRECADASTRO_INDEX = 'precadastro_index'
    PAG_PROPAC_DETALHES = 'propac_detalhes'

    PAGINAS = (
        (PAGINA_RELATORIO_LISTAR, u'Relatórios - Listar'),
        (PAGINA_AGENDAMENTO_CONFIRMAR, u'Agendamento - Confirmar Agendamento'),
        (PAG_ASSISTIDO_CADASTRAR, u'Assistido - Cadastrar'),
        (PAG_ATENDIMENTO_ATENDER, u'Atendimento - Atender'),
        (PAG_ATENDIMENTO_ATENDER_BTN_REQUERENTE, u'Atendimento - Atender - Botão Requerente'),
        (PAG_ATENDIMENTO_ATENDER_BTN_REQUERIDO, u'Atendimento - Atender - Botão Requerido'),
        (PAG_ATENDIMENTO_CONFLITOS_CORRIGIDOS, u'Atendimento - Conflitos Corrigidos'),
        (PAG_DILIGENCIA_INDEX, u'Diligência - Index'),
        (PAG_ITINERANTE_INDEX, u'Itinerante - Index'),
        (PAG_LIVRE_DETALHES_BTN_CALCULO_HORAS, u'Livre - Detalhes - Botão Cálculo de Horas'),
        (PAG_MULTIDISCIPLINAR_INDEX, u'Multidisciplinar - Index'),
        (PAG_PRECADASTRO_INDEX, u'Precadastro (129) - Index'),
        (PAG_RECEPCAO_DETALHES_BTN_CARTA_CONVITE, u'Recepção - Detalhes Atendimento - Botão Carta Convite'),
        (PAG_RECEPCAO_DETALHES_BTN_REQUERENTE, u'Recepção - Detalhes Atendimento - Botão Requerente'),
        (PAG_RECEPCAO_DETALHES_BTN_REQUERIDO, u'Recepção - Detalhes Atendimento - Botão Requerido'),
        (PAG_PROPAC_DETALHES, u'PROPAC - Detalhes'),
    )

    pagina = models.CharField(max_length=255, choices=PAGINAS)
    posicao = models.PositiveSmallIntegerField(default=1)
    titulo = models.CharField(max_length=255)
    parametros = JSONField(default={}, blank=True)
    classe_css = models.CharField(
        max_length=255,
        blank=True,
        default='fas fa-file-pdf text-error',
        help_text='Classe CSS (Ex: fas fa-chart-pie text-success)')

    objects = LocalManager()

    class Meta:
        verbose_name = u'Local'
        verbose_name_plural = u'Locais'
        ordering = ['pagina', 'posicao', 'titulo']

    def __str__(self):
        return self.titulo

    def pode_parametrizar(self):
        return self.pagina == Local.PAGINA_RELATORIO_LISTAR


class Relatorios(models.Model):

    class Meta:
        permissions = (
            ('view_filter_defensores', 'Can view filtro defensores'),
            ('view_filter_servidores', 'Can view filtro servidores'),
        )
