# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from contrib.models import Cargo, Servidor
from defensor.models import Atuacao


def adiciona(apps, schema_editor):
    cargo = Cargo.objects.create(nome='OFICIAL DE DILIGÊNCIA')

    Atuacao.objects.filter(defensoria__nucleo__diligencia=True).update(cargo_id=cargo.id)


def adiciona_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0019_cargo'),
        ('defensor', '0010_atuacao_cargo'),
        ('nucleo', '0005_nucleo_diligencia'),
    ]

    operations = [
        migrations.RunPython(adiciona, adiciona_reverse)
    ]
