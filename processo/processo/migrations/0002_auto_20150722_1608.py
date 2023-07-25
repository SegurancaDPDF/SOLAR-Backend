# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0004_auto_20150611_0956'),
        ('processo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='audiencia',
            name='baixado_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='audiencia',
            name='data_baixa',
            field=models.DateTimeField(verbose_name='Data de Baixa', null=True, editable=False),
        ),
        migrations.AddField(
            model_name='fase',
            name='data_exclusao',
            field=models.DateTimeField(verbose_name='Data de Exclus\xe3o', null=True, editable=False),
        ),
        migrations.AddField(
            model_name='fase',
            name='excluido_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='parte',
            name='data_exclusao',
            field=models.DateTimeField(verbose_name='Data de Exclus\xe3o', null=True, editable=False),
        ),
        migrations.AddField(
            model_name='parte',
            name='excluido_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='processo',
            name='cadastrado_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='processo',
            name='data_cadastro',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True),
        ),
        migrations.AddField(
            model_name='processo',
            name='data_exclusao',
            field=models.DateTimeField(verbose_name='Data de Exclus\xe3o', null=True, editable=False),
        ),
        migrations.AddField(
            model_name='processo',
            name='excluido_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
