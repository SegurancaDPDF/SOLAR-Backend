# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0004_auto_20150611_0956'),
        ('atendimento', '0013_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensor',
            name='comarca',
            field=models.ForeignKey(default=None, blank=True, to='contrib.Comarca', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
