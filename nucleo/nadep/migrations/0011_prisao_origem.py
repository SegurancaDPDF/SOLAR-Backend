# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0010_remissao'),
    ]

    operations = [
        migrations.AddField(
            model_name='prisao',
            name='origem',
            field=models.OneToOneField(related_name='originada', null=True, blank=True, to='nadep.Prisao', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
