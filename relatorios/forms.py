# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django import forms

from contrib.forms import BootstrapForm
from contrib.models import Papel

from . import models


class BuscarRelatorioForm(forms.Form):
    tipo = forms.ChoiceField(
        choices=((None, 'Selecione um tipo...'),) + models.Relatorio.LISTA_TIPO,
        required=False,
        widget=forms.Select(attrs={'class': 'span2'})
    )
    filtro = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'off',
                'class': 'span3',
                'placeholder': 'Buscar pelo título de relatório...'
            }
        )
    )
    local = forms.ModelChoiceField(
        queryset=models.Local.objects.ativos(),
        empty_label="Selecione um local...",
        required=False,
        widget=forms.Select(attrs={'class': 'span3'})
    )
    papel = forms.ModelChoiceField(
        queryset=Papel.objects.filter(ativo=True).order_by('nome'),
        empty_label="Selecione um papel...",
        required=False,
        widget=forms.Select(attrs={'class': 'span3'})
    )


class EditarRelatorioForm(BootstrapForm):
    class Meta:
        model = models.Relatorio
        fields = ['titulo', 'caminho', 'locais', 'papeis']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'span12',
            }),
            'caminho': forms.TextInput(attrs={
                'class': 'span12 noupper',
            }),
            'locais': forms.CheckboxSelectMultiple(),
            'papeis': forms.CheckboxSelectMultiple(),
        }


class EditarRelatorioNaoParametrizavelForm(EditarRelatorioForm):
    def __init__(self, *args, **kwargs):
        self.base_fields['locais'].queryset = self.base_fields['locais'].queryset.nao_parametrizaveis()
        super(EditarRelatorioForm, self).__init__(*args, **kwargs)


class EditarRelatorioParametrizavelForm(EditarRelatorioForm):
    def __init__(self, *args, **kwargs):
        self.base_fields['locais'].queryset = self.base_fields['locais'].queryset.parametrizaveis()
        super(EditarRelatorioParametrizavelForm, self).__init__(*args, **kwargs)


class EditarRelatorioMetabaseForm(BootstrapForm):
    def __init__(self, *args, **kwargs):
        self.base_fields['locais'].queryset = self.base_fields['locais'].queryset.parametrizaveis()
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.Relatorio
        fields = ['titulo', 'metabase_dashboard_id', 'locais', 'papeis']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'span12',
            }),
            'metabase_dashboard_id': forms.NumberInput(attrs={
                'class': 'span6',
                'required': True,
            }),
            'locais': forms.CheckboxSelectMultiple(),
            'papeis': forms.CheckboxSelectMultiple(),
        }


class ParametrizarRelatorioForm(BootstrapForm):
    class Meta:
        model = models.Relatorio
        fields = ['parametros']
