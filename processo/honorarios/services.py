# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.core.cache import cache

# Modulos locais
from .models import Honorario, AlertaProcessoMovimento


class HonorarioService(object):
    # classe que contém funções para manipular e gerar cache de objetos Honorario

    def gerar_cache_honorarios_ativos(self, cache_name='honorarios.processosalertas:'):
        # gera o cache dos honorários ativos, associando os IDs de processos e recursos vinculados
        cache_key = cache_name
        cache.delete(cache_name)
        # filtra os honorários ativos e não baixados, obtendo apenas os IDs dos processos e recursos vinculados
        honorarios = Honorario.objects.filter(
            possivel=True,
            ativo=True,
            baixado=False
        ).values(
            'id',
            'fase__processo__id',
            'recurso_vinculado__id',
        )

        arr = {}
        for honorario_processo in honorarios:
            arr[honorario_processo['fase__processo__id']] = {
                'honorario_id': honorario_processo['id'],
                'processo_id': honorario_processo['fase__processo__id'],
                'recurso_id': honorario_processo['recurso_vinculado__id'],
            }
            if honorario_processo['recurso_vinculado__id']:
                arr[honorario_processo['recurso_vinculado__id']] = {
                    'honorario_id': honorario_processo['id'],
                    'processo_id': honorario_processo['fase__processo__id'],
                    'recurso_id': honorario_processo['recurso_vinculado__id'],
                }

        cache_data = arr
        cache.set(cache_key, cache_data)

    def valida_processo_id_cache(self, processo_id, cache_name='honorarios.processosalertas:'):
        # verifica se o ID de um processo existe no cache de honorários ativos

        cache_data = cache.get(cache_name)

        if not cache_data:  # se não há dados no cache, gera o cache novamente
            self.gerar_cache_honorarios_ativos(cache_name)
            cache_data = cache.get(cache_name)

        processo_id = int(processo_id)
        if cache_data and processo_id in cache_data:
            return cache_data[processo_id]['honorario_id']

        return None

    def cria_alerta_honorario(self, honorario_id):
        # cria um alerta de movimentação de honorário, baseado em informações do objeto Honorario
        honorario = Honorario.objects.get(id=honorario_id)
        if honorario.recurso_finalizado:
            mensagem = 'Processo {} ou recurso {} movimentados'.format(
                honorario.fase.processo.numero_inteiro,
                honorario.recurso_vinculado.numero_inteiro if honorario.recurso_vinculado else ''
            )
        else:
            mensagem = 'Nova movimentação no processo {} identificada'.format(
                honorario.fase.processo.numero_inteiro
            )
        alerta = AlertaProcessoMovimento(honorario=honorario, mensagem=mensagem)
        alerta.save()
