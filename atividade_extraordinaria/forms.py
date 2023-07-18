# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django import forms
from django.contrib.auth.models import User

# Solar
from contrib.models import Defensoria
from contrib.form_fields import UserModelChoiceField

from core.forms import EditarEventoForm

from . import models

# Classe de formulário para busca de atividades extraordinárias.


class BuscarAtividadeExtraordinariaForm(forms.Form):
    data_inicial = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'span1 datepicker',
                'autocomplete': 'off',
                'placeholder': 'Data Inicial',
                'data-date-format': 'dd/mm/yy'}))

    data_final = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'span1 datepicker',
                'autocomplete': 'off',
                'placeholder': 'Data Final',
                'data-date-format': 'dd/mm/yy'}))

    participante = UserModelChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'span3 ativar-select2'}),
        empty_label='< Selecione um participante >',
        queryset=User.objects.filter(
            servidor__ativo=True,
        ).order_by('first_name', 'last_name')
    )

    defensoria = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'span3 ativar-select2'}),
        empty_label='< Selecione uma defensoria >',
        queryset=Defensoria.objects.filter(ativo=True, pode_cadastrar_atividade_extraordinaria=True)
    )

    tipo = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'span2 ativar-select2'}),
        empty_label='< Selecione um tipo >',
        queryset=models.AtividadeExtraordinariaTipo.objects.ativos().order_by('nome')
    )

    filtro = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'span2',
                'placeholder': 'Buscar pelo título...'}))

# Classe de formulário para criar ou editar uma atividade extraordinária.


class AtividadeExtraordinariaForm(forms.ModelForm):
    class Meta:
        model = models.AtividadeExtraordinaria
        fields = ['titulo', 'data_referencia', 'encerrado_em', 'tipo', 'setor_criacao', 'numero', 'historico',
                  'complemento', 'area']

        widgets = {
            'acao': forms.Select(attrs={'class': 'span12', 'data-form': 'select2'}),
        }

# Classe de formulário para editar uma atividade extraordinária.


class EditarAtividadeExtraordinariaForm(EditarEventoForm):

    def __init__(self, *args, **kwargs):

        super(EditarAtividadeExtraordinariaForm, self).__init__(*args, **kwargs)

        # filtra tipos de eventos válidos
        self.fields['tipo'].queryset = models.AtividadeExtraordinariaTipo.objects.ativos()

        # campos somente leitura
        self.fields['data_referencia'].widget.attrs['readonly'] = True
        self.fields['setor_criacao'].widget.attrs['readonly'] = True
        self.fields['setor_encaminhado'].widget.attrs['readonly'] = True

# Classe de formulário para encerrar uma atividade extraordinária.


class EncerrarAtividadeExtraordinariaForm(forms.ModelForm):
    class Meta:
        model = models.AtividadeExtraordinaria
        fields = ['encerrado_em']
