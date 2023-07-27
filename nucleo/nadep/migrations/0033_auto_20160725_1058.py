# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0032_auto_20160615_1052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='soltura',
            name='tipo',
            field=models.SmallIntegerField(verbose_name='Tipo', choices=[(1, 'Dec. Ju\xedz do Ato Convers\xe3o em Flagrante'), (2, 'Habeas Corpus'), (3, 'Liberdade Provis\xf3ria'), (4, 'Pagamento de Fian\xe7a'), (5, 'Revoga\xe7\xe3o de Pris\xe3o Preventiva'), (6, 'Senten\xe7a Absolut\xf3ria'), (7, 'Relaxamento de Pris\xe3o')]),
        ),
    ]
