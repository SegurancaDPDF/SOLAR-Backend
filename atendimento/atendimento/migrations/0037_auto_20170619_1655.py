# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0036_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarefa',
            name='resposta_para',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Defensoria', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
