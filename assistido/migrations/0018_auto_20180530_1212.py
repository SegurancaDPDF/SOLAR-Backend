# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0017_pessoa_aderiu_zapdefensoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='renda',
            name='numero_membros_economicamente_ativos',
            field=models.SmallIntegerField(default=0, help_text='N\xfamero de membros na entidade familiar economicamente ativos', verbose_name='N\xba Membros Economicamente Ativos'),
        ),
        migrations.AlterField(
            model_name='patrimonio',
            name='tem_outros_bens',
            field=models.BooleanField(default=False, verbose_name='Possui Outros Bens'),
        ),
        migrations.AlterField(
            model_name='patrimonio',
            name='valor_outros_bens',
            field=models.DecimalField(default=0, help_text='Valor total, em R$, de outros bens e direitos', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='renda',
            name='numero_membros',
            field=models.SmallIntegerField(default=1, help_text='N\xfamero de membros na entidade familiar', verbose_name='N\xba Membros', validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
