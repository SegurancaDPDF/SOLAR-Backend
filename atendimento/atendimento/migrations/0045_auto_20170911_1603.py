# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0044_auto_20170901_1658'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='documento_resposta',
            field=models.OneToOneField(related_name='origem_resposta', null=True, default=None, blank=True, to='atendimento.Documento', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='documento',
            name='prazo_resposta',
            field=models.DateTimeField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='documento',
            name='status_resposta',
            field=models.PositiveSmallIntegerField(default=None, null=True, blank=True, choices=[(0, 'Pendente'), (1, 'Respondido'), (2, 'N\xe3o Respondido')]),
        ),
    ]
