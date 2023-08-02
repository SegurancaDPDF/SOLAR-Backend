# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# standard
from datetime import datetime
import os
import re

# third-party
from constance import config

# django
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.urls import reverse
from django.utils.functional import cached_property

# project
from contrib import constantes
from contrib.models import Bairro, Dados, Endereco, Telefone
from notificacoes.tasks import notificar_alteracao_cadastro_assistido
# application
from . import forms
from . import models


class PessoaAssistidaService(object):

    pessoa: models.PessoaAssistida = None
    pessoa_dict = None
    request = None
    dados = None

    def __init__(self, pessoa_dict: dict, request) -> None:
        self.pessoa_dict = pessoa_dict
        self.request = request
        self.dados = Dados(request.body.decode('utf-8')).dados

    def get_dict_from_key(self, key: str) -> dict:
        if key in self.pessoa_dict and type(self.pessoa_dict[key]) == dict:
            return self.pessoa_dict[key]
        else:
            return dict()

    def get_list_from_key(self, key: str) -> list:
        if key in self.pessoa_dict and type(self.pessoa_dict[key]) == list:
            return self.pessoa_dict[key]
        else:
            return list()

    @staticmethod
    def cpf_cnpj_existe(cpf, pessoa_id=None):

        pessoas = models.PessoaAssistida.objects.ativos().filter(cpf=cpf)

        if pessoa_id:
            pessoas = pessoas.exclude(id=pessoa_id)

        return pessoas.exists()

    @property
    def enderecos(self) -> list:
        return self.dados.get('enderecos', [])

    @cached_property
    def perfil(self):
        return PerfilCamposObrigatoriosService(self.request).get_perfil(tipo_pessoa=self.tipo_pessoa)

    @cached_property
    def tipo_cadastro(self):
        return self.pessoa_dict.get('tipo_cadastro')

    @cached_property
    def tipo_parte(self) -> int:
        return self.request.GET.get('tipo')

    @cached_property
    def tipo_pessoa(self):
        return self.pessoa_dict['tipo']

    def clean_data(self):

        self.pessoa_dict['situacoes'] = self.situacoes_to_list()
        self.pessoa_dict['profissao'] = self.get_or_create_profissao()

        if self.tipo_pessoa == constantes.TIPO_PESSOA_FISICA:

            if self.pessoa_dict.get('data_nascimento') is not None:
                self.pessoa_dict['data_nascimento'] = self.pessoa_dict['data_nascimento'][0:10]

            if self.pessoa_dict.get('rg_data_expedicao') is not None:
                self.pessoa_dict['rg_data_expedicao'] = self.pessoa_dict['rg_data_expedicao'][0:10]

        else:

            self.pessoa_dict['data_nascimento'] = None
            self.pessoa_dict['rg_data_expedicao'] = None

        self.clean_data_enderecos()

    def clean_data_enderecos(self):
        if self.enderecos is not None:
            for endereco in self.enderecos:
                if endereco.get('bairro_id') is None and endereco.get('bairro') is not None:

                    nome_bairro = re.sub(' +', ' ', endereco.get('bairro').strip().upper())

                    try:
                        bairro, _ = Bairro.objects.get_or_create(
                            municipio_id=endereco.get('municipio_id'),
                            nome__iexact=nome_bairro,
                            desativado_em=None,
                            defaults={
                                # necessário por ter usado uma func no get_or_create para esse field
                                'nome': nome_bairro
                            }
                        )
                    except Bairro.MultipleObjectsReturned:
                        bairro = Bairro.objects.filter(
                            municipio_id=endereco.get('municipio_id'),
                            nome__iexact=nome_bairro,
                            desativado_em=None
                        ).first()
                    finally:
                        endereco['bairro_id'] = bairro.id

    def modificado_hoje(self) -> bool:
        resultado = False
        modificado_em = self.pessoa_dict.get('modificado_em')

        if modificado_em:
            if not isinstance(modificado_em, datetime):
                modificado_em = datetime.strptime(modificado_em[0:10], "%Y-%m-%d")
            if modificado_em.date() == datetime.now().date():
                resultado = True

        return resultado

    def situacoes_to_list(self) -> list:

        situacoes = []
        situacoes_dict = self.get_dict_from_key('situacoes')

        for key in situacoes_dict:
            if key and situacoes_dict[key]:
                situacoes.append(key)

        return situacoes

    def gerar_concessoes_acesso(self):
        # Ao cadastrar o assistido cria concessão de acesso para todos as lotações do usuário que está cadastrando  # noqa: E501
        if self.pessoa_dict.get('id') is None and config.SITUACOES_SIGILOSAS and self.pessoa_dict.get('situacoes'):
            situacoes = models.Situacao.objects.filter(id__in=self.pessoa_dict.get('situacoes'))
            situacao_sigilo_selecionada = False
            for situacao in situacoes:
                situacoes_configuradas = re.sub(r"\s+", "", config.SITUACOES_SIGILOSAS)
                if situacoes_configuradas.find(',') != -1:
                    situacoes_configuradas = situacoes_configuradas.split(',')
                else:
                    situacoes_configuradas = ['', situacoes_configuradas]

                for situacao_configurada in situacoes_configuradas:
                    if situacao.codigo == situacao_configurada:
                        situacao_sigilo_selecionada = True

            if situacao_sigilo_selecionada:
                conceder_acesso_dono(self.request.user.servidor.defensor, self.request.user.servidor.defensor.defensorias, self.pessoa.id)  # noqa: E501

        # Caso seja selecionado a situação sigilosa e não houver acessos cadastrados
        # (assistido criado anteriormente a feature) é inserido novo acesso para quem está editando o registro
        if self.pessoa_dict.get('id') is not None and config.SITUACOES_SIGILOSAS:
            if not models.Acesso.objects.filter(assistido_id=self.pessoa.id).exists():
                conceder_acesso_dono(self.request.user.servidor.defensor, self.request.user.servidor.defensor.defensorias, self.pessoa.id)  # noqa: E501

    def gerar_notificacoes(self):
        # cria a tarefa no celery para notificar usuarios sobre a alteração do cadastro do assistido (1x no dia)
        if config.NOTIFICAR_ALTERACAO_CADASTRO_ASSISTIDO and not self.modificado_hoje:
            notificar_alteracao_cadastro_assistido.apply_async(kwargs={
                'user_remetente_id': self.request.user.id,
                'url_callback': self.request.build_absolute_uri(
                    reverse('assistido_editar', args=[self.pessoa.id])
                ),
                'assistido_id': self.pessoa.id,
            }, queue='sobdemanda')

    def get_or_create_profissao(self):

        profissao = None
        nome = self.pessoa_dict.get('profissao')

        if nome and self.tipo_pessoa == constantes.TIPO_PESSOA_FISICA:

            nome = nome.strip().upper()
            profissao = models.Profissao.objects.filter(nome=nome).only('id').order_by('id').first()

            if not profissao:
                profissao = models.Profissao.objects.create(nome=nome)

        return profissao

    def get_form(self):

        if self.tipo_pessoa == constantes.TIPO_PESSOA_FISICA:
            return forms.CadastrarPessoa(
                data=self.pessoa_dict,
                instance=self.pessoa,
                required_fields=self.perfil.configuracao_to_json(form_name='CadastrarPessoa')
            )
        else:
            return forms.CadastrarPessoaJuridica(
                data=self.pessoa_dict,
                instance=self.pessoa,
                required_fields=self.perfil.configuracao_to_json(form_name='CadastrarPessoa')
            )

    def moradia_estrutura_to_list(self) -> list:
        moradia_estrutura = []
        for estrutura in self.get_list_from_key('estrutura'):
            if self.pessoa_dict.get('estrutura')[estrutura]:
                moradia_estrutura.append(estrutura)

        return moradia_estrutura

    def salvar_enderecos(self) -> tuple[bool, list]:
        if self.tipo_cadastro == models.PessoaAssistida.CADASTRO_COMPLETO and self.enderecos:
            return self.salvar_enderecos_completo()
        elif self.tipo_cadastro == models.PessoaAssistida.CADASTRO_SIMPLIFICADO:
            self.salvar_enderecos_simplificado()
        return True, []

    def possui_endereco_principal(self):
        # verifica se possui endereço principal
        for endereco in self.enderecos:
            if endereco.get('principal'):
                return True

        return False

    def salvar_enderecos_completo(self) -> tuple[bool, list]:

        errors = []
        enderecos_id = []

        # se houver mais de um endereço e nenhum for o principal
        if len(self.enderecos) > 1 and not self.possui_endereco_principal():

            errors.append(['Endereço', 'Deve haver ao menos um endereço principal'])

        else:

            for endereco in self.enderecos:

                endereco_existente = Endereco.objects.filter(
                    id=endereco.get('id')
                ).only(
                    'logradouro',
                    'numero',
                    'complemento',
                    'cep',
                    'bairro_id',
                    'municipio_id',
                    'tipo_area',
                    'principal',
                    'tipo'
                ).first()

                salvar_endereco = False
                if endereco_existente:
                    if endereco_existente.logradouro != endereco.get('logradouro'):
                        salvar_endereco = True

                    elif endereco_existente.numero != endereco.get('numero'):
                        salvar_endereco = True

                    elif endereco_existente.complemento != endereco.get('complemento'):
                        salvar_endereco = True

                    elif endereco_existente.cep != endereco.get('cep'):
                        salvar_endereco = True

                    elif endereco_existente.bairro_id != endereco.get('bairro_id'):
                        salvar_endereco = True

                    elif endereco_existente.municipio_id != endereco.get('municipio_id'):
                        salvar_endereco = True

                    elif endereco_existente.tipo_area != endereco.get('tipo_area').get('id'):
                        salvar_endereco = True

                    elif endereco_existente.principal != endereco.get('principal'):
                        salvar_endereco = True

                    elif endereco_existente.tipo != endereco.get('tipo').get('id', Endereco.TIPO_ENDERECO_RESIDENCIAL):  # noqa: E501
                        salvar_endereco = True

                    # se houver apenas um endereço o mesmo será definido como principal
                    elif len(self.enderecos) == 1 and not endereco.get('principal'):
                        salvar_endereco = True
                        endereco['principal'] = True

                # se houve modificação no endereço já existente ou se é endereço novo
                if salvar_endereco or not endereco_existente:

                    obj, novo = Endereco.objects.update_or_create(
                        id=endereco.get('id'),
                        defaults={
                            'logradouro': endereco.get('logradouro'),
                            'numero': endereco.get('numero'),
                            'complemento': endereco.get('complemento'),
                            'cep': endereco.get('cep'),
                            'bairro_id': endereco.get('bairro_id'),
                            'municipio_id': endereco.get('municipio_id'),
                            'tipo_area': endereco.get('tipo_area').get('id'),
                            'principal': endereco.get('principal'),
                            'tipo': endereco.get('tipo').get('id', Endereco.TIPO_ENDERECO_RESIDENCIAL),
                        }
                    )

                    if novo:
                        self.pessoa.enderecos.add(obj)

                    enderecos_id.append(obj.id)

                elif endereco_existente:
                    enderecos_id.append(endereco.get('id'))

            # desativar os endereços excluídos
            for endereco in self.pessoa.enderecos.all().filter(desativado_em=None):
                if endereco.id not in enderecos_id:
                    endereco.desativar(self.request.user)

        return (len(errors) > 0), errors

    def salvar_enderecos_simplificado(self):

        # Se não tem endereço, mudou de município ou cadastro de endereço completo, cria novo endereço
        if not self.pessoa.endereco or self.pessoa.endereco.municipio_id != self.pessoa_dict.get('municipio') or config.MODO_EXIBICAO_ENDERECO_129 == '1':  # noqa: E501

            # Remove qualquer endereço principal que já possuía antes
            for endereco in self.pessoa.enderecos.principais():
                endereco.principal = False
                endereco.desativar(self.request.user)

            bairro = None

            if self.pessoa_dict.get('bairro'):
                try:
                    bairro, _ = Bairro.objects.get_or_create(
                        municipio_id=self.pessoa_dict.get('municipio'),
                        nome__iexact=self.pessoa_dict.get('bairro'),
                        desativado_em=None,
                        defaults={
                            # necessário por ter usado uma func no get_or_create para esse field
                            'nome': self.pessoa_dict.get('bairro')
                        }
                    )
                except Bairro.MultipleObjectsReturned:
                    bairro = Bairro.objects.filter(
                        municipio_id=self.pessoa_dict.get('municipio'),
                        nome__iexact=self.pessoa_dict.get('bairro'),
                        desativado_em=None
                    ).first()

            # cria e adiciona novo endereço para o município informado
            endereco = Endereco.objects.create(
                municipio_id=self.pessoa_dict.get('municipio'),
                bairro=bairro,
                logradouro=self.pessoa_dict.get('logradouro'),
                numero=self.pessoa_dict.get('numero'),
                complemento=self.pessoa_dict.get('complemento'),
                cep=self.pessoa_dict.get('cep'),
                principal=True
            )

            self.pessoa.enderecos.add(endereco)

    def salvar_filiacoes(self) -> tuple[bool, list]:
        from atendimento.atendimento.models import Pessoa as PessoaAtendimento

        errors = []

        if self.tipo_pessoa == constantes.TIPO_PESSOA_JURIDICA:

            self.pessoa.filiacoes.all().delete()

        else:

            for filiacao in self.get_list_from_key('filiacao'):

                if 'nome' in filiacao and filiacao['nome']:

                    models.Filiacao.objects.update_or_create(
                        id=filiacao['id'],
                        defaults={
                            'pessoa_assistida': self.pessoa,
                            'nome': filiacao['nome'],
                            'tipo': filiacao['tipo']
                        }
                    )

                elif self.tipo_parte == PessoaAtendimento.TIPO_REQUERENTE:

                    errors.append([models.Filiacao.LISTA_TIPO[filiacao['tipo']][1], 'Esse campo é obrigatório.'])

        return (len(errors) > 0), errors

    def salvar_membros(self):

        for membro in self.get_list_from_key('membros'):

            if membro['id'] and membro['desativado_em']:

                models.Dependente.objects.filter(
                    id=membro['id']
                ).update(
                    desativado_por=self.request.user,
                    desativado_em=datetime.now()
                )

            elif 'nome' in membro and membro['nome']:

                models.Dependente.objects.update_or_create(
                    id=membro['id'],
                    defaults={
                        'pessoa': self.pessoa,
                        'nome': membro.get('nome'),
                        'renda': membro.get('renda'),
                        'parentesco': membro.get('parentesco'),
                        'situacao_dependente_id': membro.get('situacao_dependente'),
                        'tipo_renda_id': membro.get('tipo_renda'),
                    }
                )

    def salvar_foto(self) -> tuple[bool, list]:

        errors = []
        foto = self.request.session.get('foto')

        if foto:
            nome = os.path.basename(foto)
            try:
                with open(foto, 'rb') as image:
                    self.pessoa.foto.save(nome, image)
            except Exception:
                errors.append(['Foto', 'Erro ao salvar'])

            self.request.session['foto'] = None

        return (len(errors) > 0), errors

    def salvar_moradia(self) -> tuple[bool, list]:

        errors = []
        moradia = self.pessoa_dict.get('moradia')

        if moradia and self.tipo_pessoa == constantes.TIPO_PESSOA_FISICA:

            moradia['estrutura'] = self.moradia_estrutura_to_list()

            moradia_form = forms.CadastrarMoradia(
                data=moradia,
                instance=self.pessoa.moradia,
                required_fields=self.perfil.configuracao_to_json(form_name='CadastrarMoradia')
            )

            if moradia_form.is_valid():
                self.pessoa.moradia = moradia_form.save()
                self.pessoa.save()
            else:
                errors = [(k, v[0]) for k, v in moradia_form.errors.items()]

        return (len(errors) > 0), errors

    def salvar_patrimonio(self):
        for patrimonio in self.get_list_from_key('patrimonios'):
            patrimonial, _ = models.Patrimonial.objects.update_or_create(
                id=patrimonio.get('id'),
                defaults={
                    'tipo_id': patrimonio.get('tipo').get('id'),
                    'valor': float(patrimonio.get('valor')),
                    'descricao': patrimonio.get('descricao'),
                    'eh_bem_familia': False if patrimonio.get('eh_bem_familia') is None else patrimonio.get('eh_bem_familia'),  # noqa: E501
                    'pessoa': self.pessoa
                }
            )
            patrimonio['id'] = patrimonial.id

    def salvar_renda(self):

        errors = []

        # Renda
        if hasattr(self.pessoa, 'renda'):
            renda = self.pessoa.renda
        else:
            renda = models.Renda(pessoa=self.pessoa)

        renda_form = forms.RendaForm(
            data=self.pessoa_dict,
            instance=renda,
            required_fields=self.perfil.configuracao_to_json(form_name='RendaForm')
        )

        if renda_form.is_valid():
            renda_form.save()
        else:
            errors = [(k, v[0]) for k, v in renda_form.errors.items()]

        return (len(errors) > 0), errors

    def salvar_telefones(self):

        errors = []

        for telefone in self.get_list_from_key('telefones'):

            if telefone['numero'] is not None:

                try:
                    obj, _ = Telefone.objects.update_or_create(
                        ddd=telefone['ddd'],
                        numero=telefone['numero'],
                        tipo=telefone['tipo'],
                        defaults={
                            'nome': telefone.get('nome')
                        }
                    )
                except Telefone.MultipleObjectsReturned:
                    telefones = Telefone.objects.filter(
                        ddd=telefone['ddd'],
                        numero=telefone['numero'],
                        tipo=telefone['tipo']
                    )

                    telefones.update(nome=telefone.get('nome'))
                    obj = telefones.first()

                if telefone['id'] != obj.id and telefone['id'] is not None:

                    try:
                        self.pessoa.telefones.remove(Telefone.objects.get(id=telefone['id']))
                    except Exception:
                        errors.append(['Telefone', 'Erro ao excluir'])

                self.pessoa.telefones.add(obj)

        return (len(errors) > 0), errors


