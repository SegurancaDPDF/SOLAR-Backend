# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bulk_update.helper import bulk_update
from django.db import migrations, models
from django.db.models.functions import Length

from contrib.models import Util


def migrate_data(apps, schema_editor):

    Endereco = apps.get_model("contrib", "Endereco")

    enderecos = Endereco.objects.annotate(cep_len=Length('cep')).filter(cep_len__gt=8)

    print('\nCorrigindo endereços com cep mascarado/inválido...')

    for endereco in enderecos:
        endereco.cep = Util.so_numeros(endereco.cep)[:8]

    print('Registrando alteracao no banco de dados...')

    if len(enderecos):
        bulk_update(enderecos, update_fields=['cep'], batch_size=1000)

    print('Concluido!')


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0062_defensoria_aceita_agendamento_choices'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
        ),
        migrations.AlterField(
            model_name='endereco',
            name='cep',
            field=models.CharField(blank=True, default=None, max_length=10, null=True, verbose_name='CEP'),
        ),
    ]
