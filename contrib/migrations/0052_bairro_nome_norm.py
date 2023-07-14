# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bulk_update.helper import bulk_update
from django.db import migrations, models

from contrib.models import Util


def migrate_data(apps, schema_editor):

    Bairro = apps.get_model("contrib", "Bairro")

    bairros = Bairro.objects.all()

    print('\nAplicando o nome normalizado nos Bairros...')

    for bairro in bairros:
        bairro.nome_norm = Util.normalize(bairro.nome)

    print('Registrando alteracao no banco de dados...')
    if len(bairros):
        bulk_update(bairros, update_fields=['nome_norm'], batch_size=1000)

    print('Concluido!')


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0051_distribuicao_por_polo_e_competencia'),
    ]

    operations = [
        migrations.AddField(
            model_name='bairro',
            name='nome_norm',
            field=models.CharField(default='', max_length=128, db_index=True),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='bairro',
            options={'ordering': ['municipio__nome', 'nome_norm', '-desativado_em'], 'verbose_name': 'Bairro', 'verbose_name_plural': 'Bairros'},
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
        )
    ]
