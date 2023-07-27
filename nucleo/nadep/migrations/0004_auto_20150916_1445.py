# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0003_auto_20150824_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prisao',
            name='data_transito_apenado',
            field=models.DateField(null=True, verbose_name='Tr\xe2nsito em Julgado da Senten\xe7a para o(a) Apenado(a)', blank=True),
        ),
    ]
