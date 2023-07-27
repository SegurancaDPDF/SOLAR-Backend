# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
from datetime import time, datetime
import json as simplejson

# Bibliotecas de terceiros
import math
import re
import reversion
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render


# Solar
from assistido.forms import CadastrarEndereco, CadastrarPessoa
from assistido.models import PessoaAssistida
from atendimento.atendimento.models import Pessoa as AtendimentoPessoa
from atendimento.atendimento.models import Defensor as AtendimentoDefensor
from contrib.models import Dados, Telefone, Util
from defensor.models import Atuacao
from nucleo.nadep.forms import (
    AtendimentoForm,
    CadastrarTransferenciaForm,
    BuscarAtendimentoForm,
    AlterarAtendimentoForm
)
from nucleo.nadep.models import Atendimento, Prisao, Aprisionamento
from nucleo.nadep.services import Preso


@login_required
@permission_required('nadep.view_atendimento')
def buscar(request):
    """ Exibe pagina com todos atendimentos cadastrados """

    if request.method == 'POST':

        numero_registros = 25
        filtro = simplejson.loads(request.body)
        form = BuscarAtendimentoForm(filtro)

        if form.is_valid():

            atendimentos_lst = Atendimento.objects.filter(
                Q(ativo=True) &
                Q(remarcado=None)
            ).order_by(
                '-data_agendamento',
                '-data_atendimento',
                '-data_cadastro')

            if 'filtro' in filtro and filtro['filtro']:

                filtro_numero = re.sub('[^0-9]', '',  filtro['filtro'])

                if len(filtro_numero) == 12:  # Numero do Atendimento

                    atendimentos_lst = atendimentos_lst.filter(numero=filtro_numero)

                elif len(filtro_numero) == 11:  # Numero do CPF

                    pessoas_lst = set(
                        AtendimentoPessoa.objects.filter(
                            pessoa__cpf=filtro_numero,
                            ativo=True
                        ).values_list('atendimento_id', flat=True)
                    )

                else:

                    pessoas_lst = set(
                        AtendimentoPessoa.objects.filter(
                            pessoa__nome_norm__startswith=Util.normalize(filtro['filtro']),
                            ativo=True
                        ).values_list('atendimento_id', flat=True)
                    )

                if 'pessoas_lst' in locals():
                    atendimentos_lst = atendimentos_lst.filter(
                        (
                            Q(id__in=pessoas_lst) |
                            Q(inicial__in=pessoas_lst)
                        ))

            if 'comarca' in filtro and filtro['comarca']:
                atendimentos_lst = atendimentos_lst.filter((
                    Q(defensoria__comarca_id=filtro['comarca'])
                ))

            if 'defensoria' in filtro and filtro['defensoria']:
                atendimentos_lst = atendimentos_lst.filter((
                    Q(defensoria_id=filtro['defensoria'])
                ))

            if 'defensor' in filtro and filtro['defensor']:
                atendimentos_lst = atendimentos_lst.filter((
                    Q(defensor_id=filtro['defensor']) |
                    Q(substituto_id=filtro['defensor'])
                ))

            if form.cleaned_data['data_ini']:
                data_ini = form.cleaned_data['data_ini']

                atendimentos_lst = atendimentos_lst.filter((
                    (
                        Q(data_agendamento__gte=data_ini) &
                        Q(data_atendimento=None)
                    ) |
                    Q(data_atendimento__gte=data_ini)
                ))

            if form.cleaned_data['data_fim']:
                data_fim = form.cleaned_data['data_fim']
                data_fim = datetime.combine(data_fim, time.max)

                atendimentos_lst = atendimentos_lst.filter((
                    (
                        Q(data_agendamento__lte=data_fim) &
                        Q(data_atendimento=None)
                    ) |
                    Q(data_atendimento__lte=data_fim)
                ))

            primeiro = filtro['pagina'] * numero_registros
            ultimo = primeiro + numero_registros

            if filtro['pagina'] == 0:
                filtro['total'] = atendimentos_lst.count()
                filtro['paginas'] = math.ceil(float(filtro['total']) / numero_registros)

            atendimentos_lst = atendimentos_lst[primeiro:ultimo]

            atendimentos_lst = atendimentos_lst.values(
                'id',
                'inicial_id',
                'numero',
                'data_atendimento',
                'data_agendamento',
                'tipo',
                'defensoria__nome',
                'defensoria__comarca',
                'qualificacao__titulo',
                'qualificacao__area__nome',
                'defensor__servidor__nome',
                'substituto__servidor__nome',
                'prisao__tipo',
                'prisao__processo__numero',
                'prisao__pessoa__id',
                'prisao__pessoa__nome',
            )

            atendimentos = []
            for atendimento in atendimentos_lst:
                eh_extra = (atendimento['data_agendamento'] and atendimento['data_agendamento'].time() == time())
                atendimento['extra'] = eh_extra

                atendimentos.append(atendimento)

        else:

            atendimentos = []

        return JsonResponse(
            {
                'usuario': {
                    'comarca': int(request.session.get('comarca', request.user.servidor.comarca_id)),
                    'perms': {
                        'atendimento_view_recepcao': request.user.has_perm('atendimento.view_recepcao')
                    }
                },
                'atendimentos': atendimentos,
                'pagina': filtro['pagina'],
                'paginas': filtro['paginas'] if 'paginas' in filtro else 0,
                'ultima': filtro['pagina'] == filtro['paginas'] - 1 if 'paginas' in filtro else True,
                'total': filtro['total'],
                'LISTA': {
                    'TIPO': dict(Atendimento.LISTA_TIPO),
                    'PRISAO': dict(Prisao.LISTA_TIPO),
                }
            }, safe=False)

    form = BuscarAtendimentoForm(request.GET)
    angular = 'BuscarAtendimentoCtrl'

    return render(request=request, template_name="nadep/buscar_atendimento.html", context=locals())


