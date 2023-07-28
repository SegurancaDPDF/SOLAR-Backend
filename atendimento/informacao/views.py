# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import json as simplejson

# Bibliotecas de terceiros
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import redirect, render


# Solar
from atendimento.atendimento.models import (
    Atendimento,
    Cronometro,
    Informacao,
    Procedimento
)


@login_required
@permission_required('atendimento.view_informacao')
def buscar(request):
    if request.method == 'POST':

        data = simplejson.loads(request.body)
        arr = []

        if data['informacao'] != '':
            itens = Informacao.objects.filter(titulo__icontains=data['informacao'], ativo=True)

            for item in itens:
                arr.append({'id': item.id, 'titulo': item.titulo, 'texto': item.texto})

        return JsonResponse(arr, safe=False)


@login_required
@permission_required('atendimento.view_informacao')
def index(request, ligacao_numero):
    ligacao = Atendimento.objects.get(id=request.session.get('ligacao_id'))
    cronometro = Cronometro.objects.get(atendimento_id=ligacao.id).duracao

    # se parametro nao corresponde ao numero da ligacao, redireciona para link correto
    if int(ligacao.numero) != int(ligacao_numero):
        return redirect('informacao_index', ligacao.numero)

    angular = 'BuscarInformacaoModel'
    return render(request=request, template_name="atendimento/informacao/index.html", context=locals())


@login_required
@permission_required('atendimento.add_informacao')
def informar(request, informacao_id):
    ligacao = Atendimento.objects.get(id=request.session.get('ligacao_id'))
    procedimento, msg = Procedimento.objects.get_or_create(ligacao_id=ligacao.id, informacao_id=informacao_id,
                                                           tipo=Procedimento.TIPO_INFORMACAO)
    procedimento.save()

    messages.success(request, u'Procedimento cadastrado: Dúvida')

    return redirect('precadastro_continuar', ligacao.numero)
