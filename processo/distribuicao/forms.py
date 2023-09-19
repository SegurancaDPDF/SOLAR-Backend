# -*- coding: utf-8 -*-
from django import forms

from contrib.models import Comarca, Defensoria, DefensoriaVara, Vara
from defensor.models import Defensor
from procapi_client.models import SistemaWebService


class BuscarIntimacaoForm(forms.Form):
    sistema_webservice = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'span1 ativar-select2'}),
        empty_label='< Selecione um sistema >',
        queryset=SistemaWebService.objects.ativos()
    )

    comarca = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'span1 ativar-select2'}),
        empty_label='< Selecione uma comarca >',
        queryset=Comarca.objects.filter(ativo=True)
    )

    vara = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'span3 ativar-select2'}),
        empty_label='< Selecione uma vara >',
        queryset=Vara.objects.filter(ativo=True)
    )

    paridade = forms.ChoiceField(
        choices=((None, '< Selecione uma paridade >'),) + DefensoriaVara.LISTA_PARIDADE,
        required=False,
        widget=forms.Select(
            attrs={'class': 'span1 ativar-select2'}))

    defensor = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'span3 ativar-select2'}),
        empty_label='< Selecione um defensor >',
        queryset=Defensor.objects.select_related('servidor').filter(eh_defensor=True).order_by('servidor__nome')
    )

    defensoria = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'span3 ativar-select2'}),
        empty_label='< Selecione uma defensoria >',
        queryset=Defensoria.objects.filter())

    def clean_paridade(self):
        value = self.cleaned_data['paridade']

        if value and value.isdigit():
            value = int(value)
        else:
            value = None

        return value
