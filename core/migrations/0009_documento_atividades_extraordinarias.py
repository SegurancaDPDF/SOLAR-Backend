# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_atividades_extraordinarias'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='processo',
            field=models.ForeignKey(related_name='documentos', on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to='core.Processo', null=True),
        ),
    ]
