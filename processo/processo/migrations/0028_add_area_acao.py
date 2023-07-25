# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0032_defensoria_pode_vincular_processo_judicial'),
        ('processo', '0027_add_tipo_conta_estatistica_documentos'),
    ]

    operations = [
        migrations.AddField(
            model_name='acao',
            name='area',
            field=models.ForeignKey(default=None, to='contrib.Area', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AlterField(
            model_name='acao',
            name='descricao',
            field=models.CharField(default=None, max_length=512, null=True, blank=True),
        ),
    ]
