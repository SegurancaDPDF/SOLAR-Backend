# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import ast
from datetime import datetime, time, date
import json as simplejson

# Bibliotecas de terceiros
import reversion
from django.db import models

# Solar
from contrib.models import Comarca, Defensoria, Util
from core.models import AuditoriaAbstractMixin
from defensor.models import Atuacao, Defensor


# modelo de dados que representa um evento
class Evento(models.Model):
    TIPO_PERMISSAO = 0  # Libera configuracao de horarios no evento (agenda)
    TIPO_BLOQUEIO = 1  # Bloqueia qualquer permissao dentro da abrangencia do evento

    LISTA_TIPO = (
        (TIPO_PERMISSAO, 'Permissão'),
        (TIPO_BLOQUEIO, 'Bloqueio'),
    )

    titulo = models.CharField(max_length=256, null=True, blank=True, default=None)
    tipo = models.SmallIntegerField(choices=LISTA_TIPO, default=TIPO_BLOQUEIO)

    data_ini = models.DateField('Data Início')
    data_fim = models.DateField('Data Término', null=True, blank=True, default=None)
    data_validade = models.DateField('Data Validade', null=True, blank=True, default=None)

    pai = models.ForeignKey('self', related_name='filhos', blank=True, null=True, default=None,
                            on_delete=models.DO_NOTHING)
    comarca = models.ForeignKey(Comarca, blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    defensor = models.ForeignKey(Defensor, blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    defensoria = models.ForeignKey(Defensoria, related_name='agendas', blank=True, null=True, default=None,
                                   on_delete=models.DO_NOTHING)
    categoria_de_agenda = models.ForeignKey('Categoria', related_name='agendas', blank=True, null=True, default=None,
                                            on_delete=models.DO_NOTHING)

    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                       on_delete=models.DO_NOTHING)

    data_autorizacao = models.DateTimeField('Data de Autorização', null=True, blank=False, editable=False)
    autorizado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                       editable=False, on_delete=models.DO_NOTHING)

    data_exclusao = models.DateTimeField('Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)

    ativo = models.BooleanField(default=True)

    class Meta:
        app_label = 'evento'
        ordering = ['-ativo', 'defensor', '-data_cadastro', ]
        permissions = (
            ('auth_evento', 'Can authorize evento'),
            ('add_desbloqueio', 'Can add desbloqueio'),
            ('change_desbloqueio', 'Can change desbloqueio'),
            ('delete_desbloqueio', 'Can delete desbloqueio'),
            ('manage_evento_nucleo', 'Can manage evento by nucleo')
        )
        indexes = [
            models.Index(fields=['tipo', 'data_validade', 'data_fim'], name='evento_evento_idx_001'),
        ]

    def __str__(self):
        return '{} - {}'.format(self.id, self.titulo)

    def eventos(self):
        return Evento.objects.filter(pai=self, ativo=True)

    def excluir(self, excluido_por, excluir_filhos=True):

        agora = datetime.now()

        if excluir_filhos:
            self.filhos.filter(ativo=True).update(
                excluido_por=excluido_por,
                data_exclusao=agora,
                ativo=False,
            )

        self.excluido_por = excluido_por
        self.data_exclusao = agora
        self.ativo = False
        self.save()

    def autorizar(self, autorizado_por, autorizar_filhos=True):

        agora = datetime.now()

        if autorizar_filhos:
            self.filhos.filter(ativo=True).update(
                data_autorizacao=agora,
                autorizado_por=autorizado_por
            )

        self.data_autorizacao = agora
        self.autorizado_por = autorizado_por
        self.save()

    # TODO precisa ser refatorado, O Evento precisa ser vinculado ao usuario
    # Para funcionar
    @classmethod
    def get_desbloqueio_vigente_por_usuario(cls, usuario):

        hoje = date.today()

        usuarios_por_defensoria = Atuacao.objects.vigentes(
            ajustar_horario=False
        ).filter(
            defensoria__in=usuario.defensorias
        ).values_list('defensor__id', flat=True)

        resultado_desbloqueio = cls.objects.filter(
                                tipo=cls.TIPO_PERMISSAO,
                                defensor__in=usuarios_por_defensoria,
                                data_validade__gte=hoje,
                                ativo=True
                                ).order_by('-data_ini')

        return resultado_desbloqueio


# modelo de dados que representa uma agenda
class Agenda(Evento):
    TIPO_PAUTA = 0
    TIPO_EXTRA = 1

    LISTA_TIPO = (
        (TIPO_PAUTA, 'Pauta'),
        (TIPO_EXTRA, 'Extra-Pauta'),
    )

    atuacao = models.ForeignKey(Atuacao, related_name='agendas', blank=True, null=True, default=None,
                                on_delete=models.DO_NOTHING)

    hora_ini = models.TimeField('Hora Início', default=time(0, 0))
    hora_fim = models.TimeField('Hora Término', default=time(0, 0))

    vagas = models.PositiveSmallIntegerField(default=0)
    duracao = models.PositiveSmallIntegerField(default=0)
    simultaneos = models.PositiveSmallIntegerField(default=1)
    horarios = models.TextField(blank=True, null=True, default=None)
    conciliacao = models.TextField(blank=True, null=True, default=None)

    class Meta:
        app_label = 'evento'
        ordering = ['-ativo', 'atuacao__defensor', '-data_cadastro']

    def agendas(self):
        return Agenda.objects.filter(pai=self, ativo=True)

    def dias_semana(self):

        dias = []
        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

        for i, dia in enumerate(ast.literal_eval(self.horarios)):
            if len(dia):
                dias.append(dias_semana[i])

        return dias

    def dias_semana_horarios(self):

        for dia in ast.literal_eval(self.horarios):
            if len(dia):
                return dia

    def to_json(self):

        obj = Util.object_to_dict(self, {'agendas': []})
        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

        obj['atuacao'] = Util.object_to_dict(self.atuacao, {})
        obj['defensoria'] = {
            'nome': self.atuacao.defensoria.nome,
            'categorias_de_agendas': list(self.atuacao.defensoria.categorias_de_agendas.all().values('id', 'nome'))
        }

        obj['horarios'] = []

        for dia in dias_semana:
            obj['horarios'].append({'dia': dia, 'horarios': [], 'conciliacao': {}, 'ativo': True})

        for categoria, dias_da_semana in iter(simplejson.loads(self.conciliacao).items()):
            if categoria == 'forma_atendimento':
                obj['forma_atendimento'] = dias_da_semana
            else:
                for j, horarios in enumerate(dias_da_semana):
                    obj['horarios'][j]['conciliacao'][categoria] = horarios

        if self.cadastrado_por:
            obj['cadastrado_por'] = {
                'id': self.cadastrado_por.id,
                'nome': self.cadastrado_por.nome,
                'username': self.cadastrado_por.usuario.username
            }

        return obj

    def get_horarios_por_categoria(self):
        '''
        Retorna lista de horários agrupados por categoria
        '''

        dados = simplejson.loads(self.conciliacao)
        categorias = dict((x, y) for x, y in list(self.atuacao.defensoria.categorias_de_agendas.all().values_list('id', 'nome')))

        formas_atendimento = {}
        if 'forma_atendimento' in dados:
            formas_atendimento = dados['forma_atendimento']

        MEIA_NOITE = '00:00'
        DIAS_SEMANA = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

        resultado = []
        for categoria_id, dias_da_semana in iter(dados.items()):
            if categoria_id.isnumeric():
                dias = []
                forma_atendimento = formas_atendimento[categoria_id]
                for dia_da_semana, horarios in enumerate(dias_da_semana):
                    extra = False
                    if MEIA_NOITE in horarios:
                        horarios.remove(MEIA_NOITE)
                        extra = True
                    dias.append({
                        'nome': DIAS_SEMANA[dia_da_semana],
                        'pauta': len(horarios) > 0,
                        'extra': extra or len(horarios) > 0,
                        'forma_atendimento': forma_atendimento[dia_da_semana],
                        'horarios': horarios
                    })
                categoria = {
                    'categoria': {
                        'id': categoria_id,
                        'nome': categorias.get(int(categoria_id)),
                    },
                    'dias': dias
                }

                resultado.append(categoria)

        return resultado


# representa uma categoria
class Categoria(AuditoriaAbstractMixin):
    nome = models.CharField(max_length=256, unique=True)
    sigla = models.CharField(max_length=25, blank=True, null=True, default=None)
    eh_categoria_crc = models.BooleanField('É uma categoria que será utilizada no módulo CRC?', default=False)
    
    # retorna uma representação em string da categoria (seu nome)
    def __str__(self):
        return self.nome

    class Meta:
        app_label = 'evento'
        ordering = ['nome']


reversion.register(Evento)
reversion.register(Agenda)
reversion.register(Categoria)
