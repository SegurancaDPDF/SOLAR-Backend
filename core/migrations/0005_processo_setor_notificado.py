# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0035_add_aceita_agendamento_defensoria'),
        ('core', '0004_classe_adiciona_tipo_denegacao_procedimento'),
    ]

    operations = [
        migrations.AddField(
            model_name='processo',
            name='setor_notificado',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='contrib.Defensoria', null=True),
        ),
    ]
