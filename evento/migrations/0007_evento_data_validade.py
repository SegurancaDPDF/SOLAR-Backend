# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0029_redimensiona_foto_servidores'),
        ('evento', '0006_evento_defensoria'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agenda',
            options={'ordering': ['-ativo', 'atuacao__defensor', '-data_cadastro']},
        ),
        migrations.AlterModelOptions(
            name='evento',
            options={'ordering': ['-ativo', 'defensor', '-data_cadastro'], 'permissions': (('auth_evento', 'Can authorize evento'), ('add_desbloqueio', 'Can add desbloqueio'), ('change_desbloqueio', 'Can change desbloqueio'), ('delete_desbloqueio', 'Can delete desbloqueio'))},
        ),
        migrations.RemoveField(
            model_name='evento',
            name='data_cadastro',
        ),
        migrations.RenameField(
            model_name='evento',
            old_name='data_cad',
            new_name='data_cadastro'
        ),
        migrations.AlterField(
            model_name='evento',
            name='data_cadastro',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='data_validade',
            field=models.DateField(default=None, null=True, verbose_name='Data Validade', blank=True),
        ),
        migrations.AlterField(
            model_name='evento',
            name='pai',
            field=models.ForeignKey(related_name='filhos', default=None, blank=True, to='evento.Evento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
