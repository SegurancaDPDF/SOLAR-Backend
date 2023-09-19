# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0039_manifestacao_usuario_webservice'),
    ]

    operations = [
        migrations.AddField(
            model_name='manifestacao',
            name='tipo_evento',
            field=models.SmallIntegerField(default=None, help_text='Tipo do Evento no MNI', null=True, blank=True),
        ),
    ]
