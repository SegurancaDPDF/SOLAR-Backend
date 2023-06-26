# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0029_redimensiona_foto_servidores'),
        ('evento', '0007_evento_data_validade'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='autorizado_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='evento',
            name='data_autorizacao',
            field=models.DateTimeField(verbose_name='Data de Autoriza\xe7\xe3o', null=True, editable=False),
        ),
    ]
