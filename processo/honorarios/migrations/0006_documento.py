# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import processo.honorarios.models


class Migration(migrations.Migration):

    dependencies = [
        ('honorarios', '0005_auto_20160114_1109'),
    ]

    operations = [
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('anexo', models.FileField(default=None, upload_to=processo.honorarios.models.documento_file_name)),
                ('nome', models.CharField(max_length=256)),
                ('visivel', models.BooleanField(default=True, verbose_name='Ativo')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('movimento', models.ForeignKey(related_name='documentos_movimento', default=None, to='honorarios.Movimento', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['movimento', 'nome'],
                'verbose_name': 'Documento',
                'verbose_name_plural': 'Documentos',
            },
        ),
    ]
