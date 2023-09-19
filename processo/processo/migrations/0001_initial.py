# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
# Bibliotecas de terceiros
from django.db import migrations, models

# Solar
import processo.processo.models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0001_initial'),
        ('contrib', '0001_initial'),
        ('defensor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Acao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=512)),
                ('descricao', models.CharField(default=None, max_length=512, null=True)),
                ('codigo_eproc', models.CharField(default=None, max_length=25, null=True, blank=True)),
                ('codigo_cnj', models.CharField(default=None, max_length=25, null=True, blank=True)),
                ('judicial', models.BooleanField(default=True)),
                ('extrajudicial', models.BooleanField(default=False)),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
            ],
            options={
                'ordering': ['-ativo', 'nome'],
                'verbose_name': 'Tipo de A\xe7\xe3o',
                'verbose_name_plural': 'Tipos de A\xe7\xf5es',
            },
        ),
        migrations.CreateModel(
            name='DocumentoFase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('arquivo', models.FileField(default=None, null=True, upload_to=processo.processo.models.documento_fase_file_name, blank=True)),
                ('nome', models.CharField(max_length=255)),
                ('eproc', models.CharField(default=None, max_length=100, null=True, blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('data_enviado', models.DateTimeField(auto_now_add=True, null=True)),
                ('enviado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['-ativo', 'fase', 'nome'],
            },
        ),
        migrations.CreateModel(
            name='Fase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descricao', models.TextField()),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('data_protocolo', models.DateTimeField(default=None, null=True, verbose_name='Data de Protocolo')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('automatico', models.BooleanField(default=False, verbose_name='Autom\xe1tico')),
                ('atividade', models.SmallIntegerField(default=0, choices=[(1, 'Audi\xeancia'), (2, 'J\xfari'), (3, 'Senten\xe7a'), (4, 'Recurso')])),
                ('plantao', models.BooleanField(default=False, verbose_name='Plant\xe3o')),
                ('evento_eproc', models.SmallIntegerField(default=None, null=True, blank=True)),
                ('usuario_eproc', models.CharField(default=None, max_length=25, null=True, blank=True)),
            ],
            options={
                'ordering': ['-ativo', '-data_cadastro', 'tipo__nome'],
                'verbose_name': 'Fase Processual',
                'verbose_name_plural': 'Fases Processuais',
            },
        ),
        migrations.CreateModel(
            name='FaseTipo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=512)),
                ('descricao', models.CharField(default=None, max_length=512, null=True, blank=True)),
                ('codigo_eproc', models.CharField(default=None, max_length=25, null=True, blank=True)),
                ('audiencia', models.BooleanField(default=False, verbose_name='Audi\xeancia')),
                ('juri', models.BooleanField(default=False, verbose_name='J\xfari')),
                ('sentenca', models.BooleanField(default=False, verbose_name='Senten\xe7a')),
                ('recurso', models.BooleanField(default=False, verbose_name='Recurso')),
                ('judicial', models.BooleanField(default=True)),
                ('extrajudicial', models.BooleanField(default=False)),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
            ],
            options={
                'ordering': ['-ativo', 'nome'],
                'verbose_name': 'Tipo de Fase do Processo',
                'verbose_name_plural': 'Tipos de Fases dos Processos',
            },
        ),
        migrations.CreateModel(
            name='Parte',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('parte', models.SmallIntegerField(default=0, choices=[(0, 'Autora'), (1, 'R\xe9')])),
                ('data_vista', models.DateTimeField(default=None, null=True, verbose_name='Data da Vista', blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('atendimento', models.ForeignKey(related_name='+', default=None, blank=True, to='atendimento.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('defensor', models.ForeignKey(related_name='+', default=None, blank=True, to='defensor.Defensor', null=True, verbose_name='Defensor Respons\xe1vel', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('defensor_cadastro', models.ForeignKey(related_name='+', default=None, blank=True, to='defensor.Defensor', null=True, verbose_name='Defensor Cadastro', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('defensoria', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Defensoria', null=True, verbose_name='Defensoria Respons\xe1vel', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('defensoria_cadastro', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Defensoria', null=True, verbose_name='Defensoria Cadastro', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['-ativo', 'processo'],
                'verbose_name': 'Parte do Processo',
                'verbose_name_plural': 'Partes dos Processos',
            },
        ),
        migrations.CreateModel(
            name='Processo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ultima_consulta', models.DateTimeField(null=True, verbose_name='Data da Ultima Consulta')),
                ('tipo', models.SmallIntegerField(default=2, choices=[(0, 'Extrajudicial'), (1, 'F\xedsico'), (2, 'Eletr\xf4nico (e-Proc)')])),
                ('grau', models.SmallIntegerField(default=None, null=True, blank=True, choices=[(1, '1\xba Grau'), (2, '2\xba Grau')])),
                ('numero', models.CharField(max_length=50, null=True, verbose_name='N\xfamero', blank=True)),
                ('numero_puro', models.CharField(max_length=50, null=True, verbose_name='N\xfamero puro', blank=True)),
                ('chave', models.CharField(max_length=50, null=True, verbose_name='Chave', blank=True)),
                ('acao_cnj', models.CharField(max_length=50, null=True, blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('acao', models.ForeignKey(default=None, blank=True, to='processo.Acao', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('area', models.ForeignKey(default=None, blank=True, to='contrib.Area', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('comarca', models.ForeignKey(default=None, blank=True, to='contrib.Comarca', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['numero'],
            },
        ),
        migrations.CreateModel(
            name='ProcessoApenso',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('apensado', models.ForeignKey(related_name='+', default=None, blank=True, to='processo.Processo', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('apensado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('pai', models.ForeignKey(related_name='+', default=None, blank=True, to='processo.Processo', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['pai', 'apensado', 'data_cadastro'],
                'verbose_name': 'Apenso de Processo',
                'verbose_name_plural': 'Apensos de Processos',
            },
        ),
        migrations.CreateModel(
            name='Audiencia',
            fields=[
                ('fase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='processo.Fase', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('audiencia_realizada', models.BooleanField(default=False, verbose_name='Audi\xeancia Realizada')),
            ],
            bases=('processo.fase',),
        ),
        migrations.AddField(
            model_name='processo',
            name='peticao_inicial',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='processo.Fase', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='processo',
            name='vara',
            field=models.ForeignKey(default=None, blank=True, to='contrib.Vara', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='parte',
            name='processo',
            field=models.ForeignKey(related_name='parte', verbose_name='Processo', to='processo.Processo', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='fase',
            name='cadastrado_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='fase',
            name='defensor_cadastro',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='fase',
            name='defensor_substituto',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='fase',
            name='parte',
            field=models.ForeignKey(default=None, blank=True, to='processo.Parte', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='fase',
            name='processo',
            field=models.ForeignKey(default=None, blank=True, to='processo.Processo', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='fase',
            name='tipo',
            field=models.ForeignKey(default=None, blank=True, to='processo.FaseTipo', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='documentofase',
            name='fase',
            field=models.ForeignKey(to='processo.Fase', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
