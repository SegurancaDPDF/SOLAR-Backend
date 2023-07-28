# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0072_viewatendimentodefensor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarefa',
            name='setor_responsavel',
            field=models.ForeignKey(related_name='+', default=None, to='contrib.Defensoria', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
