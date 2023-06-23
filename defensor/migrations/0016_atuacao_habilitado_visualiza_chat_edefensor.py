# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0015_atuacao_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='atuacao',
            name='habilitado_chat_edefensor',
            field=models.BooleanField(default=False, verbose_name='Habilitado pra usar chat e-Defensor'),
        ),
        migrations.AddField(
            model_name='atuacao',
            name='visualiza_chat_edefensor',
            field=models.BooleanField(default=False, verbose_name='Ativada a visualiza\xe7\xe3o do chat e-Defensor'),
        ),
    ]

