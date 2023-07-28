# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0033_tarefa_responder_para'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tarefa',
            old_name='responder_para',
            new_name='resposta_para',
        ),
    ]
