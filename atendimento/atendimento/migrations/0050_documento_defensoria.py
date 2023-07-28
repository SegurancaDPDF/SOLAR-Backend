# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0016_remove_defensoria_endereco'),
        ('atendimento', '0049_auto_20180309_0936'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='defensoria',
            field=models.ForeignKey(related_name='documentos_atendimento', blank=True, to='contrib.Defensoria', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
