# Generated by Django 3.2 on 2021-10-21 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0059_defensoriavara_parte'),
        ('comarca', '0005_on_delete'),
    ]

    operations = [
        migrations.AddField(
            model_name='guiche',
            name='defensoria',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='contrib.defensoria'),
        ),
        migrations.AddField(
            model_name='guiche',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='contrib.servidor'),
        ),
        migrations.AddField(
            model_name='predio',
            name='recepcao_por_atuacao',
            field=models.BooleanField(default=False, verbose_name='Recepção mostrar apenas atuações do servidor?'),
        ),
    ]
