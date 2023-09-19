# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('honorarios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='honorario',
            name='defensor',
            field=models.ForeignKey(related_name='honorarios_defensor', default=None, blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AlterField(
            model_name='honorario',
            name='defensoria',
            field=models.ForeignKey(related_name='honorarios_defensoria', default=None, blank=True, to='contrib.Defensoria', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
