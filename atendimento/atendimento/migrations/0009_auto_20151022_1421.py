# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0008_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atendimento',
            name='inicial',
            field=models.ForeignKey(related_name='retorno', default=None, blank=True, to='atendimento.Atendimento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
