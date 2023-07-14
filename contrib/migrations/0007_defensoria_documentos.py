# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0001_initial'),
        ('contrib', '0006_auto_20160620_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoria',
            name='documentos',
            field=models.ManyToManyField(related_name='donos', to='djdocuments.Documento', blank=True),
        ),
    ]
