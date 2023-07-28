# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0074_on_delete_protect'),
    ]

    operations = [
        migrations.AddField(
            model_name='atendimento',
            name='exibir_no_painel_de_acompanhamento',
            field=models.BooleanField(default=True, verbose_name='Exibir no Painel de Acompanhamento?'),
        ),
    ]
