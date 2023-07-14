# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
import re
from bulk_update.helper import bulk_update
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields


def migrate_data(apps, schema_editor):

    Bairro = apps.get_model("contrib", "Bairro")
    Endereco = apps.get_model("contrib", "Endereco")

    # Normaliza nome dos bairros cadastrados

    bairros = Bairro.objects.exclude(nome=None)

    for bairro in bairros:
        bairro.nome = re.sub(' +', ' ', bairro.nome.strip().upper())

    if len(bairros):
        bulk_update(bairros, update_fields=['nome'], batch_size=1000)

    # recupera lista de todos os bairros duplicados
    bairros = Bairro.objects.values(
        'municipio_id',
        'nome',
    ).order_by(
        'municipio_id',
        'nome'
    ).annotate(
        total=models.Count('nome')
    ).filter(
        desativado_em=None,
        total__gte=2
    )

    agora = datetime.now()

    for bairro in bairros:
        # recupera todos os bairros com mesmo nome e municipio
        lst = Bairro.objects.filter(municipio_id=bairro['municipio_id'], nome=bairro['nome'], desativado_em=None).order_by('id')
        # recupera o primeiro registro
        primeiro = lst[0]
        # desativa todos os bairros duplicados
        outros = lst.exclude(id=primeiro.id)
        outros.update(desativado_em=agora)
        # vincula enderecos dos bairros desativados ao bairro ativo
        enderecos = Endereco.objects.filter(bairro__in=outros).update(bairro=primeiro)
        # imprime resultado
        print(bairro, enderecos)

    print('\nConcluido!')


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0025_add_auditoria_bairro'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
    ]
