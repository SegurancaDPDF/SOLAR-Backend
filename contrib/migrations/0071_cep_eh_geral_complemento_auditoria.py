# Generated by Django 3.2 on 2022-09-27 10:50

import cuser.fields
from django.conf import settings
from django.db import migrations, models
from django.db.models import Count
import django.db.models.deletion

def migrate_data(apps, schema_editor):

    CEP = apps.get_model("contrib", "CEP")
    ceps_duplicados = CEP.objects.values('cep').annotate(total=Count('cep')).order_by('cep').filter(total__gt=1)
    total = 0

    print('\nRemovendo CEPs duplicados...')
    for cep in ceps_duplicados:
        print('Removendo CEP {} duplicado...'.format(cep['cep']))
        registros, _ = CEP.objects.filter(cep=cep['cep']).delete()
        total += registros

    print('{} registros duplicados foram removidos!'.format(total))


def reverse_migrate_data(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contrib', '0070_perm_view_all_defensorias'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
        ),
        migrations.AddField(
            model_name='cep',
            name='cadastrado_em',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='cep',
            name='cadastrado_por',
            field=cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrib_cep_cadastrado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cep',
            name='complemento',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='cep',
            name='desativado_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cep',
            name='desativado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrib_cep_desativado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cep',
            name='eh_geral',
            field=models.BooleanField(default=False, verbose_name='É o cep geral do município (ignorar validação)?'),
        ),
        migrations.AddField(
            model_name='cep',
            name='modificado_em',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='cep',
            name='modificado_por',
            field=cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrib_cep_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cep',
            name='cep',
            field=models.CharField(max_length=8, unique=True),
        ),
    ]
