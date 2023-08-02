# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0018_auto_20180530_1212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pessoa',
            name='tipo',
            field=models.SmallIntegerField(default=0, null=True, verbose_name='Tipo', choices=[(0, 'Pessoa F\xedsica'), (1, 'Pessoa Jur\xeddica')]),
        ),
    ]
