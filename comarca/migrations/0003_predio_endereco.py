# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0015_auto_20170816_1445'),
        ('comarca', '0002_auto_20150525_0835'),
    ]

    operations = [
        migrations.AddField(
            model_name='predio',
            name='endereco',
            field=models.ForeignKey(blank=True, to='contrib.Endereco', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