@login_required
@reversion.create_revision(atomic=False)
def salvar(request, prisao_id):

    errors = []
    atendimento = None

    if request.method == 'POST':

        dados = simplejson.loads(request.body)
        dados_pessoa = Dados(dados['pessoa'], True)

        # Campos que nao vem na requisisao
        dados['tipo'] = Atendimento.TIPO_INICIAL
        dados['prisao'] = prisao_id
        dados['atendido_por'] = request.user.servidor.id

        try:
            pessoa = PessoaAssistida.objects.get(id=dados['pessoa']['id'])
        except ObjectDoesNotExist:
            pessoa = PessoaAssistida()

        pessoa_form = CadastrarPessoa(dados_pessoa.get_all(), instance=pessoa)

        if pessoa_form.is_valid():
            # TODO: Verificar consistencia.
            novo = (None == pessoa.id)  # noqa
            pessoa = pessoa_form.save()

            try:
                endereco_form = CadastrarEndereco(dados_pessoa.get_all(), instance=pessoa.endereco,
                                                  initial={'estado': dados_pessoa['estado'],
                                                           'municipio': dados_pessoa['municipio']})
            except KeyError:
                endereco_form = CadastrarEndereco(dados_pessoa.get_all(), instance=pessoa.endereco)

            if endereco_form.is_valid():
                pessoa.enderecos.add(endereco_form.save())

            if dados_pessoa['telefones'] is not None:

                for telefone in dados_pessoa['telefones']:

                    if telefone['numero'] is not None:

                        obj, msg = Telefone.objects.get_or_create(ddd=telefone['ddd'], numero=telefone['numero'],
                                                                  tipo=telefone['tipo'])

                        if telefone['id'] != obj.id and telefone['id'] is not None:

                            try:
                                pessoa.telefones.remove(Telefone.objects.get(id=telefone['id']))
                            except Exception as e:
                                errors.append(e)

                        pessoa.telefones.add(obj)
            # TODO: Verificar consistencia.
            prisao = Prisao.objects.get(id=prisao_id)  # noqa

            form = AtendimentoForm(dados)

            if form.is_valid():
                atendimento = form.save()

                atendimento.set_requerente(pessoa)

                reversion.set_user(request.user)
                reversion.set_comment(Util.get_comment_save(request.user, atendimento, True))

        else:
            errors.append([(k, v[0]) for k, v in pessoa_form.errors.items()])

    return JsonResponse(
        {'success': (len(errors) == 0), 'errors': errors, 'atendimento': (atendimento.id if atendimento else None)})


