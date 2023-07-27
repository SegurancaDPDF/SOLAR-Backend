from rest_framework import serializers

from . import models


class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Evento
        fields = '__all__'
        ref_name = 'ItineranteEvento'
