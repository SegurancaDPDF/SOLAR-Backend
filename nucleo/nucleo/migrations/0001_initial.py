# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Formulario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('posicao', models.SmallIntegerField(null=True, verbose_name='Posi\xe7\xe3o', blank=True)),
                ('texto', models.CharField(max_length=255)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['nucleo', 'posicao'],
                'verbose_name': 'Formul\xe1rio',
                'verbose_name_plural': 'Formul\xe1rios',
            },
        ),
        migrations.CreateModel(
            name='Nucleo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=255)),
                ('nivel', models.SmallIntegerField(default=None, null=True, blank=True)),
                ('coletivo', models.BooleanField(default=False)),
                ('agendamento', models.BooleanField(default=False)),
                ('supervisionado', models.BooleanField(default=False)),
                ('acordo', models.BooleanField(default=False)),
                ('apoio', models.BooleanField(default=True)),
                ('plantao', models.BooleanField(default=False)),
                ('ativo', models.BooleanField(default=True)),
                ('nucleo', models.ForeignKey(related_name='+', default=None, blank=True, to='nucleo.Nucleo', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['-ativo', 'nome'],
                'verbose_name': 'N\xfacleo',
                'verbose_name_plural': 'N\xfacleos',
            },
        ),
        migrations.CreateModel(
            name='Pergunta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('posicao', models.SmallIntegerField(null=True, verbose_name='Posi\xe7\xe3o', blank=True)),
                ('texto', models.CharField(max_length=255)),
                ('tipo', models.SmallIntegerField(default=0, choices=[(0, 'Texto'), (1, 'N\xfamero'), (2, 'Data'), (3, 'Lista')])),
                ('lista', models.CharField(max_length=255, null=True, blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('formulario', models.ForeignKey(to='nucleo.Formulario', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['formulario', 'posicao'],
                'verbose_name': 'Pergunta',
                'verbose_name_plural': 'Perguntas',
            },
        ),
        migrations.CreateModel(
            name='Resposta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('texto', models.CharField(max_length=255, null=True, blank=True)),
                ('atendimento', models.ForeignKey(related_name='+', to='atendimento.Atendimento', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('pergunta', models.ForeignKey(to='nucleo.Pergunta', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'verbose_name': 'Resposta',
                'verbose_name_plural': 'Respostas',
            },
        ),
        migrations.AddField(
            model_name='formulario',
            name='nucleo',
            field=models.ForeignKey(to='nucleo.Nucleo', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
