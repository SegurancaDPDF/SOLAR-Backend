# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from reversion.admin import VersionAdmin
from django.contrib import admin

# Módulos solar
from core.admin import AuditoriaVersionAdmin

# Modulos locais
from .models import Formulario, Nucleo, Pergunta, Resposta


# confinguracão do Admin para o modelo Núcleo
class NucleoAdmin(VersionAdmin):
    # define quais campos são exibidos na lista e filtros de pesquisa
    list_display = (
        'nome',
        'ativo',
        'agendamento',
        'acordo',
        'apoio',
        'plantao',
        'coletivo',
        'supervisionado',
        'propac',
        'diligencia',
        'livre',
    )


# configuração do Admin para o modelo Formulário
class FormularioAdmin(AuditoriaVersionAdmin):
    # define quais campos são exibidos na lista, filtros de pesquisa e quais campos são de somente leitura
    list_display = ('texto', 'posicao', 'nucleo', 'publico', 'exibir_em_atendimento',
                    'exibir_em_atividade_extraordinaria', 'gerar_alerta_em_atendimento', '_ativo')
    list_filter = ('publico', 'exibir_em_atendimento', 'exibir_em_atividade_extraordinaria',
                   'gerar_alerta_em_atendimento')
    search_fields = ('texto', )


# configuracão do Admin para o modelo Pergunta
class PerguntaAdmin(AuditoriaVersionAdmin):
    # define quais campos são exibidos na lista, filtros de pesquisa e campos dependentes de outras perguntas
    list_display = ('texto', 'posicao', 'tipo', 'formulario', '_ativo')
    list_filter = ('tipo', 'formulario')
    search_fields = ('texto', )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['sessao'].queryset = Pergunta.objects.ativos().filter(tipo=Pergunta.TIPO_SESSAO)
        return form


# configuracão do Admin para o modelo Resposta
class RespostaAdmin(AuditoriaVersionAdmin):
    # define quais campos são exibidos na lista, filtros de pesquisa e campos somente leitura
    readonly_fields = ('atendimento', 'evento', 'pergunta')
    search_fields = ('atendimento__numero', 'pergunta__texto')
    list_display = ('pergunta', 'texto', 'atendimento')
    list_filter = ('pergunta__formulario__nucleo', 'pergunta__formulario')
    search_fields = ('pergunta__texto', )


# registro dos modelos Núcleo, Formulário, Pergunta e Resposta no Admin do Django
admin.site.register(Nucleo, NucleoAdmin)
admin.site.register(Formulario, FormularioAdmin)
admin.site.register(Pergunta, PerguntaAdmin)
admin.site.register(Resposta, RespostaAdmin)
