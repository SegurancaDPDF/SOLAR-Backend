# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import base64
import hashlib
import json as simplejson
import logging
import mimetypes
import os
import tempfile
import time
from datetime import datetime
from urllib.parse import urlparse

# Bibliotecas de terceiros
import reversion
from constance import config
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.base import ContentFile
from django.db import transaction, IntegrityError
from django.views.decorators.cache import never_cache
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.db.models import Q
from django.http import JsonResponse, Http404, RawPostDataException
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.contrib.sites.models import Site

# Solar
from contrib import constantes
from contrib.models import (
    Dados,
    Endereco,
    EnderecoHistorico,
    Estado,
    Pais,
    Salario,
    Telefone,
    Util
)
from contrib.validators import validate_CPF_CNPJ
from relatorios.models import Local, Relatorio

# Modulos locais
from . import forms
from .models import (
    Documento,
    EstruturaMoradia,
    Filiacao,
    Patrimonial,
    PatrimonialTipo,
    PerfilCamposObrigatorios,
    Pessoa,
    PessoaAssistida,
    Profissao,
    Situacao,
    Acesso
)
from .services import (
    PerfilCamposObrigatoriosService,
    PessoaAssistidaService,
    calcula_valor_deducao_por_tipo_renda_membros_familia,
    calcula_quantidade_membros_deducao_por_situacao,
    calcula_valor_deducao_por_tipo_renda_cadastro_principal,
    calcula_valor_deducao_por_situacao_cadastro_principal,
    remove_imovel_bem_familia
)
from .tasks import notificar_solicitacao_acesso


logger = logging.getLogger(__name__)


