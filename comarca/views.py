# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
import reversion
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Case, When, Value, IntegerField, F, Q
from django.http import JsonResponse
from django.shortcuts import redirect, render


# Solar
from contrib.forms import EnderecoForm, TelefoneForm
from contrib.models import Bairro, Comarca, Endereco, Estado, Telefone, Util, Servidor
from defensor.models import Atuacao

# Modulos locais
from .forms import PredioForm
from .models import Guiche, Predio


#  define a página inicial do sistema e define informações de sessão
@login_required
def index(request, comarca_id):
    request.session['nucleo'] = None
    request.session['predio'] = None
    request.session['guiche'] = None

    if request.session.get('comarca') != comarca_id:
        request.session['comarca'] = comarca_id

    if request.GET.get('next'):
        return redirect(request.GET['next'])
    else:
        return redirect('atendimento_index')


# retorna o status de uma comarca
@login_required
def status_comarca(request):
    comarca = Comarca.objects.get(id=request.session.get('comarca'))

    atuacoes_defensores = Atuacao.objects.filter(
        defensoria__comarca=comarca,
        defensoria__nucleo=None,
        ativo=True
    ).order_by(
        'defensor__servidor__usuario__first_name'
    ).distinct(
        'defensor__servidor__usuario__first_name')

    return render(request=request, template_name="atendimento/status_comarca.html", context=locals())


# retorna uma lista de guichês de uma comarca em formato JSON
@login_required
def guiches(request):
    dados = []
    for guiche in Guiche.objects.filter(comarca=request.session.get('comarca')):
        dados.append({
            'numero': guiche.numero
        })

    return JsonResponse(dados, safe=False)


# retorna uma lista de comarcas com seus respectivos graus em formato JSON
@login_required
def listar(request):

    comarcas = Comarca.objects.ativos().annotate(
        grau=Case(
            When(
                vara__ativo=True,
                then=F('vara__grau')
                ),
            default=Value(None),
            output_field=IntegerField())
    ).order_by(
        'nome',
        'vara__grau'
    ).values(
        'id',
        'nome',
        'grau',
        'coordenadoria'
    ).distinct()

    resposta = {}

    for comarca in comarcas:

        grau = comarca.pop('grau')

        if comarca['id'] not in resposta:
            resposta[comarca['id']] = comarca
            resposta[comarca['id']]['graus'] = []

        if grau and grau not in resposta[comarca['id']]['graus']:
            resposta[comarca['id']]['graus'].append(grau)

    return JsonResponse(list(resposta.values()), safe=False)


@login_required
def buscar_predio(request):
    """Realiza uma busca por prédios com base no nome ou municipio e retorna uma lista"""

    filtro = request.GET.get('q', '')

    predios_list = Predio.objects.select_related(
        'comarca',
        'endereco__bairro',
        'endereco__municipio__estado',
        'telefone'
    ).filter(
        (
            Q(nome__icontains=filtro) |
            Q(comarca__nome__icontains=filtro)
        ) &
        Q(ativo=True)
    ).order_by('comarca__nome', 'nome')

    paginacao = Paginator(predios_list, 10)
    page = request.GET.get('page')

    try:
        predios = paginacao.page(page)
    except PageNotAnInteger:
        predios = paginacao.page(1)
    except EmptyPage:
        predios = paginacao.page(paginacao.num_pages)

    return render(request=request, template_name="comarca/buscar_predio.html", context=locals())


@login_required
@permission_required('comarca.add_predio')
def cadastrar_predio(request):
    """Exibe pagina de cadastro de prédio"""

    form = PredioForm()
    form_endereco = EnderecoForm(
        prefix='endereco',
        initial={'estado': Estado.objects.get(uf__iexact=settings.SIGLA_UF)}
    )

    form_telefone = TelefoneForm(prefix='telefone')

    return render(request=request, template_name="comarca/cadastrar_predio.html", context=locals())


@login_required
@permission_required('comarca.change_predio')
def editar_predio(request, predio_id):
    """Exibe pagina para alteracao de dados de prédio"""

    predio = Predio.objects.get(id=predio_id)

    if predio.endereco:
        estado = predio.endereco.municipio.estado_id
    else:
        estado = Estado.objects.get(uf__iexact=settings.SIGLA_UF)

    form = PredioForm(instance=predio)
    form_endereco = EnderecoForm(instance=predio.endereco, prefix='endereco', initial={'estado': estado})
    form_telefone = TelefoneForm(instance=predio.telefone, prefix='telefone')

    return render(request=request, template_name="comarca/cadastrar_predio.html", context=locals())


@login_required
@permission_required('comarca.change_predio')
@reversion.create_revision(atomic=False)
def salvar_predio(request):
    """Salva dados de predio novo ou alteracoes em existente"""

    if request.method == 'POST':

        data = request.POST.copy()
        predio_id = request.POST.get('predio-id')

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
            predio = Predio.objects.get(id=predio_id)
        except Exception:
            predio = Predio()
            predio.endereco = Endereco()
            predio.telefone = Telefone()

        form = PredioForm(data, instance=predio)
        form_endereco = EnderecoForm(data, instance=predio.endereco, prefix='endereco',
                                     initial={'estado': data['endereco-estado']})
        form_telefone = TelefoneForm(data, instance=predio.telefone, prefix='telefone')

        if form.is_valid() and form_endereco.is_valid() and form_telefone.is_valid():

            predio = form.save(commit=False)
            predio.endereco = form_endereco.save()
            predio.telefone = form_telefone.save()

            novo = (predio.id is None)
            predio.save()

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_save(request.user, predio, novo))

            messages.success(request, u'Prédio salvo com sucesso!')
            return redirect('comarca_buscar_predio')

    return render(request=request, template_name="comarca/cadastrar_predio.html", context=locals())


