# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nucleo', '0010_nucleo_corregedoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='nucleo',
            name='itinerante',
            field=models.BooleanField(default=False, help_text='Tem acesso ao m\xf3dulo Itinerante/Multir\xe3o?'),
        ),
    ]
