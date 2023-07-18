# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from constance import config
from django.db.models.signals import pre_save, post_save
from django.dispatch.dispatcher import receiver
from .models import TipoArquivo


@receiver(pre_save, sender=TipoArquivo)
def pre_save_atendimento(sender, instance, **kwargs):
    print(instance)
    instance.extensao = instance.extensao.lower()


@receiver(post_save, sender=TipoArquivo)
def post_save_tipo_arquivo(sender, instance, **kwargs):
    extensoes = TipoArquivo.objects.ativos().order_by('extensao').distinct().values_list('extensao', flat=True)
    config.FORMATO_SUPORTADO_UPLOADS = '.' + ',.'.join(extensoes)
    print(config.FORMATO_SUPORTADO_UPLOADS)