class PerfilCamposObrigatoriosService(object):
    request = None

    def __init__(self, request) -> None:
        self.request = request

    def get_tipo_parte(self):
        if self.request.GET.get('tipo') == '1':
            return models.PerfilCamposObrigatorios.PARTE_REQUERIDO
        else:
            return models.PerfilCamposObrigatorios.PARTE_REQUERENTE

    def get_parte_principal(self):
        return self.request.GET.get('principal') != "false"

    def get_tipo_processo(self):
        if self.request.GET.get('processo') == "true":
            return models.PerfilCamposObrigatorios.TIPO_PROCESSO
        else:
            return models.PerfilCamposObrigatorios.TIPO_ATENDIMENTO

    def get_perfil(self, tipo_pessoa) -> models.PerfilCamposObrigatorios:
        """Utilizado para buscar o perfil de campos obrigatórios. Auxilia no preenchimento de forms"""

        q = (Q(tipo_processo=self.get_tipo_processo()) | Q(tipo_processo=models.PerfilCamposObrigatorios.TIPO_TODOS))
        q &= (Q(tipo_parte=self.get_tipo_parte()) | Q(tipo_parte=models.PerfilCamposObrigatorios.PARTE_TODAS))
        q &= (Q(parte_principal=self.get_parte_principal()) | Q(parte_principal=None))
        q &= Q(tipo_pessoa=tipo_pessoa)

        perfil = models.PerfilCamposObrigatorios.objects.filter(q).order_by(
            'tipo_processo',
            'tipo_parte',
            'parte_principal'
        ).first()

        if not perfil:
            perfil = models.PerfilCamposObrigatorios()

        return perfil


