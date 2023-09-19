# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('honorarios', '0008_honorario_recurso_vinculado'),
    ]

    operations = [
        migrations.AddField(
            model_name='honorario',
            name='baixado',
            field=models.BooleanField(default=False, verbose_name='Honorario baixado/finalizado'),
        ),
    ]
