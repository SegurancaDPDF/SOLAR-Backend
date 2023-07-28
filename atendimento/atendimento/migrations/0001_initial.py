# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models
import django.db.models.deletion

# Solar
import atendimento.atendimento.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Acordo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.PositiveSmallIntegerField(default=0, choices=[(0, 'Sim - Partes entraram em acordo'), (1, 'N\xe3o - Partes n\xe3o entraram em acordo'), (2, 'N\xe3o - Requerente n\xe3o compareceu'), (3, 'N\xe3o - Requerido n\xe3o compareceu'), (4, 'N\xe3o - Ambas partes n\xe3o compareceram')])),
            ],
        ),
        migrations.CreateModel(
            name='Atendimento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero', models.BigIntegerField(null=True, blank=True)),
                ('tipo', models.PositiveSmallIntegerField(default=0, choices=[(0, 'Liga\xe7\xe3o'), (1, 'Inicial'), (2, 'Retorno'), (3, 'Recep\xe7\xe3o'), (4, 'Apoio de N\xfacleo Especializado'), (5, 'Anota\xe7\xe3o'), (6, 'Processo'), (7, 'Visita ao Preso')])),
                ('agenda', models.PositiveSmallIntegerField(default=0, choices=[(0, 'Pauta'), (1, 'Extra-Pauta')])),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')),
                ('data_agendamento', models.DateTimeField(default=None, null=True, verbose_name='Data do agendamento', blank=True)),
                ('data_atendimento', models.DateTimeField(default=None, null=True, verbose_name='Data do atendimento', blank=True)),
                ('historico', models.TextField(default=None, null=True, blank=True)),
                ('historico_recepcao', models.TextField(default=None, null=True, blank=True)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-ativo', '-numero'],
                'verbose_name': 'Atendimento Geral',
                'verbose_name_plural': 'Atendimentos Gerais',
                'permissions': (('view_129', 'Can view 129'), ('view_recepcao', 'Can view Recep\xe7\xe3o'), ('view_defensor', 'Can view Defensor')),
            },
        ),
        migrations.CreateModel(
            name='Coletivo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('propac', models.CharField(max_length=25)),
            ],
            options={
                'verbose_name': 'Atendimento Coletivo',
                'verbose_name_plural': 'Atendimentos Coletivos',
            },
        ),
        migrations.CreateModel(
            name='Cronometro',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inicio', models.DateTimeField(default=None, null=True, verbose_name='In\xedcio', blank=True)),
                ('termino', models.DateTimeField(auto_now=True, verbose_name='T\xe9rmino')),
                ('duracao', models.IntegerField(default=0, verbose_name='Dura\xe7\xe3o')),
                ('finalizado', models.BooleanField(default=False)),
                ('motivo_finalizou_ligacao', models.PositiveSmallIntegerField(default=0, choices=[(0, 'Finalizada'), (1, 'Caiu'), (2, 'Engano'), (3, 'Trote'), (4, 'Tempo Expirado'), (5, 'Desist\xeancia')])),
            ],
            options={
                'verbose_name': 'Cron\xf4metro',
                'verbose_name_plural': 'Cronometros',
            },
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('arquivo', models.FileField(default=None, null=True, upload_to=atendimento.atendimento.models.documento_file_name, blank=True)),
                ('nome', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('data_enviado', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'ordering': ['-ativo', '-atendimento__numero', 'nome'],
            },
        ),
        migrations.CreateModel(
            name='Encaminhamento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=200)),
                ('email', models.EmailField(default=None, max_length=128, null=True, blank=True)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-ativo', 'nome'],
            },
        ),
        migrations.CreateModel(
            name='Especializado',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=255)),
                ('ativo', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Impedimento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('justificativa', models.TextField()),
                ('data_confirmado', models.DateTimeField(default=None, null=True, blank=True)),
                ('data_cancelado', models.DateTimeField(default=None, null=True, blank=True)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-ativo', 'pessoa__nome', 'defensor'],
            },
        ),
        migrations.CreateModel(
            name='Informacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titulo', models.CharField(max_length=200)),
                ('texto', models.TextField()),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-ativo', 'titulo'],
                'verbose_name': 'Informa\xe7\xe3o',
                'verbose_name_plural': 'Informa\xe7\xf5es',
            },
        ),
        migrations.CreateModel(
            name='Itinerante',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=200)),
                ('ativo', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Justificativa',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('justificativa', models.TextField(default=None, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pergunta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.CharField(unique=True, max_length=64)),
                ('texto', models.CharField(default='', max_length=255)),
                ('dica', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Pergunta',
                'verbose_name_plural': 'Perguntas',
            },
        ),
        migrations.CreateModel(
            name='Pessoa',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.SmallIntegerField(choices=[(0, 'Requerente'), (1, 'Requerido')])),
                ('responsavel', models.BooleanField(default=False)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-ativo', '-atendimento__numero', 'tipo', '-responsavel', 'pessoa__nome'],
                'verbose_name': 'Parte',
                'verbose_name_plural': 'Partes',
            },
        ),
        migrations.CreateModel(
            name='Procedimento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')),
                ('tipo', models.SmallIntegerField(choices=[(1, 'Agendamento Inicial'), (2, 'Agendamento Retorno'), (3, 'Encaminhamento'), (4, 'Informa\xe7\xe3o'), (5, 'Reagendamento')])),
            ],
            options={
                'ordering': ['-data_cadastro'],
            },
        ),
        migrations.CreateModel(
            name='Qualificacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titulo', models.CharField(max_length=255)),
                ('texto', models.TextField(default=None, null=True, blank=True)),
                ('perguntas', models.TextField(default=None, null=True, blank=True)),
                ('documentos', models.TextField(default=None, null=True, blank=True)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-ativo', 'titulo'],
                'verbose_name': 'Qualfica\xe7\xe3o',
                'verbose_name_plural': 'Qualifica\xe7\xf5es'
            },
        ),
        migrations.CreateModel(
            name='Resposta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('texto', models.CharField(default='', max_length=255)),
            ],
            options={
                'verbose_name': 'Resposta',
                'verbose_name_plural': 'Respostas',
            },
        ),
        migrations.CreateModel(
            name='Tarefa',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prioridade', models.SmallIntegerField(default=None, null=True, blank=True, choices=[(-1, 'Alerta'), (0, 'Urgente'), (1, 'Alta'), (2, 'Normal'), (3, 'Baixa')])),
                ('titulo', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('descricao', models.TextField(default=None, null=True, blank=True)),
                ('data_inicial', models.DateField(null=True, blank=True)),
                ('data_final', models.DateField(null=True, blank=True)),
                ('data_finalizado', models.DateTimeField(null=True, blank=True)),
                ('status', models.SmallIntegerField(default=0, null=True, blank=True, choices=[(0, 'Cadastrado'), (1, 'Pendente'), (2, 'Cumprido')])),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-ativo', '-atendimento__numero', 'titulo'],
            },
        ),
        migrations.CreateModel(
            name='Defensor',
            fields=[
                ('atendimento_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='atendimento.Atendimento', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('data_distribuido', models.DateTimeField(default=None, null=True, blank=True)),
                ('data_finalizado', models.DateTimeField(default=None, null=True, blank=True)),
            ],
            options={
                'ordering': ['-ativo', '-numero'],
                'verbose_name': 'Atendimento',
                'verbose_name_plural': 'Atendimentos',
            },
            bases=('atendimento.atendimento',),
        ),
        migrations.AddField(
            model_name='tarefa',
            name='atendimento',
            field=models.ForeignKey(default=None, blank=True, to='atendimento.Atendimento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='tarefa',
            name='documento',
            field=models.ForeignKey(default=None, blank=True, to='atendimento.Documento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