@never_cache
@login_required
def avaliar(request):
    """Avalia se o assistido é hipossuficiente. JS faz chamada POST na tela de cadastro do assistido"""

    resposta = {'success': False}

    if request.method == 'POST':
        dados = simplejson.loads(request.body)

        # Define o tipo_pessoa para validação
        tipo_pessoa = dados.get('tipo', 0)

        # Obtém salário atual para o tipo de pessoa (física ou jurídica?)
        salario = Salario.atual(tipo_pessoa)

        if salario:

            renda_per_capita = 0
            soma_patrimonios_sem_investimentos = 0
            soma_patrimonios_do_tipo_investimento = 0
            patrimonial_tipo = PatrimonialTipo.objects.get(nome='Investimentos')

            # Desconsidera o primeiro item do tipo Imóveis
            if settings.SIGLA_UF.upper() == 'PR':
                dados['patrimonios'] = remove_imovel_bem_familia(dados.get('patrimonios'))

            if 'patrimonios' in dados and len(dados.get('patrimonios')) and dados.get('patrimonios')[0].get('tipo'):
                patrimonios_sem_investimentos = filter(
                    lambda patrimonio: patrimonio['tipo']['id'] != patrimonial_tipo.id, dados.get('patrimonios'))
                patrimonios_do_tipo_investimento = filter(
                    lambda patrimonio: patrimonio['tipo']['id'] == patrimonial_tipo.id, dados.get('patrimonios'))
                for patrimonio in patrimonios_sem_investimentos:
                    soma_patrimonios_sem_investimentos += float(patrimonio.get('valor', 0))
                for patrimonio in patrimonios_do_tipo_investimento:
                    soma_patrimonios_do_tipo_investimento += float(patrimonio.get('valor', 0))

            valor_bens = soma_patrimonios_sem_investimentos
            valor_investimentos = soma_patrimonios_do_tipo_investimento

            eh_hipossuficiente = True
            passou_renda_individual = True
            passou_renda_familiar = True
            passou_renda_per_capita = True
            passou_salario_funcionario = True
            passou_valor_bens = True
            passou_valor_investimentos = True

            valor_deducao_por_tipo_renda = 0.00
            valor_deducao_por_situacao = 0.00

            # Cálculo para Pessoa Física
            if tipo_pessoa == constantes.TIPO_PESSOA_FISICA:

                numero_membros = float(dados.get('numero_membros')) if dados.get('numero_membros') else 0
                renda_individual = float(dados.get('ganho_mensal')) if dados.get('ganho_mensal') else 0
                renda_familiar = float(dados.get('ganho_mensal_membros')) if dados.get('ganho_mensal_membros') else 0

                # Obs: Este cálculo atende a resolução da DPE-RN
                if settings.SIGLA_UF.upper() == 'RN':

                    # Renda Per Capita = ((Renda Extra + Rendas Familiar) – Despesas Dedutíveis) / Quantidade de Membros
                    patrimoniais = dados.get('patrimonios')

                    itens_renda_extra = filter(
                        lambda patrimonio: patrimonio['tipo']['grupo'] == PatrimonialTipo.GRUPO_RENDA_EXTRA,
                        patrimoniais)
                    total_renda_extra = sum(float(item.get('valor')) for item in itens_renda_extra)

                    itens_despesa_dedutivel = filter(
                        lambda patrimonio: patrimonio['tipo']['grupo'] == PatrimonialTipo.GRUPO_DESPESA_DEDUTIVEL,
                        patrimoniais)

                    total_despesa_dedutivel = sum(float(item.get('valor')) for item in itens_despesa_dedutivel)

                    renda_per_capita = (renda_familiar + total_renda_extra - total_despesa_dedutivel) / numero_membros

                    eh_hipossuficiente = passou_renda_per_capita = salario.validar_renda_per_capita(renda_per_capita)

                # Obs: Este cálculo atende a resolução da DPE-PR
                elif settings.SIGLA_UF.upper() == 'PR':
                    patrimoniais = dados.get('patrimonios')
                    membros = dados.get('membros')

                    quantidade_membros_deducao_por_situacao = calcula_quantidade_membros_deducao_por_situacao(membros)
                    valor_deducao_por_tipo_renda = calcula_valor_deducao_por_tipo_renda_membros_familia(membros)
                    if dados.get('id') is not None:
                        quantidade_membros_deducao_por_situacao += calcula_valor_deducao_por_situacao_cadastro_principal(dados.get('id'))  # noqa: E501
                        valor_deducao_por_tipo_renda += calcula_valor_deducao_por_tipo_renda_cadastro_principal(dados.get('id'))  # noqa: E501

                    itens_despesa_dedutivel = filter(
                        lambda patrimonio: patrimonio['tipo']['grupo'] == PatrimonialTipo.GRUPO_DESPESA_DEDUTIVEL,
                        patrimoniais)

                    total_despesa_dedutivel = sum(float(item.get('valor')) for item in itens_despesa_dedutivel)

                    if quantidade_membros_deducao_por_situacao > 0 and quantidade_membros_deducao_por_situacao < 4:
                        valor_deducao_por_situacao = ((float(salario.valor)/2) * quantidade_membros_deducao_por_situacao)  # noqa: E501
                    elif quantidade_membros_deducao_por_situacao > 3:
                        valor_deducao_por_situacao = float(salario.valor) * 2

                    if numero_membros and renda_familiar:
                        try:
                            renda_per_capita = (renda_familiar) / numero_membros
                        except ZeroDivisionError as e:
                            logger.error('Erro de Divisão Por Zero na avaliação de renda do assistido. %s' % e)
                            renda_per_capita = 0

                    if numero_membros == 1:
                        passou_renda_individual = salario.validar_renda_individual(renda_individual - total_despesa_dedutivel - valor_deducao_por_situacao - valor_deducao_por_tipo_renda)  # noqa: E501
                    else:
                        passou_renda_familiar = salario.validar_renda_familiar(renda_familiar - total_despesa_dedutivel - valor_deducao_por_situacao - valor_deducao_por_tipo_renda)  # noqa: E501
                        passou_renda_per_capita = salario.validar_renda_per_capita(renda_per_capita)

                    passou_valor_bens = salario.validar_valor_bens(valor_bens)

                    passou_valor_investimentos = salario.validar_valor_investimentos(valor_investimentos)

                    if not passou_renda_individual or not passou_valor_bens or not passou_valor_investimentos or (
                            not passou_renda_familiar):
                        eh_hipossuficiente = False

                # Obs: Este cálculo atende a resolução da DPE-PR
                elif settings.SIGLA_UF.upper() == 'RO':

                    patrimonios_e_dedutores = dados['patrimonios']
                    if patrimonios_e_dedutores:
                        for reducao in patrimonios_e_dedutores:
                            if reducao["tipo"]['grupo'] == 21:
                                if isinstance(reducao["valor"], int):
                                    if reducao["valor"] > 0:
                                        valor_deducao_por_situacao += reducao["valor"]
                    if numero_membros and renda_familiar:
                        try:
                            renda_per_capita = renda_familiar / numero_membros
                        except ZeroDivisionError as e:
                            logger.error('Erro de Divisão Por Zero na avaliação de renda do assistido. %s' % e)
                            renda_per_capita = 0

                    if numero_membros > 5:
                        salario.indice_renda_individual = 4
                        salario.indice_renda_familiar = 4
                    # DPE-RO não considera renda per_capita e individual
                    passou_renda_individual = True
                    passou_renda_per_capita = True

                    # Avaliação prevista no regulamento
                    passou_renda_familiar = salario.validar_renda_familiar(
                        renda_familiar - valor_deducao_por_situacao
                    )
                    passou_valor_bens = salario.validar_valor_bens(
                        valor_bens
                    )
                    passou_valor_investimentos = salario.validar_valor_investimentos(
                        valor_investimentos
                    )

                    if (not passou_valor_bens or not passou_valor_investimentos or not passou_renda_familiar):
                        eh_hipossuficiente = False

                # Obs: Este cálculo atende a resolução da DPE-SE
                elif settings.SIGLA_UF.upper() == 'SE':
                    eh_hipossuficiente = passou_renda_individual = salario.validar_renda_individual(renda_individual)

                # Obs: Este cálculo atende a resolução da DPE-TO
                else:

                    if numero_membros and renda_familiar:
                        try:
                            renda_per_capita = renda_familiar / numero_membros
                        except ZeroDivisionError as e:
                            logger.error('Erro de Divisão Por Zero na avaliação de renda do assistido. %s' % e)
                            renda_per_capita = 0

                    if numero_membros == 1:
                        passou_renda_individual = salario.validar_renda_individual(renda_individual)
                    else:
                        passou_renda_familiar = salario.validar_renda_familiar(renda_familiar)
                        passou_renda_per_capita = salario.validar_renda_per_capita(renda_per_capita)

                    passou_valor_bens = salario.validar_valor_bens(valor_bens)
                    passou_valor_investimentos = salario.validar_valor_investimentos(valor_investimentos)

                    if not passou_renda_individual or not passou_valor_bens or not passou_valor_investimentos or (
                            not passou_renda_familiar and not passou_renda_per_capita):
                        eh_hipossuficiente = False

            # Cálculo para Pessoa Jurídica (Este cálculo atende a resolução da DPE-TO)
            else:

                salario_funcionario = float(dados.get('salario_funcionario', 0))
                passou_salario_funcionario = salario.validar_valor_salario_funcionario(salario_funcionario)

                if not passou_valor_bens or not passou_valor_investimentos or not passou_salario_funcionario:
                    eh_hipossuficiente = False

            resposta = {
                'success': True,
                'renda_individual': passou_renda_individual,
                'renda_familiar': passou_renda_familiar,
                'renda_per_capita': passou_renda_per_capita,
                'total_bens': passou_valor_bens,
                'total_investimentos': passou_valor_investimentos,
                'salario_funcionario': passou_salario_funcionario,
                'hipossuficiente': eh_hipossuficiente,
                'salario': Util.object_to_dict(salario),
                'valor_deducao_por_situacao': valor_deducao_por_situacao,
                'valor_deducao_por_tipo_renda': valor_deducao_por_tipo_renda
            }

    return JsonResponse(resposta)


