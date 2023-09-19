# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0004_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentoTipo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=255)),
                ('eproc', models.CharField(default=None, max_length=100, null=True, blank=True)),
                ('grau', models.SmallIntegerField(default=0, choices=[(0, 'Todos'), (1, '1\xba Grau'), (2, '2\xba Grau')])),
                ('ativo', models.BooleanField(default=True)),
            ],
        ),
    ]
