# -*- coding: utf-8 -*-
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.dispatch.dispatcher import receiver
from datetime import datetime

from .models import Movimento, Procedimento


@receiver(pre_save, sender=Procedimento)  # funcao de pre-salvamento para populacao de dados do procedimento
def pre_save_popula_dados_procedimento(sender, instance, **kwargs):
    # verifica se não há data de ultima movimentacao definida para o procedimento
    if not instance.data_ultima_movimentacao:
        # define a data de ultima movimentacao
        instance.data_ultima_movimentacao = datetime.now()


@receiver(post_save, sender=Movimento)  # funcao de pós-salvamento para alterar a data de última movimentacao
def post_save_altera_data_ultima_movimentacao_procedimento(sender, instance, **kwargs):
    # obtem a data de última movimentacao do procedimento relacionado ao movimento
    procedimento_data = instance.procedimento.data_ultima_movimentacao
    if not procedimento_data or procedimento_data < instance.data_cadastro:
        instance.procedimento.data_ultima_movimentacao = instance.data_cadastro
        instance.procedimento.save()


@receiver(pre_save, sender=Movimento)  # funcao de pre-salvamento para alterar o número do procedimento
def pre_save_altera_numero_procedimento_ao_lancar_movimento_tipo_instauracao(sender, instance, **kwargs):
    if instance.tipo.instauracao and instance.eh_precadastro is False:
        if instance.procedimento.numero.startswith(settings.PROCEDIMENTO_SIGLA_PROCEDIMENTO):
            # substitui a sigla do procedimento pela sigla do PROPAC no número do procedimento
            novo_numero = instance.procedimento.numero
            instance.procedimento.tipo = Procedimento.TIPO_PROPAC
            instance.procedimento.numero = novo_numero.replace(settings.PROCEDIMENTO_SIGLA_PROCEDIMENTO,
                                                               settings.PROCEDIMENTO_SIGLA_PROPAC)
            instance.procedimento.save()

        # verifica se há movimentos ativos sem instauracao no procedimento
        if instance.procedimento.movimentos_ativos_sem_instauracao().exists():
            instance.volume = 1
            instance.ordem_volume = 1
            for movimento in instance.procedimento.movimentos_ativos_sem_instauracao():
                if movimento.ordem_volume + 1 > movimento.maximo_movimentos_por_volume():
                    movimento.ordem_volume = 1
                    movimento.volume = movimento.volume + 1
                else:
                    movimento.ordem_volume = movimento.ordem_volume + 1
                movimento.save()


@receiver(post_save, sender=Procedimento)  # funcao de pós-salvamento para gerar o número do procedimento
def post_save_post_save_gerar_numero_procedimento(sender, instance, **kwargs):
    if instance.numero is None or instance.numero == '':
        ano_corrente = datetime.now().year
        posicao = Procedimento.objects.filter(data_cadastro__year=ano_corrente).count()
        if instance.tipo == Procedimento.TIPO_PROCEDIMENTO:
            sigla_procedimento = settings.PROCEDIMENTO_SIGLA_PROCEDIMENTO
        else:
            sigla_procedimento = settings.PROCEDIMENTO_SIGLA_PROPAC
        instance.numero = '{0}{1:06d}/{2}'.format(sigla_procedimento, posicao, ano_corrente)
        instance.save()
