# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comarca', '0001_initial'),
        ('contrib', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='predio',
            name='comarca',
            field=models.ForeignKey(related_name='predios', to='contrib.Comarca', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='guiche',
            name='comarca',
            field=models.ForeignKey(to='contrib.Comarca', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='guiche',
            name='predio',
            field=models.ForeignKey(blank=True, to='comarca.Predio', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
