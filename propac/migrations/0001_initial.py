# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import propac.models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0026_qualificacao_titulo_norm'),
        ('contrib', '0008_auto_20161018_1500'),
        ('defensor', '0006_defensorassessor_defensorsupervisor'),
        ('djdocuments', '0003_unaccent_pg_extension'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentoPropac',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(default='', max_length=255, blank=True)),
                ('anexo', models.FileField(null=True, upload_to=propac.models.documento_file_name, blank=True)),
                ('anexo_original_nome_arquivo', models.CharField(default='', max_length=128, blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('data_remocao', models.DateTimeField(null=True, verbose_name='Data de Remocao', blank=True)),
                ('motivo_remocao', models.CharField(default=None, max_length=256, null=True, verbose_name='Motivo remo\xe7\xe3o(256 letras)', blank=True)),
                ('data_exclusao', models.DateTimeField(verbose_name='Data de Exclus\xe3o', null=True, editable=False)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('documento', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='djdocuments.Documento', null=True)),
                ('excluido_por', models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
        ),
        migrations.CreateModel(
            name='Movimento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('eh_precadastro', models.BooleanField(default=True, verbose_name='\xc9 precadastro', editable=False)),
                ('data_movimento', models.DateTimeField(null=True, verbose_name='Data de Movimento')),
                ('volume', models.SmallIntegerField()),
                ('ordem_volume', models.SmallIntegerField()),
                ('ativo', models.BooleanField(default=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('data_remocao', models.DateTimeField(null=True, verbose_name='Data de Remocao', blank=True)),
                ('motivo_remocao', models.CharField(default=None, max_length=256, null=True, verbose_name='Motivo remo\xe7\xe3o(256 letras)', blank=True)),
                ('data_exclusao', models.DateTimeField(verbose_name='Data de Exclus\xe3o', null=True, editable=False)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('excluido_por', models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['-data_cadastro'],
                'verbose_name': 'Movimento',
                'verbose_name_plural': 'Movimentos',
            },
        ),
        migrations.CreateModel(
            name='MovimentoTipo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(default=None, max_length=128, blank=True)),
                ('codigo', models.SlugField(default=None, unique=True, max_length=128, blank=True)),
                ('instauracao', models.BooleanField(default=False, verbose_name='Instauracao')),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Tipo de Movimento',
                'verbose_name_plural': 'Tipos de Movimentos',
            },
        ),
        migrations.CreateModel(
            name='Procedimento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('defensor_responsavel_nome', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('defensoria_responsavel_nome', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('representante', models.CharField(default=None, max_length=1024, null=True, blank=True)),
                ('representado', models.CharField(default=None, max_length=1024, null=True, blank=True)),
                ('acesso', models.SmallIntegerField(default=30, choices=[(10, 'Acesso P\xfablico'), (20, 'Acesso Restrito'), (30, 'Acesso Privado')])),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)),
                ('numero', models.CharField(null=True, max_length=50, blank=True, unique=True, verbose_name='N\xfamero', db_index=True)),
                ('assunto', models.CharField(default=None, max_length=256, blank=True, null=True, verbose_name='Objeto', db_index=True)),
                ('tipo', models.SmallIntegerField(default=10, choices=[(10, 'Procedimento Preparatorio'), (20, 'Propac')])),
                ('situacao', models.SmallIntegerField(default=10, choices=[(10, 'Movimento'), (20, 'Encerrado'), (30, 'Arquivado'), (40, 'Desarquivado')])),
                ('data_ultima_movimentacao', models.DateTimeField(null=True, verbose_name='Data da Ultima Movimenta\xe7\xe3o', blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('atendimentos', models.ManyToManyField(related_name='procedimentos', to='atendimento.Atendimento', blank=True)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('defensor_responsavel', models.ForeignKey(related_name='procedimentos', default=None, blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('defensoria_responsavel', models.ForeignKey(related_name='procedimentos', default=None, blank=True, to='contrib.Defensoria', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('defensorias_acesso', models.ManyToManyField(related_name='procedimentos_vinculados', to='contrib.Defensoria', blank=True)),
            ],
            options={
                'ordering': ['-data_ultima_movimentacao'],
                'verbose_name': ' Procedimento e Propac',
                'verbose_name_plural': ' Procedimentos e Propacs',
            },
        ),
        migrations.CreateModel(
            name='SituacaoProcedimento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('situacao', models.SmallIntegerField(default=10, choices=[(10, 'Movimento'), (20, 'Encerrado'), (30, 'Arquivado'), (40, 'Desarquivado')])),
                ('motivo', models.CharField(default=None, max_length=256, null=True, verbose_name='Motivo remo\xe7\xe3o(256 letras)', blank=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('ativo', models.BooleanField(default=True)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('procedimento', models.ForeignKey(related_name='situacoes', default=None, to='propac.Procedimento', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['-pk'],
                'verbose_name': 'Situa\xe7\xe3o do procedimento',
                'verbose_name_plural': 'Situa\xe7\xf5es dos procedimentos',
            },
        ),
        migrations.CreateModel(
            name='TipoAnexoDocumentoPropac',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=255, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='movimento',
            name='procedimento',
            field=models.ForeignKey(related_name='movimentos', default=None, blank=True, to='propac.Procedimento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='movimento',
            name='removido_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='movimento',
            name='tipo',
            field=models.ForeignKey(related_name='+', default=None, to='propac.MovimentoTipo', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='documentopropac',
            name='movimento',
            field=models.ForeignKey(related_name='documentos', to='propac.Movimento', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='documentopropac',
            name='removido_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='documentopropac',
            name='tipo_anexo',
            field=models.ForeignKey(related_name='documentos', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='propac.TipoAnexoDocumentoPropac', null=True),
        ),
    ]
