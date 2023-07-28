# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0039_auto_20170629_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atendimento',
            name='agenda',
            field=models.ForeignKey(default=1, to='evento.Categoria', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
