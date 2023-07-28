# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0010_auto_20170419_1544'),
        ('atendimento', '0032_auto_20161207_1011'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarefa',
            name='responder_para',
            field=models.ForeignKey(related_name='+', default=None, to='contrib.Defensoria', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
