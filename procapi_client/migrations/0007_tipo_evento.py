# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields

# Classe de migração cria um novo modelo chamado "TipoEvento" no banco de dados, que possui vários campos e relacionamentos com outros modelos.
# A migração altera a restrição de unicidade do modelo "TipoEvento".

class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0042_manifestacao_fase_perm_view_distribuicao'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('procapi_client', '0006_area_da_competencia_opcional'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoEvento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=512, verbose_name='Nome')),
                ('nome_norm', models.CharField(max_length=512, verbose_name='Nome (Normalizado)')),
                ('disponivel_em_peticao_avulsa', models.BooleanField(default=False, verbose_name='Dispon\xedvel em Peti\xe7\xe3o Avulsa?')),
                ('disponivel_em_peticao_com_aviso', models.BooleanField(default=False, verbose_name='Dispon\xedvel em Peti\xe7\xe3o com Aviso?')),
                ('codigo_mni', models.IntegerField(verbose_name='C\xf3digo MNI')),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='procapi_client_tipoevento_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='procapi_client_tipoevento_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='procapi_client_tipoevento_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('sistema_webservice', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Sistema Web Service', to='procapi_client.SistemaWebService')),
                ('tipos_de_fase', models.ManyToManyField(related_name='tipos_de_evento', db_table='procapi_client_tipoevento_fasestipo', to='processo.FaseTipo')),
            ],
            options={
                'ordering': ['sistema_webservice__nome', 'nome'],
                'verbose_name': 'Tipo de Evento ProcAPI',
                'verbose_name_plural': 'Tipos de Evento ProcAPI',
            },
        ),
        migrations.AlterUniqueTogether(
            name='tipoevento',
            unique_together=set([('codigo_mni', 'sistema_webservice')]),
        ),
    ]
