# Generated by Django 3.2 on 2022-05-27 23:31
# Importações necessárias
from django.db import migrations, models

# Classe de migração do Django,# usada para alterar um campo específico do modelo "OrgaoJulgador".

class Migration(migrations.Migration):

    dependencies = [
        ('procapi_client', '0012_orgaojulgador'), # Dependência da migração anterior
    ]

    operations = [
        migrations.AlterField(
            model_name='orgaojulgador',
            name='codigo_mni',
            field=models.CharField(max_length=25, verbose_name='Código MNI'),
        ),
    ]
