# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0039_alter_field_url_on_menuextra'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoria',
            name='pode_cadastrar_atividade_extraordinaria',
            field=models.BooleanField(default=False, help_text='Habilita CRUD de Atividade Extraordin\xe1ria no painel do Defensor Atuante', verbose_name='Pode cadastrar Atividade Extraordin\xe1ria?'),
        ),
        migrations.AlterField(
            model_name='menuextra',
            name='url',
            field=models.URLField(blank=True),
        ),
    ]
