# Generated by Django 3.2 on 2021-06-14 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0017_django_32'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='tipo',
            field=models.SmallIntegerField(choices=[(0, 'Portaria'), (1, 'Ato'), (2, 'Edital'), (3, 'Resolução')], default=0),
        ),
    ]
