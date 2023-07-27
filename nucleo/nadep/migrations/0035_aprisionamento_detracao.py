# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0034_auto_20160803_1646'),
    ]

    operations = [
        migrations.AddField(
            model_name='aprisionamento',
            name='detracao',
            field=models.BooleanField(default=False, verbose_name='Detra\xe7\xe3o'),
        ),
    ]
