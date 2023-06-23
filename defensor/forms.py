# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
from datetime import date, datetime, time

# Bibliotecas de terceiros
from django import forms
from django.db.models import Q
from django.forms.utils import ErrorList

# Modulos locais
from contrib.forms import BootstrapForm
from .models import Atuacao, Documento, InscricaoEditalPlantao


# formulário do django que é usado para criar ou atualizar objetos do model Atuacao
class AtuacaoForm(forms.ModelForm):

    class Meta:
        model = Atuacao
        fields = ['defensoria', 'defensor', 'titular', 'tipo', 'data_inicial', 'data_final', 'pode_assinar_ged', 'observacao', 'designacao_extraordinaria']  # noqa: E501


# criar ou atualizar objetos do modelo Documento
class DocumentoForm(forms.ModelForm):

    class Meta:
        model = Documento
        fields = ['tipo', 'numero', 'data']


# excluir uma instância do modelo Atuacao.
class ExcluirAtuacaoForm(BootstrapForm):

    class Meta:
        model = Atuacao
        fields = ['data_final']

    def __init__(self, *args, **kwargs):
        super(ExcluirAtuacaoForm, self).__init__(*args, **kwargs)
        self.fields['data_final'].widget = forms.HiddenInput()


# criar ou atualizar objetos do modelo Atuacao relacionados à lotação
class LotacaoForm(BootstrapForm):

    class Meta:
        model = Atuacao
        fields = ('defensor', 'defensoria', 'data_inicial', 'data_final', 'pode_assinar_ged')

    def __init__(self, *args, **kwargs):

        super(LotacaoForm, self).__init__(*args, **kwargs)

        self.fields['defensor'].widget = forms.HiddenInput()
        self.fields['defensoria'].widget.attrs = {'class': 'span12', 'required': 'true'}
        self.fields['data_inicial'].widget.input_type = 'datetime-local'
        self.fields['data_final'].widget.input_type = 'datetime-local'
        self.initial['data_inicial'] = str(datetime.now().date()) + 'T00:00'
        self.fields['data_inicial'].widget.attrs = {
            'class': 'span6',
            'required': 'true'
        }
      
        self.fields['data_final'].widget.attrs = {
            'class': 'span6',
           
        }

    def clean_data_inicial(self):

        data_inicial = self.cleaned_data["data_inicial"]

        if data_inicial.date() < datetime.now().date():
            raise forms.ValidationError("A data inicial não pode ser anterior a hoje")

        return data_inicial

    def clean_data_final(self):

        data_final = self.cleaned_data["data_final"]

        if data_final:
            
            if data_final < self.cleaned_data["data_inicial"]:
                raise forms.ValidationError("A data final não pode ser anterior à data inicial")

        return data_final

    def is_valid(self):

        valido = super(LotacaoForm, self).is_valid()

        if valido:

            defensor = self.cleaned_data["defensor"]
            defensoria = self.cleaned_data["defensoria"]

            atuacoes = defensor.atuacoes().filter(
                Q(defensoria=defensoria) &
                (
                    Q(data_final__gte=self.cleaned_data["data_inicial"]) |
                    Q(data_final=None)
                )
            )

            if self.cleaned_data["data_final"]:
                atuacoes.filter(data_inicial__lte=self.cleaned_data["data_final"])

            if atuacoes.exists():
                valido = False
                self._errors['defensoria'] = ErrorList([
                    u'O servidor {0} já está lotado em {1}'.format(defensor, defensoria)
                ])

        return valido


# pesquisar editais de plantão
class BuscarEditalPlantaoForm(forms.Form):
    data_inicial = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'ng-model': 'filtro.data_inicial',
                'ng-change': 'validar()',
                'autocomplete': 'off',
                'class': 'span1 datepicker',
                'placeholder': 'Data Inicial',
                'data-date-format': 'dd/mm/yy'}))

    data_final = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'ng-model': 'filtro.data_final',
                'ng-change': 'validar()',
                'autocomplete': 'off',
                'class': 'span1 datepicker',
                'placeholder': 'Data Final',
                'data-date-format': 'dd/mm/yy'}))

    def __init__(self, *args, **kwargs):
        super(BuscarEditalPlantaoForm, self).__init__(*args, **kwargs)


# criar ou cancelar inscrições em editais de plantão
class InscricaoPlantaoForm(forms.ModelForm):
    class Meta:
        model = InscricaoEditalPlantao
        fields = [
            'defensor',
            'edital',
            'vaga'
        ]

    def is_valid(self, acao):
        if super(InscricaoPlantaoForm, self).is_valid():
            inscricao_existente = InscricaoEditalPlantao.objects.filter(
                defensor=self.cleaned_data['defensor'],
                edital=self.cleaned_data['edital'],
                vaga=self.cleaned_data['vaga'],
                ativo=True
            ).exists()

            data_abertura_inscricao = self.cleaned_data['edital'].data_abertura_inscricao
            data_fechamento_inscricao = self.cleaned_data['edital'].data_fechamento_inscricao
            data_hoje = date.today()

            esta_no_intervalo_de_inscricao = data_hoje >= data_abertura_inscricao and data_hoje <= data_fechamento_inscricao  # noqa: E501

            if not self.cleaned_data['defensor'].posicao_lista_antiguidade:
                self.add_error('vaga', "Não consta a informação da posição na lista de antiguidade no cadastro do seu perfil de usuário, entre em contato com o Departamento de Informática para realizar a atualização.")  # noqa: E501
                return False

            if not self.cleaned_data['defensor'].eh_defensor:
                self.add_error('vaga', "Seu perfil de usuário não é de defensor e a inscrição é aberta somente a defensores.")  # noqa: E501
                return False

            if not self.cleaned_data['vaga']:
                self.add_error('vaga', "Selecione uma das datas na lista.")
                return False

            if self.cleaned_data['vaga'] and self.cleaned_data['defensor'] and self.cleaned_data['edital'] and acao == "inscrever":  # noqa: E501
                if not esta_no_intervalo_de_inscricao:
                    self.add_error('vaga', "Inscrição fora do intervalo de datas. O período é entre " + data_abertura_inscricao.strftime("%d/%m/%Y") + " e " + data_fechamento_inscricao.strftime("%d/%m/%Y"))  # noqa: E501
                    return False
                if inscricao_existente:
                    self.add_error('vaga', "Inscrição já foi realizada nesta data")
                    return False
                if not self.cleaned_data['edital'].status == self.cleaned_data['edital'].STATUS_ATIVO:
                    self.add_error('vaga', "Edital não está ativo para receber inscrição")
                    return False
                return True

            if self.cleaned_data['vaga'] and self.cleaned_data['defensor'] and self.cleaned_data['edital'] and acao == "cancelar":  # noqa: E501
                if not esta_no_intervalo_de_inscricao:
                    self.add_error('vaga', "Cancelamento fora do intervalo de datas. O período é entre " + data_abertura_inscricao.strftime("%d/%m/%Y") + " e " + data_fechamento_inscricao.strftime("%d/%m/%Y"))  # noqa: E501
                    return False
                if not inscricao_existente:
                    self.add_error('vaga', "Não foi realizada inscrição nesta data")
                    return False
                if not self.cleaned_data['edital'].status == self.cleaned_data['edital'].STATUS_ATIVO:
                    self.add_error('vaga', "Edital não está ativo para receber cancelamentos")
                    return False
                return True

        return False
