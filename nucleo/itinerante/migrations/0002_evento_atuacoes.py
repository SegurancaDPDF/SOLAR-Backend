# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0004_auto_20151022_1421'),
        ('itinerante', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='atuacoes',
            field=models.ManyToManyField(to='defensor.Atuacao'),
        ),
    ]
