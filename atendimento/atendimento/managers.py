# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from django.db.models import Q
from datetime import datetime

from core.managers import AuditoriaBaseQuerySet


class BaseQuerySet(models.QuerySet):
    def inativos(self):
        return self.filter(ativo=False)

    def ativos(self):
        return self.filter(ativo=True)


class BaseManager(models.Manager.from_queryset(BaseQuerySet)):
    pass


class AtendimentoQuerySet(BaseQuerySet):
    def tipo_nucleo(self):
        from .models import Atendimento
        return self.filter(tipo=Atendimento.TIPO_NUCLEO)

    def ultimos_validos(self):
        from .models import Qualificacao, Atendimento
        return self.filter(
            qualificacao__tipo__in=[
                Qualificacao.TIPO_PEDIDO,
                Qualificacao.TIPO_REMETIMENTO,
                # TODO verificar os possíveis impactos do tipo de qualificacao de arquivamento,
                # pois atendimentos dos respectivos tipos serão exibidos em outras telas quando
                # filtrado por ultimos_validos.
                Qualificacao.TIPO_ARQUIVAMENTO_COM_RESOLUCAO,
                Qualificacao.TIPO_ARQUIVAMENTO_SEM_RESOLUCAO,
                Qualificacao.TIPO_DESARQUIVAMENTO
            ],
            remarcado=None,
            ativo=True
        ).exclude(
            tipo__in=[Atendimento.TIPO_NUCLEO, Atendimento.TIPO_PROCESSO]
        ).exclude(
            filhos__tipo=Atendimento.TIPO_NUCLEO
        ).order_by(
            '-data_atendimento'
        )


class AtendimentoManager(models.Manager.from_queryset(AtendimentoQuerySet)):
    pass


class DocumentoQuerySet(BaseQuerySet):
    def documento_online_assinado(self):
        return self.filter(
            documento_online__esta_assinado=True
        )

    def anexos(self):
        return self.filter(
            documento_online=None
        ).exclude(
            arquivo=''
        )

    def atendimento_ativo(self):
        return self.filter(
            atendimento__ativo=True
        )

    def ativos(self):
        return self.filter(
            ativo=True
        )

    def pendentes(self):
        return self.filter(
            Q(arquivo='') &
            Q(documento_online__isnull=True)
        )

    def nao_pendentes(self):
        return self.filter(
            ~Q(arquivo='') |
            Q(documento_online__isnull=False)
        )

    def ordem_data_cadastro_crescente(self):
        return self.order_by(
            'data_cadastro'
        )


class DocumentoManager(models.Manager.from_queryset(DocumentoQuerySet)):
    pass


class ImpedimentoQuerySet(BaseQuerySet):
    def nao_recorridos(self):
        return self.filter(data_recurso=None)

    def nao_avaliados(self):
        return self.filter(data_avaliacao=None)


class ImpedimentoManager(models.Manager.from_queryset(ImpedimentoQuerySet)):
    pass


class QualificacaoQuerySet(BaseQuerySet):
    def pedidos(self):
        from .models import Qualificacao
        return self.filter(tipo=Qualificacao.TIPO_PEDIDO)

    def atividades(self):
        from .models import Qualificacao
        return self.filter(tipo=Qualificacao.TIPO_ATIVIDADE)

    def anotacoes(self):
        from .models import Qualificacao
        return self.filter(tipo=Qualificacao.TIPO_ANOTACAO)

    def notificacoes(self):
        from .models import Qualificacao
        return self.filter(tipo=Qualificacao.TIPO_NOTIFICACAO)

    def tarefas(self):
        from .models import Qualificacao
        return self.filter(tipo=Qualificacao.TIPO_TAREFA)


class QualificacaoManager(models.Manager.from_queryset(QualificacaoQuerySet)):
    def get_or_create_by_acao(self, acao, exibir_em_atendimentos=True):
        from .models import Qualificacao

        qualificacao = None

        # Procura/Cria qualificação correspondente ao nome e área informados
        try:
            qualificacao, nova = Qualificacao.objects.get_or_create(
                titulo_norm=acao.nome_norm,
                area=acao.area,
                ativo=True,
                defaults={
                    'titulo': acao.nome,
                    'acao': acao,
                    'exibir_em_atendimentos': exibir_em_atendimentos
                }
            )
        except MultipleObjectsReturned:
            qualificacao = Qualificacao.objects.filter(
                titulo_norm=acao.nome_norm,
                area_id=acao.area,
                ativo=True
            ).first()

        return qualificacao


class FormaAtendimentoQuerySet(AuditoriaBaseQuerySet):
    def vigentes(self):
        queryset = (
            Q(data_inicial__lte=datetime.now()) &
            Q(
                Q(data_final=None) |
                Q(data_final__gte=datetime.now())
            ) &
            Q(desativado_por=None) &
            Q(desativado_em=None)
        )

        return self.filter(queryset)

    def vigentes_defensor(self):
        return self.vigentes().filter(aparece_defensor=True)


class FormaAtendimentoManager(models.Manager.from_queryset(FormaAtendimentoQuerySet)):
    pass


class TipoColetividadeQuerySet(AuditoriaBaseQuerySet):
    def vigentes(self):
        return self.filter(
            Q(data_inicial__lte=datetime.now()) &
            Q(
                Q(data_final=None) |
                Q(data_final__gte=datetime.now())
            )
        )


class TipoColetividadeManager(models.Manager.from_queryset(TipoColetividadeQuerySet)):
    pass
