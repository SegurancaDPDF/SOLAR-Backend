# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0026_novos_tipos_de_parte'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentofase',
            name='tipo',
            field=models.ForeignKey(related_name='documentos', on_delete=django.db.models.deletion.DO_NOTHING, default=None, to='processo.DocumentoTipo', help_text='Tipo de Documento', null=True),
        ),
        migrations.AddField(
            model_name='documentotipo',
            name='conta_estatistica',
            field=models.BooleanField(default=True, help_text='Conta Estat\xedsticas?'),
        ),
    ]
