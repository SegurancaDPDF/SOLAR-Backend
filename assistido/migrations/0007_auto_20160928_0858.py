# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0006_auto_20160803_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pessoa',
            name='declara_identidade_genero',
            field=models.BooleanField(default=False, verbose_name='Declara identidade de g\xeanero'),
        ),
        migrations.AlterField(
            model_name='pessoa',
            name='declara_orientacao_sexual',
            field=models.BooleanField(default=False, verbose_name='Declara orienta\xe7\xe3o sexual'),
        ),
    ]
