# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from atendimento.atendimento.models import Documento
from processo.processo.models import Manifestacao

# Modulos locais
from .models import Movimento, Honorario
from .services import HonorarioService


# função acionada após a criação ou atualização de um objeto Movimento
@receiver(post_save, sender=Movimento)
def alterar_valores_processo_honorario(sender, instance, **kwargs):
    if instance.tipo == Movimento.TIPO_AGUARDANDO_PET:
        # atualiza o valor estimado no objeto honorário associado ao movimento
        instance.honorario.valor_estimado = instance.valor_estimado
        instance.honorario.save()

    if instance.tipo == Movimento.TIPO_BAIXA:
        # atualiza o valor efetivo e marca o honorário como "baixado" no objeto honorário associado ao movimento
        instance.honorario.valor_efetivo = instance.valor_efetivo
        instance.honorario.baixado = True
        instance.honorario.save()


# função acionada após a criação ou atualização de um objeto Honorario
@receiver(post_save, sender=Honorario)
def gerar_cache_honorario(sender, instance, **kwargs):
    # se o honorário é possível, está ativo e não está baixado
    if instance.possivel and instance.ativo and not instance.baixado:
        # chama o serviço "HonorarioService" para gerar o cache dos honorários ativos
        cache_service = HonorarioService()
        cache_service.gerar_cache_honorarios_ativos()


# função acionada após a criação ou atualização de um objeto Documento
@receiver(post_save, sender=Documento)
def movimentar_honorario_ao_criar_ged(sender, instance=None, created=False, **kwargs):
    if instance.atendimento and instance.atendimento.at_defensor:
        # pega o primeiro honorário associado ao defensor do atendimento
        honorario = instance.atendimento.at_defensor.honorarios.first()
        if honorario and not honorario.has_peticao and instance.documento_online and created:
            Movimento.objects.create(
                honorario=honorario,
                tipo=Movimento.TIPO_PETICAO,
                anotacao='(Movimentado automaticamente. GED nº {})'.format(
                    instance.documento_online.identificador_versao
                ),
                cadastrado_por=instance.cadastrado_por
            )


# função acionada após a criação ou atualização de um objeto Manifestacao
@receiver(post_save, sender=Manifestacao)
def movimentar_honorario_ao_salvar_peticionamento(sender, instance=None, created=False, **kwargs):
    # pega o primeiro honorário associado ao atendimento da parte da manifestação
    honorario = instance.parte.atendimento.honorarios.first()
    if honorario:
        if not honorario.has_encaminhado_def:
            Movimento.objects.create(
                honorario=honorario,
                tipo=Movimento.TIPO_ENCAMINHADO_DEF,
                anotacao='(Movimentado automaticamente. Manifestação nº {})'.format(instance.id),
                defensor=instance.defensor.servidor.defensor,
                defensoria=instance.defensoria,
                cadastrado_por=instance.cadastrado_por.servidor
            )
        if not honorario.has_protocolo and instance.situacao == Manifestacao.SITUACAO_PROTOCOLADO:
            Movimento.objects.create(
                honorario=honorario,
                tipo=Movimento.TIPO_PROTOCOLO,
                anotacao='(Movimentado automaticamente. Protocolo nº {})'.format(instance.protocolo_resposta),
                defensor=instance.defensor.servidor.defensor,
                defensoria=instance.defensoria,
                cadastrado_por=instance.enviado_por.servidor
            )
