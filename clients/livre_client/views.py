# -*- coding: utf-8 -*-

# Biblioteca Padrao

# Bibliotecas de terceiros
import base64
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404

# Bibliotecas locais
from clients.livre_client.services import APIRelatorio


@login_required
def consultar_relatorio(request, processo_numero: str, relatorio_tipo: int) -> HttpResponse:

    api = APIRelatorio(request)
    sucesso, resposta = api.consultar(processo_numero, relatorio_tipo)

    if not sucesso:
        raise Http404

    # Responde com o conteúdo do documento
    if resposta['return']:
        conteudo = base64.decodebytes(resposta['return']['conteudo'].encode())
        response = HttpResponse(content=conteudo)
        response['Content-Type'] = resposta['return']['mimeType']
    else:
        response = HttpResponse('Conteúdo não disponível para visualização!')

    return response
