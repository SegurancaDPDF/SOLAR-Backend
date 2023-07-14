# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0028_verbose_name_fields_salario'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoria',
            name='distribuir_ao_encaminhar',
            field=models.BooleanField(default=False, help_text='Flag para determinar se a Defensoria distribui automaticamente ao encaminhar agendamento', verbose_name='Deve distribuir agendamento ao encaminhar?'),
        ),
        migrations.AddField(
            model_name='defensoria',
            name='encaminhamento_distribuido',
            field=models.BooleanField(default=False, help_text='Flag para determinar se a Defensoria recebe distribuicao automatica', verbose_name='Permite receber encaminhamento distribuido?'),
        ),
    ]