@login_required
@reversion.create_revision(atomic=False)
def salvar_visita(request, prisao_id):
    if request.method == 'POST':

        errors = []

        dados = simplejson.loads(request.body)

        # Campos que nao vem na requisisao
        dados['tipo'] = Atendimento.TIPO_VISITA
        dados['prisao'] = prisao_id

        novo = True
        atendimento = None
        atendimento_processo = None

        if 'id' in dados and dados['id']:

            # Se id foi passado, carrega visita
            atendimento = Atendimento.objects.get(id=dados['id'])
            novo = False

        else:

            # Se nova visita, valida atendimento inicial
            if 'inicial' in dados and dados['inicial']:

                atendimento_inicial = AtendimentoDefensor.objects.get(id=dados['inicial'])

                # Se atendimento informado como inicial possui um inicial, corrige o relacionamento
                if atendimento_inicial.inicial_id:
                    dados['inicial'] = atendimento_inicial.inicial_id
                # Senão, se atendimento é do tipo processo, remove o relaciomanento
                elif atendimento_inicial.tipo == Atendimento.TIPO_PROCESSO:
                    dados['inicial'] = None
                    atendimento_processo = atendimento_inicial

            else:

                return JsonResponse({
                    'success': False,
                    'message': 'Erro ao salvar: A prisão ou processo não estão vinculados a um atendimento!'
                })

        if 'atuacao' in dados and dados['atuacao']:
            atuacao = Atuacao.objects.get(id=dados['atuacao'])
            if atuacao.tipo == Atuacao.TIPO_SUBSTITUICAO:
                dados['defensor'] = atuacao.titular_id
                dados['substituto'] = atuacao.defensor_id

        prisao = Prisao.objects.get(id=prisao_id)
        preso = Preso(prisao.pessoa)

        if atendimento:
            form = AlterarAtendimentoForm(dados, instance=atendimento)
        else:
            form = AtendimentoForm(dados)

        if form.is_valid():

            atendimento = form.save(commit=False)
            atendimento.modificado_por = request.user.servidor

            if atendimento.substituto:
                atendimento.atendido_por = atendimento.substituto.servidor
            else:
                atendimento.atendido_por = atendimento.defensor.servidor

            if novo:
                atendimento.cadastrado_por = request.user.servidor

            atendimento.save()

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_save(request.user, atendimento, novo))

            if novo:

                # aplica atendimento como inicial do atendimento para processo caso houver
                if atendimento_processo:

                    atendimento_processo.partes.update(atendimento=atendimento)  # transfere pessoas
                    atendimento_processo.tarefa_set.update(atendimento=atendimento)  # transfere tarefas
                    atendimento_processo.parte_set.update(atendimento=atendimento)  # transfere parte de processo
                    atendimento_processo.visualizacoes.update(atendimento=atendimento)  # transfere visualizações
                    atendimento_processo.acesso_set.update(atendimento=atendimento)  # transfere acesso

                    atendimento_processo.inicial = atendimento
                    atendimento_processo.save()

                estabelecimento_penal_atual = preso.estabelecimento_penal_atual()

                if not estabelecimento_penal_atual or dados['estabelecimento_penal'] != estabelecimento_penal_atual.id:

                    aprisionamento = Aprisionamento(situacao=Aprisionamento.SITUACAO_TRANSFERIDO,
                                                    origem_cadastro=Aprisionamento.ORIGEM_REGISTRO,
                                                    cadastrado_por=request.user.servidor)

                    formTransferencia = CadastrarTransferenciaForm({
                        'prisao': dados['prisao'],
                        'estabelecimento_penal': dados['estabelecimento_penal'],
                        'data_inicial': dados['data_atendimento'],
                        'historico': '(TRANSFERÊNCIA AUTOMÁTICA ORIGINADA DE VISITA)',
                    }, instance=aprisionamento)

                    if formTransferencia.is_valid():
                        formTransferencia.save()

        else:

            errors = [({'field': k, 'message': v[0]}) for k, v in form.errors.items()]

        return JsonResponse({
            'success': (len(errors) == 0),
            'errors': errors,
            'atendimento': (atendimento.id if atendimento else None),
            'numero': (atendimento.numero if atendimento else None)
        })

    return JsonResponse({'success': False})


@login_required
def listar(request, prisao_id):
    atendimentos = []
    prisao = Prisao.objects.get(id=prisao_id)

    for atendimento in prisao.atendimentos():
        atendimentos.append({
            'id': atendimento.id,
            'numero': atendimento.numero,
            'data_atendimento': atendimento.data_atendimento.strftime('%Y-%m-%dT%H:%M:00-03:00'),
            'defensor': {'id': atendimento.defensor.id, 'nome': atendimento.defensor.nome},
            'defensoria': {'id': atendimento.defensoria.id, 'nome': atendimento.defensoria.nome},
            'requerente': atendimento.requerente.pessoa.nome if atendimento.requerente else None,
            'parentesco_preso': Atendimento.LISTA_GRAU_PARENTESCO[atendimento.parentesco_preso][1],
            'assunto': atendimento.assunto,
            'historico': atendimento.historico
        })

    return JsonResponse(atendimentos, safe=False)


@login_required
def listar_visita(request, prisao_id):
    atendimentos = []
    prisao = Prisao.objects.get(id=prisao_id)

    for atendimento in prisao.visitas():
        atendimentos.append({
            'id': atendimento.id,
            'numero': atendimento.numero,
            'data_atendimento': atendimento.data_atendimento.strftime('%Y-%m-%dT%H:%M:00-03:00'),
            'defensor': {'id': atendimento.defensor.id, 'nome': atendimento.defensor.nome},
            'defensoria': {'id': atendimento.defensoria.id, 'nome': atendimento.defensoria.nome},
            'historico': atendimento.historico
        })

    return JsonResponse(atendimentos, safe=False)


@login_required
@reversion.create_revision(atomic=False)
@permission_required('nadep.delete_atendimento')
def excluir(request, atendimento_numero):
    atendimento = get_object_or_404(Atendimento, numero=atendimento_numero, ativo=True)
    atendimento.ativo = False
    atendimento.save()

    reversion.set_user(request.user)
    reversion.set_comment(Util.get_comment_delete(request.user, atendimento))

    messages.success(request, u'Atendimento excluído')

    return redirect('nadep_visualizar_prisao', atendimento.prisao.id)


@login_required
@permission_required('nadep.view_atendimento')
def visualizar(request, atendimento_numero):
    atendimento = get_object_or_404(Atendimento, numero=atendimento_numero)
    prisao = atendimento.prisao
    pessoa = atendimento.requerente

    request.session['atendimento'] = atendimento

    return render(request=request, template_name="nadep/visualizar_atendimento.html", context=locals())
