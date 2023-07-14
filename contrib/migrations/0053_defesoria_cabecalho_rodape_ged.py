# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0052_bairro_nome_norm'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoria',
            name='cabecalho_documento',
            field=models.TextField(help_text='Para utilizar formata\xe7\xe3o, utilize tags HTML', verbose_name='Cabe\xe7alho Documento GED', blank=True),
        ),
        migrations.AddField(
            model_name='defensoria',
            name='rodape_documento',
            field=models.TextField(help_text='Para utilizar formata\xe7\xe3o, utilize tags HTML', verbose_name='Rodap\xe9 Documento GED', blank=True),
        ),
    ]
