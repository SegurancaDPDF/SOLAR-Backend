# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields

# Migração com o Django

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contrib', '0030_perm_view_all_comarcas'),
    ]

    operations = [
        migrations.CreateModel(
            name='Termo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('titulo', models.CharField(max_length=255, verbose_name='Titulo')),
                ('descricao', models.TextField(verbose_name='Descri\xe7\xe3o')),
                ('tipo_resposta', models.CharField(max_length=10, verbose_name='Tipo de Resposta', choices=[('un', '\xdanica'), ('mu', 'Multipla')])),
                ('data_inicio', models.DateField(null=True, verbose_name='Data de In\xedcio', blank=True)),
                ('data_finalizacao', models.DateField(null=True, verbose_name='Data de Finaliza\xe7\xe3o', blank=True)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='aceite_termo_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='aceite_termo_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='aceite_termo_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['cadastrado_em'],
                'verbose_name': 'Termo',
                'verbose_name_plural': 'Termos',
            },
        ),
        migrations.CreateModel(
            name='TermoResposta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('titulo_termo', models.CharField(verbose_name='Titulo', max_length=255, editable=False)),
                ('descricao_termo', models.TextField(verbose_name='Descri\xe7\xe3o', editable=False)),
                ('aceite', models.BooleanField()),
                ('data_resposta', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='aceite_termoresposta_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='aceite_termoresposta_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='aceite_termoresposta_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('servidor', models.ForeignKey(to='contrib.Servidor', on_delete=django.db.models.deletion.PROTECT)),
                ('termo', models.ForeignKey(to='aceite.Termo', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'ordering': ['data_resposta'],
                'verbose_name': 'Resposta de Termo',
                'verbose_name_plural': 'Respostas dos Termos',
            },
        ),
        migrations.AddField(
            model_name='termo',
            name='servidores',
            field=models.ManyToManyField(to='contrib.Servidor', through='aceite.TermoResposta'),
        ),
    ]
