# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0009_servidor_profissao'),
        ('assistido', '0009_auto_20170324_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='data_exclusao',
            field=models.DateTimeField(default=None, verbose_name='Data de Exclus\xe3o', null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='documento',
            name='excluido_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
