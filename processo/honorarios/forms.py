# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django import forms

from .models import Honorario, Movimento
from contrib.models import Comarca, Area

# Solar


class HonorariosituacaoForm(forms.ModelForm):  # alterar a situação do Honorário

    class Meta:
        model = Honorario
        fields = ['situacao']


class movimentoForm(forms.ModelForm):  # adicionar/editar um Movimento relacionado a um Honorário

    class Meta:
        model = Movimento
        fields = '__all__'
        exclude = ['cadastrado_por', 'tipo', 'honorario', 'ativo']


class BuscarHonorariosForm(forms.Form):  # busca para filtrar Honorários com base em diferentes critérios

    situacao = forms.ChoiceField(
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'span2 ativar-select2'}))

    movimentacao = forms.ChoiceField(
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'span3 ativar-select2'}))

    data_ini = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'span1 datepicker',
                'placeholder': 'Data Inicial',
                'autocomplete': 'off',
                'data-date-format': 'dd/mm/yy'}))

    data_fim = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'span1 datepicker',
                'placeholder': 'Data Final',
                'autocomplete': 'off',
                'data-date-format': 'dd/mm/yy'}))

    comarca = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'span3 ativar-select2',
        }),
        empty_label='< TODAS COMARCAS >',
        queryset=Comarca.objects.filter(ativo=True)
    )

    def __init__(self, *args, **kwargs):
        super(BuscarHonorariosForm, self).__init__(*args, **kwargs)

        situacoes = [['', '< TODAS SITUAÇÕES >'], ['0', 'Novos'], ['1', 'Recursos'], ['2', 'Transitados e Julgados']]
        self.fields['situacao'].choices = situacoes

        movimentacoes = [
            ['', '< TODAS MOVIMENTAÇÕES >'],
            ['1', 'Aguardando Peticionamento'],
            ['2', 'Peticionado'],
            ['3', 'Encaminhado ao Defensor'],
            ['4', 'Protocolado'],
            ['6', 'Suspenso'],
            ['5', 'Baixado']
        ]

        self.fields['movimentacao'].choices = movimentacoes


class BuscarAnaliseForm(forms.Form):  # busca para filtrar Análises de Honorários com base em diferentes critérios

    data_ini = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'span1 datepicker',
                'placeholder': 'Data Inicial',
                'autocomplete': 'off',
                'data-date-format': 'dd/mm/yy'}))

    data_fim = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'span1 datepicker',
                'placeholder': 'Data Final',
                'autocomplete': 'off',
                'data-date-format': 'dd/mm/yy'}))

    area = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'span3 ativar-select2',
        }),
        empty_label='< TODAS ÁREAS >',
        queryset=Area.objects.filter(ativo=True)
    )

    comarca = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'span3 ativar-select2',
        }),
        empty_label='< TODAS COMARCAS >',
        queryset=Comarca.objects.filter(ativo=True)
    )

    numero = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'span3',
                'placeholder': 'Nº ou classe do processo'}))


class SuspenderForm(forms.ModelForm):  # suspender um Honorário

    class Meta:
        model = Honorario
        fields = ['suspenso_ate']


class MovimentoSuspencaoForm(forms.ModelForm):  # adicionar uma anotação a um Movimento de suspensão

    class Meta:
        model = Movimento
        fields = ['anotacao']
