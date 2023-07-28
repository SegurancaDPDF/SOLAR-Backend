# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0042_auto_20170821_1142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pessoa',
            name='atendimento',
            field=models.ForeignKey(related_name='partes', to='atendimento.Atendimento', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
