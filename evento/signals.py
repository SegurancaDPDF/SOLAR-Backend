# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import json as simplejson

# Bibliotecas de terceiros
from django.core.cache import cache
from django.db.models.signals import post_save, pre_save
from django.dispatch.dispatcher import receiver

# Modulos locais
from .models import Agenda, Evento


@receiver(pre_save, sender=Agenda)
def pre_save_agenda(sender, instance, **kwargs):
    instance.tipo = Agenda.TIPO_PERMISSAO
    instance.comarca = instance.atuacao.defensoria.comarca
    instance.defensor = instance.atuacao.defensor

    # Força formatação dos horários da agenda para "HH:MM"
    if instance.conciliacao:

        horarios = simplejson.loads(instance.conciliacao)
        formas_atendimento = horarios.pop('forma_atendimento', None)

        for categoria in horarios:
            for dia, _ in enumerate(horarios[categoria]):
                for vaga, horario in enumerate(horarios[categoria][dia]):
                    horarios[categoria][dia][vaga] = '{:02d}:{:02d}'.format(*[int(x) for x in horario.split(':')])

        if formas_atendimento:
            horarios['forma_atendimento'] = formas_atendimento

        instance.conciliacao = simplejson.dumps(horarios)


@receiver(pre_save, sender=Evento)
def pre_save_evento(sender, instance, **kwargs):
    if instance.tipo is None:
        instance.tipo = Evento.TIPO_BLOQUEIO


@receiver(post_save, sender=Evento)
def post_save_evento(sender, instance, **kwargs):
    if instance.tipo == Evento.TIPO_BLOQUEIO:
        # Remove caches dependentes
        cache.delete_many([
            'evento.listar:',
        ])
    elif instance.tipo == Evento.TIPO_PERMISSAO:
        # Remove caches dependentes
        cache.delete_many([
            'evento.desbloqueio_listar:',
        ])
        if instance.defensor_id:
            cache.delete_many([
                'evento.agenda_listar:{}'.format(instance.defensor_id),
            ])


@receiver(post_save, sender=Agenda)
def post_save_agenda(sender, instance, **kwargs):
    if instance.defensor_id:
        cache.delete_many([
            'evento.agenda_listar:{}'.format(instance.defensor_id),
        ])
