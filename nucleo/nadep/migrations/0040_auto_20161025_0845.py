# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0039_prisao_prestacao_pecuniaria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aprisionamento',
            name='prisao',
            field=models.ForeignKey(related_name='aprisionamentos', to='nadep.Prisao', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