@login_required
@permission_required('assistido.view_pessoaassistida')
def buscar(request):

    # Redireciona para 129 se existe ligação ativa
    if request.session.get('ligacao_id'):
        return redirect('{}?next={}'.format(reverse('precadastro_index'), reverse('assistido_buscar')))

    if request.method == 'POST':

        data = simplejson.loads(request.body)

        pessoas = []

        q = Q(desativado_em=None)

        if data.get('cpf'):
            q &= Q(cpf=data['cpf'])

        elif data.get('id'):
            q &= Q(id=data['id'])

        else:

            if data.get('nome'):

                nomes = Util.text_to_soundex(data['nome'])
                q_nome = Q()

                for nome in nomes:
                    q_nome &= Q(nome_soundex__icontains=nome)

                # Só busca por nome social caso seja tipo pessoa física
                q_nome_social = Q(
                    Q(tipo=constantes.TIPO_PESSOA_FISICA) &
                    Q(nome_social__icontains=data['nome'])
                )

                # Só busca por nome fantasia (apelido) caso seja tipo pessoa jurídica
                q_nome_fantasia = Q(
                    Q(tipo=constantes.TIPO_PESSOA_JURIDICA) &
                    Q(apelido__icontains=data['nome'])
                )

                q &= Q(q_nome | q_nome_social | q_nome_fantasia)

            if data.get('filiacao'):
                nomes = Util.text_to_soundex(data['filiacao'])
                for nome in nomes:
                    q &= Q(filiacoes__nome_soundex__icontains=nome)

            if data.get('data_nascimento'):

                try:
                    data['data_nascimento'] = datetime.datetime.strptime(data['data_nascimento'], '%Y-%m-%dT%H:%M:%S.000Z')  # noqa: E501
                except Exception:
                    pass
                else:
                    q &= Q(data_nascimento=data['data_nascimento'].date())

        pessoa_anterior = None

        # Só executa o Bloqueio de Maria caso não tenha preenchido cpf e id
        if not data.get('cpf') and not data.get('id'):

            # Se a consulta retornar uma quantidade acima do limite configurado será retornada uma mensagem
            # de alerta para que o usuário faça filtros mais elaborados
            pessoas_count = PessoaAssistida.objects.filter(q).distinct().count()

            if config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MAX_PESSOAS and pessoas_count > config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MAX_PESSOAS:  # noqa: E501
                return JsonResponse({
                    'sucesso': False,
                    'mensagem': 'Erro: Seriam retornados mais de {} registros. Preencha mais campos e tente novamente.'.format(  # noqa: E501
                        pessoas_count
                    )
                })

        filtro_pessoas = PessoaAssistida.objects.filter(q).distinct().values(
            'id',
            'cpf',
            'nome',
            'nome_social',
            'apelido',
            'tipo',
            'data_nascimento',
            'filiacoes__nome'
        ).order_by(
            'nome'
        )

        for pessoa in filtro_pessoas:

            if pessoa['id'] != pessoa_anterior:

                pessoa_anterior = pessoa['id']
                pessoa['filiacao'] = []

                if pessoa['data_nascimento']:
                    pessoa['data_nascimento'] = pessoa['data_nascimento'].isoformat()

                pessoas.append(pessoa)

            if pessoa['filiacoes__nome']:
                pessoas[-1]['filiacao'].append({'nome': pessoa.pop('filiacoes__nome')})
            else:
                pessoa.pop('filiacoes__nome')

        return JsonResponse({
            'sucesso': True,
            'pessoas': pessoas
        }, safe=False)

    angular = 'BuscarPessoaModel'

    return render(request=request, template_name="assistido/buscar.html", context=locals())


@login_required
def cpf_existe(request):
    """Utilizado para verificar se já existe alguma pessoa cadastrada com o CPF/CNPJ informado."""

    if request.method == 'POST':

        # carrega e trata dados recebidos via ajax
        dados = Dados(request.body)

        # procura pessoa com o cpf informado
        pessoa = PessoaAssistida.objects.ativos().filter(
            cpf=dados['cpf']
        ).exclude(
            id=dados['id']
        ).only('id', 'nome').first()

        if pessoa:
            resposta = {'existe': True, 'id': pessoa.id, 'nome': pessoa.nome}
        else:
            resposta = {'existe': False}

        return JsonResponse(resposta)


@never_cache
@login_required
@permission_required('assistido.change_pessoaassistida')
def editar(request, pessoa_id=None, tipo_pessoa=None):
    """Utilizado para carregar/renderizar a página de edição de Assistido"""

    # Converte para int
    if tipo_pessoa is not None:
        tipo_pessoa = int(tipo_pessoa)

    modificado_hoje = 'false'
    pessoa_assistida_form_initial = {}
    endereco_form_initial = {}
    permissao_acessar = True

    # Campos somente leitura
    readonly_fields = []

    # Se for Cadastrar uma nova Pessoa
    if pessoa_id is None or pessoa_id == '0':
        assistido = PessoaAssistida()

        # Se não passou tipo_pessoa irá cadastrar uma pessoa física por padrão
        if tipo_pessoa is None:
            tipo_pessoa = constantes.TIPO_PESSOA_FISICA

        assistido.tipo = tipo_pessoa

        endereco_form_initial = {
            'estado': Estado.objects.get(uf__iexact=settings.SIGLA_UF).id
        }

        if hasattr(request.user.servidor.comarca, 'municipio') and request.user.servidor.comarca.municipio:
            endereco_form_initial['municipio'] = request.user.servidor.comarca.municipio.id

        pessoa_assistida_form_initial = {
            'nome': request.GET.get('nome', '').upper(),
            'cpf': request.GET.get('cpf', '')
        }

    # Se for Editar uma Pessoa
    else:

        assistido = get_object_or_404(
            PessoaAssistida,
            id=pessoa_id,
            desativado_em=None
        )

        # trata o tipo_pessoa para salvar
        if tipo_pessoa is not None:
            assistido.tipo = tipo_pessoa
        else:
            tipo_pessoa = assistido.tipo

        atendimentos = assistido.atendimentos.filter(atendimento__ativo=True, ativo=True)

        if assistido.tipo_cadastro == PessoaAssistida.CADASTRO_COMPLETO:
            if assistido.modificado_em and assistido.modificado_em.date() == datetime.now().date():
                modificado_hoje = 'true'

        if assistido.endereco:
            endereco_form_initial = {
                'estado': assistido.endereco.municipio.estado_id,
                'municipio': assistido.endereco.municipio.id
            }
        situacoes = list(assistido.situacoes.all().values_list('codigo', flat=True))
        acesso_solicitado = assistido.acesso_solicitado(request.user.servidor)

        situacoes_configuradas = config.SITUACOES_SIGILOSAS
        if situacoes_configuradas:
            if situacoes_configuradas.find(',') != -1:
                situacoes_configuradas = situacoes_configuradas.split(',')
            else:
                situacoes_configuradas = ['', situacoes_configuradas]

            for situacao_configurada in situacoes_configuradas:
                if situacao_configurada in situacoes and config.SITUACOES_SIGILOSAS:
                    if assistido.permissao_acessar(usuario=request.user) or assistido.acesso_concedido(request.user.servidor):  # noqa: E501
                        permissao_acessar = True
                    else:
                        permissao_acessar = False
        not_permissao_acessar = not permissao_acessar

        # Adiciona campos que não podem ser alterados em cadastros protegidos
        if assistido.cadastro_protegido:
            readonly_fields = ['cpf', 'nome', 'apelido', 'nome_social']
        # Adiciona campos preenchidos que não podem ser alterados
        elif assistido.cpf:

            # Só bloqueia campo cpf/cnpj se o número for válido (para permitir correção)
            try:
                validate_CPF_CNPJ(assistido.cpf)
            except Exception:
                pass
            else:
                readonly_fields.append('cpf')

    perfil = PerfilCamposObrigatoriosService(request).get_perfil(tipo_pessoa=tipo_pessoa)
    requerente = request.GET.get('tipo') != "1"
    pessoa = None

    if tipo_pessoa == constantes.TIPO_PESSOA_FISICA:
        if pessoa_id is None or pessoa_id == '0':
            pessoa = forms.CadastrarPessoa(
                required_fields=perfil.configuracao_to_json(form_name='CadastrarPessoa'),
                ignored_fields=['orientacao_sexual', 'identidade_genero', 'nome_social'],
                initial=pessoa_assistida_form_initial
            )
        else:

            pessoa = forms.CadastrarPessoa(
                required_fields=perfil.configuracao_to_json(form_name='CadastrarPessoa'),
                ignored_fields=['orientacao_sexual', 'identidade_genero', 'nome_social'],
                readonly_fields=readonly_fields
            )

        moradia = forms.CadastrarMoradia(
            required_fields=perfil.configuracao_to_json(form_name='CadastrarMoradia'),
        )

        # cria arrays para CheckboxList (requerido para AngularJS)
        estruturas = EstruturaMoradia.objects.all()
        situacoes = Situacao.objects.ativos()

    else:
        if pessoa_id is None or pessoa_id == '0':
            pessoa = forms.CadastrarPessoaJuridica(
                required_fields=perfil.configuracao_to_json(form_name='CadastrarPessoa'),
                ignored_fields=['orientacao_sexual', 'identidade_genero', 'nome_social'],
                initial=pessoa_assistida_form_initial
            )
        else:
            pessoa = forms.CadastrarPessoaJuridica(
                required_fields=perfil.configuracao_to_json(form_name='CadastrarPessoa'),
                ignored_fields=['orientacao_sexual', 'identidade_genero', 'nome_social'],
                readonly_fields=readonly_fields
            )

    telefone = forms.CadastrarTelefone(
        prefix='telefone'
    )

    documento = forms.DocumentoForm(
        prefix='documento'
    )

    renda = forms.RendaForm(
        required_fields=perfil.configuracao_to_json(form_name='RendaForm'),
        prefix='renda'
    )

    endereco = forms.CadastrarEndereco(
        required_fields=perfil.configuracao_to_json(form_name='CadastrarEndereco'),
        initial=endereco_form_initial
    )

    try:
        salario_minimo = Salario.atual(tipo_pessoa).valor
    except AttributeError as e:
        # tratamento para caso não hava salário cadastrado conforme o tipo de pessoa
        logger.warning("Não há Salário cadastrado para o tipo pessoa %s. %s" % (tipo_pessoa, e))
        salario_minimo = 0

    if request.GET.get('tab'):
        tab = request.GET.get('tab')
    else:
        tab = 0

    relatorios = Relatorio.objects.filter(
        papeis=request.user.servidor.papel,
        locais__pagina=Local.PAG_ASSISTIDO_CADASTRAR
    ).ativos()

    defensorias = request.user.servidor.defensor.defensorias.values('id', 'nome', 'codigo')
    sigla_uf = settings.SIGLA_UF.upper()
    angular = 'CadastrarPessoaModel'

    template_name = 'assistido/{}/cadastrar.html'.format(settings.SIGLA_UF)

    if not os.path.exists('templates/{}'.format(template_name)):
        template_name = 'assistido/cadastrar.html'

    # renderiza pagina
    return render(request=request, template_name=template_name, context=locals())


