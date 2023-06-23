# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0011_auto_20190402_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atuacao',
            name='cadastrado_por',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, editable=False, to='contrib.Servidor', null=True),
        ),
        migrations.AlterField(
            model_name='atuacao',
            name='cargo',
            field=models.ForeignKey(related_name='all_atuacoes', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='contrib.Cargo', null=True),
        ),
        migrations.AlterField(
            model_name='atuacao',
            name='defensor',
            field=models.ForeignKey(related_name='all_atuacoes', on_delete=django.db.models.deletion.PROTECT, to='defensor.Defensor'),
        ),
        migrations.AlterField(
            model_name='atuacao',
            name='defensoria',
            field=models.ForeignKey(related_name='all_atuacoes', on_delete=django.db.models.deletion.PROTECT, to='contrib.Defensoria'),
        ),
        migrations.AlterField(
            model_name='atuacao',
            name='documento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='defensor.Documento', null=True),
        ),
        migrations.AlterField(
            model_name='atuacao',
            name='excluido_por',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, editable=False, to='contrib.Servidor', null=True),
        ),
        migrations.AlterField(
            model_name='atuacao',
            name='titular',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='defensor.Defensor', null=True),
        ),
        migrations.AlterField(
            model_name='defensor',
            name='supervisor',
            field=models.ForeignKey(related_name='assessores', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='defensor.Defensor', null=True),
        ),
        migrations.AlterField(
            model_name='supervisor',
            name='cadastrado_por',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, editable=False, to='contrib.Servidor', null=True),
        ),
        migrations.AlterField(
            model_name='supervisor',
            name='defensor',
            field=models.ForeignKey(related_name='supervisionados', on_delete=django.db.models.deletion.PROTECT, to='defensor.Defensor'),
        ),
        migrations.AlterField(
            model_name='supervisor',
            name='excluido_por',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, editable=False, to='contrib.Servidor', null=True),
        ),
        migrations.AlterField(
            model_name='supervisor',
            name='supervisor',
            field=models.ForeignKey(related_name='supervisores', on_delete=django.db.models.deletion.PROTECT, blank=True, to='defensor.Defensor', null=True),
        ),
    ]
