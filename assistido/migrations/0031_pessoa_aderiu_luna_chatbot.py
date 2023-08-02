# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0030_alter_estado_civil_pessoa'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoa',
            name='aderiu_luna_chatbot',
            field=models.BooleanField(default=False, verbose_name='Aderiu a Luna Chatbot'),
        ),
    ]