@login_required
def listar_acesso(request, assistido_id):
    resposta = {'solicitacoes': [], 'concessoes': [], 'possui_acesso_administracao': []}

    lst = Acesso.objects.filter(
        assistido_id=assistido_id, data_revogacao=None, ativo=True
    ).order_by(
        'data_concessao', 'data_solicitacao'
    )

    for acesso in lst:
        obj = {
            'concessao': {
                'id': acesso.defensoria_id,
                'nome': acesso.defensoria.nome,
                'tipo': 'defensoria',
            } if acesso.defensoria else {
                'id': acesso.servidor_id,
                'nome': acesso.servidor.nome,
                'tipo': 'servidor',
            },
            'data_solicitacao': Util.date_to_json(acesso.data_solicitacao) if acesso.data_solicitacao else None,
            'data_concessao': Util.date_to_json(acesso.data_concessao) if acesso.data_concessao else None,
            'concedido': True if acesso.data_concessao else False,
            'dono': True if acesso.nivel == Acesso.NIVEL_ADMINISTRACAO else False,
        }

        if acesso.data_concessao:
            resposta['concessoes'].append(obj)
        else:
            resposta['solicitacoes'].append(obj)

    servidor = request.user.servidor
    resposta['possui_acesso_administracao'] = servidor.possui_acesso_administracao_em_assistido(resposta['concessoes'])

    return JsonResponse(resposta, safe=False)


@login_required
def conceder_acesso(request, pessoa_id):
    dados_acesso = Dados(request.body)
    if dados_acesso['tipo'] == 'servidor':
        acesso, created = Acesso.objects.update_or_create(
            assistido_id=pessoa_id,
            servidor_id=dados_acesso['id'] if dados_acesso['id'] else None,
            defaults={
                'data_concessao': datetime.now(),
                'concedido_por': request.user.servidor.defensor,
                'data_revogacao': None,
                'revogado_por': None,
                'nivel': Acesso.NIVEL_EDICAO
            })

    if dados_acesso['tipo'] == 'defensoria':
        acesso, created = Acesso.objects.update_or_create(
            assistido_id=pessoa_id,
            defensoria_id=dados_acesso['id'] if dados_acesso['id'] else None,
            defaults={
                'data_concessao': datetime.now(),
                'concedido_por': request.user.servidor.defensor,
                'data_revogacao': None,
                'revogado_por': None,
                'nivel': Acesso.NIVEL_EDICAO
            })

    return JsonResponse({'success': True})


@login_required
def revogar_acesso(request, pessoa_id):
    dados = Dados(request.body)
    pessoa = PessoaAssistida.objects.get(id=pessoa_id)
    if dados['tipo'] == 'defensoria':

        Acesso.objects.filter(
            assistido=pessoa,
            defensoria_id=dados['id']
        ).update(
            data_revogacao=datetime.now(),
            revogado_por=request.user.servidor.defensor
        ),

    if dados['tipo'] == 'servidor':

        Acesso.objects.filter(
            assistido=pessoa,
            servidor_id=dados['id']
        ).update(
            data_revogacao=datetime.now(),
            revogado_por=request.user.servidor.defensor
        ),

    return JsonResponse({'success': True})


@login_required
def solicitar_acesso(request, pessoa_id):
    Acesso.objects.update_or_create(
        assistido_id=pessoa_id,
        servidor_id=request.user.servidor.id,
        defaults={
            'data_solicitacao': datetime.now(),
            'data_concessao': None,
            'concedido_por': None,
            'data_revogacao': None,
            'revogado_por': None
        })
    if config.NOTIFICACAO_SOLICITACAO_SIGILO and settings.DEFAULT_FROM_EMAIL and config.SITUACOES_SIGILOSAS:
        notificar_solicitacao_acesso.apply_async(kwargs={
            'pessoa_id': pessoa_id, 'user_id': request.user.id, 'url_solar': Site.objects.get_current().domain
            }, queue='sobdemanda')

    return JsonResponse({'success': True})


