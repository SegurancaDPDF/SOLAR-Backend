# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contrib.validators


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0046_pessoa_email_lower'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pessoa',
            name='cpf',
            field=models.CharField(default=None, validators=[contrib.validators.validate_CPF_CNPJ], max_length=32, blank=True, null=True, verbose_name='CPF', db_index=True),
        ),
    ]
