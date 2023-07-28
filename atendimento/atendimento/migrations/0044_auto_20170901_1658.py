# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0012_auto_20170821_1136'),
        ('atendimento', '0043_auto_20170901_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='pessoa',
            field=models.ForeignKey(related_name='+', blank=True, to='assistido.PessoaAssistida', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AlterField(
            model_name='pessoa',
            name='tipo',
            field=models.SmallIntegerField(choices=[(0, 'Requerente'), (1, 'Requerido'), (4, 'Diligencia')]),
        ),
    ]
