# Generated by Django 3.2 on 2022-11-09 07:49

from django.db import migrations, models

def migrate_data(apps, schema_editor):

    Prioridade = apps.get_model("processo", "Prioridade")

    Prioridade.objects.exclude(
        cadastrado_por=None
    ).update(
        disponivel_para_peticionamento=True
    )

def reverse_migrate_data(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0052_manifestacaoparte'),
    ]

    operations = [
        migrations.AddField(
            model_name='prioridade',
            name='disponivel_para_peticionamento',
            field=models.BooleanField(default=False, verbose_name='Disponível para peticionamento?'),
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
    ]
