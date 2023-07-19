# Generated by Django 3.2 on 2022-06-02 15:42
# Importações necessárias

from django.db import migrations, models

# Classe de migração do Django,# usada para alterar um campo específico do modelo "TipoEvento".
class Migration(migrations.Migration):

    dependencies = [
        ('procapi_client', '0013_alter_orgaojulgador_codigo_mni'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipoevento',
            name='codigo_mni',
            field=models.CharField(max_length=25, verbose_name='Código MNI'),
        ),
    ]