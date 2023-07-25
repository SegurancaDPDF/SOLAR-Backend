# -*- coding: utf-8 -*-
from django import forms

from constance import config

from contrib.models import Defensoria
from defensor.models import Defensor
from procapi_client.models import SistemaWebService
from processo.processo.models import Aviso
from redis import ConnectionError


class BuscarIntimacaoForm(forms.Form):

    usa_defensor = True
    usa_defensoria = True

    # Tratamento de Erros do Redis Durante Build no CI/CD Gitlab
    try:
        usa_defensor = config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSOR_AUTOMATICAMENTE
        usa_defensoria = config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSORIA_AUTOMATICAMENTE
    except ConnectionError:
        # Ignora erro propositalmente
        pass
    except NameError:
        # Ignora erro propositalmente
        pass

    sistema_webservice = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'span2 ativar-select2'}),
        empty_label='< Selecione um sistema >',
        queryset=SistemaWebService.objects.ativos()
    )

    data_inicial = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'disabled': 'disabled',
                'class': 'span1 datepicker',
                'autocomplete': 'off',
                'placeholder': 'Data Inicial',
                'data-date-format': 'dd/mm/yyyy'}))

    data_final = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'disabled': 'disabled',
                'class': 'span1 datepicker',
                'autocomplete': 'off',
                'placeholder': 'Data Final',
                'data-date-format': 'dd/mm/yyyy'}))

    setor_responsavel = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'span3 ativar-select2',
                'disabled': not usa_defensoria
            }),
        empty_label='< Selecione uma defensoria >',
        queryset=Defensoria.objects.filter(ativo=True)
    )

    responsavel = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'span3 ativar-select2',
            }),
        empty_label='< Selecione um defensor >',
        queryset=Defensor.objects.select_related('servidor').filter(eh_defensor=True).order_by('servidor__nome')
    )

    tipo = forms.ChoiceField(
        choices=((None, '< Selecione um tipo >'),) + Aviso.LISTA_TIPO,
        required=False,
        widget=forms.Select(
            attrs={'class': 'span2 ativar-select2'}))

    situacao = forms.ChoiceField(
        choices=((None, '< Selecione >'),) + Aviso.LISTA_SITUACAO,
        required=False,
        widget=forms.Select(
            attrs={'class': 'span2 ativar-select2'}))

    def clean_situacao(self):
        value = self.cleaned_data['situacao']

        if value and value.isdigit():
            value = int(value)
        else:
            value = None

        return value

    def __init__(self, *args, **kwargs):

        # Obtém dados do usuário logado
        usuario = kwargs.pop('usuario', None)

        super(BuscarIntimacaoForm, self).__init__(*args, **kwargs)

        # Se usuário não tem permissão para ver todos atendimentos, restringe informações de acordo com suas lotações
        if not usuario.has_perm(perm='atendimento.view_all_atendimentos'):
            self.fields['setor_responsavel'].queryset = usuario.servidor.defensor.defensorias
            self.fields['responsavel'].queryset = usuario.servidor.defensor.lista_supervisores
