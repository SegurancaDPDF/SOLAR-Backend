# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0011_auto_20170816_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pessoa',
            name='nome_soundex',
            field=models.CharField(db_index=True, max_length=256, null=True, blank=True),
        ),
    ]
