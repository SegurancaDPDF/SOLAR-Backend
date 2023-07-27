# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0014_auto_20151119_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='remissao',
            name='para_progressao',
            field=models.BooleanField(default=True, verbose_name='Para Progress\xe3o?'),
        ),
        migrations.AlterField(
            model_name='tipificacao',
            name='tipo',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(0, 'Comum'), (1, 'Hediondo')]),
        ),
    ]
