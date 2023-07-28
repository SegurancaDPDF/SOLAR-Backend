# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0046_auto_20171017_1420'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='atendimento',
            options={'ordering': ['-ativo', '-numero'], 'verbose_name': 'Atendimento Geral', 'verbose_name_plural': 'Atendimentos Gerais', 'permissions': (('view_all_atendimentos', 'Can view all atendimentos'), ('view_129', 'Can view 129'), ('view_recepcao', 'Can view Recep\xe7\xe3o'), ('view_defensor', 'Can view Defensor'), ('view_distribuicao', 'Can view Distribui\xe7\xe3o'), ('agendar_com_bloqueio', 'Pode agendar em dia com bloqueio (feriado)'))},
        ),
    ]