@login_required
def get_predios(request):
    defensor = request.user.servidor.defensor
    atuacoes = defensor.atuacoes_vigentes()

    # Se tem atuação, obtem lista de todos prédios das defensorias
    if atuacoes.count():

        predios = Predio.objects.filter(defensoria__in=atuacoes.values_list('defensoria_id', flat=True))

    # Senão, obtém lista com prédios da comarca
    else:
        predios = Predio.objects.filter(comarca=request.session.get('comarca', 0), ativo=True).order_by('nome')

    if predios.count() == 1:
        request.session['predio'] = predios.first().id
        return redirect('painel_predio_set', predios.first().id)

    predios_lst = []
    for predio in predios:
        predios_lst.append({'predio': predio.nome, 'id': predio.id})

    return JsonResponse({'predios': predios_lst, 'success': True})


@login_required
def get_guiche(request):

    servidor = request.user.servidor
    guiche_atual = Guiche.objects.filter(usuario=servidor, ativo=True).order_by('id').last()

    if guiche_atual:
        dados = {
            'numero': guiche_atual.numero,
            'andar': guiche_atual.andar,
            'tipo': {
                'id': guiche_atual.tipo,
                'nome': guiche_atual.get_tipo_display()
            },
            'defensoria': {
                'id': guiche_atual.defensoria.id,
                'nome': guiche_atual.defensoria.nome
            },
            'predio_atual': {
                'nome': guiche_atual.defensoria.predio.nome
            },
        }
        return JsonResponse({
            'success': True,
            'guiche_atual': dados,
            'defensorias_disponiveis': defensorias_disponiveis(servidor)
        })
    else:
        return JsonResponse({'success': True, 'defensorias_disponiveis': defensorias_disponiveis(servidor)})


def defensorias_disponiveis(servidor):
    lista = []
    atuacoes_vigentes = servidor.defensor.atuacoes_vigentes()
    for atuacao in atuacoes_vigentes:
        lista.append({
            'defensoria': {
                'id': atuacao.defensoria.id,
                'nome': atuacao.defensoria.nome,
                'predio': {
                    'id': atuacao.defensoria.predio.id,
                    'nome': atuacao.defensoria.predio.nome,
                    'qtd_andares': atuacao.defensoria.predio.qtd_andares,
                },
            },
        })
    return lista


@login_required
def salvar_guiche(request):
    if request.method == 'POST':
        predio_id = int(request.POST.get('predio_id'))
        tipo_id = int(request.POST.get('tipo_id'))
        andar = int(request.POST.get('andar'))
        numero = int(request.POST.get('numero'))
        defensoria_id = int(request.POST.get('defensoria_id'))
        servidor = request.user.servidor
        usuario = request.user
        forcarTrocaDeGuiche = False if request.POST.get('forcarTrocaDeGuiche') == 'false' else True
        existe_usuario_com_esse_guiche = False

        # se o tipo for guichê, ou seja, somente um balcão para uma pessoa
        if tipo_id == 1:
            # faz um filtro para saber se já existe guiche com essas informaçẽos
            guiches = Guiche.objects.filter(
                numero=numero,
                predio_id=predio_id,
                tipo=tipo_id,
                andar=andar,
                ativo=True
            )

            if guiches:
                for guiche in guiches:
                    if forcarTrocaDeGuiche:
                        remover_guiche(request, guiche.usuario.usuario.id)
                        existe_usuario_com_esse_guiche = False
                    else:
                        nome_antigo_usuario = guiche.usuario.nome
                        existe_usuario_com_esse_guiche = True

            if not existe_usuario_com_esse_guiche or forcarTrocaDeGuiche:
                # remove guichês antigos
                remover_guiche(request, usuario.id)
                # criar guiche para o usuário
                Guiche.objects.create(
                    numero=numero,
                    ativo=True,
                    defensoria_id=defensoria_id,
                    usuario=servidor,
                    comarca=servidor.comarca,
                    predio_id=predio_id,
                    tipo=tipo_id,
                    andar=andar
                )
                return JsonResponse({'success': True})
            else:
                return JsonResponse({
                    'success': False,
                    'dados': {
                        'nome_antigo_usuario': nome_antigo_usuario,
                        'mensagem': "Guichê já ocupado no mesmo prédio",
                    }
                })

        # tipo sala. Várias pessoas em uma sala.
        elif tipo_id == 2:
            remover_guiche(request, usuario.id)
            Guiche.objects.create(
                numero=numero,
                defensoria_id=defensoria_id,
                usuario=servidor,
                comarca=servidor.comarca,
                predio_id=predio_id,
                tipo=tipo_id,
                andar=andar
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'mensagem': str("Tipo de guichê não permitido")})


@login_required
def remover_guiche(request, servidor_id):
    servidor = Servidor.objects.get(usuario_id=servidor_id)
    guiches = Guiche.objects.filter(usuario_id=servidor.id, ativo=True)

    for guiche in guiches:
        guiche_antigo = Guiche.objects.filter(numero=guiche.numero, ativo=True).first()

        guiche_antigo.ativo = False
        guiche_antigo.save()
