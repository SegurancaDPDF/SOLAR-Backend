# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0020_criar_cargos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servidor',
            name='profissao',
        ),
    ]
