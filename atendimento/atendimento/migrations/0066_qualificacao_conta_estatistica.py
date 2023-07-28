# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0065_qualificacao_add_tipo_anotacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='qualificacao',
            name='conta_estatistica',
            field=models.BooleanField(default=True, help_text='Conta Estat\xedsticas?'),
        ),
    ]
