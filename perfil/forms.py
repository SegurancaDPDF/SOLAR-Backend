# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django import forms
from django.contrib.auth.models import User
from django.forms.models import ModelForm

# função para editar senha


class EditarSenhaPerfil(forms.Form):
    nova_senha = forms.CharField(label="Nova senha", widget=forms.PasswordInput, required=False)
    confirmar_nova_senha = forms.CharField(label="Confirmar nova senha", widget=forms.PasswordInput, required=False)

    def clean(self):

        if len(self.cleaned_data['nova_senha']) <= 5:
            raise ValueError("A nova senha precisa ter no mínimo 6 caracteres")

        elif not self.cleaned_data['nova_senha'] == self.cleaned_data['confirmar_nova_senha']:
            raise ValueError("As novas senhas precisam ser iguais")

# função para editar perfil


class EditarPerfil(ModelForm):

    class Meta:
        fields = '__all__'
        model = User
