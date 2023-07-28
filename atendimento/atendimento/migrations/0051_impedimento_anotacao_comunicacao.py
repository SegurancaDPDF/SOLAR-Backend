# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0050_documento_defensoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='impedimento',
            name='anotacao_comunicacao',
            field=models.TextField(null=True),
        ),
    ]
