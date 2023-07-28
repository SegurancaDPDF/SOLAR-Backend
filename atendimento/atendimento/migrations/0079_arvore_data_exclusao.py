# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0078_atendimento_add_tipo_notificacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='arvore',
            name='data_exclusao',
            field=models.DateTimeField(verbose_name='Data de Exclus\xe3o', null=True, editable=False),
        ),
    ]