def remove_imovel_bem_familia(patrimonios):
    for patrimonio in patrimonios:
        nome_patrimonio = patrimonio['tipo']['nome']
        if nome_patrimonio == 'Imóveis':
            patrimonios.remove(patrimonio)

    return patrimonios


def conceder_acesso_dono(usuario, defensorias, pessoa_id):
    for defensoria in defensorias:
        models.Acesso.objects.update_or_create(
            assistido_id=pessoa_id,
            defensoria_id=defensoria.id,
            defaults={
                'data_concessao': datetime.now(),
                'concedido_por': usuario,
                'data_revogacao': None,
                'revogado_por': None,
                'nivel': models.Acesso.NIVEL_ADMINISTRACAO
            })


def calcula_valor_deducao_por_tipo_renda_cadastro_principal(id_assistido):
    valor_deducao_por_tipo_renda = 0.0
    try:
        dados = models.PessoaAssistida.objects.get(id=id_assistido).renda.__dict__
        if 'tipo_renda' in dados and dados['tipo_renda'] is not None:
            tipo_renda_cadastro_principal = models.TipoRenda.objects.get(id=dados['tipo_renda'])
            if tipo_renda_cadastro_principal.eh_deducao_salario_minimo:
                if float(dados['ganho_mensal']) > float(models.Salario.atual().valor):
                    valor_deducao_por_tipo_renda += float(models.Salario.atual().valor)
                else:
                    valor_deducao_por_tipo_renda += float(dados['ganho_mensal'])
            elif tipo_renda_cadastro_principal.valor_maximo_deducao > 0:
                if float(dados['ganho_mensal']) > tipo_renda_cadastro_principal.valor_maximo_deducao:
                    valor_deducao_por_tipo_renda += float(tipo_renda_cadastro_principal.valor_maximo_deducao)  # noqa: E501
                else:
                    valor_deducao_por_tipo_renda += float(dados['ganho_mensal'])
        return valor_deducao_por_tipo_renda
    except ObjectDoesNotExist:
        return 0.0


