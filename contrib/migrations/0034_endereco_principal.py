# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from bulk_update.helper import bulk_update
from django.conf import settings


def do_define_endereco_principal(apps, schema_editor):
    Endereco = apps.get_model("contrib", "Endereco")

    total = 0

    while Endereco.objects.filter(desativado_em=None, principal=False).exists():

        enderecos = Endereco.objects.filter(
            desativado_em=None,
            principal=False
        ).order_by()[:1000]

        for a in enderecos:
            a.principal = True

        bulk_update(enderecos, update_fields=['principal'], batch_size=1000)

        total += enderecos.count()
        print("Em progresso: {}".format(total))

    print ('\nMigração finalizada. {} registros afetados!'.format(total))


def do_define_endereco_principal_revese(apps, schema_editor):
    Endereco = apps.get_model("contrib", "Endereco")

    total = 0

    while Endereco.objects.filter(desativado_em=None, principal=True).exists():

        enderecos = Endereco.objects.filter(
            desativado_em=None,
            principal=True
        ).order_by()[:1000]

        for a in enderecos:
            a.principal = False

        bulk_update(enderecos, update_fields=['principal'], batch_size=1000)

        total += enderecos.count()
        print("Em progresso: {}".format(total))

    print ('\nMigração reverse finalizada. {} registros afetados!'.format(total))


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contrib', '0033_endereco_historico'),
    ]

    operations = [
        migrations.RunPython(
            code=do_define_endereco_principal,
            reverse_code=do_define_endereco_principal_revese,
            atomic=True
        )
    ]
