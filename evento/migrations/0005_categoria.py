# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evento', '0004_auto_20160222_1400'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(unique=True, max_length=256)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-ativo', 'nome'],
            },
        ),
    ]
