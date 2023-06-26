# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('evento', '0003_auto_20150722_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agenda',
            name='atuacao',
            field=models.ForeignKey(related_name='agendas', default=None, blank=True, to='defensor.Atuacao', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AlterField(
            model_name='agenda',
            name='duracao',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='agenda',
            name='hora_fim',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name='Hora T\xe9rmino'),
        ),
        migrations.AlterField(
            model_name='agenda',
            name='hora_ini',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name='Hora In\xedcio'),
        ),
        migrations.AlterField(
            model_name='agenda',
            name='vagas',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
