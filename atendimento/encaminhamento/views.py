# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import json as simplejson

# Bibliotecas de terceiros
import reversion
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView

# Solar
from atendimento.atendimento.models import (
    Atendimento,
    Cronometro,
    Encaminhamento,
    Procedimento
)
from contrib.models import Bairro, Endereco, Estado, Util
from contrib.forms import EnderecoForm, TelefoneForm
from luna_chatbot_client.tasks import chatbot_notificar_requerente_encaminhamento_externo

# Modulos locais
from .forms import EncaminhamentoForm


@login_required
@permission_required('atendimento.add_encaminhamento')
def encaminhar(request, ligacao_numero, encaminhamento_id):
    ligacao = Atendimento.objects.get(numero=ligacao_numero)
    procedimento, msg = Procedimento.objects.get_or_create(ligacao=ligacao, encaminhamento_id=encaminhamento_id,
                                                           tipo=Procedimento.TIPO_ENCAMINHAMENTO)

    messages.success(request, u'Procedimento cadastrado: Encaminhamento')

    # Notifica assistido via chatbot Luna
    chatbot_notificar_requerente_encaminhamento_externo.apply_async(
        kwargs={'numero': ligacao.numero, 'encaminhamento_id': encaminhamento_id},
        queue='sobdemanda'
    )

    if request.GET.get('next'):
        return redirect(request.GET.get('next')) 
    else:
        return redirect('precadastro_continuar', ligacao.numero)


class IndexView(ListView):
    queryset = Encaminhamento.objects.filter(ativo=True)
    paginate_by = 50
    template_name = 'atendimento/encaminhamento/index.html'

    def get_context_data(self, **kwargs):

        context = super(IndexView, self).get_context_data(**kwargs)

        pode_cadastrar = self.request.user.has_perm(perm='atendimento.add_encaminhamento') 
        pode_editar = self.request.user.has_perm(perm='atendimento.change_encaminhamento') 

        # Atualiza variáveis de contexto (visíveis no template)
        context.update({
            'form': EncaminhamentoForm(self.request.GET),
            'pode_cadastrar': pode_cadastrar,
            'pode_editar': pode_editar,
        })

        return context

    def get_queryset(self):

        queryset = super(IndexView, self).get_queryset()
        q = Q()

        form = EncaminhamentoForm(self.request.GET)

        if form.is_valid():

            data = form.cleaned_data

            # Filtro por nome
            if data.get('nome'):
                q &= Q(nome__icontains=data.get('nome'))

        return queryset.filter(q)


class LigacaoView(IndexView):
    def get_context_data(self, **kwargs):

        context = super(LigacaoView, self).get_context_data(**kwargs)

        ligacao = Atendimento.objects.get(numero=self.kwargs.get('ligacao_numero'))
        cronometro, novo = Cronometro.objects.get_or_create(atendimento=ligacao)

        # Atualiza variáveis de contexto (visíveis no template)
        context.update({
            'ligacao': ligacao,
            'cronometro': cronometro,
            'next': self.request.GET.get('next', ''),
            'pode_cadastrar': False,
            'pode_editar': False,
        })

        return context


@login_required
@permission_required('atendimento.add_encaminhamento')
def cadastrar(request):
    """Exibe pagina de cadastro de órgão para encaminhamento"""

    form = EncaminhamentoForm()
    form_endereco = EnderecoForm(
        prefix='endereco',
        initial={'estado': Estado.objects.get(uf__iexact=settings.SIGLA_UF)}
    )

    form_telefone = TelefoneForm(prefix='telefone')

    return render(request=request, template_name="atendimento/encaminhamento/cadastrar.html", context=locals())


@login_required
@permission_required('atendimento.change_encaminhamento')
def editar(request, encaminhamento_id):
    """Exibe pagina para alteracao de dados de órgão para encaminhamento"""

    orgao = Encaminhamento.objects.get(id=encaminhamento_id)

    if orgao.endereco:
        estado = orgao.endereco.municipio.estado_id
    else:
        estado = Estado.objects.get(uf__iexact=settings.SIGLA_UF)

    form = EncaminhamentoForm(instance=orgao)
    form_endereco = EnderecoForm(instance=orgao.endereco, prefix='endereco', initial={'estado': estado})
    form_telefone = TelefoneForm(instance=orgao.telefone, prefix='telefone')

    return render(request=request, template_name="atendimento/encaminhamento/cadastrar.html", context=locals())


@login_required
@permission_required('atendimento.change_encaminhamento')
@reversion.create_revision(atomic=False)
def salvar(request):
    """Salva dados de órgão novo ou alteracoes em existente"""

    if request.method == 'POST':

        data = request.POST.copy()
        orgao_id = request.POST.get('orgao-id')

        # Recupera bairro informado
        try:
            bairro, msg = Bairro.objects.get_or_create(
                municipio_id=data['endereco-municipio'],
                nome=data['endereco-bairro_nome']
            )
        except Bairro.MultipleObjectsReturned:
            bairro = Bairro.objects.filter(
                municipio_id=data['endereco-municipio'],
                nome=data['endereco-bairro_nome']
            ).first()

        data['endereco-bairro'] = bairro.id

        try:
            orgao = Encaminhamento.objects.get(id=orgao_id)
        except Exception:
            orgao = Encaminhamento()
            orgao.endereco = Endereco()

        form = EncaminhamentoForm(data, instance=orgao)
        form_endereco = EnderecoForm(data, instance=orgao.endereco, prefix='endereco',
                                     initial={'estado': data['endereco-estado']})
        form_telefone = TelefoneForm(data, instance=orgao.telefone, prefix='telefone')

        if form.is_valid() and form_endereco.is_valid() and form_telefone.is_valid():

            orgao = form.save(commit=False)
            orgao.endereco = form_endereco.save()
            orgao.telefone = form_telefone.save()

            novo = (orgao.id is None)
            orgao.save()

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_save(request.user, orgao, novo))

            messages.success(request, u'Órgão salvo com sucesso!')

            return redirect('encaminhamento_index')

    return render(request=request, template_name="atendimento/encaminhamento/cadastrar.html", context=locals())