def calcula_valor_deducao_por_situacao_cadastro_principal(id_assistido):
    situacoes_abatimento = list(models.Situacao.objects.filter(eh_situacao_deducao=True).values_list('id', flat=True))
    situacoes_assistido = list(models.PessoaAssistida.objects.get(id=id_assistido).situacoes.all().values_list("id", flat=True))
    quantidade_membros_deducao_por_situacao = 0
    for situacao_assistido in situacoes_assistido:
        if situacao_assistido in situacoes_abatimento:
            quantidade_membros_deducao_por_situacao += 1
    return quantidade_membros_deducao_por_situacao


def calcula_valor_deducao_por_tipo_renda_membros_familia(membros):
    valor_deducao_por_tipo_renda = 0.0
    for membro in membros:
        if membro['id'] and membro['tipo_renda'] is not None:
            tipo_renda = models.TipoRenda.objects.get(id=membro['tipo_renda'])
            if tipo_renda.eh_deducao_salario_minimo:
                if float(membro['renda']) > float(models.Salario.atual().valor):
                    valor_deducao_por_tipo_renda += float(models.Salario.atual().valor)
                else:
                    valor_deducao_por_tipo_renda += float(membro['renda'])
            elif tipo_renda.valor_maximo_deducao > 0:
                if float(membro['renda']) > tipo_renda.valor_maximo_deducao:
                    valor_deducao_por_tipo_renda += float(tipo_renda.valor_maximo_deducao)
                else:
                    valor_deducao_por_tipo_renda += float(membro['renda'])
    return valor_deducao_por_tipo_renda


def calcula_quantidade_membros_deducao_por_situacao(membros):
    situacoes_abatimento = list(models.Situacao.objects.filter(eh_situacao_deducao=True).values_list('id', flat=True))
    quantidade_membros_deducao_por_situacao = 0
    for membro in membros:
        if membro['id'] and membro['situacao_dependente'] is not None and membro['situacao_dependente'] in situacoes_abatimento:
            quantidade_membros_deducao_por_situacao += 1
    return quantidade_membros_deducao_por_situacao
