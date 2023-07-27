# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging

# Bibliotecas de terceiros
import reversion
from constance import config
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render


# Solar
from contrib.forms import EnderecoForm, TelefoneForm
from contrib.models import Bairro, Endereco, Estado, Util, Municipio
from nucleo.nucleo.models import Resposta
from nucleo.nadep.forms import EstabelecimentoPenalForm
from nucleo.nadep.models import EstabelecimentoPenal


logger = logging.getLogger(__name__)


@login_required
@permission_required('nadep.view_estabelecimentopenal')
def buscar_estabelecimento(request):
    """Realiza uma busca por estabelecimentos penais com base no nome ou municipio e retorna uma lista"""

    if not request.GET.get('page'):
        request.session['filtro_estabelecimento'] = None

    if request.POST:
        filtro = request.POST.get('q', '')
        request.session['filtro_estabelecimento'] = filtro
        page = ''
    else:
        page = request.GET.get('page')
        if request.session.get('filtro_estabelecimento'):
            filtro = request.session.get('filtro_estabelecimento')
        else:
            filtro = ''

    estabelecimentos_list = EstabelecimentoPenal.objects.select_related(
        'tipo',
        'endereco__municipio__estado'
    ).filter(
        (
            Q(nome__icontains=filtro) |
            Q(endereco__municipio__nome__icontains=filtro)
        ) &
        Q(ativo=True)
    ).order_by('-inspecionado_pela_dpe', 'endereco__municipio__nome', 'nome')

    # Obtém dados da última inspeção realizada em cada estabelecimento penal
    inspecoes = []
    if config.ID_PERGUNTA_FORMULARIO_INSPECAO_LIVRE:
        inspecoes = Resposta.objects.filter(
            pergunta=config.ID_PERGUNTA_FORMULARIO_INSPECAO_LIVRE
        ).distinct(
            'texto'
        ).order_by(
            'texto',
            '-evento__data_referencia'
        )

    paginacao = Paginator(estabelecimentos_list, 9)

    try:
        estabelecimentos = paginacao.page(page)
    except PageNotAnInteger:
        estabelecimentos = paginacao.page(1)
    except EmptyPage:
        estabelecimentos = paginacao.page(paginacao.num_pages)

    return render(request=request, template_name="nadep/buscar_estabelecimento.html", context=locals())


@login_required
def buscar_estabelecimento_json(request, municipio_id=None):

    arr = []
    lst = EstabelecimentoPenal.objects.filter(ativo=True).order_by('endereco__municipio__nome', 'nome')

    if municipio_id:
        lst = lst.filter(endereco__municipio_id=municipio_id)

    for i in lst:
        arr.append({'id': i.id, 'nome': i.nome, 'municipio': i.endereco.municipio.nome})

    return JsonResponse(arr, safe=False)


@login_required
def buscar_municipio_json(request):

    arr = []
    lst = Municipio.objects.filter(id__in=EstabelecimentoPenal.objects.values('endereco__municipio_id'))

    for i in lst:
        arr.append({'id': i.id, 'nome': i.nome})

    return JsonResponse(arr, safe=False)


@login_required
@permission_required('nadep.add_estabelecimentopenal')
def cadastrar_estabelecimento(request):
    """Exibe pagina de cadastro de estabelecimento penal"""

    request.session['estabelecimento_id'] = None

    form = EstabelecimentoPenalForm()
    form_endereco = EnderecoForm(
        prefix='endereco',
        initial={'estado': Estado.objects.get(uf__iexact=settings.SIGLA_UF)}
    )
    form_telefone = TelefoneForm(prefix='telefone')

    return render(request=request, template_name="nadep/cadastrar_estabelecimento.html", context=locals())


@login_required
@permission_required('nadep.change_estabelecimentopenal')
def editar_estabelecimento(request, estabelecimento_id):
    """Exibe pagina para alteracao de dados de estabelecimento penal"""

    request.session['estabelecimento_id'] = estabelecimento_id
    estabelecimento = EstabelecimentoPenal.objects.get(id=estabelecimento_id)

    form = EstabelecimentoPenalForm(instance=estabelecimento)
    form_endereco = EnderecoForm(instance=estabelecimento.endereco, prefix='endereco',
                                 initial={'estado': estabelecimento.endereco.municipio.estado.id})
    form_telefone = TelefoneForm(instance=estabelecimento.telefone, prefix='telefone')

    return render(request=request, template_name="nadep/cadastrar_estabelecimento.html", context=locals())


@login_required
@reversion.create_revision(atomic=False)
def salvar_estabelecimento(request):
    """Salva dados de estabelecimento penal novo ou alteracoes em existente"""

    if request.method == 'POST':

        data = request.POST.copy()

        # Recupera bairro informado
        try:
            bairro, msg = Bairro.objects.get_or_create(
                municipio_id=data['endereco-municipio'],
                nome__iexact=data['endereco-bairro_nome'],
                desativado_em=None,
                defaults={
                    # necessário por ter usado uma func no get_or_create para esse field
                    'nome': data['endereco-bairro_nome']
                }
            )
        except Bairro.MultipleObjectsReturned:
            bairro = Bairro.objects.filter(
                municipio_id=data['endereco-municipio'],
                nome__iexact=data['endereco-bairro_nome'],
                desativado_em=None
            ).first()

        data['endereco-bairro'] = bairro.id

        try:
            estabelecimento = EstabelecimentoPenal.objects.get(id=request.session.get('estabelecimento_id'))
        except Exception:
            estabelecimento = EstabelecimentoPenal()
            estabelecimento.endereco = Endereco()

        form = EstabelecimentoPenalForm(data, instance=estabelecimento)
        form_endereco = EnderecoForm(data, instance=estabelecimento.endereco, prefix='endereco',
                                     initial={'estado': data['endereco-estado']})
        form_telefone = TelefoneForm(data, instance=estabelecimento.telefone, prefix='telefone')

        if form.is_valid() and form_endereco.is_valid() and form_telefone.is_valid():
            estabelecimento = form.save(commit=False)
            estabelecimento.endereco = form_endereco.save()
            estabelecimento.telefone = form_telefone.save()

            novo = (estabelecimento.id is None)
            estabelecimento.save()

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_save(request.user, estabelecimento, novo))

            messages.success(request, u'Estabelecimento penal salvo com sucesso!')
            return redirect('nadep_buscar_estabelecimento')

    return render(request=request, template_name="nadep/cadastrar_estabelecimento.html", context=locals())


@login_required
@reversion.create_revision(atomic=False)
@permission_required('nadep.delete_estabelecimentopenal')
def excluir_estabelecimento(request, estabelecimento_id):
    """Exclui estabelecimento penal informado"""

    estabelecimento = get_object_or_404(EstabelecimentoPenal, id=estabelecimento_id, ativo=True)
    estabelecimento.ativo = False
    estabelecimento.save()

    reversion.set_user(request.user)
    reversion.set_comment(Util.get_comment_delete(request.user, estabelecimento))

    messages.success(request, u'Estabelecimento penal excluído')

    return redirect('nadep_buscar_estabelecimento')
