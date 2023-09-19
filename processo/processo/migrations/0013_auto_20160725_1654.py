# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0012_auto_20160624_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fase',
            name='processo',
            field=models.ForeignKey(related_name='fases', to='processo.Processo', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
