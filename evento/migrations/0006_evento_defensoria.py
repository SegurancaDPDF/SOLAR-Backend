# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0012_defensoria_categorias_de_agendas'),
        ('evento', '0005_categoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='defensoria',
            field=models.ForeignKey(related_name='agendas', default=None, blank=True, to='contrib.Defensoria', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
