# Generated by Django 3.2 on 2023-06-06 20:56

from django.conf import settings
from django.db import migrations
import django.db.models.deletion
import django_currentuser.db.models.fields
import django_currentuser.middleware


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contrib', '0080_generopessoa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bairro',
            name='cadastrado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrib_bairro_cadastrado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='bairro',
            name='modificado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, on_update=True, related_name='contrib_bairro_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cargo',
            name='cadastrado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrib_cargo_cadastrado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cargo',
            name='modificado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, on_update=True, related_name='contrib_cargo_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cartorio',
            name='cadastrado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrib_cartorio_cadastrado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cartorio',
            name='modificado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, on_update=True, related_name='contrib_cartorio_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cep',
            name='cadastrado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrib_cep_cadastrado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cep',
            name='modificado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, on_update=True, related_name='contrib_cep_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='defensoriaetiqueta',
            name='cadastrado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrib_defensoriaetiqueta_cadastrado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='defensoriaetiqueta',
            name='modificado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, on_update=True, related_name='contrib_defensoriaetiqueta_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='defensoriavara',
            name='cadastrado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrib_defensoriavara_cadastrado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='defensoriavara',
            name='modificado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, on_update=True, related_name='contrib_defensoriavara_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='endereco',
            name='cadastrado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrib_endereco_cadastrado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='endereco',
            name='modificado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, on_update=True, related_name='contrib_endereco_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='etiqueta',
            name='cadastrado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrib_etiqueta_cadastrado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='etiqueta',
            name='modificado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, on_update=True, related_name='contrib_etiqueta_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='generopessoa',
            name='cadastrado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrib_generopessoa_cadastrado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='generopessoa',
            name='modificado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, on_update=True, related_name='contrib_generopessoa_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='historicologin',
            name='cadastrado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrib_historicologin_cadastrado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='historicologin',
            name='modificado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, on_update=True, related_name='contrib_historicologin_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='identidadegenero',
            name='cadastrado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrib_identidadegenero_cadastrado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='identidadegenero',
            name='modificado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, on_update=True, related_name='contrib_identidadegenero_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='menuextra',
            name='cadastrado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrib_menuextra_cadastrado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='menuextra',
            name='modificado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, on_update=True, related_name='contrib_menuextra_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='orientacaosexual',
            name='cadastrado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrib_orientacaosexual_cadastrado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='orientacaosexual',
            name='modificado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, on_update=True, related_name='contrib_orientacaosexual_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
    ]