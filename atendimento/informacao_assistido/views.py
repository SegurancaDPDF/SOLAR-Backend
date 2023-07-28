# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip
from datetime import datetime

# Biblitecas de terceiros
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render
from django.template.context import RequestContext

# Solar
from atendimento.atendimento.models import (
    Atendimento,
    InformacaoAssistido,
    Procedimento
)


@login_required
@permission_required('atendimento.view_informacao')
def index(request):
    return render("atendimento/informacao_assistido/default.html",
                  locals(),
                  context_instance=RequestContext(request))


@login_required
@permission_required('atendimento.add_informacao')
def salvar(request):
    ligacao = Atendimento.objects.get(
        id=request.session.get('ligacao_id'))  # Recupera-se o objeto Atendimento através do ID do atendimento
    data = datetime.now()  # Captura-se a data da submissão da informação
    assistido = str(ligacao.get_requerentes()[0])  # O nome do assistido qual solicitou informação
    atendente = str(request.user.servidor)  # O nome do atendente da informação do assistido
    informacao = request.POST.get("informacao", "")  # A informação submetida

    informacao_assistido, msg = InformacaoAssistido.objects.get_or_create(data=data, assistido=assistido,
                                                                          # Instanciando um objeto do tipo assistido
                                                                          atendente=atendente,
                                                                          informacao=informacao)

    informacao_assistido.save()  # Salvando a informação

    ligacao_informacao = Atendimento.objects.create(origem=ligacao, tipo=Atendimento.TIPO_INFORMACAO, ativo=True)

    procedimento, msg = Procedimento.objects.get_or_create(ligacao_id=ligacao.id,
                                                           atendente=request.user,
                                                           tipo=Procedimento.TIPO_INFORMACAO_ASSISTIDO,
                                                           attprocedimento=ligacao_informacao)
    procedimento.save()

    messages.success(request, u'Informação cadastrada: Informação')  # Popup de sucesso ao cadastrar

    return redirect('precadastro_continuar', ligacao.id)  # Redirecionamento para página do atendimento
