# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0008_auto_20161018_1500'),
        ('atendimento', '0030_auto_20161201_1022'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensor',
            name='distribuido_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
