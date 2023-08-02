# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0032_pessoa_orientacao_sexual'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pessoa',
            name='tipo_orientacao_sexual',
        ),
    ]
