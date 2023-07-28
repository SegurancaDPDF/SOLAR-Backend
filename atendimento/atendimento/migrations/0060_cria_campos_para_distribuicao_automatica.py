# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0029_cria_campos_para_distribuicao_automatica_de_encaminhamento'),
        ('atendimento', '0059_vw_atendimento_dia_nome_social'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensor',
            name='data_encaminhado',
            field=models.DateTimeField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='defensor',
            name='encaminhado_para',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Defensoria', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
