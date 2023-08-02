# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from datetime import datetime


def migrate_data(apps, schema_editor):

    PessoaAssistida = apps.get_model("assistido", "PessoaAssistida")
    User = apps.get_model("auth", "User")

    agora = datetime.now()
    usuario = User.objects.filter(is_superuser=True, is_active=True, is_staff=True).order_by('date_joined').first()

    PessoaAssistida.objects.filter(
        ativo=False,
        desativado_em__isnull=True
    ).update(
        desativado_por=usuario,
        desativado_em=agora
    )

def reverse_migrate_data(apps, schema_editor):

    PessoaAssistida = apps.get_model("assistido", "PessoaAssistida")

    PessoaAssistida.objects.filter(
        desativado_em__isnull=False
    ).update(
        ativo=False
    )


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0026_aumenta_apelido'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
        migrations.AlterModelOptions(
            name='pessoaassistida',
            options={'ordering': ['-desativado_em', 'nome'], 'verbose_name': 'Assistido', 'verbose_name_plural': 'Assistidos'},
        ),
        migrations.RemoveField(
            model_name='pessoaassistida',
            name='ativo',
        ),
    ]
