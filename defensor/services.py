# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import json as simplejson
from datetime import datetime
from urllib.request import urlopen

# Bibliotecas de terceiros
from django.conf import settings

# Solar
from contrib.models import Defensoria, Util

# Modulos locais
from .models import Atuacao, Defensor


def desativa_atuacao():
    atuacoes_encerradas = Atuacao.objects.filter(
        data_final__lt=datetime.now(),
        ativo=True
    )

    for atuacao in atuacoes_encerradas:
        atuacao.ativo = False
        atuacao.save()

    return atuacoes_encerradas.exists()


def consultar_api_plantao():
    FORMATO_DATA = '%Y-%m-%dT%H:%M:%S'

    # Recupera informacoes do sistema de plantao
    url = settings.PLANTAO_API_URL
    response = urlopen(url)
    eventos = []

    try:
        eventos = simplejson.loads(response.read())
    except ValueError:
        pass

    for evento in eventos:

        for plantao in evento['plantao_lotacoes']:

            lotacao = plantao['plantao_local']

            # Obtém datas dos plantões
            data_inicial = None
            data_final = None
            data_atualizacao = None

            if 'periodo_inicio' in lotacao:
                data_inicial = datetime.strptime(lotacao['periodo_inicio'][:19], FORMATO_DATA)

            if 'periodo_fim' in lotacao:
                data_final = datetime.strptime(lotacao['periodo_fim'][:19], FORMATO_DATA)

            if 'updated_at' in lotacao:
                data_atualizacao = datetime.strptime(lotacao['updated_at'][:19], FORMATO_DATA)

            # Verifica se plantão ainda é válido
            if data_final and data_final >= datetime.now():

                defensor = None
                defensoria = None

                # Obtém dados do defensor
                if 'servidor' in lotacao:
                    defensor = Defensor.objects.filter(
                        servidor__cpf=lotacao['servidor']['cpf']
                    ).first()

                # Obtém dados da defensoria
                if 'lotacao' in lotacao:
                    defensorias = Defensoria.objects.filter(
                        comarca__codigo=lotacao['lotacao']['codigo'],
                        nucleo__plantao=True,
                        ativo=True
                    )

                    atuacao = lotacao.get('atuacao', '').strip()

                    # Se informado, filtra defensoria por atuação
                    if len(atuacao) > 0:
                        defensorias = defensorias.filter(
                            atuacao=Util.normalize(atuacao)
                        )

                    defensoria = defensorias.first()

                # Verifica se encontrou defensor e defensoria
                if defensor and defensoria:

                    if defensor.eh_defensor:
                        tipo = Atuacao.TIPO_ACUMULACAO
                    else:
                        tipo = Atuacao.TIPO_LOTACAO

                    # Verifica se existe atuação vinculada ao evento de plantão
                    existe_plantao_local = Atuacao.objects.filter(
                        codigo_plantao=evento['id'],
                        codigo_plantao_local=lotacao['id']
                    ).exists()

                    # Se existe, atualiza informações
                    if existe_plantao_local:
                        Atuacao.objects.update_or_create(
                            codigo_plantao=evento['id'],
                            codigo_plantao_local=lotacao['id'],
                            defaults={
                                'defensor': defensor,
                                'defensoria': defensoria,
                                'tipo': tipo,
                                'data_inicial': data_inicial,
                                'data_final': data_final,
                                'data_atualizacao': data_atualizacao,
                                'pode_assinar_ged': defensor.eh_defensor,
                                'ativo': True
                            })
                    # Senão, cria/atualiza a partir dos dados do defensor/defensoria/período
                    else:
                        Atuacao.objects.update_or_create(
                            defensor=defensor,
                            defensoria=defensoria,
                            data_inicial=data_inicial,
                            data_final=data_final,
                            defaults={
                                'codigo_plantao': evento['id'],
                                'codigo_plantao_local': lotacao['id'],
                                'tipo': tipo,
                                'data_inicial': data_inicial,
                                'data_final': data_final,
                                'data_atualizacao': data_atualizacao,
                                'pode_assinar_ged': defensor.eh_defensor,
                                'ativo': True
                            }
                        )
