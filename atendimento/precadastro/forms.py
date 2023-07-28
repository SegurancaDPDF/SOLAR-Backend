# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django import forms

# Solar
from contrib.models import Comarca, Estado, Municipio
from defensor.models import Defensor
from evento.models import Categoria


class EnderecoForm(forms.Form):
    estado = forms.ModelChoiceField(queryset=Estado.objects.order_by('nome'), empty_label=None)
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.order_by('nome'), empty_label='Selecione...')
    bairro = forms.CharField()
    complemento = forms.CharField()
    logradouro = forms.CharField(required=False)
    numero = forms.CharField()
    cep = forms.CharField()

    def __init__(self, *args, **kwargs):

        super(EnderecoForm, self).__init__(*args, **kwargs)

        self.fields['cep'].widget = forms.TextInput(attrs={'class': 'span6', 'ui-mask': '99.999-999',
                                                           'ng-change': 'consultaCep()', 'id': 'cep'})

        self.fields['estado'].widget.attrs = {'class': 'span2', 'ng-change': 'listar_municipios()'}
        self.fields['municipio'].widget.attrs = {'class': 'span8', 'ng-change': 'modificou()',
                                                 'ng-options': 'i.id as i.nome for i in municipios',
                                                 'data-validate': '{required:true,number:true}'}

        self.fields['bairro'].widget = forms.TextInput(
            attrs={'class': 'span6', 'placeholder': 'Bairro', 'id': 'logradouro'})

        self.fields['logradouro'].widget = forms.TextInput(attrs={'class': 'span6', 'placeholder': 'Logradouro', 'id': 'logradouro'})  # noqa: E501

        self.fields['numero'].widget = forms.TextInput(attrs={'class': 'span6', 'placeholder': 'Número', 'id': 'numero'})  # noqa: E501

        self.fields['complemento'].widget = forms.TextInput(attrs={'class': 'span6', 'placeholder': 'Complemento', 'id': 'complemento'})  # noqa: E501

        # carrega lista de municipios do estado selecionado
        try:
            self.fields['municipio'].queryset = Municipio.objects.filter(estado_id=kwargs['initial']['estado'])
        except Exception:
            self.fields['municipio'].queryset = Municipio.objects.none()

        # coloca o atributo 'ng-model' em todos campos
        for field in self.fields:
            self.fields[field].widget.attrs['ng-model'] = 'pessoa.' + field


class PainelForm(forms.Form):

    SITUACAO_PENDENTE = 1
    SITUACAO_DISTRIBUIDO = 2
    SITUACAO_AGENDADO = 3
    SITUACAO_BAIXADO = 4

    LISTA_SITUACAO = (
        (SITUACAO_PENDENTE, 'Aguardando distribuição'),
        (SITUACAO_DISTRIBUIDO, u'Aguardando análise'),
        (SITUACAO_AGENDADO, u'Agendados'),
        (SITUACAO_BAIXADO, u'Encaminhados/Excluídos'),
    )

    data_inicial = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'span1 datepicker',
                'autocomplete': 'off',
                'placeholder': 'Data Inicial',
                'data-date-format': 'dd/mm/yyyy'}))

    data_final = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'span1 datepicker',
                'autocomplete': 'off',
                'placeholder': 'Data Final',
                'data-date-format': 'dd/mm/yyyy'}))

    comarca = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'span3 ativar-select2'}),
        empty_label='< Selecione uma comarca >',
        queryset=Comarca.objects.filter(ativo=True)
    )

    responsavel = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'span3 ativar-select2'}),
        empty_label='< Selecione um responsável >',
        queryset=Defensor.objects.select_related('servidor').atuacoes_vigentes().filter(
            all_atuacoes__defensoria__agendamento_online=True
        ).distinct()
    )

    agenda = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'span3 ativar-select2'}),
        empty_label='< Selecione uma categoria >',
        queryset=Categoria.objects.filter(eh_categoria_crc=True)
    )

    situacao = forms.ChoiceField(
        choices=((None, '< Selecione >'),) + LISTA_SITUACAO,
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

        super(PainelForm, self).__init__(*args, **kwargs)

        # Se usuário não tem permissão para ver todos atendimentos, restringe informações de acordo com suas lotações
        if usuario and not usuario.has_perm(perm='atendimento.view_all_atendimentos'):
            self.fields['responsavel'].queryset = usuario.servidor.defensor.listar_lotados(
                eh_agendamento_online=True
            )
