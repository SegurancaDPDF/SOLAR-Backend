# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver

# Modulos locais
from .models import Formulario, Pergunta


@receiver(pre_save, sender=Formulario)
def pre_save_formulario(sender, instance, **kwargs):
    # atribui uma posição ao Formulário se estiver vazio
    if instance.posicao is None:
        instance.posicao = Formulario.objects.ativos().filter(nucleo=instance.nucleo).count()


@receiver(pre_save, sender=Pergunta)
def pre_save_pergunta(sender, instance, **kwargs):
    # atribui uma posição à Pergunta se estiver vazia
    if instance.posicao is None:
        instance.posicao = Pergunta.objects.ativos().filter(
            formulario=instance.formulario,
            sessao=instance.sessao
        ).count()
