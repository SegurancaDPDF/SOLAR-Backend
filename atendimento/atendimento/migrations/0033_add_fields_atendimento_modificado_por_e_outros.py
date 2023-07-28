# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0011_defensoria_grau'),
        ('atendimento', '0032_auto_20161207_1011'),
    ]

    operations = [
        migrations.AddField(
            model_name='atendimento',
            name='data_modificacao',
            field=models.DateTimeField(auto_now=True, verbose_name='Data de Modifica\xe7\xe3o', null=True),
        ),
        migrations.AddField(
            model_name='atendimento',
            name='modificado_por',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', default=None, blank=True, to='contrib.Servidor', null=True),
        ),
    ]
