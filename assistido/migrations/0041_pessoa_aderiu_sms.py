# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0040_pessoa_rg_data_expedicao'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoa',
            name='aderiu_sms',
            field=models.BooleanField(default=False, verbose_name='Aderiu ao SMS'),
        ),
    ]
