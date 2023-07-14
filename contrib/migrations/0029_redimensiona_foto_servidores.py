# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contrib.models


def migrate_data(apps, schema_editor):

    Servidor = apps.get_model("contrib", "Servidor")

    # Procura por servidores que possuem foto
    servidores = Servidor.objects.exclude(foto=None)

    # Atualiza cadastro (a foto é redimensionada ao salvar)
    for servidor in servidores:
        print(servidor.nome)
        servidor.save()

    print('Concluido!')


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0028_verbose_name_fields_salario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servidor',
            name='foto',
            field=models.ImageField(default=None, upload_to=contrib.models.servidor_photo_name, null=True, verbose_name='Foto', blank=True),
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
    ]

