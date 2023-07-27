# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Guiche',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero', models.IntegerField(default=0, verbose_name='N\xfamero')),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['comarca__nome', 'predio__nome', 'numero'],
                'verbose_name': 'Guich\xea',
            },
        ),
        migrations.CreateModel(
            name='Predio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=255)),
                ('visao_comarca', models.BooleanField(default=False)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['comarca__nome', 'nome'],
                'verbose_name': 'Pr\xe9dio',
            },
        ),
    ]
