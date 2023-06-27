from rest_framework import serializers

from . import models


# criar endpoints restantes do app Indeferimento
class IndeferimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Indeferimento
        fields = '__all__'
