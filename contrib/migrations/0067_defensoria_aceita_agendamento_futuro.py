# Generated by Django 3.2 on 2022-05-24 16:09

from django.db import migrations, models


def migrate_data(apps, schema_editor):

    Defensoria = apps.get_model("contrib", "Defensoria")

    total = Defensoria.objects.filter(
        nucleo__multidisciplinar=True
    ).update(
        aceita_agendamento_futuro=False
    )

    print('{} registros alterados!'.format(total))


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0066_defensoriavara_regex'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoria',
            name='aceita_agendamento_futuro',
            field=models.BooleanField(default=True, verbose_name='Aceita agendamento futuro?'),
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
        ),
    ]