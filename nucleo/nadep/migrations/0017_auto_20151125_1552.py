# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0004_auto_20150611_0956'),
        ('nadep', '0016_auto_20151124_1654'),
    ]

    operations = [
        migrations.AddField(
            model_name='aprisionamento',
            name='data_exclusao',
            field=models.DateTimeField(verbose_name='Data de Exclus\xe3o', null=True, editable=False),
        ),
        migrations.AddField(
            model_name='aprisionamento',
            name='excluido_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
