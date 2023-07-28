# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0008_auto_20161018_1500'),
        ('atendimento', '0027_auto_20161121_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='atendimento',
            name='participantes',
            field=models.ManyToManyField(related_name='participantes', to='contrib.Servidor', blank=True),
        ),
    ]
