# -*- coding: utf-8 -*-

# Bibliotecas de terceiros
from django.db.models import Q, QuerySet, Manager
from django.utils import timezone
from . import models


class AuditoriaBaseQuerySet(QuerySet):
    def ativos(self):  # retorna apenas os objetos que não possuem o campo desativado_em preenchido
        return self.filter(desativado_em=None)

    def inativos(self):
        return self.exclude(desativado_em=None)


class AuditoriaBaseManager(Manager.from_queryset(AuditoriaBaseQuerySet)):
    pass


class ClasseQuerySet(AuditoriaBaseQuerySet):
    def tipo_pedido(self):
        return self.filter(tipo=models.Classe.TIPO_PEDIDO)

    def tipo_impedimento(self):
        return self.filter(tipo=models.Classe.TIPO_IMPEDIMENTO)

    def tipo_suspeicao(self):
        return self.filter(tipo=models.Classe.TIPO_SUSPEICAO)

    def tipo_negacao(self):
        return self.filter(tipo=models.Classe.TIPO_NEGACAO)

    def tipo_negacao_hipossuficiencia(self):
        return self.filter(tipo=models.Classe.TIPO_NEGACAO_HIPOSSUFICIENCIA)

    def tipo_negacao_procedimento(self):
        """Negação da Classe Especial para o DPG"""
        return self.filter(tipo=models.Classe.TIPO_NEGACAO_PROCEDIMENTO)

    def processo_indeferimento(self):
        return self.filter(tipo_processo=models.Processo.TIPO_INDEFERIMENTO)


class ClasseManager(Manager.from_queryset(ClasseQuerySet)):
    pass


class EventoQuerySet(AuditoriaBaseQuerySet):

    def tipo_peticao(self):
        return self.filter(tipo__tipo=models.TipoEvento.TIPO_PETICAO)

    def tipo_recurso(self):
        return self.filter(tipo__tipo=models.TipoEvento.TIPO_RECURSO)

    def tipo_encaminhamento(self):
        return self.filter(tipo__tipo=models.TipoEvento.TIPO_ENCAMINHAMENTO)

    def tipo_recebimento(self):
        return self.filter(tipo__tipo=models.TipoEvento.TIPO_RECEBIMENTO)

    def tipo_decisao(self):
        return self.filter(tipo__tipo=models.TipoEvento.TIPO_DECISAO)

    def tipo_baixa(self):
        return self.filter(tipo__tipo=models.TipoEvento.TIPO_BAIXA)

    def em_edicao(self):
        return self.filter(em_edicao=True)

    def ordem_crescente(self):
        return self.order_by('numero')

    def ordem_decrescente(self):
        return self.order_by('-numero')


