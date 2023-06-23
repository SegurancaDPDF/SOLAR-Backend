# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0013_atuacao_pode_assinar_ged'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defensor',
            name='senha_eproc',
            field=models.CharField(default='', help_text='Senha MNI (depreciado)', max_length=100, verbose_name='Senha MNI', blank=True),
        ),
        migrations.AlterField(
            model_name='defensor',
            name='usuario_eproc',
            field=models.TextField(default='', help_text='Usu\xe1rio(s) MNI separados por v\xedgula', verbose_name='Usu\xe1rio(s) MNI', blank=True),
        ),
    ]
