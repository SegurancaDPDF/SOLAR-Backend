# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
from datetime import datetime

# Bibliotecas de terceiros
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver

# Modulos locais
from .models import Pessoa, PessoaAssistida


@receiver(pre_save, sender=Pessoa)
@receiver(pre_save, sender=PessoaAssistida)
def pre_save_pessoa(sender, instance, **kwargs):
    if instance.genero_id in [Pessoa.SEXO_MASCULINO, Pessoa.SEXO_FEMININO, Pessoa.SEXO_DESCONHECIDO]:
        instance.sexo = instance.genero_id
    else:
        instance.sexo = None