class EventoManager(Manager.from_queryset(EventoQuerySet)):

    def create_encaminhamento(self, processo, setor_encaminhado):

        # procura por tipo evento compatível
        tipo_evento = models.TipoEvento.objects.ativos().filter(
            tipo_processo=processo.tipo,
            tipo=models.TipoEvento.TIPO_ENCAMINHAMENTO,
        ).first()

        if not tipo_evento:
            raise Exception('Impossível criar evento de encaminhamento: TIPO_ENCAMINHAMENTO inexistente!')

        # cria evento de confirmação de recebimento
        return self.create(
            processo=processo,
            numero=processo.eventos.count()+1,
            setor_criacao=processo.setor_atual,
            setor_encaminhado=setor_encaminhado,
            data_referencia=timezone.now(),
            tipo=tipo_evento
        )

    def create_recebimento(self, processo):

        # procura por tipo evento compatível
        tipo_evento = models.TipoEvento.objects.ativos().filter(
            tipo_processo=processo.tipo,
            tipo=models.TipoEvento.TIPO_RECEBIMENTO,
        ).first()

        if not tipo_evento:
            raise Exception('Impossível criar evento de recebimento: TIPO_RECEBIMENTO inexistente!')

        # procura por ultimo evento do processo
        ultimo_evento = processo.eventos.ativos().filter().ordem_decrescente().first()
        historico = tipo_evento.nome

        if ultimo_evento:
            if ultimo_evento.setor_encaminhado_id == processo.setor_encaminhado_id:
                historico = '{} - ref. ao evento {}'.format(tipo_evento, ultimo_evento.numero)
            else:
                raise Exception('Impossível criar evento de recebimento: setor do processo não é o mesmo do último evento!')  # noqa: E501

        # cria evento de confirmação de recebimento
        return self.create(
            processo=processo,
            numero=processo.eventos.count()+1,
            setor_criacao=processo.setor_encaminhado,
            data_referencia=timezone.now(),
            historico=historico.upper(),
            tipo=tipo_evento
        )

    def create_baixa(self, processo, historico=None):

        # procura por tipo evento compatível
        tipo_evento = models.TipoEvento.objects.ativos().filter(
            tipo_processo=processo.tipo,
            tipo=models.TipoEvento.TIPO_BAIXA,
        ).first()

        if not tipo_evento:
            raise Exception('Impossível criar evento de baixa: TIPO_BAIXA inexistente!')

        # cria evento de confirmação de recebimento
        return self.create(
            processo=processo,
            numero=processo.eventos.count()+1,
            setor_criacao=processo.setor_atual,
            data_referencia=timezone.now(),
            tipo=tipo_evento,
            historico=historico
        )


class DocumentoQuerySet(AuditoriaBaseQuerySet):
    def anexos(self):
        return self.filter(
            documento=None
        ).exclude(
            arquivo=''
        )

    def pendentes(self):
        return self.filter(
            (
                Q(arquivo='') &
                Q(documento=None)
            ) |
            Q(documento__esta_assinado=False)
        )

    def ordem_alfabetica(self):
        return self.order_by('nome')

    def tipo_ged_assinados(self):
        return self.filter(documento__esta_assinado=True)

    def tipo_ged_nao_assinados(self):
        return self.filter(documento__esta_assinado=False)

    def validos(self):
        return self.filter(
            ~Q(documento=None) |
            ~Q(arquivo='')
        )


class DocumentoManager(Manager.from_queryset(DocumentoQuerySet)):
    pass


class ProcessoQuerySet(AuditoriaBaseQuerySet):
    def tipo_indeferimento(self):
        return self.filter(tipo=models.Processo.TIPO_INDEFERIMENTO)

    def baixados(self):
        return self.filter(situacao=models.Processo.SITUACAO_BAIXADO)

    def em_movimento(self):
        return self.filter(situacao=models.Processo.SITUACAO_MOVIMENTO)


class ProcessoManager(Manager.from_queryset(ProcessoQuerySet)):
    pass


class TipoEventoQuerySet(AuditoriaBaseQuerySet):

    def tipo_peticao(self):
        return self.filter(tipo=models.TipoEvento.TIPO_PETICAO)

    def tipo_recurso(self):
        return self.filter(tipo=models.TipoEvento.TIPO_RECURSO)

    def tipo_encaminhamento(self):
        return self.filter(tipo=models.TipoEvento.TIPO_ENCAMINHAMENTO)

    def tipo_recebimento(self):
        return self.filter(tipo=models.TipoEvento.TIPO_RECEBIMENTO)

    def tipo_decisao(self):
        return self.filter(tipo=models.TipoEvento.TIPO_DECISAO)

    def tipo_baixa(self):
        return self.filter(tipo=models.TipoEvento.TIPO_BAIXA)

    def tipo_anotacao(self):
        return self.filter(tipo=models.TipoEvento.TIPO_ANOTACAO)

    def tipo_atividade(self):
        return self.filter(tipo=models.TipoEvento.TIPO_ATIVIDADE)

    def tipo_brinquedoteca(self):
        return self.filter(tipo=models.TipoEvento.TIPO_BRINQUEDOTECA)


class TipoEventoManager(Manager.from_queryset(TipoEventoQuerySet)):
    pass
