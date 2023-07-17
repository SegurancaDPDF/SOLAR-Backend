# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from rest_framework import serializers

from . import models


class LocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Local
        fields = '__all__'


class RelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Relatorio
        fields = '__all__'
