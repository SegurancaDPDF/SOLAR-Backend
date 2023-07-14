# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0043_tipotelefonesms'),
    ]

    operations = [
        migrations.AddField(
            model_name='papel',
            name='css_label_class',
            field=models.CharField(default='', help_text='Usado para definir a cor de labels', max_length=25, verbose_name='CSS Label Class', choices=[('', 'Default'), ('label-success', 'Success'), ('label-warning', 'Warning'), ('label-important', 'Important'), ('label-info', 'Info'), ('label-inverse', 'Inverse')]),
        ),
    ]
