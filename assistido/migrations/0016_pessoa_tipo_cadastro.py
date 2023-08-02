# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0015_auto_20180111_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoa',
            name='tipo_cadastro',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Tipo Cadastro', choices=[(10, 'Simplificado'), (20, 'Completo')]),
        ),
    ]
