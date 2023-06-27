# -*- coding: utf-8 -*-

from datetime import date

# Bibliotecas de terceiros
from django.db.models import QuerySet, Manager
from django.db import transaction
from django.db.models import Case, When, IntegerField

from . import models

from core.models import Classe, Parte, Processo
from defensor.models import Atuacao


class IndeferimentoQuerySet(QuerySet):
    def ativos(self):
        return self.filter(processo__desativado_em=None)

    def inativos(self):
        return self.exclude(processo__desativado_em=None)

    def deferidos(self):
        return self.filter(resultado=models.Indeferimento.RESULTADO_DEFERIDO)

    def indeferidos(self):
        return self.filter(resultado=models.Indeferimento.RESULTADO_INDEFERIDO)

    def avaliados(self):
        return self.exclude(resultado=models.Indeferimento.RESULTADO_NAO_AVALIADO)

    def nao_avaliados(self):
        return self.filter(resultado=models.Indeferimento.RESULTADO_NAO_AVALIADO)

    def em_movimento(self):
        return self.filter(processo__situacao=Processo.SITUACAO_MOVIMENTO)

    def annotate_prateleiras(self, setor):
        return self.annotate(
            prateleira=Case(
                When(
                    processo__situacao=Processo.SITUACAO_BAIXADO,
                    then=4),  # baixado
                When(
                    processo__situacao=Processo.SITUACAO_MOVIMENTO,
                    processo__setor_atual=setor,
                    processo__setor_encaminhado__isnull=False,
                    then=3),  # encaminhado
                When(
                    processo__situacao=Processo.SITUACAO_MOVIMENTO,
                    processo__setor_atual=setor,
                    processo__setor_encaminhado__isnull=True,
                    then=2),  # em analise
                When(
                    processo__situacao=Processo.SITUACAO_MOVIMENTO,
                    processo__setor_encaminhado=setor,
                    then=1),  # recebido
                output_field=IntegerField()
            )
        ).filter(
            prateleira__isnull=False
        )


class IndeferimentoManager(Manager.from_queryset(IndeferimentoQuerySet)):

    def get_or_create_atendimento_pessoa(self, atendimento, atuacao_id, pessoa_id, classe_id, setor_encaminhado_id=None,
                                         setores_notificados_ids=None,
                                         justificativa=None,
                                         medida_pretendida=None
                                         ):

        # Carrega informações de objetos relacionados
        classe = Classe.objects.get(id=classe_id)

        if atuacao_id:
            atuacao = Atuacao.objects.get(id=atuacao_id)
            defensor_id = atuacao.defensor_id
            defensoria_id = atuacao.defensoria_id
        else:
            defensor_id = atendimento.substituto_id if atendimento.substituto_id else atendimento.defensor_id
            defensoria_id = atendimento.defensoria_id

        indeferimentos = atendimento.indeferimentos.ativos().filter(
            defensor_id=defensor_id,
            pessoa_id=pessoa_id,
            processo__cadastrado_em__gt=date.today()
        )

        if indeferimentos.em_movimento().exists():
            raise Exception('Não foi possível criar indeferimento: já existe processo em andamento!')

        indeferimento = indeferimentos.first()

        if not indeferimento:

            # Se necessário registrar recurso no início do processo, a situação inicial será Peticionamento
            if classe.indeferimento_pode_registrar_recurso == Classe.INDEFERIMENTO_REGISTRAR_RECURSO_NO_INICIO:
                situacao_inicial = Processo.SITUACAO_PETICIONAMENTO
            else:
                situacao_inicial = Processo.SITUACAO_MOVIMENTO

            with transaction.atomic():
                # Processo
                processo = Processo.objects.create(
                    setor_criacao_id=defensoria_id,
                    setor_atual_id=defensoria_id,
                    setor_encaminhado_id=setor_encaminhado_id,
                    classe_id=classe_id,
                    tipo=Processo.TIPO_INDEFERIMENTO,
                    situacao=situacao_inicial,
                )

                if isinstance(setores_notificados_ids, (list, tuple)):
                    for setor_notificado_id in setores_notificados_ids:
                        processo.setores_notificados.add(setor_notificado_id)

                # Parte - validar: parte de processo ou pessoa em indeferimento?
                Parte.objects.create(
                    processo=processo,
                    pessoa_id=pessoa_id,
                    tipo=Parte.TIPO_ATIVO
                )

                # Indeferimento
                indeferimento = models.Indeferimento.objects.create(
                    processo=processo,
                    atendimento=atendimento,
                    defensor_id=defensor_id,
                    defensoria_id=defensoria_id,
                    pessoa_id=pessoa_id,  # validar: parte de processo ou pessoa em indeferimento?
                    justificativa=justificativa,
                    medida_pretendida=medida_pretendida
                )

        return indeferimento
