# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0015_auto_20160425_1037'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='atendimento',
            options={'ordering': ['-ativo', '-numero'], 'verbose_name': 'Atendimento Geral', 'verbose_name_plural': 'Atendimentos Gerais', 'permissions': (('view_129', 'Can view 129'), ('view_recepcao', 'Can view Recep\xe7\xe3o'), ('view_defensor', 'Can view Defensor'), ('view_distribuicao', 'Can view Distribui\xe7\xe3o'))},
        ),
        migrations.AlterField(
            model_name='atendimento',
            name='historico',
            field=models.TextField(default=None, null=True, verbose_name='Hist\xf3rico Atendimento', blank=True),
        ),
        migrations.AlterField(
            model_name='atendimento',
            name='historico_recepcao',
            field=models.TextField(default=None, null=True, verbose_name='Hist\xf3rico Agendamento', blank=True),
        ),
    ]
