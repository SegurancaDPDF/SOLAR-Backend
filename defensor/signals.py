# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
from datetime import datetime, time

# Bibliotecas de terceiros
from django.core.cache import cache
from django.db.models.signals import post_save, pre_save
from django.dispatch.dispatcher import receiver

# Modulos locais
from .models import Atuacao


@receiver(pre_save, sender=Atuacao)
def pre_save_atuacao(sender, instance, **kwargs):
    from atendimento.atendimento.models import Defensor as AtendimentoDefensor

    # Se for atuação de defensor o padrão é que pode assinar GED
    if instance.defensor.eh_defensor:
        instance.pode_assinar_ged = True

    # Atualiza vinculo do substituto aos atendimentos do periodo de substituição
    if instance.tipo == Atuacao.TIPO_SUBSTITUICAO:

        if instance.id:
            atuacao = Atuacao.objects.get(id=instance.id)
            AtendimentoDefensor.objects.filter(
                defensoria=atuacao.defensoria,
                defensor=atuacao.titular,
                substituto=atuacao.defensor,
                data_agendamento__gte=atuacao.data_inicial,
                data_agendamento__lte=datetime.combine(atuacao.data_final, time.max),
                ativo=True
            ).update(substituto=None)

        AtendimentoDefensor.objects.filter(
            defensoria=instance.defensoria,
            defensor=instance.titular,
            substituto=None,
            data_agendamento__gte=instance.data_inicial,
            data_agendamento__lte=datetime.combine(instance.data_final, time.max),
            ativo=True
        ).update(substituto=instance.defensor)


@receiver(post_save, sender=Atuacao)
def post_save_atuacao(sender, instance, **kwargs):

    ano = instance.data_inicial.year
    defensor = instance.defensor

    if not defensor.eh_defensor:
        defensor.ativo = defensor.all_atuacoes.vigentes(ajustar_horario=False).exists()
        defensor.save()

    cache.delete_many([
        'defensor.atuacao_listar:%s' % defensor.id,
        'defensor.comarcas_listar:%s:%s' % (defensor.id, ano),
        'defensor.substitutos_listar:%s' % defensor.id
    ])
