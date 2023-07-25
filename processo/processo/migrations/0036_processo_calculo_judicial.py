# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0035_processo_competencia_mni'),
    ]

    operations = [
        migrations.AddField(
            model_name='processo',
            name='calculo_judicial',
            field=models.CharField(max_length=50, null=True, verbose_name='C\xf3digo do C\xe1lculo Judicial', blank=True),
        ),
        migrations.AlterField(
            model_name='processo',
            name='nivel_sigilo',
            field=models.SmallIntegerField(default=0, verbose_name='N\xedvel de Sigilo', choices=[(0, 'P\xfablico'), (1, 'Segredo de Justi\xe7a'), (2, 'Sigilo m\xednimo'), (3, 'Sigilo m\xe9dio'), (4, 'Sigilo intenso'), (5, 'Sigilo absoluto')]),
        ),
        migrations.AlterField(
            model_name='processo',
            name='originario',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='processo.Processo', null=True, verbose_name='Processo Origin\xe1rio', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AlterField(
            model_name='processo',
            name='valor_causa',
            field=models.FloatField(default=None, null=True, verbose_name='Valor da Causa', blank=True),
        ),
    ]
