# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.core.cache import cache
from django.db.models.signals import post_save, pre_save
from django.dispatch.dispatcher import receiver

# Modulos locais
from .models import Acao, Audiencia, Fase, FaseTipo, Parte, Processo


@receiver(pre_save, sender=Processo)
def limpar_calculo_judicial(sender, instance, **kwargs):
    if instance.calculo_judicial:
        instance.calculo_judicial = ''.join(e for e in instance.calculo_judicial if e.isalnum())


@receiver(pre_save, sender=Processo)
def gerar_numero_puro(sender, instance, **kwargs):
    if instance.tipo != Processo.TIPO_EXTRA and instance.numero and instance.numero_puro != instance.numero_inteiro:
        instance.numero_puro = instance.numero_inteiro


@receiver(pre_save, sender=Processo)
def gerar_numero_formatado(sender, instance, **kwargs):
    if not instance.numero or instance.numero == instance.numero_inteiro:
        instance.numero = instance.numero_formatado


@receiver(post_save, sender=Processo)
def post_save_processo(sender, instance, **kwargs):
    # Remove caches dependentes
    cache.delete_many([
        'processo.get_json:%s' % instance.numero_inteiro
    ])


@receiver(post_save, sender=Parte)
def post_save_parte(sender, instance, **kwargs):
    # Remove caches dependentes
    cache.delete_many([
        'processo.get_json:%s' % instance.processo.numero_inteiro
    ])


@receiver(pre_save, sender=Audiencia)
@receiver(pre_save, sender=Fase)
def pre_save_fase(sender, instance, **kwargs):
    if instance.tipo:
        if instance.tipo.sentenca:
            instance.atividade = Fase.ATIVIDADE_SENTENCA
        elif instance.tipo.recurso:
            instance.atividade = Fase.ATIVIDADE_RECURSO
        elif instance.tipo.juri:
            instance.atividade = Fase.ATIVIDADE_JURI
        elif instance.tipo.audiencia:
            instance.atividade = Fase.ATIVIDADE_AUDIENCIA
        elif instance.tipo.peticao_inicial:
            instance.atividade = Fase.ATIVIDADE_PETICAO_INICIAL
        elif instance.tipo.habeas_corpus:
            instance.atividade = Fase.ATIVIDADE_HABEAS_CORPUS


@receiver(post_save, sender=Audiencia)
@receiver(post_save, sender=Fase)
def post_save_fase(sender, instance, **kwargs):
    # Remove caches dependentes
    cache.delete_many([
        'processo.listar_fases:%s' % instance.processo.numero_inteiro
    ])


@receiver(post_save, sender=Acao)
def post_save_acao(sender, instance, **kwargs):
    # Remove caches dependentes
    cache.delete_many([
        'processo.listar_acao:'
    ])


@receiver(pre_save, sender=FaseTipo)
def pre_save_fase_tipo(sender, instance, **kwargs):
    if instance.codigo_eproc:
        if instance.codigo_eproc.strip().isdigit():
            instance.codigo_eproc = str(int(instance.codigo_eproc.strip()))
    if instance.codigo_cnj:
        if instance.codigo_cnj.strip().isdigit():
            instance.codigo_cnj = str(int(instance.codigo_cnj.strip()))


@receiver(post_save, sender=FaseTipo)
def post_save_fase_tipo(sender, instance, **kwargs):
    # Remove caches dependentes
    cache.delete_many([
        'processo.listar_fase_tipo:'
    ])
