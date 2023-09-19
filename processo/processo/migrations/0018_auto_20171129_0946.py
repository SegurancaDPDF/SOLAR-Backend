# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0017_acao_acao_penal'),
    ]

    operations = [
        migrations.AddField(
            model_name='processo',
            name='atualizado',
            field=models.BooleanField(default=False, verbose_name='Atualizado via ProcAPI'),
        ),
        migrations.AddField(
            model_name='processo',
            name='atualizando',
            field=models.BooleanField(default=False, verbose_name='Atualizando via ProcAPI'),
        ),
        migrations.AddField(
            model_name='processo',
            name='ultima_modificacao',
            field=models.DateTimeField(null=True, verbose_name='Data da \xdaltima Modifica\xe7\xe3o no ProcAPI', blank=True),
        ),
        migrations.AlterField(
            model_name='processo',
            name='ultima_consulta',
            field=models.DateTimeField(null=True, verbose_name='Data da \xdaltima Consulta para Atualiza\xe7\xe3o no ProcAPI', blank=True),
        ),
    ]
