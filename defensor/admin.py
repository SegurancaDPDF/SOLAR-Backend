# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

# Bibliotecas de terceiros
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from reversion.admin import VersionAdmin
from django.contrib import admin

# Modulos locais
from contrib.models import Servidor
from atendimento.atendimento.models import Defensor as AtendimentoDefensor

from .models import Atuacao, Defensor, Documento, EditalConcorrenciaPlantao, VagaEditalPlantao


# define as configurações de administração para o model Atuacao.
class AtuacaoAdmin(VersionAdmin):
    pre_exclude = []
    if not settings.USAR_EDEFENSOR:
        pre_exclude.append('habilitado_chat_edefensor')
    exclude = pre_exclude

    search_fields = ('defensor__servidor__nome', 'defensoria__nome')
    readonly_fields = ('data_cadastro', 'cadastrado_por', 'data_atualizacao', 'data_exclusao', 'excluido_por')
    list_display = ('defensor', 'tipo', 'titular', 'defensoria', 'periodo', 'documento', 'ativo')
    list_filter = ('defensor__eh_defensor', 'tipo', 'data_inicial', 'defensoria__comarca')

    def periodo(self, obj):
        if obj.data_final is None:
            return obj.data_inicial.strftime("%d/%m/%Y %H:%M:%S") + ' |  ------------- '
        else:
            return obj.data_inicial.strftime("%d/%m/%Y %H:%M:%S") + ' | ' + obj.data_final.strftime("%d/%m/%Y %H:%M:%S")

    periodo.admin_order_field = 'data_inicial'
    periodo.short_description = 'Período'

    @admin.action(description='Transferir atendimentos e agendamentos para UMA Atuação')
    def transferir_atendimentos(self, request, queryset):
        """Transfere os atendimentos e agendamentos para o defensor da atuação selecionada"""

        atuacao = queryset.first()

        if not atuacao:
            messages.error(request, 'Selecione apenas UMA Substituição ou Acumulação')
            return
        elif atuacao.tipo == Atuacao.TIPO_LOTACAO:
            messages.error(request, 'Apenas os tipos Subsituição ou Acumulação são permitidos')
            return

        # monta o filtro Q para buscar os atendimentos e agendamentos da atuação

        # atendimento não remarcado
        q = Q(remarcado=None)
        # atendimento da mesma defensoria da atuação
        q &= Q(defensoria=atuacao.defensoria)

        # data_agendamento ou data_atendimento maior ou igual a data_inicial da atuação
        q &= (Q(data_agendamento__gte=atuacao.data_inicial) | Q(data_atendimento__gte=atuacao.data_inicial))

        # se atuação tem data_final
        if atuacao.data_final:
            # data_agendamento ou data_atendimento menor ou igual a data_final da atuação
            q &= (Q(data_agendamento__lte=atuacao.data_final) | Q(data_atendimento__lte=atuacao.data_final))

        atendimentos = AtendimentoDefensor.objects.filter(q)

        with transaction.atomic():
            for atendimento in atendimentos:
                if atuacao.tipo == Atuacao.TIPO_SUBSTITUICAO:
                    atendimento.defensor = atuacao.titular
                    atendimento.substituto = atuacao.defensor
                else:
                    # se for acumulação
                    atendimento.defensor = atuacao.defensor
                    atendimento.substituto = None

                atendimento.save()

        messages.success(request, u'{} atendimentos transferidos para a Atuação de ID {}'.format(atendimentos.count(), atuacao.id))  # noqa: E501

    actions = [transferir_atendimentos]


# define as configurações de administração para o model Defensor.
class DefensorAdmin(VersionAdmin):
    search_fields = ('servidor__nome', 'usuario_eproc')
    list_display = ('nome', 'eh_defensor', 'usuario_eproc', 'ativo')


# define as configurações de administração para o model Documento.
class DocumentoAdmin(VersionAdmin):
    list_display = ('nome', 'data', 'tipo', 'ativo')


# define as configurações de administração para o model DefensorAssessor.
class DefensorAssessorAdmin(VersionAdmin):
    search_fields = ('servidor__usuario__first_name', 'servidor__usuario__last_name', 'usuario_eproc')
    list_display = ('nome', 'usuario_eproc', 'supervisor', 'ativo')
    list_filter = ('ativo', 'servidor__comarca')
    exclude = ('eh_defensor',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "servidor":
            if request.resolver_match.args:
                obj_id = request.resolver_match.args[0]
                kwargs["queryset"] = Servidor.objects.filter((Q(defensor=None) & Q(ativo=True)) | Q(defensor=obj_id))
            else:
                kwargs["queryset"] = Servidor.objects.filter(Q(defensor=None) & Q(ativo=True))

        if db_field.name == "supervisor":
            kwargs["queryset"] = Defensor.objects.filter(supervisor=None, eh_defensor=True, ativo=True)

        return super(DefensorAssessorAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        return super(DefensorAssessorAdmin, self).get_queryset(request).exclude(supervisor=None)


# configurações de administração para o modelo DefensorSupervisor.
class DefensorSupervisorAdmin(VersionAdmin):
    search_fields = ('servidor__usuario__first_name', 'servidor__usuario__last_name', 'usuario_eproc')
    list_display = ('nome', 'usuario_eproc', 'eh_defensor', 'ativo')
    list_filter = ('ativo', 'eh_defensor', 'servidor__comarca')
    exclude = ('supervisor',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "servidor":
            if request.resolver_match.args:
                obj_id = request.resolver_match.args[0]
                kwargs["queryset"] = Servidor.objects.filter(Q(defensor=None) | Q(defensor=obj_id))
            else:
                kwargs["queryset"] = Servidor.objects.filter(Q(defensor=None))

        return super(DefensorSupervisorAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


# define as configurações de administração para o modelo EditalConcorrenciaPlantao.
class EditalConcorrenciaPlantaoAdmin(VersionAdmin):
    list_display = ('descricao', 'data_inicio', 'data_final', 'data_abertura_inscricao', 'data_fechamento_inscricao', 'status')  # noqa: E501


class VagaEditalPlantaoAdmin(VersionAdmin):
    pass


admin.site.register(Atuacao, AtuacaoAdmin)
admin.site.register(VagaEditalPlantao, VagaEditalPlantaoAdmin)
admin.site.register(Defensor, DefensorAdmin)
admin.site.register(Documento, DocumentoAdmin)
admin.site.register(EditalConcorrenciaPlantao, EditalConcorrenciaPlantaoAdmin)
