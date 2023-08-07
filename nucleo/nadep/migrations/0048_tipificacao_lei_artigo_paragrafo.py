# Generated by Django 3.2 on 2022-08-08 10:29

import cuser.fields
import django.db.models.deletion
from datetime import datetime
from django.conf import settings
from django.db import migrations, models

def migrate_data(apps, schema_editor):

    Tipificacao = apps.get_model("nadep", "Tipificacao")
    User = apps.get_model("auth", "User")

    agora = datetime.now()
    usuario = User.objects.filter(is_superuser=True, is_active=True, is_staff=True).order_by('date_joined').first()

    Tipificacao.objects.filter(
        ativo=False,
        desativado_em__isnull=True
    ).update(
        desativado_por=usuario,
        desativado_em=agora
    )

def reverse_migrate_data(apps, schema_editor):

    Tipificacao = apps.get_model("nadep", "Tipificacao")

    Tipificacao.objects.filter(
        desativado_em__isnull=False
    ).update(
        ativo=False
    )

class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0047_estabelecimento_tipo_email_sexo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tipificacao',
            old_name='data_cadastro',
            new_name='cadastrado_em',
        ),
        migrations.AlterField(
            model_name='tipificacao',
            name='cadastrado_em',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='tipificacao',
            name='nome',
            field=models.TextField(),
        ),
        migrations.AddField(
            model_name='tipificacao',
            name='cadastrado_por',
            field=cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nadep_tipificacao_cadastrado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tipificacao',
            name='desativado_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tipificacao',
            name='desativado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nadep_tipificacao_desativado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tipificacao',
            name='modificado_em',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='tipificacao',
            name='modificado_por',
            field=cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nadep_tipificacao_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tipificacao',
            name='artigo_lei',
            field=models.CharField(blank=True, max_length=25, null=True, verbose_name='Artigo da Lei'),
        ),
        migrations.AddField(
            model_name='tipificacao',
            name='numero_lei',
            field=models.CharField(blank=True, max_length=25, null=True, verbose_name='Número da Lei'),
        ),
        migrations.AddField(
            model_name='tipificacao',
            name='paragrafo_lei',
            field=models.CharField(blank=True, max_length=25, null=True, verbose_name='Parágrafo da Lei'),
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
        migrations.RemoveField(
            model_name='tipificacao',
            name='ativo',
        ),
        migrations.AlterModelOptions(
            name='tipificacao',
            options={'ordering': ['-desativado_em', 'nome'], 'verbose_name': 'Tipificação', 'verbose_name_plural': 'Tipificações'},
        ),
    ]