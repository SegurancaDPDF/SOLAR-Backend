# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_tipoevento_anotacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classe',
            name='tipo_processo',
            field=models.PositiveSmallIntegerField(default=None, null=True, blank=True, choices=[(10, 'Atendimento'), (20, 'Apoio'), (30, 'Tarefa'), (40, 'Processo'), (50, 'PROPAC'), (60, 'Indeferimento'), (70, 'Atividade Extraordin\xe1ria')]),
        ),
        migrations.AddField(
            model_name='evento',
            name='titulo',
            field=models.CharField(default=None, max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='evento',
            name='processo',
            field=models.ForeignKey(related_name='eventos', on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to='core.Processo', null=True),
        ),
        migrations.AlterField(
            model_name='evento',
            name='numero',
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='evento',
            unique_together=set([]),
        ),
        migrations.AlterField(
            model_name='processo',
            name='tipo',
            field=models.PositiveSmallIntegerField(choices=[(10, 'Atendimento'), (20, 'Apoio'), (30, 'Tarefa'), (40, 'Processo'), (50, 'PROPAC'), (60, 'Indeferimento'), (70, 'Atividade Extraordin\xe1ria')]),
        ),
        migrations.AlterField(
            model_name='tipoevento',
            name='tipo_processo',
            field=models.PositiveSmallIntegerField(default=None, null=True, blank=True, choices=[(10, 'Atendimento'), (20, 'Apoio'), (30, 'Tarefa'), (40, 'Processo'), (50, 'PROPAC'), (60, 'Indeferimento'), (70, 'Atividade Extraordin\xe1ria')]),
        ),
    ]
