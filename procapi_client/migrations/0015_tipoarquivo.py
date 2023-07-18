# Generated by Django 3.2 on 2022-08-26 09:39
# Importações necessárias

import cuser.fields
from constance import config
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from redis import ConnectionError

# Função para migrar dados durante a migração do banco de dados.

def migrate_data(apps, schema_editor):

    SistemaWebService = apps.get_model("procapi_client", "SistemaWebService")
    TipoArquivo = apps.get_model("procapi_client", "TipoArquivo")

    try:
        for extensao in config.FORMATO_SUPORTADO_UPLOADS.split(','):
            for sistema in SistemaWebService.objects.filter(desativado_em=None):
                TipoArquivo.objects.create(
                    sistema_webservice=sistema,
                    extensao=extensao.replace('.', '').lower(),
                    tamanho_maximo=10
                )
    except ConnectionError:
        pass
# Função para reverter a migração de dados.

def reverse_migrate_data(apps, schema_editor):
    TipoArquivo = apps.get_model("procapi_client", "TipoArquivo")
    extensoes = TipoArquivo.objects.filter(desativado_em=None).order_by('extensao').distinct().values_list('extensao', flat=True)

    if len(extensoes) > 0:
        try:
            config.FORMATO_SUPORTADO_UPLOADS = '.' + ',.'.join(extensoes)
        except ConnectionError:
            pass
#  Classe responsável pela migração de banco de dados.

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('procapi_client', '0014_alter_tipoevento_codigo_mni'),
    ]
    # cria a classe de modelo "TipoArquivo"
    operations = [
        migrations.CreateModel(
            name='TipoArquivo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(blank=True, null=True)),
                ('extensao', models.CharField(help_text='Ex: PDF, JPG, MP3', max_length=10, verbose_name='Extensão')),
                ('tamanho_maximo', models.IntegerField(help_text='Em Megabytes (MB)', verbose_name='Tamanho máximo (MB)')),
                ('cadastrado_por', cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='procapi_client_tipoarquivo_cadastrado_por', to=settings.AUTH_USER_MODEL)),
                ('desativado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='procapi_client_tipoarquivo_desativado_por', to=settings.AUTH_USER_MODEL)),
                ('modificado_por', cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='procapi_client_tipoarquivo_modificado_por', to=settings.AUTH_USER_MODEL)),
                ('sistema_webservice', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='procapi_client.sistemawebservice', verbose_name='Sistema Web Service')),
            ],
            options={
                'verbose_name': 'Tipo de Arquivo ProcAPI',
                'verbose_name_plural': 'Tipos de Arquivo ProcAPI',
                'ordering': ['extensao', 'sistema_webservice__nome'],
                'unique_together': {('sistema_webservice', 'extensao')},
            },
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
        )
    ]
