# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Atuacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('data_atualizacao', models.DateTimeField(default=None, null=True, verbose_name='Data da \xfaltima atualiza\xe7\xe3o', blank=True)),
                ('data_exclusao', models.DateTimeField(verbose_name='Data de Exclus\xe3o', null=True, editable=False)),
                ('tipo', models.SmallIntegerField(default=2, choices=[(0, 'Substitui\xe7\xe3o'), (1, 'Acumula\xe7\xe3o'), (2, 'Titularidade')])),
                ('data_inicial', models.DateTimeField()),
                ('data_final', models.DateTimeField(default=None, null=True, blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('codigo_plantao', models.CharField(default=None, max_length=25, null=True, verbose_name='C\xf3d. Plant\xe3o', blank=True)),
                ('codigo_plantao_local', models.CharField(default=None, max_length=25, null=True, verbose_name='C\xf3d. Plant\xe3o Local', blank=True)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['defensor__servidor__usuario__first_name', '-ativo', '-tipo', 'data_inicial'],
                'verbose_name': 'Atua\xe7\xe3o',
                'verbose_name_plural': 'Atua\xe7\xf5es',
            },
        ),
        migrations.CreateModel(
            name='Defensor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('usuario_eproc', models.CharField(default=None, max_length=100, null=True, blank=True)),
                ('senha_eproc', models.CharField(default=None, max_length=100, null=True, blank=True)),
                ('nao_possui_eproc', models.BooleanField(default=False)),
                ('ativo', models.BooleanField(default=True)),
                ('servidor', models.OneToOneField(to='contrib.Servidor', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('supervisor', models.ForeignKey(related_name='assessores', default=None, blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['supervisor__id', 'servidor__usuario__first_name', 'servidor__usuario__last_name'],
                'verbose_name': 'Defensor',
                'verbose_name_plural': 'Defensores',
            },
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero', models.SmallIntegerField()),
                ('data', models.DateField()),
                ('tipo', models.SmallIntegerField(default=0, choices=[(0, 'Portaria'), (1, 'Ato'), (2, 'Edital')])),
                ('doe_numero', models.SmallIntegerField(default=None, null=True, blank=True)),
                ('doe_data', models.DateField(default=None, null=True, blank=True)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-ativo', 'tipo', 'data', 'numero'],
            },
        ),
        migrations.CreateModel(
            name='Supervisor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('data_atualizacao', models.DateTimeField(default=None, null=True, verbose_name='Data da \xfaltima atualiza\xe7\xe3o', blank=True)),
                ('data_exclusao', models.DateTimeField(verbose_name='Data de Exclus\xe3o', null=True, editable=False)),
                ('data_inicial', models.DateTimeField(null=True)),
                ('data_final', models.DateTimeField(default=None, null=True, blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('codigo_plantao', models.CharField(default=None, max_length=25, null=True, verbose_name='C\xf3d. Plant\xe3o', blank=True)),
                ('codigo_plantao_local', models.CharField(default=None, max_length=25, null=True, verbose_name='C\xf3d. Plant\xe3o Local', blank=True)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('defensor', models.ForeignKey(related_name='supervisionados', to='defensor.Defensor', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('excluido_por', models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('supervisor', models.ForeignKey(related_name='supervisores', blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
        ),
        migrations.AddField(
            model_name='atuacao',
            name='defensor',
            field=models.ForeignKey(related_name='all_atuacoes', to='defensor.Defensor', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='atuacao',
            name='defensoria',
            field=models.ForeignKey(related_name='+', to='contrib.Defensoria', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='atuacao',
            name='documento',
            field=models.ForeignKey(blank=True, to='defensor.Documento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='atuacao',
            name='excluido_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='atuacao',
            name='titular',
            field=models.ForeignKey(related_name='+', blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
