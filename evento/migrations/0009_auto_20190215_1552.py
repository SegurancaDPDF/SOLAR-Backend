# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evento', '0008_autorizacao'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='evento',
            options={'ordering': ['-ativo', 'defensor', '-data_cadastro'], 'permissions': (('auth_evento', 'Can authorize evento'), ('add_desbloqueio', 'Can add desbloqueio'), ('change_desbloqueio', 'Can change desbloqueio'), ('delete_desbloqueio', 'Can delete desbloqueio'), ('manage_evento_nucleo', 'Can manage evento by nucleo'))},
        ),
    ]
