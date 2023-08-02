# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

# Solar
from contrib import constantes


def migrate_data(apps, schema_editor):

    Pessoa = apps.get_model("assistido", "Pessoa")
    PerfilCamposObrigatorios = apps.get_model("assistido", "PerfilCamposObrigatorios")

    Pessoa.objects.filter(
        tipo=None
    ).update(
        tipo=constantes.TIPO_PESSOA_FISICA
    )

    PerfilCamposObrigatorios.objects.filter(
        tipo_pessoa=None
    ).update(
        tipo_pessoa=constantes.TIPO_PESSOA_FISICA
    )


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0023_add_perm_assistido_unificar_pessoa'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
        migrations.AlterField(
            model_name='pessoa',
            name='tipo',
            field=models.SmallIntegerField(default=0, verbose_name='Tipo', choices=[(0, 'Pessoa F\xedsica'), (1, 'Pessoa Jur\xeddica')]),
        ),
        migrations.AlterField(
            model_name='perfilcamposobrigatorios',
            name='tipo_pessoa',
            field=models.SmallIntegerField(default=0, verbose_name='Tipo de Pessoa', choices=[(0, 'Pessoa F\xedsica'), (1, 'Pessoa Jur\xeddica')]),
        ),
    ]