@login_required
@permission_required('assistido.delete_pessoaassistida')
@reversion.create_revision(atomic=False)
def excluir(request, pessoa_id):
    pessoa = get_object_or_404(PessoaAssistida, id=pessoa_id, desativado_em=None)
    pessoa.desativar(request.user)

    reversion.set_user(request.user)
    reversion.set_comment(Util.get_comment_delete(request.user, pessoa))

    messages.success(request, u'Pessoa excluída')

    return redirect(request.GET.get('next', 'assistido_editar'))


@login_required
@permission_required('assistido.delete_documento')
def excluir_documento(request, pessoa_id, documento_id):

    success = False
    mensagem = None

    if request.method == 'POST':

        try:
            documento = Documento.objects.get(id=documento_id, pessoa_id=pessoa_id, ativo=True)
            documento.excluir(request.user.servidor)
        except Exception:
            mensagem = u'Erro ao excluir: O documento não existe!'
        else:
            mensagem = u'Documento excluído!'
            success = True

    if request.is_ajax():
        return JsonResponse({'success': success, 'mensagem': mensagem})
    else:
        if success:
            messages.success(request, mensagem)
        else:
            messages.error(request, mensagem)
        return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@permission_required('assistido.delete_filiacao')
@reversion.create_revision(atomic=False)
def excluir_filiacao(request):

    if request.method == 'POST':

        dados = simplejson.loads(request.body)

        filiacao = Filiacao.objects.filter(id=dados['id']).first()

        if filiacao:
            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_delete(request.user, filiacao))

            filiacao.delete()

            return JsonResponse({'success': True})

    return JsonResponse({'success': False})


@login_required
def excluir_endereco(request):
    """Utilizado para excluir (desativar) o endereço do Assistido na tela de edição"""

    sucesso = False
    mensagem = 'Erro ao excluir o endereço!'

    if request.method == 'POST':

        dados = simplejson.loads(request.body)

        endereco = Endereco.objects.filter(
            id=dados['id']
        ).only(
            'id',
            'principal'
        ).first()

        if endereco:
            if not endereco.principal:
                endereco.desativar(request.user)
                sucesso = True
                mensagem = 'Endereço excluído!'
            else:
                mensagem = 'Não é permitido excluir o endereço principal!'
        else:
            'Endereço inexistente.'

    return JsonResponse({'sucesso': sucesso, 'mensagem': mensagem})


@login_required
@permission_required('assistido.change_pessoaassistida')
@reversion.create_revision(atomic=False)
def excluir_telefone(request, pessoa_id):
    if request.method == 'POST':

        dados = simplejson.loads(request.body)

        if 'id' in dados and dados['id']:

            telefone = Telefone.objects.get(id=dados['id'])

            pessoa = PessoaAssistida.objects.get(id=pessoa_id)
            pessoa.telefones.remove(telefone)

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_save(request.user, pessoa, False))

            return JsonResponse({'success': True})

    return JsonResponse({'error': True})


@never_cache
@login_required
def get_json(request, assistido_id=None):
    """Utilizado para preencher o assistido em uma requisição json"""

    pessoa = None

    if assistido_id:
        pessoa = PessoaAssistida.objects.select_related(
            'naturalidade_pais',
            'profissao',
            'moradia',
            'renda',
            'patrimonio',
            'cadastrado_por__servidor'
        ).prefetch_related(
            'enderecos',
            'enderecos__bairro',
            'enderecos__municipio',
            'telefones',
            'deficiencias',
            'bens'
        ).ativos().filter(
            id=assistido_id
        ).first()

    # se nova pessoa, retorna valores padrão
    if not pessoa:
        pessoa = PessoaAssistida(
            nacionalidade=0,
            naturalidade_pais=Pais.objects.filter(iso='BR').first()
        )

    dict = pessoa.to_dict()
    return JsonResponse(dict)


@never_cache
@login_required
def get_json_by_cpf(request, cpf):
    try:
        pessoa = PessoaAssistida.objects.get(cpf=cpf)
    except ObjectDoesNotExist:
        pessoa = Pessoa(cpf=cpf)

    return JsonResponse(pessoa.to_dict())


@login_required
def get_json_enderecos_pessoa_assistida(request, pessoa_id):
    """Utilizado para listar os Endereços da Pessoa Assistida na página de Editar Assistido"""

    sucesso = False
    mensagem = 'Pessoa assistida não encontrada'

    resposta = {
        'sucesso': sucesso,
        'mensagem': mensagem
    }

    if request.method == 'GET':

        enderecos = []
        dados = None

        if pessoa_id and pessoa_id != '0':
            pessoa = Pessoa.objects.filter(
                id=pessoa_id
            ).only(
                'id',
                'enderecos__logradouro',
                'enderecos__numero',
                'enderecos__complemento',
                'enderecos__cep',
                'enderecos__bairro__id',
                'enderecos__bairro__nome',
                'enderecos__municipio__id',
                'enderecos__municipio__nome',
                'enderecos__municipio__estado__id',
                'enderecos__municipio__estado__nome',
                'enderecos__municipio__estado__uf',
                'enderecos__tipo_area',
                'enderecos__tipo',
                'enderecos__principal',
                'enderecos__cadastrado_por',
                'enderecos__modificado_por',
                'enderecos__desativado_por',
                'enderecos__cadastrado_em'
            ).first()

            if pessoa:
                sucesso = True
                mensagem = None

                i = 0
                for endereco in pessoa.enderecos.all().filter(desativado_em=None):

                    cep = None
                    if endereco.cep:
                        cep = endereco.cep

                    tipo_nome = None
                    if endereco.tipo:
                        tipo_nome = dict(Endereco.LISTA_TIPO_ENDERECO)[endereco.tipo]

                    tipo_area_nome = None
                    if endereco.tipo_area is not None:
                        tipo_area_nome = dict(Endereco.LISTA_AREA)[endereco.tipo_area]

                    bairro_id = None
                    bairro_nome = None
                    if endereco.bairro:
                        bairro_id = endereco.bairro.id
                        bairro_nome = endereco.bairro.nome

                    municipio_id = None
                    municipio_nome = None
                    estado_id = None
                    estado_nome = None
                    estado_uf = None

                    if endereco.municipio:
                        municipio_id = endereco.municipio.id
                        municipio_nome = endereco.municipio.nome

                        if endereco.municipio.estado:
                            estado_id = endereco.municipio.estado.id
                            estado_nome = endereco.municipio.estado.nome
                            estado_uf = endereco.municipio.estado.uf

                    cadastrado_por_nome = None
                    cadastrado_por_username = None
                    modificado_por_nome = None
                    modificado_por_username = None

                    if endereco.cadastrado_por:
                        cadastrado_por_nome = endereco.cadastrado_por.servidor.nome
                        cadastrado_por_username = endereco.cadastrado_por.username

                    if endereco.modificado_por:
                        modificado_por_nome = endereco.modificado_por.servidor.nome
                        modificado_por_username = endereco.modificado_por.username

                    enderecos.append({
                        'id': endereco.id,
                        'logradouro': endereco.logradouro if endereco.logradouro else None,
                        'numero': endereco.numero if endereco.numero else None,
                        'complemento': endereco.complemento if endereco.complemento else None,
                        'cep': cep if endereco.cep else None,
                        'bairro_id': bairro_id,
                        'bairro': bairro_nome,
                        'municipio_id': municipio_id,
                        'municipio': municipio_nome,
                        'estado_id': estado_id,
                        'estado_nome': estado_nome,
                        'estado': estado_uf,
                        'tipo_area': {
                            'id': endereco.tipo_area,
                            'nome': tipo_area_nome
                        },
                        'tipo': {
                            'id': endereco.tipo,
                            'nome': tipo_nome
                        },
                        'principal': endereco.principal,
                        'index': i,
                        'cadastrado_por_nome': cadastrado_por_nome,
                        'cadastrado_por_username': cadastrado_por_username,
                        'modificado_por_nome': modificado_por_nome,
                        'modificado_por_username': modificado_por_username,
                        'cadastrado_em': endereco.cadastrado_em,
                        'modificado_em': endereco.modificado_em,
                    })

                    i += 1
        elif pessoa_id == '0':
            # retornará apenas os dados de lista_tipo e lista_tipo_area
            sucesso = True

        dados = {
            'pessoa_assistida_id': pessoa_id,
            'enderecos': enderecos,
            'lista_tipo': dict(Endereco.LISTA_TIPO_ENDERECO),
            'lista_tipo_area': dict(Endereco.LISTA_AREA)
        }

        resposta.update({
            'sucesso': sucesso,
            'mensagem': mensagem,
            'dados': dados
        })

    return JsonResponse(resposta)


