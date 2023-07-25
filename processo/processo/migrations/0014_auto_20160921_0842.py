# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0013_auto_20160725_1654'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='processo',
            options={'ordering': ['numero_puro', 'id']},
        ),
        migrations.AlterField(
            model_name='processo',
            name='tipo',
            field=models.SmallIntegerField(default=2, choices=[(0, 'Extrajudicial'), (1, 'F\xedsico'), (2, 'Eletr\xf4nico (e-Proc)'), (3, 'Processo Administrativo Disciplinar (PAD)')]),
        ),
        migrations.AlterField(
            model_name='processo',
            name='ultima_consulta',
            field=models.DateTimeField(null=True, verbose_name='Data da Ultima Consulta', blank=True),
        ),
    ]
