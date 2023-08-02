# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0003_auto_20160406_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='filiacao',
            name='nome_norm',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='nome_norm',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