@login_required
def get_json_enderecos_historico_pessoa_assistida(request, pessoa_id):
    """Utilizado para buscar o histórico de endereços do assistido mostrado na página de cadastro de assitido"""

    sucesso = False
    mensagem = 'Pessoa assistida não encontrada'

    resposta = {
        'sucesso': sucesso,
        'mensagem': mensagem
    }

    if request.method == 'GET':

        enderecos_id = Pessoa.objects.filter(
            id=pessoa_id
        ).values_list(
            'enderecos__id', flat=True
        )

        historicos = EnderecoHistorico.objects.filter(
            endereco_id__in=enderecos_id
        ).select_related(
            'bairro',
            'municipio',
            'municipio__estado',
            'cadastrado_por',
            'modificado_por',
            'desativado_por',
        ).only(
            'id',
            'endereco_id',
            'logradouro',
            'numero',
            'complemento',
            'cep',
            'bairro__id',
            'bairro__nome',
            'municipio__id',
            'municipio__nome',
            'municipio__estado__id',
            'municipio__estado__nome',
            'municipio__estado__uf',
            'tipo_area',
            'tipo',
            'principal',
            'cadastrado_por',
            'modificado_por',
            'desativado_por',
            'cadastrado_em',
            'modificado_em',
            'desativado_em'
        )

        historicos_dict = []

        for endereco in historicos.all():

            cep = None
            if endereco.cep:
                cep = endereco.cep

            tipo_nome = None
            if endereco.tipo:
                tipo_nome = dict(Endereco.LISTA_TIPO_ENDERECO)[endereco.tipo]

            tipo_area_nome = None
            if endereco.tipo_area is not None:
                tipo_area_nome = dict(Endereco.LISTA_AREA)[endereco.tipo_area]

            bairro_id = None
            bairro_nome = None
            if endereco.bairro:
                bairro_id = endereco.bairro.id
                bairro_nome = endereco.bairro.nome

            municipio_id = None
            municipio_nome = None
            estado_id = None
            estado_nome = None
            estado_uf = None

            if endereco.municipio:
                municipio_id = endereco.municipio.id
                municipio_nome = endereco.municipio.nome

                if endereco.municipio.estado:
                    estado_id = endereco.municipio.estado.id
                    estado_nome = endereco.municipio.estado.nome
                    estado_uf = endereco.municipio.estado.uf

            cadastrado_por_nome = None
            cadastrado_por_username = None
            modificado_por_nome = None
            modificado_por_username = None
            desativado_por_nome = None
            desativado_por_username = None

            if endereco.cadastrado_por:
                cadastrado_por_nome = endereco.cadastrado_por.servidor.nome
                cadastrado_por_username = endereco.cadastrado_por.username

            if endereco.modificado_por:
                modificado_por_nome = endereco.modificado_por.servidor.nome
                modificado_por_username = endereco.modificado_por.username

            if endereco.desativado_por:
                desativado_por_nome = endereco.desativado_por.servidor.nome
                desativado_por_username = endereco.desativado_por.username

            historicos_dict.append({
                'id': endereco.id,
                'logradouro': endereco.logradouro if endereco.logradouro else None,
                'numero': endereco.numero if endereco.numero else None,
                'complemento': endereco.complemento if endereco.complemento else None,
                'cep': cep if endereco.cep else None,
                'bairro_id': bairro_id,
                'bairro': bairro_nome,
                'municipio_id': municipio_id,
                'municipio': municipio_nome,
                'estado_id': estado_id,
                'estado_nome': estado_nome,
                'estado': estado_uf,
                'tipo_area': {
                    'id': endereco.tipo_area,
                    'nome': tipo_area_nome
                },
                'tipo': {
                    'id': endereco.tipo,
                    'nome': tipo_nome
                },
                'principal': endereco.principal,
                'cadastrado_por_nome': cadastrado_por_nome,
                'cadastrado_por_username': cadastrado_por_username,
                'modificado_por_nome': modificado_por_nome,
                'modificado_por_username': modificado_por_username,
                'desativado_por_nome': desativado_por_nome,
                'desativado_por_username': desativado_por_username,
                'cadastrado_em': endereco.cadastrado_em,
                'modificado_em': endereco.modificado_em,
                'desativado_em': endereco.desativado_em
            })

        dados = {
            'pessoa_assistida_id': pessoa_id,
            'enderecos_historico': historicos_dict
        }

        sucesso = True
        mensagem = None

        resposta.update({
            'sucesso': sucesso,
            'mensagem': mensagem,
            'dados': dados
        })

        return JsonResponse(resposta)


