# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0044_pessoa_certidao_civil'),
    ]

    operations = [
        migrations.AddField(
            model_name='patrimonialtipo',
            name='grupo',
            field=models.SmallIntegerField(default=10, verbose_name='Grupo', choices=[(10, 'Patrim\xf4nio'), (21, 'Despesa Dedut\xedvel'), (22, 'Despesa N\xe3o Dedut\xedvel'), (30, 'Renda Extra')]),
        ),
    ]
