# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0022_renomear_labels_campos_renda_assistido'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pessoa',
            options={'ordering': ['nome'], 'permissions': (('unificar_pessoa', 'Pode unificar pessoa'),)},
        ),
    ]
