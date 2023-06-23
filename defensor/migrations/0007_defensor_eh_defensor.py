# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0006_defensorassessor_defensorsupervisor'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensor',
            name='eh_defensor',
            field=models.BooleanField(default=False, verbose_name='Defensor P\xfablico?'),
        ),
    ]
