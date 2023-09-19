# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0038_manifestacaodocumento_posicao'),
    ]

    operations = [
        migrations.RenameField(
            model_name='manifestacao',
            old_name='codigo_sistema_procapi',
            new_name='sistema_webservice',
        ),
        migrations.AlterField(
            model_name='manifestacao',
            name='sistema_webservice',
            field=models.CharField(default=None, max_length=100, null=True, help_text='Identificador do Sistema Webservice no ProcAPI', blank=True),
        ),
        migrations.AddField(
            model_name='manifestacao',
            name='usuario_webservice',
            field=models.CharField(default=None, max_length=100, null=True, help_text='Identificador do Usu\xe1rio Webservice no ProcAPI', blank=True),
        ),
    ]
