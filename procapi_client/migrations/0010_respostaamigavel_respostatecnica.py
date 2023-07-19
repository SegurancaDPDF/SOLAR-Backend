# Generated by Django 3.2 on 2021-07-29 20:41
# Importações necessárias

import cuser.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

# Classe de migração do Django, usado para criar dois modelos "RespostaAmigavel" e "RespostaTecnica" no banco de dados.


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('procapi_client', '0009_alter_competencia_principal'),
    ]

    operations = [
        migrations.CreateModel(
            name='RespostaAmigavel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(blank=True, null=True)),
                ('descricao', models.CharField(blank=True, max_length=512, unique=True, verbose_name='Descrição')),
                ('cadastrado_por', cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='procapi_client_respostaamigavel_cadastrado_por', to=settings.AUTH_USER_MODEL)),
                ('desativado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='procapi_client_respostaamigavel_desativado_por', to=settings.AUTH_USER_MODEL)),
                ('modificado_por', cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='procapi_client_respostaamigavel_modificado_por', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Resposta Amigável',
                'verbose_name_plural': 'Respostas Amigáveis',
                'ordering': ['descricao'],
            },
        ),
        migrations.CreateModel(
            name='RespostaTecnica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(blank=True, null=True)),
                ('descricao', models.CharField(blank=True, max_length=512, verbose_name='Descrição')),
                ('regex', models.CharField(blank=True, max_length=512, unique=True, verbose_name='Regex')),
                ('cadastrado_por', cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='procapi_client_respostatecnica_cadastrado_por', to=settings.AUTH_USER_MODEL)),
                ('desativado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='procapi_client_respostatecnica_desativado_por', to=settings.AUTH_USER_MODEL)),
                ('modificado_por', cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='procapi_client_respostatecnica_modificado_por', to=settings.AUTH_USER_MODEL)),
                ('resposta_amigavel', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='procapi_client.respostaamigavel', verbose_name='Resposta Amigável')),
                ('sistema_webservices', models.ManyToManyField(db_table='procapi_client_respostatecnica_sistemawebservice', related_name='respostas_tecnicas', to='procapi_client.SistemaWebService')),
            ],
            options={
                'verbose_name': 'Resposta Técnica',
                'verbose_name_plural': 'Respostas Técnicas',
                'ordering': ['descricao'],
            },
        ),
    ]