# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas padrao
from datetime import datetime

# Bibliotecas de terceiros
from django import forms
from django.forms.utils import ErrorList

# Modulos SOLAR
from contrib.models import Defensoria

# Modulos locais
from . import models


class DocumentoUploadForm(forms.ModelForm):

    arquivo = forms.FileField(required=True)

    class Meta:
        model = models.Documento
        fields = ['arquivo']


class RenomearDocumentoForm(forms.ModelForm):

    class Meta:
        model = models.Documento
        fields = ['nome']

    def is_valid(self):
        # verifica se o formulario é válido. Realiza validacoes adicionais para renomear o documento
        valid = super(RenomearDocumentoForm, self).is_valid()

        if valid:

            if not self.instance.evento.em_edicao:
                self._errors['nome'] = 'Não é possível renomear documento de evento já protocolado'
                valid = False

            if self.instance.documento and self.instance.documento.esta_assinado:
                self._errors['nome'] = 'Não é possível renomear documentos ged já assinados'
                valid = False

        return valid


class EventoForm(forms.ModelForm):  # editar dados do evento antes de finalizá-lo

    def __init__(self, *args, **kwargs):  # configura o atributo required para os campos obrigatórios

        super(EventoForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            if self.fields[field].required:
                self.fields[field].widget.attrs['required'] = True
        # atualiza a consulta do campo setor_encaminhado com base no processo
        if kwargs.get('instance') and kwargs.get('instance').processo:
            self.fields['setor_encaminhado'].queryset = Defensoria.objects.ativos().exclude(
                id=kwargs.get('instance').processo.setor_atual_id
            )


class NovoEventoForm(EventoForm):

    data_data_referencia = forms.DateField(required=False)
    hora_data_referencia = forms.TimeField(required=False)

    incluir_documentos = forms.ChoiceField(
        choices=(
            (True, 'Sim'),
            (False, 'Não')
        ),
        initial=True,
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'span6'
            }
        )
    )

    class Meta:
        model = models.Evento
        fields = ['tipo', 'setor_criacao', 'setor_encaminhado', 'data_referencia', 'historico']

    def clean(self):

        cleaned_data = super(NovoEventoForm, self).clean()
        # verifica se as datas e horas de referência estão preenchidas
        data_referencia = cleaned_data.get('data_data_referencia')
        hora_referencia = cleaned_data.get('hora_data_referencia')

        if data_referencia and hora_referencia:
            cleaned_data['data_referencia'] = datetime.combine(data_referencia, hora_referencia)
        else:
            cleaned_data['data_referencia'] = self.instance.data_referencia

        return cleaned_data

    def is_valid(self):  # verifica se o formulario é válido

        valid = super(NovoEventoForm, self).is_valid()

        if valid:

            evento = self.instance
            ultimo = evento.processo.eventos.ativos().last()

            # Verifica se evento anterior é um encaminhamento feito pelo mesmo setor atual
            if ultimo and ultimo.setor_encaminhado and ultimo.setor_criacao == evento.setor_criacao:
                valid = False
                self._errors['setor_criacao'] = ErrorList([
                    u'O processo já foi encaminhado para outro setor!'
                ])

        return valid


class EditarEventoForm(EventoForm):  # edicao de eventos

    class Meta:
        model = models.Evento
        fields = ['data_referencia', 'setor_criacao', 'titulo', 'historico', 'tipo', 'setor_encaminhado']
        widgets = {
            'data_referencia': forms.TextInput(attrs={
                'class': 'datepicker',
                'autocomplete': 'off',
                'data-date-format': 'dd/mm/yyyy'
            }),
            'tipo': forms.Select(attrs={
                'class': 'span12',
                'onchange': 'this.form.submit()'
            }),
            'setor_criacao': forms.Select(attrs={
                'class': 'span12',
            }),
            'setor_encaminhado': forms.Select(attrs={
                'class': 'span12',
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'span12',
            }),
            'historico': forms.Textarea(attrs={
                'class': 'span12',
                'rows': '5',
                'placeholder': 'Digite aqui anotações adicionais...'
            }),
        }

    def __init__(self, *args, **kwargs):

        super(EditarEventoForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            # se evento anotação, desativa campo setor responsavel
            if kwargs.get('instance').tipo.tipo == models.TipoEvento.TIPO_ANOTACAO:
                del self.fields['setor_encaminhado']
