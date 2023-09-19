# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='audiencia',
            name='custodia',
            field=models.SmallIntegerField(default=0, choices=[(0, 'N\xe3o se aplica'), (10, '1. Relaxamento de Flagrante'), (21, '2.1. Liberdade Provis\xf3ria - com fian\xe7a'), (22, '2.2. Liberdade Provis\xf3ria - sem fian\xe7a'), (23, '2.3. Liberdade Provis\xf3ria - com medida cautelar'), (24, '2.3. Liberdade Provis\xf3ria - sem medida cautelar'), (30, '3. Manteve a pris\xe3o')]),
        ),
    ]
