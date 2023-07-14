# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nucleo', '0001_initial'),
        ('comarca', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=200)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': '\xc1rea',
                'verbose_name_plural': '\xc1reas',
            },
        ),
        migrations.CreateModel(
            name='Atualizacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.SmallIntegerField(choices=[(0, 'Implementa\xe7\xe3o'), (1, 'Atualiza\xe7\xe3o'), (2, 'Corre\xe7\xe3o')])),
                ('data', models.DateTimeField()),
                ('texto', models.CharField(max_length=512)),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
            ],
            options={
                'ordering': ['-ativo', '-data'],
                'verbose_name': 'Atualiza\xe7\xe3o',
                'verbose_name_plural': 'Atualiza\xe7\xf5es',
            },
        ),
        migrations.CreateModel(
            name='Bairro',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=128)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Bairro',
                'verbose_name_plural': 'Bairros',
            },
        ),
        migrations.CreateModel(
            name='CEP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('logradouro', models.CharField(max_length=256, null=True, blank=True)),
                ('cep', models.CharField(max_length=8)),
                ('bairro', models.ForeignKey(blank=True, to='contrib.Bairro', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ('cep',),
                'verbose_name': 'CEP',
                'verbose_name_plural': 'CEPs',
            },
        ),
        migrations.CreateModel(
            name='Comarca',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Data da \xfaltima atualiza\xe7\xe3o', null=True)),
                ('nome', models.CharField(max_length=512)),
                ('codigo', models.CharField(default=None, max_length=25, null=True, verbose_name='C\xf3d. Athenas', blank=True)),
                ('codigo_eproc', models.CharField(default=None, max_length=25, null=True, verbose_name='C\xf3d. E-Proc', blank=True)),
                ('ativo', models.BooleanField(default=False, verbose_name='Ativo')),
                ('coordenadoria', models.ForeignKey(blank=True, to='contrib.Comarca', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['-ativo', 'nome'],
                'verbose_name': 'Comarca',
                'verbose_name_plural': 'Comarcas',
            },
        ),
        migrations.CreateModel(
            name='Defensoria',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=255)),
                ('numero', models.SmallIntegerField(default=0)),
                ('atuacao', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('areas', models.ManyToManyField(to='contrib.Area', blank=True)),
                ('comarca', models.ForeignKey(to='contrib.Comarca', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['comarca__nome', 'numero'],
                'verbose_name': 'Defensoria',
                'verbose_name_plural': 'Defensorias',
            },
        ),
        migrations.CreateModel(
            name='Deficiencia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=512)),
                ('ativo', models.BooleanField(default=False, verbose_name='Ativo')),
            ],
            options={
                'verbose_name': 'Defici\xeancia',
                'verbose_name_plural': 'Defici\xeancias',
            },
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=256)),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Documento',
                'verbose_name_plural': 'Documentos',
            },
        ),
        migrations.CreateModel(
            name='Endereco',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('logradouro', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('numero', models.CharField(default=None, max_length=32, null=True, verbose_name='N\xfamero', blank=True)),
                ('complemento', models.CharField(default=None, max_length=512, null=True, verbose_name='Complemento', blank=True)),
                ('cep', models.CharField(default=None, max_length=32, null=True, verbose_name='CEP', blank=True)),
                ('tipo_area', models.SmallIntegerField(default=0, null=True, blank=True, choices=[(0, 'Urbana'), (1, 'Rural')])),
                ('bairro', models.ForeignKey(default=None, blank=True, to='contrib.Bairro', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['logradouro'],
                'verbose_name': 'Endere\xe7o',
                'verbose_name_plural': 'Endere\xe7os',
            },
        ),
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=32)),
                ('uf', models.CharField(max_length=2)),
            ],
            options={
                'ordering': ['uf'],
                'verbose_name': 'Estado',
                'verbose_name_plural': 'Estados',
            },
        ),
        migrations.CreateModel(
            name='Municipio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=128)),
                ('comarca', models.ForeignKey(blank=True, to='contrib.Comarca', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('estado', models.ForeignKey(to='contrib.Estado', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Munic\xedpio',
                'verbose_name_plural': 'Munic\xedpios',
            },
        ),
        migrations.CreateModel(
            name='Pais',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('iso', models.CharField(max_length=2)),
                ('iso3', models.CharField(max_length=3)),
                ('numero', models.CharField(default=None, max_length=3, null=True, blank=True)),
                ('nome', models.CharField(max_length=128)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Pa\xeds',
                'verbose_name_plural': 'Pa\xedses',
            },
        ),
        migrations.CreateModel(
            name='Salario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vigencia', models.DateField()),
                ('valor', models.DecimalField(max_digits=16, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='Servidor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('cpf', models.CharField(max_length=32)),
                ('data_nascimento', models.DateField(default=None, null=True, blank=True)),
                ('sexo', models.SmallIntegerField(default=None, null=True, blank=True, choices=[(0, 'Masculino'), (1, 'Feminino')])),
                ('matricula', models.CharField(default=None, max_length=32, null=True, blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('foto', models.ImageField(default=None, upload_to='servidor', null=True, verbose_name='Foto', blank=True)),
                ('data_atualizacao', models.DateTimeField(default=None, null=True, blank=True)),
                ('comarca', models.ForeignKey(to='contrib.Comarca', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['usuario__first_name', 'usuario__last_name'],
                'verbose_name': 'Servidor',
                'verbose_name_plural': 'Servidores',
            },
        ),
        migrations.CreateModel(
            name='Telefone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ddd', models.SmallIntegerField(null=True, blank=True)),
                ('numero', models.CharField(max_length=10, verbose_name='N\xfamero')),
                ('tipo', models.SmallIntegerField(choices=[(0, 'Celular'), (1, 'Residencial'), (2, 'Comercial'), (3, 'Recado')])),
            ],
            options={
                'verbose_name': 'Telefone',
                'verbose_name_plural': 'Telefones',
            },
        ),
        migrations.CreateModel(
            name='Vara',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_cadastro', models.DateField(default=None, null=True, verbose_name='Data de Cadastro')),
                ('data_atualizacao', models.DateField(default=None, null=True, verbose_name='Data da \xfaltima atualiza\xe7\xe3o')),
                ('nome', models.CharField(max_length=512)),
                ('codigo_eproc', models.CharField(default=None, max_length=25, null=True, blank=True)),
                ('ativo', models.BooleanField(default=False, verbose_name='Ativo')),
                ('comarca', models.ForeignKey(to='contrib.Comarca', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['-ativo', 'nome'],
                'verbose_name': 'Vara',
                'verbose_name_plural': 'Varas',
            },
        ),
        migrations.AddField(
            model_name='servidor',
            name='telefones',
            field=models.ManyToManyField(default=None, to='contrib.Telefone', blank=True),
        ),
        migrations.AddField(
            model_name='servidor',
            name='usuario',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='endereco',
            name='municipio',
            field=models.ForeignKey(to='contrib.Municipio', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='defensoria',
            name='endereco',
            field=models.ForeignKey(blank=True, to='contrib.Endereco', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='defensoria',
            name='nucleo',
            field=models.ForeignKey(blank=True, to='nucleo.Nucleo', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='defensoria',
            name='predio',
            field=models.ForeignKey(blank=True, to='comarca.Predio', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='cep',
            name='municipio',
            field=models.ForeignKey(blank=True, to='contrib.Municipio', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='bairro',
            name='municipio',
            field=models.ForeignKey(blank=True, to='contrib.Municipio', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
