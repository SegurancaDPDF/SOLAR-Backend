# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0004_auto_20150611_0956'),
    ]

    operations = [
        migrations.AddField(
            model_name='area',
            name='penal',
            field=models.BooleanField(default=False),
        ),
    ]
