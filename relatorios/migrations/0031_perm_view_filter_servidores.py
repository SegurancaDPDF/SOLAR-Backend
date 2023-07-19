# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.contrib.auth.models import Permission

def migrate_data(apps, schema_editor):

    perm_relatorios = Permission.objects.filter(codename='view_relatorios', content_type__model='relatorios').first()
    perm_filtro = Permission.objects.filter(codename='view_filter_servidores', content_type__model='relatorios').first()

    # Adiciona nova permissão para todos grupos de permissão (mantém compatibilidade)
    print(u'\nAdicionando permissão...')

    if perm_relatorios and perm_filtro:
        for grupo in perm_relatorios.group_set.all():
            print(u'Adicionando permissão ao grupo {}'.format(grupo))
            grupo.permissions.add(perm_filtro)

def reverse_migrate_data(apps, schema_editor):

    perm_filtro = Permission.objects.filter(codename='view_filter_servidores', content_type__model='relatorios').first()

    # Remove nova permissão de todos grupos de permissão (mantém compatibilidade)
    print(u'\nRemovendo permissão...')

    if perm_filtro:
        for grupo in perm_filtro.group_set.all():
            print(u'Removendo permissão do grupo {}'.format(grupo))
            grupo.permissions.remove(perm_filtro)


class Migration(migrations.Migration):

    dependencies = [
        ('relatorios', '0030_add_local_e_relatorio'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='relatorios',
            options={'permissions': (('view_filter_defensores', 'Can view filtro defensores'), ('view_filter_servidores', 'Can view filtro servidores'))},
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
    ]