@login_required
def listar_comunidade(request):
    arr = []
    lst = Pessoa.objects.filter(
        tipo=constantes.TIPO_PESSOA_JURIDICA,
        nome__icontains=request.GET.get('q', '')).order_by('nome')[:5]

    for i in lst:
        arr.append(i.to_dict())

    return JsonResponse(arr, safe=False)


@login_required
@cache_page(60 * 60 * 24 * 7)  # 7 dias
def listar_profissao(request):
    profissoes = Profissao.objects.all().distinct('nome').values_list('nome', flat=True).order_by('nome')
    return JsonResponse(list(profissoes), safe=False)


@never_cache
@login_required
def listar_documento(request, pessoa_id=None):

    documentos = Documento.objects.ativos().filter(pessoa_id=pessoa_id)
    resposta = []

    for documento in documentos:

        url = None
        filetype = None

        if documento.arquivo:
            url = documento.arquivo.url
            filetype, encoding = mimetypes.guess_type(documento.arquivo.url, strict=True)

        resposta.append({
            'id': documento.id,
            'nome': documento.nome,
            'arquivo': url,
            'enviado_por_nome': documento.enviado_por.nome if documento.enviado_por else None,
            'enviado_por_username': documento.enviado_por.usuario.username if documento.enviado_por else None,
            'data_enviado': documento.data_enviado,
            'filetype': filetype
        })

    return JsonResponse(resposta, safe=False)


@never_cache
@login_required
@reversion.create_revision(atomic=False)
@permission_required('assistido.add_pessoaassistida')
def salvar(request):
    """Salva a PessoaAssistida. Também é utilizado para Editar"""

    # resposta padrao
    resposta = {'success': False, 'errors': {}}
    errors = []

    if request.method == 'POST':

        # carrega e trata dados recebidos via ajax
        try:
            dados = Dados(request.body.decode('utf-8')).dados
        except RawPostDataException:
            return JsonResponse(resposta)

        pessoa_dict = dados.get('pessoa')
        # valida tipo de pessoa (default: pessoa fisica)
        if pessoa_dict.get('tipo') not in [constantes.TIPO_PESSOA_FISICA, constantes.TIPO_PESSOA_JURIDICA]:
            pessoa_dict['tipo'] = constantes.TIPO_PESSOA_FISICA

        pessoa = None
        pessoa_service = PessoaAssistidaService(pessoa_dict, request)

        # verifica se já existe outra pessoa com o cpf informado
        cpf_cnpj_existe = False

        if pessoa_dict.get('cpf'):

            pessoa_dict['cpf'] = Util.so_numeros(pessoa_dict.get('cpf'))
            cpf_cnpj_existe = pessoa_service.cpf_cnpj_existe(pessoa_dict.get('cpf'), pessoa_dict.get('id'))

            if cpf_cnpj_existe:
                errors.append(['CPF/CNPJ', 'O número informado já está vinculado a outra pessoa!'])

        if not cpf_cnpj_existe:

            # tenta carregar registro, se nao conseguir carrega novo
            if pessoa_dict.get('id') is not None and pessoa_dict.get('id') != 0:
                pessoa_service.pessoa = pessoa = PessoaAssistida.objects.filter(id=pessoa_dict.get('id')).only('id').first()
            else:
                pessoa_service.pessoa = pessoa = PessoaAssistida()

            # força atualização dos dados de auditoria
            pessoa.modificado_por = request.user
            pessoa.modificado_em = datetime.now()
            pessoa.tipo = pessoa_service.tipo_pessoa

            pessoa_service.clean_data()

            pessoa_form = pessoa_service.get_form()

            if pessoa_form.is_valid():

                with transaction.atomic():

                    # Salva registro da pessoa
                    novo = (pessoa_dict.get('id') is None)
                    pessoa_service.pessoa = pessoa = pessoa_form.save()

                    _, moradia_errors = pessoa_service.salvar_moradia()
                    errors += moradia_errors

                    _, enderecos_errors = pessoa_service.salvar_enderecos()
                    errors += enderecos_errors

                    _, telefones_errors = pessoa_service.salvar_telefones()
                    errors += telefones_errors

                    _, filiacoes_errors = pessoa_service.salvar_filiacoes()
                    errors += filiacoes_errors

                    pessoa_service.salvar_membros()

                    _, renda_errors = pessoa_service.salvar_renda()
                    errors += renda_errors

                    pessoa_service.salvar_patrimonio()

                    _, foto_errors = pessoa_service.salvar_foto()
                    errors += foto_errors

                    if len(errors) > 0:
                        transaction.set_rollback(rollback=True)

            else:

                # inclui erros no array de erros
                errors += [(k, v[0]) for k, v in pessoa_form.errors.items()]

            if len(errors) == 0:

                resposta['success'] = True
                resposta['id'] = pessoa.id
                resposta['pessoa'] = pessoa.to_dict()
                resposta['pessoa']['patrimonios'] = pessoa_dict.get('patrimonios')

                pessoa_service.gerar_notificacoes()
                pessoa_service.gerar_concessoes_acesso()

                reversion.set_user(request.user)
                reversion.set_comment(Util.get_comment_save(request.user, pessoa, novo))

            else:

                resposta['errors'] = errors

    return JsonResponse(resposta)


@login_required
@permission_required('assistido.add_documento')
def salvar_documento(request, pessoa_id=None):

    if request.method == 'POST':

        pessoa_id = request.POST.get('pessoa_id', pessoa_id)
        pessoa = Pessoa.objects.only('id', 'tipo').get(id=pessoa_id)

        documento = Documento(pessoa_id=pessoa_id, enviado_por=request.user.servidor)
        form = forms.DocumentoForm(request.POST, request.FILES, instance=documento)
        errors = []

        if form.is_valid():
            documento = form.save()
        else:
            errors += [(k, v[0]) for k, v in form.errors.items()]

        if request.is_ajax():

            url = None
            filetype = None

            if documento.arquivo:
                url = documento.arquivo.url
                filetype, encoding = mimetypes.guess_type(documento.arquivo.url, strict=True)

            documento_dict = {
                'id': documento.id,
                'nome': documento.nome,
                'arquivo': url,
                'documento': documento.documento_id if documento.documento_id else None,
                'enviado_por_nome': documento.enviado_por.nome if documento.enviado_por else None,
                'enviado_por_username': documento.enviado_por.usuario.username if documento.enviado_por else None,
                'data_enviado': documento.data_enviado,
                'filetype': filetype
            }

            resposta = {
                'sucesso': len(errors) == 0,
                'errors': errors,
                'documento': documento_dict
            }

            return JsonResponse(resposta)

        else:

            url = request.META.get('HTTP_REFERER', '/')
            tab = 6 if pessoa.tipo == constantes.TIPO_PESSOA_FISICA else 4

            if url.find('tab=') == -1:
                if url.find('?') >= 0:
                    url += '&tab={}'.format(tab)
                else:
                    url += '?tab={}'.format(tab)

            # recupera parametros na URL anterior e injeta na url de editar assistido
            parsed = urlparse(url)
            url = '{}?{}'.format(
                reverse('assistido_editar', args=[pessoa.id]),
                parsed.query
            )

            return redirect(url)

    else:

        raise Http404


