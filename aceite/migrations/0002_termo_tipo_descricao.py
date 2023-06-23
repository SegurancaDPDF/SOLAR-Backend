# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aceite', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='termo',
            name='tipo_descricao',
            field=models.CharField(default='txt', max_length=5, choices=[('txt', 'Texto Puro'), ('html', 'Texto HTML')]),
        ),
    ]
