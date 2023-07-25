# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0030_novos_graus_processo'),
    ]

    operations = [
        migrations.AddField(
            model_name='fase',
            name='data_termino_protocolo',
            field=models.DateTimeField(default=None, null=True, verbose_name='Data T\xe9rmino do Protocolo', blank=True),
        ),
    ]
