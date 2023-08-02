# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0029_add_dependentes_pessoa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pessoaassistida',
            name='estado_civil',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Estado Civil', choices=[(0, 'Solteiro(a)'), (1, 'Casado(a)'), (2, 'Viuvo(a)'), (3, 'Divorciado(a)'), (4, 'Uni\xe3o est\xe1vel'), (5, 'Separado judicialmente')]),
        ),
    ]
