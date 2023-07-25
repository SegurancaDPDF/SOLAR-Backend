# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contrib', '0045_defensoria_pode_cadastrar_peticionamento'),
        ('processo', '0033_processo_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='Manifestacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('enviado_em', models.DateTimeField(null=True, blank=True)),
                ('respondido_em', models.DateTimeField(null=True, blank=True)),
                ('protocolo_resposta', models.CharField(default=None, max_length=100, null=True, blank=True)),
                ('mensagem_resposta', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('codigo_procapi', models.CharField(default=None, max_length=100, null=True, help_text='C\xf3digo Identificador da Manifesta\xe7\xe3o no ProcAPI', blank=True)),
                ('codigo_sistema_procapi', models.CharField(default=None, max_length=100, null=True, help_text='C\xf3digo Identificador do Sistema Webservice no ProcAPI', blank=True)),
                ('tipo', models.SmallIntegerField(default=20, choices=[(10, 'Peti\xe7\xe3o Inicial'), (20, 'Peti\xe7\xe3o')])),
                ('situacao', models.SmallIntegerField(default=10, choices=[(10, 'Em An\xe1lise'), (20, 'Na Fila'), (30, 'Protocolado'), (90, 'Falha do protocolo')])),
                ('enviando', models.BooleanField(default=False, verbose_name='Enviando para ProcAPI')),
                ('enviado', models.BooleanField(default=False, verbose_name='Enviado para ProcAPI')),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='processo_manifestacao_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('defensor', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('defensoria', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='contrib.Defensoria', null=True)),
                ('desativado_por', models.ForeignKey(related_name='processo_manifestacao_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('enviado_por', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('manifestante', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='processo_manifestacao_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('parte', models.ForeignKey(to='processo.Parte', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'verbose_name': 'Manifesta\xe7\xe3o',
                'verbose_name_plural': 'Manifesta\xe7\xf5es',
            },
        ),
        migrations.CreateModel(
            name='ManifestacaoDocumento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('origem', models.SmallIntegerField(default=10, choices=[(10, 'Atendimento'), (20, 'Pessoa')])),
                ('origem_id', models.IntegerField()),
                ('tipo_mni', models.IntegerField(default=None, null=True, blank=True)),
                ('nivel_sigilo', models.SmallIntegerField(default=0, choices=[(0, 'P\xfablico'), (1, 'Segredo de Justi\xe7a'), (2, 'Sigilo m\xednimo'), (3, 'Sigilo m\xe9dio'), (4, 'Sigilo intenso'), (5, 'Sigilo absoluto')])),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='processo_manifestacaodocumento_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='processo_manifestacaodocumento_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('manifestacao', models.ForeignKey(related_name='documentos', to='processo.Manifestacao', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='processo_manifestacaodocumento_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Documento de Manifesta\xe7\xe3o',
                'verbose_name_plural': 'Documentos de Manifesta\xe7\xf5es',
            },
        ),
        migrations.CreateModel(
            name='Prioridade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=512)),
                ('codigo_mni', models.CharField(max_length=25)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='processo_prioridade_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='processo_prioridade_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='processo_prioridade_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Prioridade',
                'verbose_name_plural': 'Prioridades',
            },
        ),
        migrations.AlterModelOptions(
            name='processoassunto',
            options={'ordering': ['processo', '-principal', 'assunto']},
        ),
        migrations.AddField(
            model_name='processo',
            name='intervencao_mp',
            field=models.BooleanField(default=False, help_text='Interven\xe7\xe3o do Minist\xe9rio P\xfablico?', verbose_name='Interven\xe7\xe3o do Minist\xe9rio P\xfablico'),
        ),
        migrations.AddField(
            model_name='processo',
            name='nivel_sigilo',
            field=models.SmallIntegerField(default=0, choices=[(0, 'P\xfablico'), (1, 'Segredo de Justi\xe7a'), (2, 'Sigilo m\xednimo'), (3, 'Sigilo m\xe9dio'), (4, 'Sigilo intenso'), (5, 'Sigilo absoluto')]),
        ),
        migrations.AddField(
            model_name='processo',
            name='originario',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='processo.Processo', help_text='Processo Origin\xe1rio', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='processo',
            name='valor_causa',
            field=models.FloatField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='processoassunto',
            name='principal',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='processoassunto',
            unique_together=set([('processo', 'assunto')]),
        ),
        migrations.AddField(
            model_name='processo',
            name='prioridades',
            field=models.ManyToManyField(to='processo.Prioridade', blank=True),
        ),
    ]
