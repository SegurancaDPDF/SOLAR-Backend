# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0092_tipo_atendimento_apoio'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoa',
            name='representante',
            field=models.ForeignKey(related_name='representados', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='atendimento.Pessoa', null=True),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='representante_modalidade',
            field=models.CharField(default=None, max_length=2, null=True, blank=True, choices=[('P', 'Representa\xe7\xe3o legal de ascendente (pais)'), ('AP', 'Assist\xeancia dos pais'), ('SP', 'Substitui\xe7\xe3o ou representa\xe7\xe3o processual nos caos de a\xe7\xf5es coletivas'), ('T', 'Tutoria'), ('C', 'Curadoria')]),
        ),
    ]
