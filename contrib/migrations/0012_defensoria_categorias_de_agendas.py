# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evento', '0005_categoria'),
        ('contrib', '0011_defensoria_grau'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoria',
            name='categorias_de_agendas',
            field=models.ManyToManyField(to='evento.Categoria', blank=True),
        ),
    ]
