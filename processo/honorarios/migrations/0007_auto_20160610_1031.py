# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('honorarios', '0006_documento'),
    ]

    operations = [
        migrations.AddField(
            model_name='honorario',
            name='recurso_finalizado',
            field=models.BooleanField(default=False, help_text='Ao finalizar o Recurso, deve ser marcado como True para liberar as movimentacoes.'),
        ),
        migrations.AlterField(
            model_name='documento',
            name='visivel',
            field=models.BooleanField(default=True, verbose_name='Visivel'),
        ),
    ]
