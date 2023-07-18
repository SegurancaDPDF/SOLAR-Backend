# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields

# Classe de migração do Django, usado para criar dois modelos no banco de dados com seus próprios campos e opções de configuração.
# As operações definidas na migração são responsáveis por criar os modelos "Competencia" e "SistemaWebService"  no banco de dados.

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contrib', '0047_defensoria_vara'),
        ('procapi_client', '0004_historicoconsultaprocesso'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competencia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=512, verbose_name='Nome', blank=True)),
                ('principal', models.BooleanField(default=False, verbose_name='Principal')),
                ('codigo_mni', models.PositiveSmallIntegerField(verbose_name='C\xf3digo MNI')),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='\xc1rea da Compet\xeancia', to='contrib.Area')),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='procapi_client_competencia_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='procapi_client_competencia_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='procapi_client_competencia_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['area__nome', 'sistema_webservice__nome', '-principal', 'nome'],
                'verbose_name': 'Compet\xeancia ProcAPI',
                'verbose_name_plural': 'Compet\xeancias ProcAPI',
            },
        ),
        migrations.CreateModel(
            name='SistemaWebService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=512, verbose_name='Nome', blank=True)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='procapi_client_sistemawebservice_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='procapi_client_sistemawebservice_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='procapi_client_sistemawebservice_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Sistema Web Service',
                'verbose_name_plural': 'Sistemas Web Service',
            },
        ),
        migrations.AddField(
            model_name='competencia',
            name='sistema_webservice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Sistema Web Service', to='procapi_client.SistemaWebService'),
        ),
        migrations.AlterUniqueTogether(
            name='competencia',
            unique_together=set([('codigo_mni', 'sistema_webservice')]),
        ),
    ]
