# Generated by Django 3.2 on 2022-07-28 08:21

import cuser.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricoConsulta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(blank=True, null=True)),
                ('ip', models.CharField(blank=True, db_index=True, max_length=15, null=True, verbose_name='Endereço IP')),
                ('servico', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('parametros', models.JSONField(blank=True, null=True)),
                ('resposta', models.TextField(blank=True, default=None, null=True)),
                ('sucesso', models.BooleanField(default=False)),
                ('cadastrado_por', cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='livre_client_historicoconsulta_cadastrado_por', to=settings.AUTH_USER_MODEL)),
                ('desativado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='livre_client_historicoconsulta_desativado_por', to=settings.AUTH_USER_MODEL)),
                ('modificado_por', cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='livre_client_historicoconsulta_modificado_por', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Histórico de Consulta Livre API',
                'verbose_name_plural': 'Históricos de Consulta Livre API',
                'ordering': ['-cadastrado_em'],
            },
        ),
    ]
