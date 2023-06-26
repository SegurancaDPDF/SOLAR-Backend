# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0001_initial'),
        ('defensor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titulo', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('tipo', models.SmallIntegerField(default=1, choices=[(0, 'Permiss\xe3o'), (1, 'Bloqueio')])),
                ('data_cad', models.DateTimeField(auto_now_add=True, verbose_name='Data Cadastro')),
                ('data_ini', models.DateField(verbose_name='Data In\xedcio')),
                ('data_fim', models.DateField(default=None, null=True, verbose_name='Data T\xe9rmino', blank=True)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-ativo', 'defensor', '-data_cad'],
            },
        ),
        migrations.CreateModel(
            name='Agenda',
            fields=[
                ('evento_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='evento.Evento', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('hora_ini', models.TimeField(verbose_name='Hora In\xedcio')),
                ('hora_fim', models.TimeField(verbose_name='Hora T\xe9rmino')),
                ('vagas', models.PositiveSmallIntegerField()),
                ('duracao', models.PositiveSmallIntegerField()),
                ('simultaneos', models.PositiveSmallIntegerField(default=1)),
                ('horarios', models.TextField(default=None, null=True, blank=True)),
                ('atuacao', models.ForeignKey(related_name='+', default=None, blank=True, to='defensor.Atuacao', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['-ativo', 'atuacao__defensor', '-data_cad'],
            },
            bases=('evento.evento',),
        ),
        migrations.AddField(
            model_name='evento',
            name='comarca',
            field=models.ForeignKey(default=None, blank=True, to='contrib.Comarca', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='evento',
            name='defensor',
            field=models.ForeignKey(default=None, blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='evento',
            name='pai',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='evento.Evento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
