# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django import forms

# Solar
from contrib.forms import BootstrapForm

# Modulos locais
from .models import (
    Predio
)


class PredioForm(BootstrapForm):
    class Meta:
        model = Predio
        fields = ('id', 'nome', 'comarca', 'qtd_andares')

    def __init__(self, *args, **kwargs):
        self.base_fields['nome'].widget = forms.TextInput(attrs={'class': 'span9', 'data-validate': '{required:true}'})
        super(PredioForm, self).__init__(*args, **kwargs)
