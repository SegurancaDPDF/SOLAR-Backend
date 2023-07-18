# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import json
import datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from contrib.models import Servidor
from .models import Termo, TermoResposta

# Função para criar uma consulta para filtrar os termos disponíveis


@login_required
def get_termo_json(request, servidor_id):

    hoje = datetime.datetime.today()

    q = Q(desativado_em=None)
    q &= Q(Q(data_inicio__lte=hoje) | Q(data_inicio=None))
    q &= Q(Q(data_finalizacao__gte=hoje) | Q(data_finalizacao=None))
    q &= Q(
            ~Q(servidores__pk=servidor_id) |
            (
                Q(servidores__pk=servidor_id) &
                ~Q(termoresposta__desativado_em=None)
            )
        )

    termos = Termo.objects.filter(q).distinct().values()
    return JsonResponse(list(termos), safe=False)

# Função para verifica se a resposta já existe antes de criar uma nova


@login_required
def post_termo_json(request):
    sucesso = True
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            termo = data.get('id', None)
            servidor = data.get('servidor_id', None)

            if servidor and termo:

                servidor = Servidor.objects.get(pk=servidor)
                termo = Termo.objects.get(pk=termo)

                if not TermoResposta.objects.filter(servidor=servidor, termo=termo).exists():
                    TermoResposta.objects.create(
                        termo=termo,
                        servidor=servidor,
                        aceite=data.get('aceito', False),
                        titulo_termo=data.get('titulo'),
                        descricao_termo=data.get('descricao')
                    )
        except Exception:
            sucesso = False

    return JsonResponse(sucesso, safe=False)
