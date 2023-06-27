# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from django.db import models

from core.models import Classe as CoreClasse, Processo as CoreProcesso

from . import managers


class Indeferimento(models.Model):
    # define as constantes e a lista de opções para o campo resultado
    RESULTADO_NAO_AVALIADO = 0  
    RESULTADO_DEFERIDO = 10
    RESULTADO_INDEFERIDO = 20
    RESULTADO_RECEBIDO = 30

    LISTA_RESULTADO = (
        (RESULTADO_NAO_AVALIADO, 'Não Avaliado'),
        (RESULTADO_DEFERIDO, 'Deferimento'),
        (RESULTADO_INDEFERIDO, 'Indeferimento'),
        (RESULTADO_RECEBIDO, 'Recebimento'),
    )
    # define as constantes e a lista de opções para o campo tipo_baixa
    BAIXA_NAO_REALIZADA = 0
    BAIXA_REMARCADO = 10
    BAIXA_ENCAMINHADO = 20
    BAIXA_NEGADO = 30

    LISTA_BAIXA = (
        (BAIXA_NAO_REALIZADA, 'Não Realizada'),
        (BAIXA_REMARCADO, 'Retorno Marcado'),
        (BAIXA_ENCAMINHADO, 'Encaminhamento Marcado'),
        (BAIXA_NEGADO, 'Atendimento Negado'),
    )
    # define um relacionamento de um-para-um com a classe Processo do módulo core.models
    processo = models.OneToOneField(
        to='core.Processo',
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING,
        related_name='indeferimento'
    )
    # define um relacionamento de chave estrangeira com a classe Defensor do módulo atendimento
    atendimento = models.ForeignKey(
        to='atendimento.Defensor',
        blank=False,
        null=False,
        on_delete=models.DO_NOTHING,
        related_name='indeferimentos'
    )

    # Parte 'Ativa' se gerar um processo
    pessoa = models.ForeignKey(
        to='assistido.PessoaAssistida',
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING,
        related_name='indeferimentos'
    )
    # relacionamento de chave estrangeira com a classe Defensor do módulo defensor
    defensor = models.ForeignKey(
        to='defensor.Defensor',
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING,
        related_name='indeferimentos'
    )
    # relacionamento de chave estrangeira com a classe Defensoria do módulo contrib
    defensoria = models.ForeignKey(
        to='contrib.Defensoria',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name='indeferimentos'
    )
    # define campos de texto para medida_pretendida e justificativa
    medida_pretendida = models.TextField(blank=True, null=True)
    justificativa = models.TextField(blank=True, null=True)

    resultado = models.SmallIntegerField(
        choices=LISTA_RESULTADO,
        blank=True,
        null=True,
        default=RESULTADO_NAO_AVALIADO
    )

    tipo_baixa = models.SmallIntegerField(
        choices=LISTA_BAIXA,
        blank=True,
        null=True,
        default=BAIXA_NAO_REALIZADA
    )

    objects = managers.IndeferimentoManager()

    # retorna uma representação em string do objeto Indeferimento
    def __str__(self):
        return '{} - {} x {}'.format(self.atendimento, self.pessoa, self.defensor)

    # gera e retorna o número do processo com base no ano de cadastro e no total de processos de indeferimento
    def gerar_numero_processo(self):

        ano = self.processo.cadastrado_em.year
        total = CoreProcesso.objects.tipo_indeferimento().filter(
            cadastrado_em__year=ano,
            id__lte=self.processo.id
        ).count()

        self.processo.numero = '{:03d}/{}'.format(total, ano)
        self.processo.save()

        return self.processo.numero
    
    # verifica se é possível registrar um recurso com base nas condições do processo e classe
    @property
    def pode_recorrer(self):
        pode_recorrer = False

        if self.processo.classe.tipo in [CoreClasse.TIPO_NEGACAO, CoreClasse.TIPO_NEGACAO_HIPOSSUFICIENCIA]:
            if self.processo.situacao == CoreProcesso.SITUACAO_PETICIONAMENTO and \
                    self.processo.classe.indeferimento_pode_registrar_recurso == CoreClasse.INDEFERIMENTO_REGISTRAR_RECURSO_NO_INICIO:  # noqa: E501
                pode_recorrer = True
            elif self.processo.situacao == CoreProcesso.SITUACAO_MOVIMENTO and \
                    self.processo.classe.indeferimento_pode_registrar_recurso == CoreClasse.INDEFERIMENTO_REGISTRAR_RECURSO_NO_MEIO:  # noqa: E501
                pode_recorrer = True

        return pode_recorrer

    # retorna as decisões ativas do processo em ordem crescente
    @property
    def decisoes(self):
        return self.processo.eventos.ativos().tipo_decisao().ordem_crescente().filter(
            em_edicao=False
        )
    
    # retorna a última decisão do processo
    @property
    def decisao(self):
        return self.decisoes.last()

    # retorna o último documento relacionado à última decisão do processo
    @property
    def ultima_decisao_documento(self):
        return self.processo.documentos.filter(evento=self.decisao).last()

    # verifica se existem decisões no processo
    @property
    def possui_decisao(self):
        return self.decisoes.exists()

    # retorna o primeiro recurso ativo do processo
    @property
    def recurso(self):
        return self.processo.eventos.ativos().tipo_recurso().filter(
            em_edicao=False,
        ).first()

    # verifica se existem recursos no processo
    @property
    def possui_recurso(self):
        return self.processo.eventos.ativos().tipo_recurso().filter(
            em_edicao=False,
        ).exists()

    # retorna o primeiro evento de baixa ativo do processo
    @property
    def baixa(self):
        return self.processo.eventos.ativos().tipo_baixa().first()

    # verifica se o processo foi baixado
    @property
    def baixado(self):
        return not self.tipo_baixa == self.BAIXA_NAO_REALIZADA

    def get_cor_resultado(self):
        if self.resultado == self.RESULTADO_DEFERIDO:
            return 'success'
        elif self.resultado == self.RESULTADO_INDEFERIDO:
            return 'important'
        elif self.resultado == self.RESULTADO_RECEBIDO:
            return 'info'
        else:
            return ''
