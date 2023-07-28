# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0040_manifestacao_tipo_evento'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('atendimento', '0094_add_documento_assinado'),
    ]

    operations = [
        migrations.CreateModel(
            name='QualificacaoAssunto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('principal', models.BooleanField(default=False, verbose_name='Principal')),
                ('assunto', models.ForeignKey(verbose_name='Assunto Processual', to='processo.Assunto', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='atendimento_qualificacaoassunto_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='atendimento_qualificacaoassunto_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='atendimento_qualificacaoassunto_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'db_table': 'atendimento_qualificacao_assunto',
                'ordering': ['qualificacao', '-principal', 'assunto'],
                'verbose_name': 'Assunto de Qualifica\xe7\xe3o',
                'verbose_name_plural': 'Assuntos das Qualifica\xe7\xf5es',
            },
        ),
        migrations.AddField(
            model_name='qualificacao',
            name='acao',
            field=models.ForeignKey(default=None, blank=True, to='processo.Acao', null=True, verbose_name='Processo A\xe7\xe3o', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='qualificacaoassunto',
            name='qualificacao',
            field=models.ForeignKey(verbose_name='Qualifica\xe7\xe3o', to='atendimento.Qualificacao', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='qualificacao',
            name='assuntos',
            field=models.ManyToManyField(to='processo.Assunto', through='atendimento.QualificacaoAssunto'),
        ),
        migrations.AlterUniqueTogether(
            name='qualificacaoassunto',
            unique_together=set([('assunto', 'qualificacao')]),
        ),
    ]
