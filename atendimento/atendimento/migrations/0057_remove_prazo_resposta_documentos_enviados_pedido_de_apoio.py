# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_data(apps, schema_editor):

    # Atendimento = apps.get_model("atendimento", "Atendimento")
    Documento = apps.get_model("atendimento", "Documento")

    total = Documento.objects.filter(
        atendimento__filhos__tipo=4  # Atendimento.TIPO_NUCLEO
    ).exclude(
        prazo_resposta=None
    ).update(
        prazo_resposta=None,
        status_resposta=0  # Documento.STATUS_RESPOSTA_PENDENTE
    )


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0056_vw_atendimento_dia'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
    ]
