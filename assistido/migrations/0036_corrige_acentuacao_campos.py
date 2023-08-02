# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0035_remove_pessoa_tipo_identidade_genero'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pessoa',
            name='identidade_genero',
            field=models.ForeignKey(verbose_name='Identidade de G\xeanero', blank=True, to='contrib.IdentidadeGenero', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AlterField(
            model_name='pessoa',
            name='orientacao_sexual',
            field=models.ForeignKey(verbose_name='Orienta\xe7\xe3o Sexual', blank=True, to='contrib.OrientacaoSexual', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
