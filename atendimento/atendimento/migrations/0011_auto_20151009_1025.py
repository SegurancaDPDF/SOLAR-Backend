# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0010_auto_20151007_1115'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assunto',
            options={'ordering': ['-ativo', 'pai__ordem', 'ordem']},
        ),
        migrations.AlterField(
            model_name='assunto',
            name='codigo',
            field=models.CharField(max_length=256, null=True, verbose_name='C\xf3digo', blank=True),
        ),
        migrations.AlterField(
            model_name='assunto',
            name='descricao',
            field=models.CharField(max_length=256, null=True, verbose_name='Desci\xe7\xe3o Completa (Caminho)', blank=True),
        ),
        migrations.AlterField(
            model_name='assunto',
            name='titulo',
            field=models.CharField(max_length=256, verbose_name='T\xedtulo'),
        ),
        migrations.AlterField(
            model_name='atendimento',
            name='assuntos',
            field=models.ManyToManyField(related_name='atendimentos', to='atendimento.Assunto', blank=True),
        ),
    ]
