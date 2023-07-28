# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0006_auto_20150723_0952'),
    ]

    operations = [
        migrations.AddField(
            model_name='atendimento',
            name='motivo_exclusao',
            field=models.CharField(default=None, max_length=255, null=True, blank=True),
        ),
    ]
