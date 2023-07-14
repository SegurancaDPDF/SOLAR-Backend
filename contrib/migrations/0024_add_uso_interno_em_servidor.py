# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0023_cria_papeis_padrao'),
    ]

    operations = [
        migrations.AddField(
            model_name='servidor',
            name='uso_interno',
            field=models.BooleanField(default=False, help_text='Define que este servidor \xe9 de uso interno do sistema'),
        ),
    ]
