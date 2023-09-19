# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging
from datetime import timedelta

# Bibliotecas de terceiros
from django.core.management.base import BaseCommand

from freezegun import freeze_time

# Modulos locais
from ...models import Fase, FaseTipo, Manifestacao

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Associa tabela manifestação com a tabela fases processuais"

    def handle(self, *args, **options):
        WARNING = '\033[93m'
        ENDC = '\033[0m'

        erros = 0

        # Procura por todas manifestações protocoladas sem vínculo a uma fase processual
        manifestacoes = Manifestacao.objects.ativos().filter(
            situacao=Manifestacao.SITUACAO_PROTOCOLADO,
            respondido_em__isnull=False,
            fase=None
        ).order_by('id')

        for manifestacao in manifestacoes:

            # Verifica se já existe uma fase protocolada no mesmo momento da manifestação (margem de erro: 1 minuto)
            fase = manifestacao.parte.processo.fases.filter(
                manifestacao__isnull=True,
                data_protocolo__range=[
                    manifestacao.respondido_em - timedelta(seconds=60),
                    manifestacao.respondido_em + timedelta(seconds=60)
                ],
                ativo=True
            ).first()

            # Se não existe fase protocolada, cria uma nova
            if not fase:

                # Procura por tipo correspondente
                tipo_fase = FaseTipo.objects.filter(
                    tipos_de_evento__codigo_mni=manifestacao.tipo_evento,
                    tipos_de_evento__sistema_webservice__nome=manifestacao.sistema_webservice
                ).first()

                # Se encontrou tipo correspondente, cria nova fase processual
                if tipo_fase:
                    with freeze_time(manifestacao.cadastrado_em):
                        fase = Fase.objects.create(
                            tipo=tipo_fase,
                            processo=manifestacao.parte.processo,
                            parte=manifestacao.parte,
                            defensoria=manifestacao.defensoria,
                            defensor_cadastro=manifestacao.defensor.servidor.defensor if manifestacao.defensor else None,  # noqa: E501
                            data_protocolo=manifestacao.respondido_em,
                            cadastrado_por=manifestacao.cadastrado_por.servidor,
                            automatico=True
                        )

            # Se criou/encontrou fase processual, vincula à manifestação
            if fase:
                manifestacao.fase = fase
                manifestacao.save()
                print(u'Manifestação {} vinculada à fase processual {}'.format(manifestacao.id, fase.id))
            # Se não encontrou, exibe mensagem de erro
            else:

                erros += 1

                if manifestacao.tipo_evento is None:
                    print(WARNING + u'Erro ao criar Fase para Manifestação {}: O campo "Tipo Evento" não foi preenchido!'.format(  # noqa: E501
                        manifestacao.id
                    ) + ENDC)
                else:
                    print(WARNING + u'Erro ao criar Fase para Manifestação {}: O Tipo Evento {} não está associado a um tipo de fase!'.format(  # noqa: E501
                        manifestacao.id, manifestacao.tipo_evento
                    ) + ENDC)

        if erros:
            print(WARNING + u'Esse script encontrou {} erro(s). Corrija-os e execute este script novamente!'.format(erros) + ENDC)  # noqa: E501
        else:
            print(u'Concluído!')
