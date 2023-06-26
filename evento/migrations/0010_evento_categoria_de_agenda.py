# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('evento', '0009_auto_20190215_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='categoria_de_agenda',
            field=models.ForeignKey(related_name='agendas', default=None, blank=True, to='evento.Categoria', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
