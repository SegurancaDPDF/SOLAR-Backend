# Generated by Django 3.2 on 2021-06-14 08:28
# Importações necessárias

from django.db import migrations, models

# Classe de migração que altera um campo do modelo "Competencia".

class Migration(migrations.Migration):

    dependencies = [
        ('procapi_client', '0008_historico_consulta_teor_comunicacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competencia',
            name='principal',
            field=models.BooleanField(blank=True, default=False, verbose_name='Principal'),
        ),
    ]
