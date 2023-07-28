# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0099_interesse_conciliacao_justificativa_nao_interesse'),
    ]

    operations = [
        migrations.AddField(
            model_name='qualificacao',
            name='disponivel_para_agendamento_via_app',
            field=models.BooleanField(default=False, verbose_name='Dispon\xedvel para agendamento via apps (Luna, eDefensor, etc)?'),
        ),
    ]
