# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0029_redimensiona_foto_servidores'),
        ('indeferimento', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='indeferimento',
            name='defensoria',
            field=models.ForeignKey(
                related_name='indeferimentos',
                on_delete=django.db.models.deletion.DO_NOTHING,
                blank=True,
                to='contrib.Defensoria',
                null=True
            ),
        ),
    ]
