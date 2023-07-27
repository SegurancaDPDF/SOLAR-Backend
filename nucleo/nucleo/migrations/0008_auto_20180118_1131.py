# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nucleo', '0007_nucleo_encaminhamento'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='nucleo',
            options={'ordering': ['-ativo', 'nome'], 'verbose_name': 'N\xfacleo', 'verbose_name_plural': 'N\xfacleos', 'permissions': (('admin_multidisciplinar', 'Can admin multidisciplinar'),)},
        ),
    ]
