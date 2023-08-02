# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0016_pessoa_tipo_cadastro'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoa',
            name='aderiu_zap_defensoria',
            field=models.BooleanField(default=False, verbose_name='Aderiu ao Zap Defensoria'),
        ),
    ]
