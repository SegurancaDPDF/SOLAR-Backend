# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.models
import django.db.models.deletion
from django.conf import settings
import cuser.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0013_fix_pronto_para_assinar'),
        ('contrib', '0017_auto_20180509_0844'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assistido', '0016_pessoa_tipo_cadastro'),
    ]

    operations = [
        migrations.CreateModel(
            name='Apenso',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('tipo', models.PositiveSmallIntegerField(default=None, null=True, blank=True, choices=[(10, 'Dependente'), (20, 'Apensado')])),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='core_apenso_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='core_apenso_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='core_apenso_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Classe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('tipo', models.PositiveSmallIntegerField(default=8, choices=[(8, 'Pedido'), (6030, 'Impedimento'), (6040, 'Suspei\xe7\xe3o'), (6050, 'Nega\xe7\xe3o'), (6051, 'Nega\xe7\xe3o por Hipossufici\xeancia')])),
                ('tipo_processo', models.PositiveSmallIntegerField(default=None, null=True, blank=True, choices=[(10, 'Atendimento'), (20, 'Apoio'), (30, 'Tarefa'), (40, 'Processo'), (50, 'PROPAC'), (60, 'Indeferimento')])),
                ('nome', models.CharField(max_length=255)),
                ('nome_norm', models.CharField(max_length=255)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='core_classe_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='core_classe_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=255)),
                ('arquivo', models.FileField(null=True, upload_to=core.models.documento_file_name, blank=True)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='core_documento_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='core_documento_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('documento', models.ForeignKey(related_name='core_documentos', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='djdocuments.Documento', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Evento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('data_referencia', models.DateTimeField(blank=True)),
                ('numero', models.SmallIntegerField()),
                ('historico', models.TextField(default=None, null=True, blank=True)),
                ('em_edicao', models.BooleanField(default=False, verbose_name='Em edi\xe7\xe3o?', editable=False)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='core_evento_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='core_evento_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='core_evento_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ModeloDocumento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=255)),
                ('tipo', models.PositiveSmallIntegerField(default=0, choices=[(0, 'GED'), (1, 'Jasper')])),
                ('jasper_resource', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('jasper_name', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('jasper_params', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='core_modelodocumento_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='core_modelodocumento_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('ged_modelo', models.ForeignKey(related_name='core_modelo_documento', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Documento', blank=True, to='djdocuments.Documento', null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='core_modelodocumento_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Parte',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('tipo', models.PositiveSmallIntegerField(choices=[(10, 'Ativo'), (20, 'Passivo')])),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='core_parte_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='core_parte_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='core_parte_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('pessoa', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to='assistido.Pessoa')),
            ],
        ),
        migrations.CreateModel(
            name='Participante',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='core_participante_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='core_participante_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('evento', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to='core.Evento')),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='core_participante_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('papel', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to='contrib.Papel')),
                ('usuario', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Processo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)),
                ('numero', models.CharField(null=True, max_length=50, blank=True, unique=True, verbose_name='N\xfamero', db_index=True)),
                ('situacao', models.PositiveSmallIntegerField(default=10, choices=[(10, 'Peticionamento'), (20, 'Movimento'), (30, 'Baixado')])),
                ('tipo', models.PositiveSmallIntegerField(choices=[(10, 'Atendimento'), (20, 'Apoio'), (30, 'Tarefa'), (40, 'Processo'), (50, 'PROPAC'), (60, 'Indeferimento')])),
                ('baixado_em', models.DateTimeField(null=True, blank=True)),
                ('baixado_por', models.ForeignKey(related_name='core_processo_finalizado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='core_processo_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('classe', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Classe', null=True)),
                ('desativado_por', models.ForeignKey(related_name='core_processo_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='core_processo_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('setor_atual', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to='contrib.Defensoria')),
                ('setor_criacao', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to='contrib.Defensoria')),
                ('setor_encaminhado', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='contrib.Defensoria', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TipoDocumento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=255)),
                ('nome_norm', models.CharField(max_length=255)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='core_tipodocumento_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='core_tipodocumento_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='core_tipodocumento_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TipoEvento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('tipo', models.PositiveSmallIntegerField(default=8, choices=[(8, 'Peti\xe7\xe3o'), (9, 'Recurso'), (10, 'Encaminhamento'), (11, 'Recebimento'), (12, 'Decis\xe3o'), (13, 'Baixa')])),
                ('tipo_processo', models.PositiveSmallIntegerField(default=None, null=True, blank=True, choices=[(10, 'Atendimento'), (20, 'Apoio'), (30, 'Tarefa'), (40, 'Processo'), (50, 'PROPAC'), (60, 'Indeferimento')])),
                ('nome', models.CharField(max_length=255)),
                ('nome_norm', models.CharField(max_length=255)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='core_tipoevento_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='core_tipoevento_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='core_tipoevento_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='parte',
            name='processo',
            field=models.ForeignKey(related_name='partes', on_delete=django.db.models.deletion.DO_NOTHING, to='core.Processo'),
        ),
        migrations.AddField(
            model_name='modelodocumento',
            name='tipo_documento',
            field=models.ForeignKey(related_name='modelos', on_delete=django.db.models.deletion.DO_NOTHING, to='core.TipoDocumento'),
        ),
        migrations.AddField(
            model_name='evento',
            name='parte',
            field=models.ForeignKey(related_name='eventos', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Parte', null=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='participantes',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='core.Participante'),
        ),
        migrations.AddField(
            model_name='evento',
            name='processo',
            field=models.ForeignKey(related_name='eventos', on_delete=django.db.models.deletion.DO_NOTHING, to='core.Processo'),
        ),
        migrations.AddField(
            model_name='evento',
            name='setor_criacao',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to='contrib.Defensoria'),
        ),
        migrations.AddField(
            model_name='evento',
            name='setor_encaminhado',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='contrib.Defensoria', null=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='tipo',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to='core.TipoEvento'),
        ),
        migrations.AddField(
            model_name='documento',
            name='evento',
            field=models.ForeignKey(related_name='documentos', on_delete=django.db.models.deletion.DO_NOTHING, to='core.Evento'),
        ),
        migrations.AddField(
            model_name='documento',
            name='modelo',
            field=models.ForeignKey(related_name='documentos', blank=True, to='core.ModeloDocumento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='documento',
            name='modificado_por',
            field=cuser.fields.CurrentUserField(related_name='core_documento_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='documento',
            name='parte',
            field=models.ForeignKey(related_name='documentos', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Parte', null=True),
        ),
        migrations.AddField(
            model_name='documento',
            name='processo',
            field=models.ForeignKey(related_name='documentos', on_delete=django.db.models.deletion.DO_NOTHING, to='core.Processo'),
        ),
        migrations.AddField(
            model_name='documento',
            name='tipo',
            field=models.ForeignKey(related_name='documentos', on_delete=django.db.models.deletion.DO_NOTHING, to='core.TipoDocumento'),
        ),
        migrations.AddField(
            model_name='classe',
            name='modelos_documentos',
            field=models.ManyToManyField(related_name='classes', to='core.ModeloDocumento', blank=True),
        ),
        migrations.AddField(
            model_name='classe',
            name='modificado_por',
            field=cuser.fields.CurrentUserField(related_name='core_classe_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='apenso',
            name='processo_destino',
            field=models.ForeignKey(related_name='originarios', on_delete=django.db.models.deletion.DO_NOTHING, to='core.Processo'),
        ),
        migrations.AddField(
            model_name='apenso',
            name='processo_origem',
            field=models.ForeignKey(related_name='dependentes', on_delete=django.db.models.deletion.DO_NOTHING, to='core.Processo'),
        ),
        migrations.AlterUniqueTogether(
            name='parte',
            unique_together=set([('processo', 'pessoa')]),
        ),
        migrations.AlterUniqueTogether(
            name='evento',
            unique_together=set([('processo', 'numero')]),
        ),
        migrations.AlterUniqueTogether(
            name='apenso',
            unique_together=set([('processo_origem', 'processo_destino')]),
        ),
    ]
