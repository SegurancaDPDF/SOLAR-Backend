# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0007_auto_20160928_0858'),
        ('contrib', '0008_auto_20161018_1500'),
    ]

    operations = [
        migrations.AddField(
            model_name='servidor',
            name='profissao',
            field=models.ForeignKey(blank=True, to='assistido.Profissao', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
