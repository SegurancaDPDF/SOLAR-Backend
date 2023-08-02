# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0002_auto_20150525_0835'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoaassistida',
            name='automatico',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='filiacao',
            name='tipo',
            field=models.SmallIntegerField(choices=[(0, 'M\xe3e'), (1, 'Pai')]),
        ),
        migrations.AlterField(
            model_name='pessoaassistida',
            name='cartao_sus',
            field=models.BooleanField(default=False, verbose_name='Cart\xe3o SUS'),
        ),
        migrations.AlterField(
            model_name='pessoaassistida',
            name='falecido',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='pessoaassistida',
            name='idoso',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='pessoaassistida',
            name='plano_saude',
            field=models.BooleanField(default=False, verbose_name='Plano de Sa\xfade'),
        ),
        migrations.AlterField(
            model_name='pessoaassistida',
            name='pne',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='pessoaassistida',
            name='preso',
            field=models.BooleanField(default=False),
        ),
    ]
