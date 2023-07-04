# Importações necessárias
from rest_framework import serializers

from . import models

# A classe Meta especifica o modelo a ser utilizado
# e os campos que devem ser incluídos no processo de serialização/desserialização.


class AtividadeExtraordinariaTipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AtividadeExtraordinariaTipo
        fields = '__all__'


class AtividadeExtraordinariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AtividadeExtraordinaria
        fields = '__all__'
