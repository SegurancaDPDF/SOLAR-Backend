# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_data(apps, schema_editor):
    Processo = apps.get_model("core", "Processo")

    for processo in Processo.objects.exclude(setor_notificado=None):
        print(processo.numero, processo.setor_notificado.nome)
        processo.setores_notificados.add(processo.setor_notificado)
        processo.save()


def reverse_migrate_data(apps, schema_editor):
    Processo = apps.get_model("core", "Processo")

    for processo in Processo.objects.exclude(setores_notificados=None):
        print(processo.numero, processo.setores_notificados.all().values_list('nome', flat=True))
        processo.setor_notificado = processo.setores_notificados.first()
        processo.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0036_defensoria_tipo_painel_de_acompanhamento'),
        ('core', '0005_processo_setor_notificado'),
    ]

    operations = [
        migrations.AddField(
            model_name='processo',
            name='setores_notificados',
            field=models.ManyToManyField(related_name='processos_notificados', to='contrib.Defensoria', blank=True),
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
        migrations.RemoveField(
            model_name='processo',
            name='setor_notificado',
        ),
    ]
