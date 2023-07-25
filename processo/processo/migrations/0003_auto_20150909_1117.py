# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0002_audiencia_custodia'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assunto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=512)),
                ('codigo_eproc', models.CharField(default=None, max_length=25, null=True, blank=True)),
                ('codigo_cnj', models.CharField(default=None, max_length=25, null=True, blank=True)),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
            ],
        ),
        migrations.CreateModel(
            name='ProcessoAssunto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('processo', models.ForeignKey(to='processo.Processo', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('assunto', models.ForeignKey(to='processo.Assunto', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'db_table': 'processo_processo_assuntos',
            },
        ),
        migrations.AlterField(
            model_name='audiencia',
            name='custodia',
            field=models.SmallIntegerField(default=0, choices=[(0, 'N\xe3o se aplica'), (10, '1. Relaxamento de Flagrante'), (21, '2.1. Liberdade Provis\xf3ria - com fian\xe7a'), (22, '2.2. Liberdade Provis\xf3ria - sem fian\xe7a'), (23, '2.3. Liberdade Provis\xf3ria - com medida cautelar'), (24, '2.4. Liberdade Provis\xf3ria - sem medida cautelar'), (30, '3. Manteve a pris\xe3o')]),
        ),
        # migrations.AddField(
        #     model_name='processo',
        #     name='assuntos',
        #     field=models.ManyToManyField(to='processo.Assunto', blank=True),
        # ),
        migrations.AddField(
            model_name='processo',
            name='assuntos',
            field=models.ManyToManyField(to='processo.Assunto', through='processo.ProcessoAssunto'),
        ),
    ]
