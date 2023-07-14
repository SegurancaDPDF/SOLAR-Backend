# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0049_defensoria_tipo_evento'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoriavara',
            name='distribuicao_automatica',
            field=models.BooleanField(default=False, verbose_name='Distribuir Automaticamente'),
        ),
    ]
