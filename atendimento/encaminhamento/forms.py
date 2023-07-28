# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django import forms

# Solar
from contrib.forms import BootstrapForm

# Modulos locais
from atendimento.atendimento.models import (
    Encaminhamento
)


class EncaminhamentoForm(BootstrapForm):
    class Meta:
        model = Encaminhamento
        fields = ('id', 'nome', 'email')

    def __init__(self, *args, **kwargs):
        self.base_fields['nome'].widget = forms.TextInput(attrs={'class': 'span9', 'data-validate': '{required:true}'})
        super(EncaminhamentoForm, self).__init__(*args, **kwargs)
