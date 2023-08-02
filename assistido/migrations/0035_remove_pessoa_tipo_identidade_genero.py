# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0034_pessoa_identidade_genero'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pessoa',
            name='tipo_identidade_genero',
        ),
    ]
