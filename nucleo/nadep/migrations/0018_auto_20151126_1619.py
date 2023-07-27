# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0002_auto_20150525_0835'),
        ('nadep', '0017_auto_20151125_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='atendimento',
            name='interessado',
            field=models.ForeignKey(blank=True, to='assistido.PessoaAssistida', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AlterField(
            model_name='prisao',
            name='duracao_pena_anos',
            field=models.SmallIntegerField(default=0, verbose_name='Dura\xe7\xe3o da Pena (Anos)', blank=True),
        ),
        migrations.AlterField(
            model_name='prisao',
            name='duracao_pena_dias',
            field=models.SmallIntegerField(default=0, verbose_name='Dura\xe7\xe3o da Pena (Dias)', blank=True),
        ),
        migrations.AlterField(
            model_name='prisao',
            name='duracao_pena_meses',
            field=models.SmallIntegerField(default=0, verbose_name='Dura\xe7\xe3o da Pena (Meses)', blank=True),
        ),
    ]
