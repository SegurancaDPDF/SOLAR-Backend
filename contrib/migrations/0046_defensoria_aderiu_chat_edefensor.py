# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0045_defensoria_pode_cadastrar_peticionamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoria',
            name='aderiu_chat_edefensor',
            field=models.BooleanField(default=False, verbose_name='Aderiu Chat e-Defensor'),
        ),
    ]

