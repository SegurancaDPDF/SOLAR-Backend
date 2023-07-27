# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nucleo', '0011_nucleo_itinerante'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nucleo',
            name='corregedoria',
        ),
        migrations.RemoveField(
            model_name='nucleo',
            name='diretoria',
        ),
        migrations.RemoveField(
            model_name='nucleo',
            name='dpg',
        ),
        migrations.AddField(
            model_name='nucleo',
            name='indeferimento',
            field=models.BooleanField(default=False, help_text='Tem acesso ao m\xf3dulo Indeferimento?'),
        ),
        migrations.AddField(
            model_name='nucleo',
            name='indeferimento_pode_receber_impedimento',
            field=models.BooleanField(default=False, verbose_name='Pode receber indeferimento por impedimento?'),
        ),
        migrations.AddField(
            model_name='nucleo',
            name='indeferimento_pode_receber_negacao',
            field=models.BooleanField(default=False, verbose_name='Pode receber indeferimento por nega\xe7\xe3o?'),
        ),
        migrations.AddField(
            model_name='nucleo',
            name='indeferimento_pode_receber_suspeicao',
            field=models.BooleanField(default=False, verbose_name='Pode receber indeferimento por suspei\xe7\xe3o?'),
        ),
        migrations.AddField(
            model_name='nucleo',
            name='indeferimento_pode_registrar_baixa',
            field=models.BooleanField(default=False, verbose_name='Pode registrar baixa em Indeferimento?'),
        ),
        migrations.AddField(
            model_name='nucleo',
            name='indeferimento_pode_registrar_decisao',
            field=models.BooleanField(default=False, verbose_name='Pode registrar decis\xe3o em Indeferimento?'),
        ),
    ]
