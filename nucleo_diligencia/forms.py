# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Solar
from contrib.forms import BootstrapForm

# Modulos locais
from atendimento.atendimento.models import Defensor as Atendimento


class DistribuirNucleoDiligenciaForm(BootstrapForm):

    class Meta:
        model = Atendimento
        fields = []
