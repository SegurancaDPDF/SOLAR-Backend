# Generated by Django 3.2 on 2021-06-07 16:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0054_django_32'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoria',
            name='email',
            field=models.EmailField(blank=True, default=None, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='defensoria',
            name='mae',
            field=models.ForeignKey(blank=True, help_text='Defensoria responsável / supervisora', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='filhas', to='contrib.defensoria'),
        ),
    ]
