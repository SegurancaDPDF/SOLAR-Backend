# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0041_pessoa_aderiu_sms'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoa',
            name='aderiu_edefensor',
            field=models.BooleanField(default=False, verbose_name='Aderiu ao e-Defensor'),
        ),
    ]

