# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0029_qualificacao_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atendimento',
            name='participantes',
            field=models.ManyToManyField(related_name='atendimentos', to='contrib.Servidor', blank=True),
        ),
    ]
