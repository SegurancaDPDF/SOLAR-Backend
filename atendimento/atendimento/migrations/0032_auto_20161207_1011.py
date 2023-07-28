# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import atendimento.atendimento.models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0003_unaccent_pg_extension'),
        ('atendimento', '0031_defensor_distribuido_por'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='documento_online',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Documento', blank=True, to='djdocuments.Documento', null=True),
        ),
        migrations.AlterField(
            model_name='documento',
            name='arquivo',
            field=models.FileField(default=None, upload_to=atendimento.atendimento.models.documento_file_name, null=True, verbose_name='Anexo', blank=True),
        ),
        migrations.AlterField(
            model_name='documento',
            name='documento',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Documento', null=True, verbose_name='Tipo', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
