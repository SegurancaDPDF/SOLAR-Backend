# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Solar
from contrib.forms import BootstrapForm

# Modulos locais
from .models import Evento


class EventoForm(BootstrapForm):

    class Meta:
        model = Evento
        fields = ['titulo', 'data_inicial', 'data_final', 'municipio', 'defensoria', 'participantes']
