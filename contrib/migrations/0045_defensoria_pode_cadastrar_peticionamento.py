# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0044_papel_css_label_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoria',
            name='pode_cadastrar_peticionamento',
            field=models.BooleanField(default=False, help_text='Habilita CRUD de Peticionamentos', verbose_name='Pode cadastrar Peticionamento?'),
        ),
        migrations.AlterField(
            model_name='defensoria',
            name='pode_cadastrar_atividade_extraordinaria',
            field=models.BooleanField(default=False, help_text='Habilita CRUD de Atividade Extraordin\xe1ria', verbose_name='Pode cadastrar Atividade Extraordin\xe1ria?'),
        ),
    ]
