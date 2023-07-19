# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import django.db.models.deletion
from django.conf import settings
import cuser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0042_identidadegenero'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('relatorios', '0029_perm_view_filter_defensores'),
    ]

    operations = [
        migrations.CreateModel(
            name='Local',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('pagina', models.CharField(max_length=255, choices=[('relatorio_listar', 'Relat\xf3rios - Listar'), ('agendamento_confirmar', 'Agendamento - Confirmar Agendamento'), ('assistido_cadastrar', 'Assistido - Cadastrar'), ('atendimento_atender', 'Atendimento - Atender'), ('atendimento_atender_btn_requerente', 'Atendimento - Atender - Bot\xe3o Requerente'), ('atendimento_atender_btn_requerido', 'Atendimento - Atender - Bot\xe3o Requerido'), ('atendimento_conflitos_corrigidos', 'Atendimento - Conflitos Corrigidos'), ('diligencia_index', 'Dilig\xeancia - Index'), ('itinerante_index', 'Itinerante - Index'), ('livre_detalhes_btn_calculo_horas', 'Livre - Detalhes - Bot\xe3o C\xe1lculo de Horas'), ('multidisciplinar_index', 'Multidisciplinar - Index'), ('precadastro_index', 'Precadastro (129) - Index'), ('recepcao_detalhes_btn_carta_convite', 'Recep\xe7\xe3o - Detalhes Atendimento - Bot\xe3o Carta Convite'), ('recepcao_detalhes_btn_requerente', 'Recep\xe7\xe3o - Detalhes Atendimento - Bot\xe3o Requerente'), ('recepcao_detalhes_btn_requerido', 'Recep\xe7\xe3o - Detalhes Atendimento - Bot\xe3o Requerido'), ('propac_detalhes', 'PROPAC - Detalhes')])),
                ('titulo', models.CharField(max_length=255)),
                ('parametros', jsonfield.fields.JSONField(default={})),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='relatorios_local_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='relatorios_local_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='relatorios_local_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['pagina', 'titulo'],
                'verbose_name': 'Local',
                'verbose_name_plural': 'Locais',
            },
        ),
        migrations.CreateModel(
            name='Relatorio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('titulo', models.CharField(max_length=255, verbose_name='T\xedtulo')),
                ('caminho', models.CharField(max_length=255, verbose_name='Caminho no JasperServer')),
                ('parametros', jsonfield.fields.JSONField(default={})),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='relatorios_relatorio_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='relatorios_relatorio_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('locais', models.ManyToManyField(related_name='relatorios', to='relatorios.Local')),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='relatorios_relatorio_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('papeis', models.ManyToManyField(related_name='relatorios', to='contrib.Papel')),
            ],
            options={
                'ordering': ['titulo'],
                'verbose_name': 'Relat\xf3rio',
                'verbose_name_plural': 'Relat\xf3rios',
            },
        ),
        migrations.AlterModelOptions(
            name='relatorios',
            options={'permissions': ('view_filter_defensores', 'Can view filtro defensores')},
        ),
        migrations.RunSQL(
            sql='ALTER SEQUENCE relatorios_local_id_seq RESTART WITH 101;',
            reverse_sql=''
        ),
        migrations.RunSQL(
            sql='ALTER SEQUENCE relatorios_relatorio_id_seq RESTART WITH 101;',
            reverse_sql=''
        ),
    ]
