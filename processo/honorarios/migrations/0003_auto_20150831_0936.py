# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('honorarios', '0002_auto_20150825_1009'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='honorario',
            options={'verbose_name': 'Honor\xe1io', 'verbose_name_plural': 'Honor\xe1ios'},
        ),
    ]
