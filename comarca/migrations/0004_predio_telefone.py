# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0016_remove_defensoria_endereco'),
        ('comarca', '0003_predio_endereco'),
    ]

    operations = [
        migrations.AddField(
            model_name='predio',
            name='telefone',
            field=models.ForeignKey(blank=True, to='contrib.Telefone', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
