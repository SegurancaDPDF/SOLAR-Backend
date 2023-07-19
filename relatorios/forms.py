# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django import forms

from contrib.forms import BootstrapForm
from contrib.models import Papel

from . import models


class BuscarRelatorioForm(forms.Form):  # classe de formulario para buscar relatorios
    tipo = forms.ChoiceField(
        choices=((None, 'Selecione um tipo...'),) + models.Relatorio.LISTA_TIPO,
        required=False,
        widget=forms.Select(attrs={'class': 'span2'})
    )  # campo de escolha para o tipo do relatorio
    filtro = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'off',
                'class': 'span3',
                'placeholder': 'Buscar pelo título de relatório...'
            }
        )
    )  # campo de texto para filtrar por titulo de relatorio
    local = forms.ModelChoiceField(
        queryset=models.Local.objects.ativos(),
        empty_label="Selecione um local...",
        required=False,
        widget=forms.Select(attrs={'class': 'span3'})
    )  # campo de escolha para o local do relatorio
    papel = forms.ModelChoiceField(
        queryset=Papel.objects.filter(ativo=True).order_by('nome'),
        empty_label="Selecione um papel...",
        required=False,
        widget=forms.Select(attrs={'class': 'span3'})
    )  # campo de escolha para o papel relacionado ao relatorio


class EditarRelatorioForm(BootstrapForm):  # editar relatorios
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
        }  # widgets utilizados para cada campo do formulario


class EditarRelatorioNaoParametrizavelForm(EditarRelatorioForm):
    # classe de formulário para editar relatórios não parametrizáveis
    def __init__(self, *args, **kwargs):
        self.base_fields['locais'].queryset = self.base_fields['locais'].queryset.nao_parametrizaveis()
        super(EditarRelatorioForm, self).__init__(*args, **kwargs)


class EditarRelatorioParametrizavelForm(EditarRelatorioForm):
    # classe de formulário para editar relatórios parametrizáveis
    def __init__(self, *args, **kwargs):
        self.base_fields['locais'].queryset = self.base_fields['locais'].queryset.parametrizaveis()
        super(EditarRelatorioParametrizavelForm, self).__init__(*args, **kwargs)


class EditarRelatorioMetabaseForm(BootstrapForm):
    # editar relatórios
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
        }   # widgets utilizados para cada campo do formulário


class ParametrizarRelatorioForm(BootstrapForm):
    class Meta:
        model = models.Relatorio
        fields = ['parametros']
