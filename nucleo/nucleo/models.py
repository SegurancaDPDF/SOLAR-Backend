# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging

# Bibliotecas de terceiros
import reversion
from django.db import models
import six

from core.models import AuditoriaAbstractMixin

from . import managers

logger = logging.getLogger(__name__)


class Nucleo(models.Model):
    # armazena informações sobre os diferentes tipos de núcleos e suas permissões
    # campos do modelo Núcleo
    nome = models.CharField(max_length=255)
    nucleo = models.ForeignKey('self', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    nivel = models.SmallIntegerField(blank=True, null=True, default=None)

    # configuracões de cada tipo de Núcleo
    apoio = models.BooleanField(default=True, help_text="Aceita receber pedidos de apoio?")
    apoio_pode_registrar_atividades = models.BooleanField(
        "Pode registrar atividades em pedidos de apoio?",
        default=False
    )

    agendamento = models.BooleanField(default=False, help_text="Aceita receber agendamentos (inicial/retorno)?")
    encaminhamento = models.BooleanField(default=True, help_text="Aceita receber agendamentos via encaminhamento?")
    acordo = models.BooleanField(default=False, help_text="Aceita registrar atendimentos de acordo?")
    coletivo = models.BooleanField(default=False, help_text="Aceita registrar atendimentos coletivos?")

    supervisionado = models.BooleanField(
        default=False,
        help_text="Os assessores/estagiários só verão os atendimentos a que lhe forem distribuídos"
    )

    recursal = models.BooleanField(default=False, help_text="É um núcleo Recursal?")
    itinerante = models.BooleanField(default=False, help_text="É um núcleo Itinerante/Multirão?")
    plantao = models.BooleanField(default=False, help_text="É um núcleo de Plantão?")
    multidisciplinar = models.BooleanField(default=False, help_text="É um núcleo Multidisciplinar?")
    diligencia = models.BooleanField(default=False, help_text="É um núcleo de Diligências?")

    honorario = models.BooleanField(default=False, help_text="Tem acesso ao módulo Honorários?")
    propac = models.BooleanField(default=False, help_text="Tem acesso ao módulo Propacs?")
    livre = models.BooleanField(default=False, help_text="Tem acesso ao módulo Livre?")

    indeferimento = models.BooleanField(default=False, help_text="Tem acesso ao módulo Indeferimento?")
    indeferimento_pode_receber_negacao = models.BooleanField(
        'Pode receber indeferimento por negação?',
        default=False
    )
    indeferimento_pode_receber_suspeicao = models.BooleanField(
        'Pode receber indeferimento por suspeição?',
        default=False
    )
    indeferimento_pode_receber_impedimento = models.BooleanField(
        'Pode receber indeferimento por impedimento?',
        default=False
    )
    indeferimento_pode_registrar_decisao = models.BooleanField(
        'Pode registrar decisão em Indeferimento?',
        default=False
    )
    indeferimento_pode_registrar_baixa = models.BooleanField(
        'Pode registrar baixa em Indeferimento?',
        default=False
    )

    ativo = models.BooleanField(default=True)

    objects = managers.NucleoManager()

    class Meta:
        app_label = 'nucleo'
        ordering = ['-ativo', 'nome']
        verbose_name = u'Núcleo'
        verbose_name_plural = u'Núcleos'
        permissions = (
            ('admin_multidisciplinar', 'Can admin multidisciplinar'),
        )

    def save(self, *args, **kwargs):

        # Habilita recurso para registrar atividades em atendimento quando Multidiscplinar (necessário)
        if self.multidisciplinar:
            self.apoio_pode_registrar_atividades = True

        super(Nucleo, self).save(*args, **kwargs)

    def __str__(self):
        return self.nome


class Formulario(AuditoriaAbstractMixin):
    # armazena informações sobre os formulários usados nos atendimentos
    # relacionamento com o núcleo
    nucleo = models.ForeignKey('nucleo.Nucleo', on_delete=models.DO_NOTHING)
    posicao = models.SmallIntegerField('Posição', null=True, blank=True)
    texto = models.CharField(max_length=255)
    publico = models.BooleanField(default=False, verbose_name='Público')
    exibir_em_atendimento = models.BooleanField(default=True)
    exibir_em_atividade_extraordinaria = models.BooleanField(default=False)
    gerar_alerta_em_atendimento = models.BooleanField(default=False)

    class Meta:
        app_label = 'nucleo'
        ordering = ['nucleo', 'posicao']
        verbose_name = u'Formulário'
        verbose_name_plural = u'Formulários'

    def __str__(self):
        return '({:03d}) {}'.format(self.posicao, self.texto)

    @property
    def perguntas(self):
        return Pergunta.objects.ativos().filter(formulario=self).order_by('posicao')


class Pergunta(AuditoriaAbstractMixin):
    # armazena informações sobre as perguntas usadas nos formulários
    TIPO_TEXTO = 0
    TIPO_NUMERO = 1
    TIPO_DATA = 2
    TIPO_LISTA = 3
    TIPO_SESSAO = 4
    TIPO_LISTA_MULTIPLA = 5
    TIPO_TEXTO_LONGO = 6

    LISTA_TIPO = (
        (TIPO_TEXTO, 'Texto (Curto)'),
        (TIPO_TEXTO_LONGO, 'Texto (Longo)'),
        (TIPO_NUMERO, 'Número'),
        (TIPO_DATA, 'Data'),
        (TIPO_LISTA, 'Lista (Única)'),
        (TIPO_LISTA_MULTIPLA, 'Lista (Múltipla)'),
        (TIPO_SESSAO, 'Sessão'),
    )

    # relacionamento com o Formulário e sessão (perguntas agrupadas em sessões)
    formulario = models.ForeignKey('nucleo.Formulario', on_delete=models.DO_NOTHING)
    sessao = models.ForeignKey('nucleo.Pergunta', null=True, blank=True, on_delete=models.DO_NOTHING)

    posicao = models.SmallIntegerField('Posição', null=True, blank=True)

    texto = models.CharField(max_length=255)
    texto_complementar = models.CharField(max_length=255, null=True, blank=True)

    tipo = models.SmallIntegerField(choices=LISTA_TIPO, default=TIPO_TEXTO)

    lista = models.CharField(max_length=255, null=True, blank=True)
    lista_url = models.CharField(max_length=255, null=True, blank=True)

    classe_css = models.CharField(max_length=255, blank=True, default='', help_text='Classe CSS (Ex: input-xxlarge)')

    class Meta:
        app_label = 'nucleo'
        ordering = ['formulario', 'sessao__posicao', 'posicao']
        verbose_name = u'Pergunta'
        verbose_name_plural = u'Perguntas'

    def __str__(self):
        return u'{} - {}'.format(self.formulario, self.texto)

    @property
    def alternativas(self):
        if self.tipo in [self.TIPO_LISTA, self.TIPO_LISTA_MULTIPLA] and self.lista:
            return self.lista.split(';')
        else:
            return None


class Resposta(AuditoriaAbstractMixin):
    # armazena as respostas dadas nas perguntas dos formulários nos atendimentos
    # relacionamento com a Pergunta, Atendimento e Evento
    pergunta = models.ForeignKey('nucleo.Pergunta', on_delete=models.DO_NOTHING)
    atendimento = models.ForeignKey('atendimento.Atendimento', null=True, related_name='+', on_delete=models.DO_NOTHING)
    evento = models.ForeignKey('core.Evento', null=True, related_name='respostas', on_delete=models.DO_NOTHING)
    texto = models.TextField(null=True, blank=True)

    class Meta:
        app_label = 'nucleo'
        verbose_name = u'Resposta'
        verbose_name_plural = u'Respostas'

    def __str__(self):
        return six.text_type(self.texto) or u''


reversion.register(Nucleo)
reversion.register(Formulario)
reversion.register(Pergunta)
reversion.register(Resposta)
