# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
from datetime import datetime

# Bibliotecas de terceiros
from django.core.cache import cache
from django.db.models import F
from django.db.models.signals import post_save, pre_save
from django.dispatch.dispatcher import receiver
from django.conf import settings
from django.db import connection

# Solar
from core.pg_database_expressions import FuncDateUTC
from nucleo.nadep.models import Atendimento as AtendimentoNADEP

# Modulos locais
from .models import Defensor as AtendimentoDefensor
from .models import Assunto, Atendimento, Cronometro


@receiver(pre_save, sender=Atendimento)
@receiver(pre_save, sender=AtendimentoNADEP)
@receiver(pre_save, sender=AtendimentoDefensor)
def pre_save_atendimento(sender, instance, **kwargs):
    if instance.data_exclusao is not None:
        instance.ativo = False


@receiver(pre_save, sender=AtendimentoNADEP)
@receiver(pre_save, sender=AtendimentoDefensor)
def pre_save_atendimento_defensor(sender, instance, **kwargs):
    if instance.comarca_id is None and instance.defensoria:
        instance.comarca_id = instance.defensoria.comarca_id


@receiver(post_save, sender=Atendimento)
@receiver(post_save, sender=AtendimentoNADEP)
@receiver(post_save, sender=AtendimentoDefensor)
def post_save_atendimento(sender, instance, **kwargs):
    if instance.numero is None:
        if settings.SIGLA_UF.upper() == 'AM':
            cursor = connection.cursor()
            cursor.execute("SELECT nextval('atendimento_atendimento_numero');")
            row = cursor.fetchone()[0]
            instance.numero = row
        else:
            primeiro = Atendimento.objects.annotate(
                data_cadastro_date=FuncDateUTC(F('data_cadastro'))
            ).filter(
                data_cadastro_date=instance.data_cadastro.date()
            ).values('id').order_by('id')[:1]

            if not primeiro:
                posicao = 1
            else:
                posicao = instance.id - primeiro[0]['id'] + 1

            instance.numero = "%02d%02d%02d%06d" % (
                instance.data_cadastro.year - 2000, instance.data_cadastro.month, instance.data_cadastro.day, posicao)
        instance.save()


@receiver(post_save, sender=AtendimentoNADEP)
@receiver(post_save, sender=AtendimentoDefensor)
def post_save_atendimento_cria_arvore(sender, instance, **kwargs):
    if instance.at_inicial:
        if hasattr(instance.at_inicial, 'arvore'):
            instance.at_inicial.arvore.excluir()


@receiver(pre_save, sender=Cronometro)
def pre_save_cronometro(sender, instance, **kwargs):
    if instance.inicio is None:
        instance.inicio = datetime.now()

# alterar para mudar descricao de assunto.


@receiver(pre_save, sender=Assunto)
def pre_save_assunto(sender, instance, **kwargs):
    if instance.pai:
        instance.descricao = '{0} > {1}'.format(instance.pai.descricao, instance.titulo)
    else:
        instance.descricao = instance.titulo


@receiver(post_save, sender=Assunto)
def post_save_assunto(sender, instance, **kwargs):
    cache.delete('assunto.listar:')
