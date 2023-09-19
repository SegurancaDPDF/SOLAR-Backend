# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0010_auto_20160601_1152'),
        ('honorarios', '0007_auto_20160610_1031'),
    ]

    operations = [
        migrations.AddField(
            model_name='honorario',
            name='recurso_vinculado',
            field=models.ForeignKey(default=None, blank=True, to='processo.Processo', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