@login_required
@permission_required('assistido.add_pessoaassistida')
def salvar_foto(request):

    if request.method == "POST":

        try:

            nome = "{}.png".format(hashlib.md5(str(time.time()).encode('utf-8')).hexdigest())
            arquivo = os.path.join(tempfile.gettempdir(), nome)

            data = request.POST.get("imgBase64").replace("data:image/png;base64,", "")

            fp = open(arquivo, "wb")
            fp.write(base64.b64decode(data))
            fp.close()

            request.session['foto'] = arquivo

            return JsonResponse({'success': True, 'arquivo': arquivo})

        except Exception as e:
            return JsonResponse({
                'success': False,
                'erro': 'Erro ao salvar foto: {}'.format(str(e))
            })

    return JsonResponse({
        'success': False,
        'erro': 'Método deve ser POST'
    })


@login_required
@permission_required('assistido.add_pessoaassistida')
def salvar_foto_agora(request, pessoa_id):
    if request.method == "POST":

        try:

            arquivo = "{}.png".format(hashlib.md5(str(time.time()).encode()).hexdigest())
            data = request.POST.get("imgBase64").replace("data:image/png;base64,", "")

            pessoa = PessoaAssistida.objects.get(id=pessoa_id)
            pessoa.foto.save(arquivo, ContentFile(base64.b64decode(data)))

        except Exception as e:
            return JsonResponse({
                'success': False,
                'erro': 'Erro ao salvar foto: {}'.format(str(e))
            })

        return JsonResponse({'success': True, 'arquivo': arquivo})

    return JsonResponse({
        'success': False,
        'erro': 'Método deve ser POST'
    })


@login_required
def index_campos_obrigatorios(request):
    perfis = PerfilCamposObrigatorios.objects.all()
    return render(request, "assistido/campos_obrigatorios_index.html", locals())


@login_required
def configurar_campos_obrigatorios(request, perfil_id):

    perfil = get_object_or_404(PerfilCamposObrigatorios, id=perfil_id)

    pessoa = forms.CadastrarPessoa(
        prefix='pessoa',
        required_fields=perfil.configuracao_to_json(form_name='CadastrarPessoa')
    )

    endereco = forms.CadastrarEndereco(
        prefix='endereco',
        required_fields=perfil.configuracao_to_json(form_name='CadastrarEndereco')
    )

    moradia = forms.CadastrarMoradia(
        prefix='moradia',
        required_fields=perfil.configuracao_to_json(form_name='CadastrarMoradia')
    )

    renda = forms.RendaForm(
        prefix='renda',
        required_fields=perfil.configuracao_to_json(form_name='RendaForm')
    )

    return render(request, "assistido/campos_obrigatorios_configurar.html", locals())


@login_required
@permission_required('assistido.change_perfilcamposobrigatorios')
@reversion.create_revision(atomic=False)
def salvar_campos_obrigatorios(request, perfil_id):

    perfil = get_object_or_404(PerfilCamposObrigatorios, id=perfil_id)

    if request.method == 'POST':

        formularios = []

        formularios.append(
            forms.CadastrarPessoa(
                prefix='pessoa',
                required_fields=perfil.configuracao_to_json(form_name='CadastrarPessoa')
            )
        )

        formularios.append(
            forms.CadastrarEndereco(
                prefix='endereco',
                required_fields=perfil.configuracao_to_json(form_name='CadastrarEndereco')
            )
        )

        formularios.append(
            forms.CadastrarMoradia(
                prefix='moradia',
                required_fields=perfil.configuracao_to_json(form_name='CadastrarMoradia')
            )
        )

        formularios.append(
            forms.RendaForm(
                prefix='renda',
                required_fields=perfil.configuracao_to_json(form_name='RendaForm')
            )
        )

        data = perfil.configuracao_to_json()

        for form in formularios:

            form_name = form.__class__.__name__

            if form_name not in data:
                data[form_name] = {}

            for field in form.fields:
                data[form_name][field] = True if request.POST.get('{}-{}'.format(form.prefix, field)) else False

        perfil.configuracao = simplejson.dumps(data)
        perfil.save()

        reversion.set_user(request.user)
        reversion.set_comment(Util.get_comment_save(request.user, perfil, False))

        messages.success(request, u'Perfil "{}" atualizado com sucesso!'.format(perfil.nome))

    return redirect(reverse('campos_obrigatorios_index'))


@login_required
@permission_required('assistido.unificar_pessoa')
@reversion.create_revision(atomic=False)
def unificar(request):

    # recupera registro principal
    principal_id = request.POST.get('principal')
    # recupera registros que serão unificados
    registros = request.POST.getlist('registros')
    # remove da lista o registro principal
    registros.remove(principal_id)

    agora = timezone.now()

    principal = PessoaAssistida.objects.get(id=principal_id)
    pessoas = PessoaAssistida.objects.filter(id__in=registros)

    for pessoa in pessoas:
        # transfere atendimentos
        partes = pessoa.atendimentos.filter(ativo=True)
        try:
            partes.update(pessoa=principal)
        except IntegrityError:
            for parte in partes:
                # atualiza dados da parte da pessoa que vai permanecer
                parte.atendimento.add_pessoa(
                    pessoa_id=principal_id,
                    tipo=parte.tipo,
                    responsavel=parte.responsavel
                )
                # inativa vinculo de pessoa que vai ser desativada
                parte.ativo = False
                parte.save()

        # transfere prisões (LIVRE)
        pessoa.prisao_set.update(pessoa=principal)
        # transfere faltas (LIVRE)
        pessoa.falta_set.update(pessoa=principal)
        # transfere historico (LIVRE)
        pessoa.historico_set.update(pessoa=principal)
        # desativa cadastro
        pessoa.desativar(request.user, agora)

    return redirect(request.POST.get('next'))


@login_required
@transaction.atomic
def excluir_patrimonio_assistido_por_id(request, patrimonio_id):
    if request.method == "DELETE":
        try:
            with transaction.atomic():
                patrimonio = Patrimonial.objects.get(id=patrimonio_id)
                patrimonio.desativar(request.user)
                return JsonResponse({'success': True}, safe=False)
        except IntegrityError:
            return JsonResponse({'success': False, 'error': 'Não foi possivel excluir patrimônio'}, safe=False)
