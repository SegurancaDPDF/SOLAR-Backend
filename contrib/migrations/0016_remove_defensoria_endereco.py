# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0015_auto_20170816_1445'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='defensoria',
            name='endereco',
        ),
    ]
