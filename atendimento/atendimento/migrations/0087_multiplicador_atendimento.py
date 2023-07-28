# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0086_documento_analise_envio'),
    ]

    operations = [
        migrations.AddField(
            model_name='atendimento',
            name='multiplicador',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='qualificacao',
            name='multiplica_estatistica',
            field=models.BooleanField(default=False, help_text='Permite informar valor do campo Atendimento.multiplicador para multiplicar o valor nos relat\xf3rios?'),
        ),
    ]
