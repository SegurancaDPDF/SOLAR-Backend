# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0021_auto_20160412_1623'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='restricaoprestacaoservico',
            unique_together=set([('prisao', 'data_referencia')]),
        ),
    ]
