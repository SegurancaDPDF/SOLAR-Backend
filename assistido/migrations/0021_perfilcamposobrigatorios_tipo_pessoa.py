# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0020_avaliacao_pessoa_juridica'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfilcamposobrigatorios',
            name='tipo_pessoa',
            field=models.SmallIntegerField(default=None, null=True, verbose_name='Tipo de Pessoa', blank=True, choices=[(0, 'Pessoa F\xedsica'), (1, 'Pessoa Jur\xeddica')]),
        ),
    ]
