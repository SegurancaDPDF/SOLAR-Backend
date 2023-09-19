# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0025_processodashboard'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parte',
            name='parte',
            field=models.SmallIntegerField(default=0, choices=[(0, 'Ativa (autora)'), (1, 'Passiva (r\xe9)'), (2, 'Terceira'), (3, 'V\xedtima'), (4, 'Assistente simples desinteressado (amicus curiae e vulnerabilis)')]),
        ),
    ]
