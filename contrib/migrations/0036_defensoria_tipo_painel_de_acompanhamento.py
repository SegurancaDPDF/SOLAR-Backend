# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0035_add_aceita_agendamento_defensoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoria',
            name='tipo_painel_de_acompanhamento',
            field=models.SmallIntegerField(default=1, verbose_name='Tipo do Painel de Acompanhamento', choices=[(1, 'Padr\xe3o'), (2, 'Simplificado')]),
        ),
    ]
