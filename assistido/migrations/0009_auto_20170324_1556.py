# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0008_auto_20170222_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='data_enviado',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Data de Envio', null=True),
        ),
        migrations.AlterField(
            model_name='documento',
            name='pessoa',
            field=models.ForeignKey(related_name='documentos', to='assistido.Pessoa', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
