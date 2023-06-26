# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Solar
from contrib.forms import BootstrapForm

# Modulos locais
from .models import Agenda, Evento


class EventoForm(BootstrapForm):

    class Meta:
        model = Evento
        fields = [
            'tipo',
            'titulo',
            'data_ini',
            'data_fim',
            'data_validade',
            'comarca',
            'defensoria',
            'categoria_de_agenda',
            'pai',
            'defensor'
        ]

    # usado para validar e limpar os dados enviados pelo formulário
    def clean(self):

        cleaned_data = super(EventoForm, self).clean()

        data_ini = cleaned_data.get('data_ini')
        data_fim = cleaned_data.get('data_fim')
        data_validade = cleaned_data.get('data_validade')

        if data_ini > data_fim:
            self.add_error('data_fim', 'A data final deve ser maior ou igual à data inicial')

        if data_validade and data_validade < data_fim:
            self.add_error('data_validade', 'A data de validade deve ser maior ou igual à data final')


class AgendaForm(BootstrapForm):

    # especifica o modelo associado ao formulário 'Agenda' e os campos que serão exibidos no formulário
    class Meta:
        model = Agenda
        fields = [
            'titulo',
            'data_ini',
            'data_fim',
            'atuacao',
            'hora_ini',
            'hora_fim',
            'vagas',
            'duracao',
            'simultaneos',
            'horarios',
            'conciliacao',
            'pai'
        ]

    # valida e limpar os dados enviados pelo formulário
    def clean(self):

        cleaned_data = super(AgendaForm, self).clean()

        data_ini = cleaned_data.get('data_ini')
        data_fim = cleaned_data.get('data_fim')

        if data_ini > data_fim:
            self.add_error('data_fim', 'A data final deve ser maior ou igual à data inicial')
