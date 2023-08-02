# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import json as simplejson
import logging
import os
from datetime import date, datetime
from decimal import Decimal

import reversion
from constance import config
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import deletion, Sum
from django.templatetags.static import static

# Bibliotecas de terceiros
from django.utils.functional import cached_property
from django.db.models import Q

# Solar
from core.models import AuditoriaAbstractMixin
from core.managers import AuditoriaBaseManager
from contrib import constantes
from contrib.models import Endereco, Salario, Util, Telefone
from contrib.validators import validate_CPF_CNPJ, validate_file_size_extension
from contrib.models import Servidor


# Modulos locais
from . import managers

logger = logging.getLogger(__name__)

__all__ = (
    'Pessoa',
    'Filiacao',
    'Profissao',
    'Bem',
    'EstruturaMoradia',
    'Moradia',
    'PessoaAssistida',
    'Documento',
    'Renda',
    'Patrimonio',
    'Patrimonial',
    'PatrimonialTipo',
    'Imovel',
    'Movel',
    'Semovente'
)


class Pessoa(AuditoriaAbstractMixin):
    SEXO_MASCULINO = 0
    SEXO_FEMININO = 1
    SEXO_DESCONHECIDO = 2

    LISTA_SEXO = (
        (SEXO_MASCULINO, 'Masculino'),
        (SEXO_FEMININO, 'Feminino'),
        (SEXO_DESCONHECIDO, 'Desconhecido / Não informado'),
    )

    CERTIDAO_NASCIMENTO = 'CN'
    CERTIDAO_CASAMENTO = 'CC'

    LISTA_CERTIDAO = (
        (CERTIDAO_NASCIMENTO, 'Nascimento'),
        (CERTIDAO_CASAMENTO, 'Casamento'),
    )

    CADASTRO_SIMPLIFICADO = 10
    CADASTRO_COMPLETO = 20

    LISTA_CADASTRO = (
        (CADASTRO_SIMPLIFICADO, 'Simplificado'),
        (CADASTRO_COMPLETO, 'Completo'),
    )

    nome = models.CharField(max_length=256, db_index=True)
    apelido = models.CharField(max_length=256, null=True, blank=True, default=None)
    data_nascimento = models.DateField('Data de nascimento', null=True, blank=True, default=None)
    sexo = models.SmallIntegerField('Gênero', choices=LISTA_SEXO, null=True, blank=True, default=None)
    sexo.system_check_deprecated_details = dict(
        msg='O campo Pessoa.sexo foi depreciado, pois passou a referenciar a tabela Genero_Pessoa.',
        hint='Retire as referências ao campo dos seus relatórios antes que ele seja removido',
        id='fields.CS002'
    )

    cpf = models.CharField('CPF', max_length=32, null=True, blank=True, default=None, db_index=True,
                           validators=[validate_CPF_CNPJ])

    rg_numero = models.CharField(u'Nº RG', max_length=32, null=True, blank=True, default=None)
    rg_orgao = models.CharField(u'Orgão RG', max_length=32, null=True, blank=True)
    rg_data_expedicao = models.DateField('Data expedição RG', null=True, blank=True, default=None)

    certidao_tipo = models.CharField('Tipo Certidão Civil', choices=LISTA_CERTIDAO, max_length=2, null=True, blank=True,
                                     default=None)
    certidao_numero = models.CharField(u'Nº Certidão Civil', max_length=32, null=True, blank=True, default=None,
                                       help_text='Novo modelo (32 dígitos)')

    enderecos = models.ManyToManyField('contrib.Endereco', blank=True)
    telefones = models.ManyToManyField('contrib.Telefone', blank=True)
    email = models.EmailField(max_length=128, null=True, blank=True, default=None)

    tipo = models.SmallIntegerField(
        'Tipo',
        choices=constantes.LISTA_TIPO_PESSOA,
        blank=False,
        default=constantes.TIPO_PESSOA_FISICA
    )
    nome_soundex = models.CharField(max_length=256, null=True, blank=True, db_index=True)
    nome_norm = models.CharField(max_length=256, null=True, blank=True, db_index=True)

    nome_social = models.CharField(max_length=256, null=True, blank=True, default=None, db_index=True)
    declara_orientacao_sexual = models.BooleanField('Declara orientação sexual', default=False)
    orientacao_sexual = models.ForeignKey(
        'contrib.OrientacaoSexual',
        null=True,
        blank=True,
        verbose_name='Orientação Sexual',
        on_delete=models.DO_NOTHING)
    declara_identidade_genero = models.BooleanField('Declara identidade de gênero', default=False)
    identidade_genero = models.ForeignKey(
        'contrib.IdentidadeGenero',
        null=True,
        blank=True,
        verbose_name='Identidade de Gênero',
        on_delete=models.DO_NOTHING)
    genero = models.ForeignKey(
        "contrib.GeneroPessoa",
        null=True,
        blank=True,
        verbose_name=("Gênero"),
        on_delete=models.DO_NOTHING)

    tipo_cadastro = models.SmallIntegerField('Tipo Cadastro', choices=LISTA_CADASTRO, null=True, blank=True)
    cadastro_protegido = models.BooleanField(
        'Cadastro protegido contra alterações (cpf/cnpj, nome/razão social, apelido/nome fantasia)', default=False)

    aderiu_zap_defensoria = models.BooleanField('Aderiu ao Zap Defensoria', default=False)
    aderiu_luna_chatbot = models.BooleanField('Aderiu a Luna Chatbot', default=False)
    aderiu_sms = models.BooleanField('Aderiu ao SMS', default=False)
    aderiu_edefensor = models.BooleanField('Aderiu ao e-Defensor', default=False)

    objects = AuditoriaBaseManager()

    class Meta:
        app_label = 'assistido'
        ordering = ['nome']
        permissions = (
            ('unificar_pessoa', u'Pode unificar pessoa'),
            ('visualizar_dados_situacao_sigilosa', u'Pode visualizar dados de pessoa em situação sigilosa'),
        )

    def __str__(self):
        return self.nome

    def soundex(self):
        return str(Util.text_to_soundex(self.nome))

    @cached_property
    def endereco(self):
        if self.id:
            return self.enderecos.select_related(
                'bairro',
                'municipio__estado'
            ).ativos().principais().first()

    def enderecos_secundarios(self):
        if self.id:
            return self.enderecos.select_related(
                'bairro',
                'municipio__estado'
            ).ativos().secundarios()

    def to_dict(self):

        d = {'bens': {}, 'estrutura': {}, 'deficiencias': {}, 'situacoes': []}

        if self.id:
            if self.endereco is not None:
                if self.endereco.tipo_area is None:
                    self.endereco.tipo_area = Endereco.AREA_URBANA
                Util.object_to_dict(self.endereco, d)
                if self.endereco.bairro is not None:
                    d['bairro'] = self.endereco.bairro.nome
                if self.endereco.municipio is not None:
                    d['municipio'] = self.endereco.municipio.id
                    d['municipio_nome'] = self.endereco.municipio.nome
                    if self.endereco.municipio.estado is not None:
                        d['estado'] = self.endereco.municipio.estado.id
                        d['estado_nome'] = self.endereco.municipio.estado.uf
        else:
            Util.object_to_dict(Endereco(), d)

        # TODO: Refatorar - Conflito de tipo endereço e tipo pessoa (tipo pessoa é crítido)
        Util.object_to_dict(self, d)

        d['moradia'] = {'tipo': Moradia.TIPO_NAO_INFORMADO}
        d['filiacao'] = []
        d['membros'] = []
        d['telefones'] = []

        if self.id:

            if self.moradia is None:
                moradia = Moradia()
            else:
                moradia = self.moradia
                for estrutura in moradia.estrutura.all():
                    d['estrutura'][estrutura.id] = True

            Util.object_to_dict(moradia, d['moradia'])

            for bem in self.bens.all():
                d['bens'][bem.id] = True

            for deficiencia in self.deficiencias.all():
                d['deficiencias'][deficiencia.id] = True

            if self.profissao is not None:
                d['profissao'] = self.profissao.nome

            lista = []
            for filiacao in self.filiacoes.all():
                lista.append(Util.object_to_dict(filiacao, {}))
            d['filiacao'] = lista

            lista = []
            for mae in self.maes:
                lista.append(Util.object_to_dict(mae, {}))
            d['mae'] = lista

            lista = []
            for membro in self.membros.ativos():
                lista.append(Util.object_to_dict(membro, {}))
            d['membros'] = lista

            lista = []
            for telefone in self.telefones.all():
                lista.append(Util.object_to_dict(telefone, {}))
            d['telefones'] = lista

        if hasattr(self, 'foto') and self.foto is True and bool(self.foto.name):
            d['foto'] = str(self.foto.url)
        else:
            d['foto'] = None

        if hasattr(self, 'renda'):
            Util.object_to_dict(self.renda, d, True)
        else:
            Util.object_to_dict(Renda(), d, True)

        if hasattr(self, 'patrimonio'):
            Util.object_to_dict(self.patrimonio, d, True)
        else:
            Util.object_to_dict(Patrimonio(), d, True)

        if hasattr(self, 'cadastrado_por'):
            if hasattr(self.cadastrado_por, 'servidor'):
                d['cadastrado_por_nome'] = self.cadastrado_por.servidor.nome
        else:
            d['cadastrado_por_nome'] = None

        if hasattr(self, 'cadastrado_em'):
            d['cadastrado_em'] = self.cadastrado_em
        else:
            d['cadastrado_em'] = None

        if hasattr(self, 'modificado_por'):
            if hasattr(self.modificado_por, 'servidor'):
                d['modificado_por_nome'] = self.modificado_por.servidor.nome
        else:
            d['modificado_por_nome'] = None

        if hasattr(self, 'modificado_em'):
            d['modificado_em'] = self.modificado_em
        else:
            d['modificado_em'] = None

        d['situacoes'] = {}
        if self.id:
            for situacao in self.situacoes.all():
                d['situacoes'][situacao.id] = True

        d['codigos_situacoes'] = {}
        if self.id:
            for situacao in self.situacoes.all():
                d['codigos_situacoes'][situacao.codigo] = True

        # Necessário para inicializar no frontend, mas os dados são carregados em outra requisição
        d['patrimonios'] = []

        d['id'] = self.id
        return d

    def to_json(self):
        return simplejson.dumps(self.to_dict())

    @property
    def idade(self):
        if self.data_nascimento:
            born = self.data_nascimento
            today = date.today()
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        else:
            return 0

    @property
    def cnpj(self):
        return self.cpf

    @property
    def razao_social(self):
        return self.nome

    @property
    def nome_fantasia(self):
        return self.apelido

    @property
    def nome_tratado(self):
        """Retorna o nome tratado com nome_social (para Pessoa Física) ou nome_fantasia (para Pessoa Jurídica)"""

        if self.nome_social:
            n = self.nome_social
        else:
            n = self.nome

        if self.tipo == constantes.TIPO_PESSOA_JURIDICA:
            if self.nome_fantasia:
                n = self.nome_fantasia
            else:
                n = self.nome

        return n

    @property
    def eh_pessoa_fisica(self):
        if self.tipo == constantes.TIPO_PESSOA_FISICA:
            return True
        else:
            return False

    @property
    def telefone_para_sms(self):
        telefone = None

        telefones = self.telefones.all().order_by('pk')
        for t in telefones:
            if ((not t.numero) or (not (t.tipo == Telefone.TIPO_SMS)) or (not t.eh_movel) or (t.ddd == 0)):
                continue
            telefone = t
            break

        return telefone

    @property
    def pode_receber_sms(self):

        pode_receber_sms = (not config.USAR_SMS or
                            not config.SERVICO_SMS_DISPONIVEL or
                            not self.aderiu_sms or
                            not self.telefone_para_sms)

        return pode_receber_sms

    @property
    def telefone_para_whatsapp(self):
        telefone = self.telefones.filter(tipo=Telefone.TIPO_WHATSAPP).first()

        if telefone is not None:
            telefone = "+55{}{}".format(telefone.ddd, telefone.numero)

        return telefone

    @property
    def possui_documentos(self):
        if self.cpf or self.rg_numero or (self.certidao_numero and self.certidao_tipo):
            return True
        else:
            return False

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        self.nome_soundex = self.soundex()
        self.nome_norm = Util.normalize(self.nome)

        if not self.declara_orientacao_sexual:
            self.orientacao_sexual = None

        if not self.declara_identidade_genero:
            self.identidade_genero = None

        super(Pessoa, self).save(force_insert, force_update, using, update_fields)


class Filiacao(models.Model):
    TIPO_MAE = 0
    TIPO_PAI = 1

    LISTA_TIPO = (
        (TIPO_MAE, u'Mãe'),
        (TIPO_PAI, u'Pai'),
    )

    pessoa_assistida = models.ForeignKey('PessoaAssistida', related_name='filiacoes', on_delete=models.DO_NOTHING)
    nome = models.CharField(max_length=256, )
    tipo = models.SmallIntegerField(choices=LISTA_TIPO)
    nome_soundex = models.CharField(max_length=256, null=True, blank=True)
    nome_norm = models.CharField(max_length=256, null=True, blank=True)

    objects = managers.FiliacaoManager()

    class Meta:
        app_label = 'assistido'
        ordering = ['nome']
        verbose_name = u'Filiação'
        verbose_name_plural = u'Filiações'

    def __str__(self):
        return self.nome

    def soundex(self):
        return str(Util.text_to_soundex(self.nome))

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.nome_soundex = self.soundex()
        self.nome_norm = Util.normalize(self.nome)
        super(Filiacao, self).save(force_insert, force_update, using, update_fields)


class Profissao(models.Model):
    codigo = models.CharField(max_length=32)
    nome = models.CharField(max_length=256)

    class Meta:
        app_label = 'assistido'
        ordering = ['nome', 'codigo']
        verbose_name = u'Profissão'
        verbose_name_plural = u'Profissões'

    def __str__(self):
        if self.codigo:
            return '{0} - {1}'.format(self.nome, self.codigo)
        else:
            return self.nome


class Bem(models.Model):
    nome = models.CharField(max_length=128)

    def __str__(self):
        return self.nome

    class Meta:
        app_label = 'assistido'


class EstruturaMoradia(models.Model):
    nome = models.CharField(max_length=128)

    def __str__(self):
        return self.nome

    class Meta:
        app_label = 'assistido'


class Moradia(models.Model):
    TIPO_PROPRIO = 0
    TIPO_PROGRAMA_HABITACIONAL = 1
    TIPO_ALUGADO = 2
    TIPO_CEDIDO = 3
    TIPO_FINANCIADO = 4
    TIPO_NAO_INFORMADO = 5

    LISTA_TIPO = (
        (TIPO_NAO_INFORMADO, u'Não Informado'),
        (TIPO_PROPRIO, u'Próprio'),
        (TIPO_PROGRAMA_HABITACIONAL, u'Programa Habitacional (Doação do Gov: Federal, Estadual ou Municipal)'),
        (TIPO_ALUGADO, u'Alugado'),
        (TIPO_CEDIDO, u'Cedido'),
        (TIPO_FINANCIADO, u'Financiado'),
    )

    tipo = models.SmallIntegerField(u'Imóvel', choices=LISTA_TIPO, default=TIPO_NAO_INFORMADO)
    num_comodos = models.SmallIntegerField(u'Nº cômodos', blank=True, null=True, default=0)
    estrutura = models.ManyToManyField('EstruturaMoradia', blank=True)

    def __str__(self):
        return self.LISTA_TIPO[self.tipo][1]

    class Meta:
        app_label = 'assistido'


class PessoaAssistida(Pessoa):
    LISTA_NACIONALIDADE = (
        (0, u'Brasileiro(a)'),
        (1, u'Brasileiro(a) Naturalizado(a)'),
        (2, u'Estrangeiro(a)'),
    )

    LISTA_ESTADO_CIVIL = (
        (0, u'Solteiro(a)'),
        (1, u'Casado(a)'),
        (2, u'Viuvo(a)'),
        (3, u'Divorciado(a)'),
        (4, u'União estável'),
        (5, u'Separado judicialmente'),
    )

    LISTA_ESCOLARIDADE = (
        (0, u'Nenhuma (Analfabeto)'),
        (1, u'Fundamental Incompleto. (1° ao 9° ano)'),
        (2, u'Fundamental Completo. (1° ao 9° ano)'),
        (3, u'Médio Incompleto. (2°grau)'),
        (4, u'Médio Completo. (2° grau)'),
        (5, u'Superior Incompleto'),
        (6, u'Superior Completo'),
        (7, u'Pós-Graduado'),
    )

    LISTA_TIPO_TRABALHO = (
        (0, u'Carteira Assinada'),
        (1, u'Autônomo'),
        (2, u'Servidor Público'),
        (3, u'Aposentado'),
        (4, u'Desempregado'),
    )

    LISTA_RENDA = (
        (0, u'Sem renda'),
        (1, u'Até um salário mínimo'),
        (2, u'De um a dois salários mínimos'),
        (3, u'De dois a três salários mínimos'),
        # @todo: Ressaltar quando selecionado/listado
        (4, u'Mais de três salários mínimos'),
    )

    LISTA_SAUDE = (
        (0, u'Cartão SUS'),
        (1, u'Plano de saúde'),
    )

    LISTA_RACA = (
        (0, u'Preta'),
        (1, u'Parda'),
        (2, u'Branca'),
        (3, u'Amarela'),
        (4, u'Indígena'),
        (5, u'Não soube responder'),
    )

    situacoes = models.ManyToManyField('Situacao', blank=True)
    estado_civil = models.SmallIntegerField('Estado Civil', choices=LISTA_ESTADO_CIVIL, null=True, blank=True)
    qtd_filhos = models.SmallIntegerField('Qtd. Filhos', null=True, blank=True)
    qtd_pessoas = models.SmallIntegerField('Qtd. Pessoas',
                                           help_text=u"Quantidade de pessoas que morando junto, incluido assistido",
                                           null=True, blank=True)
    escolaridade = models.SmallIntegerField('Escolaridade', choices=LISTA_ESCOLARIDADE, null=True, blank=True)
    tipo_trabalho = models.SmallIntegerField('Tipo de trabalho', choices=LISTA_TIPO_TRABALHO, null=True, blank=True)
    qtd_estado = models.SmallIntegerField('Qtd. anos no Estado',
                                          help_text=u"Quantidade de anos que reside no Estado em que vive", null=True,
                                          blank=True)
    raca = models.SmallIntegerField(u'Cor/Raça', choices=LISTA_RACA, null=True, blank=True)

    naturalidade = models.CharField(max_length=128, null=True, blank=True)
    naturalidade_estado = models.CharField('Naturalidade (UF)', max_length=128, null=True, blank=True)
    naturalidade_pais = models.ForeignKey(
        'contrib.Pais',
        null=True,
        blank=True,
        verbose_name='País de Origem',
        on_delete=deletion.PROTECT
    )
    nacionalidade = models.SmallIntegerField(u'Nacionalidade', choices=LISTA_NACIONALIDADE, null=True, blank=True)

    cartao_sus = models.BooleanField('Cartão SUS', default=False)
    plano_saude = models.BooleanField('Plano de Saúde', default=False)
    deficiencias = models.ManyToManyField('contrib.Deficiencia', blank=True)

    profissao = models.ForeignKey(
        'Profissao',
        null=True,
        blank=True,
        on_delete=deletion.PROTECT
    )
    moradia = models.ForeignKey(
        'Moradia',
        null=True,
        blank=True,
        on_delete=deletion.PROTECT
    )
    bens = models.ManyToManyField('Bem', blank=True)

    foto = models.ImageField("Foto", upload_to='assistido', null=True, blank=True, default=None)

    automatico = models.BooleanField(default=False)

    objects = AuditoriaBaseManager()

    def nacionalidade_to_s(self):
        nacionalidades = dict(self.LISTA_NACIONALIDADE)
        return nacionalidades[self.nacionalidade]

    def get_foto(self):

        if not self.foto or not os.path.exists('{}/{}'.format(settings.MEDIA_ROOT, self.foto)):
            return static('img/default_person.jpg')

        return '{}'.format(self.foto.url)

    @property
    def pne(self):
        if self.id:
            return self.situacoes.filter(codigo=Situacao.CODIGO_PNE).exists()
        else:
            return False

    @property
    def idoso(self):
        if self.id:
            return self.situacoes.filter(codigo=Situacao.CODIGO_IDOSO).exists()
        else:
            return False

    @property
    def falecido(self):
        if self.id:
            return self.situacoes.filter(codigo=Situacao.CODIGO_FALECIDO).exists()
        else:
            return False

    @property
    def preso(self):
        if self.id:
            return self.situacoes.filter(codigo=Situacao.CODIGO_PRESO).exists()
        else:
            return False

    @property
    def maes(self):
        if self.id:
            return self.filiacoes.maes()
        else:
            return None

    @property
    def mae(self):
        if self.id:
            return self.filiacoes.maes().first()
        else:
            return None

    @property
    def pais(self):
        if self.id:
            return self.filiacoes.pais()
        else:
            return None

    @property
    def pai(self):
        if self.id:
            return self.filiacoes.pais().first()
        else:
            return None

    def acesso_solicitado(self, servidor):
        return Acesso.objects.filter(
            servidor=servidor,
            assistido=self,
            data_revogacao=None,
            data_concessao=None,
            ativo=True
        ).exists()

    def acesso_concedido(self, servidor):
        if Acesso.objects.filter(
            (
                Q(servidor=servidor)
            ),
            assistido=self,
            data_revogacao=None,
            ativo=True
        ).exclude(
            data_concessao=None
        ).exists():
            return True

        elif Acesso.objects.filter(
            (
                Q(defensoria__in=servidor.defensor.defensorias)
            ),
            assistido=self,
            data_revogacao=None,
            ativo=True
        ).exclude(
            data_concessao=None
        ).exists():
            return True

    def avaliar(self):
        """Faz avaliação de tudo que o assistido declarou.
        Há uma avaliação para Pessoa Física e outra para Pessoa Jurídica.
        """

        avaliacao = True

        if hasattr(self, 'renda'):
            if self.tipo == constantes.TIPO_PESSOA_FISICA:
                avaliacao = (
                    (
                        (
                            self.renda.numero_membros == 1 and
                            self.avaliar_renda_individual()
                        ) |
                        (
                            # TODO: Substituir sigla por configuração AND/OR na análise de renda familiar/per capita
                            self.renda.numero_membros > 1 and
                            (
                                (
                                    settings.SIGLA_UF.upper() == 'PR' and
                                    (
                                        self.avaliar_renda_familiar() and
                                        self.avaliar_renda_per_capita()
                                    )
                                ) |
                                (
                                    not settings.SIGLA_UF.upper() == 'PR' and
                                    (
                                        self.avaliar_renda_familiar() or
                                        self.avaliar_renda_per_capita()
                                    )
                                )
                            )
                        )
                    ) and
                    self.avaliar_bens() and
                    self.avaliar_investimentos()
                )
            else:
                avaliacao = (
                    self.avaliar_valor_salario_funcionario() and
                    self.avaliar_bens() and
                    self.avaliar_investimentos()
                )

        return avaliacao

    def avaliar_renda_individual(self):
        """Avalia a renda individual declarada"""

        if hasattr(self, 'renda'):
            return Salario.atual(self.tipo).validar_renda_individual(self.renda.renda_com_deducao)
        else:
            return True

    def avaliar_renda_familiar(self):
        """Avalia a renda familiar declarada"""

        if hasattr(self, 'renda'):
            return Salario.atual(self.tipo).validar_renda_familiar(self.renda.renda_com_deducao)
        else:
            return True

    def avaliar_renda_per_capita(self):
        """Avalia a renda per capita"""

        if hasattr(self, 'renda'):
            return Salario.atual(self.tipo).validar_renda_per_capita(self.renda.renda_per_capita())
        else:
            return True

    def avaliar_valor_salario_funcionario(self):
        """Avalia o maior salário pago para funcionário, prestador de serviço autônomo, sócio ou administador"""

        if hasattr(self, 'salario_funcionario'):
            return Salario.atual(self.tipo).validar_valor_salario_funcionario(self.renda.salario_funcionario)
        else:
            return True

    def avaliar_bens(self):
        """Avalia o valor dos bens declarados"""

        q = self.patrimonios.ativos().exclude(tipo__nome='Investimentos').aggregate(Sum('valor'))

        # DPE/PR remove imóvel de família destinado a residência
        if settings.SIGLA_UF.upper() == 'PR':
            q = self.patrimonios.ativos().exclude(tipo__nome='Investimentos').filter(eh_bem_familia=False).aggregate(Sum('valor'))  # noqa: E501

        return Salario.atual(self.tipo).validar_valor_bens(q['valor__sum'])

    def avaliar_investimentos(self):
        """Avalia o valor dos investimentos declarados"""

        q = self.patrimonios.ativos().filter(tipo__nome='Investimentos').aggregate(Sum('valor'))
        return Salario.atual(self.tipo).validar_valor_investimentos(q['valor__sum'])

    @property
    def avaliacao(self):
        return self.avaliar()

    def tem_filhos(self):
        if self.qtd_filhos > 0:
            return True
        else:
            return False

    def is_idoso(self):
        return self.idade >= 60 or (self.data_nascimento is None and self.idoso)

    def is_idoso_absoluto(self):
        return self.idade >= 80

    def prioridade(self):
        """Tipo de Prioridade do assistido conforme seja PNE ou pela idade"""

        from atendimento.atendimento.models import Atendimento

        prioridade = Atendimento.PRIORIDADE_0

        if self.is_idoso_absoluto():
            prioridade = Atendimento.PRIORIDADE_2
        elif self.is_idoso() or self.pne:
            prioridade = Atendimento.PRIORIDADE_1

        return prioridade

    def is_prioritario_absoluto(self):
        """Definição de prioritário absoluto: assistido com 80 anos ou mais"""
        return self.idade >= 80

    def possui_nome_social(self):
        if self.nome_social:
            return True
        else:
            return False

    def possui_nome_fantasia(self):
        if self.apelido:
            return True
        else:
            return False

    def permissao_acessar(self, usuario):

        # Pode acessar se superuser
        if usuario.is_superuser:
            return True

        # Pode acessar se tem permissão para ver todos atendimentos
        if usuario.has_perm(perm='assistido.visualizar_dados_situacao_sigilosa'):
            return True

        return False

    class Meta:
        app_label = 'assistido'
        ordering = ['-desativado_em', 'nome']
        verbose_name = u'Assistido'
        verbose_name_plural = u'Assistidos'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(PessoaAssistida, self).save(force_insert, force_update, using, update_fields)


class Acesso(models.Model):
    NIVEL_CONSULTA = 0
    NIVEL_EDICAO = 1
    NIVEL_ADMINISTRACAO = 2

    LISTA_NIVEL = (
        (NIVEL_CONSULTA, 'Consulta'),
        (NIVEL_EDICAO, 'Edição'),
        (NIVEL_ADMINISTRACAO, 'Administração'),
    )

    assistido = models.ForeignKey('assistido.PessoaAssistida', on_delete=models.DO_NOTHING)
    servidor = models.ForeignKey(Servidor, blank=True, null=True, default=None, related_name='+', on_delete=models.DO_NOTHING)  # noqa: E501
    defensoria = models.ForeignKey('contrib.Defensoria', blank=True, null=True, default=None, related_name='+', on_delete=models.DO_NOTHING)  # noqa: E501
    data_solicitacao = models.DateTimeField(blank=True, null=True, default=None)
    concedido_por = models.ForeignKey('defensor.Defensor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    data_concessao = models.DateTimeField(blank=True, null=True, default=None)
    revogado_por = models.ForeignKey('defensor.Defensor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)  # noqa: E501
    data_revogacao = models.DateTimeField(blank=True, null=True, default=None)
    nivel = models.SmallIntegerField(choices=LISTA_NIVEL, default=NIVEL_CONSULTA)
    ativo = models.BooleanField(default=True)

    @staticmethod
    def conceder_publico(assistido, concedido_por):
        acesso, created = Acesso.objects.update_or_create(
            assistido=assistido,
            servidor_id=None,
            defaults={
                'data_concessao': datetime.now(),
                'concedido_por': concedido_por,
                'data_revogacao': None,
                'revogado_por': None
            })

    @staticmethod
    def revogar_publico(assistido, revogado_por):
        Acesso.objects.filter(
            assistido=assistido,
            servidor_id=None
        ).update(
            data_revogacao=datetime.now(),
            revogado_por=revogado_por
        )


def documento_file_name(instance, filename):
    import uuid

    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)

    return '/'.join(['assistido', filename])


class Documento(models.Model):

    pessoa = models.ForeignKey(
        'Pessoa',
        related_name='documentos',
        on_delete=deletion.PROTECT
    )
    documento = models.ForeignKey('contrib.Documento', related_name='+', blank=True, null=True, default=None,
                                  on_delete=models.DO_NOTHING)
    arquivo = models.FileField("Arquivo", upload_to=documento_file_name, validators=[validate_file_size_extension])
    nome = models.CharField(max_length=255, blank=True, null=True, default=None)
    ativo = models.BooleanField(default=True)

    data_enviado = models.DateTimeField('Data de Envio', null=True, blank=False, auto_now_add=True, editable=False)
    enviado_por = models.ForeignKey(
        'contrib.Servidor',
        related_name='+',
        blank=True,
        null=True,
        default=None,
        on_delete=deletion.PROTECT
    )

    data_exclusao = models.DateTimeField('Data de Exclusão', null=True, blank=True, editable=False, default=None)
    excluido_por = models.ForeignKey(
        'contrib.Servidor',
        related_name='+',
        blank=True,
        null=True,
        editable=False,
        default=None,
        on_delete=deletion.PROTECT
    )  # noqa: E501

    documento_assinado = models.ForeignKey(
        to='assistido.DocumentoAssinado',
        related_name='+',
        blank=True,
        null=True,
        default=None,
        on_delete=models.DO_NOTHING)

    objects = managers.DocumentoManager()

    class Meta:
        app_label = 'assistido'
        ordering = ['-ativo', 'pessoa__nome', 'nome']

    @property
    def nome_norm(self):
        return Util.normalize(self.nome)

    def __str__(self):
        return "%s - %s" % (self.pessoa.nome, self.nome)

    def excluir(self, excluido_por):
        self.data_exclusao = datetime.now()
        self.excluido_por = excluido_por
        self.ativo = False
        self.save()


class DocumentoAssinado(AuditoriaAbstractMixin):
    arquivo = models.FileField("Arquivo", upload_to=documento_file_name)
    data_enviado = models.DateTimeField('Data de Envio', null=True, blank=False, auto_now_add=True, editable=False)


class Renda(models.Model):
    pessoa = models.OneToOneField(to=Pessoa, on_delete=models.DO_NOTHING)

    numero_membros = models.SmallIntegerField(
        verbose_name=u'Nº Membros',
        default=1,
        validators=[MinValueValidator(1)],
        help_text=u'Número de membros na entidade familiar')

    numero_membros_economicamente_ativos = models.SmallIntegerField(
        verbose_name=u'Nº Membros Economicamente Ativos',
        default=0,
        help_text=u'Número de membros na entidade familiar economicamente ativos')

    numero_dependentes = models.SmallIntegerField(
        verbose_name=u'Nº Dependentes',
        default=0)

    ganho_mensal = models.DecimalField(
        verbose_name='Renda Individual',
        max_digits=16,
        decimal_places=2,
        default=0,
        help_text=u'Ganhos mensais, em R$, do declarante'
    )

    ganho_mensal_membros = models.DecimalField(
        verbose_name='Renda Familiar',
        max_digits=16,
        decimal_places=2,
        default=0,
        help_text=u'Ganhos mensais, em R$, da entidade familiar'
    )

    tem_gastos_tratamento = models.BooleanField(default=False)
    valor_tratamento = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    tem_plano_saude = models.BooleanField(verbose_name=u'Plano de Saúde', default=False)

    nome_plano_saude = models.CharField(max_length=255, null=True, blank=True, default=None)
    valor_nome_saude = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    tem_beneficio_assistencial = models.BooleanField(default=False)
    valor_beneficio_assistencial = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    tem_educacao_particular_filhos = models.BooleanField(default=False)
    valor_educacao_particular_filhos = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    declarante_ir = models.BooleanField('Declara IR?', default=False)
    isento_ir = models.BooleanField('Isento IR?', default=True)
    tipo_renda = models.ForeignKey(
        'TipoRenda',
        related_name='tipos',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        verbose_name=u'Tipo de renda',
        default=None,
        help_text=u'Tipo da renda individual do assistido')
    # se paga contribuicao previdenciaria autonoma
    previdencia = models.BooleanField(default=False)

    # Exclusivo para Pessoa Jurídica
    tem_fins_lucrativos = models.BooleanField('Tem Fins Lucrativos',
                                              default=False,
                                              help_text='Selecione caso seja Pessoa Júridica e tenha fins lucrativos')

    salario_funcionario = models.DecimalField('Maior Remuneração',
                                              max_digits=16,
                                              decimal_places=2,
                                              default=0,
                                              help_text='Preencha com a maior remuneração paga mensalmente')

    def __str__(self):
        return self.pessoa.nome

    def renda_per_capita(self):
        renda_com_deducao = self.renda_com_deducao
        if self.numero_membros and renda_com_deducao:
            return renda_com_deducao / self.numero_membros
        else:
            return 0

    @property
    def renda_com_deducao(self):
        valor_deducao = 0.0
        valor_deducao_por_tipo_renda = 0.0
        valor_deducao_por_situacao = 0.0
        if settings.SIGLA_UF.upper() == 'PR':
            # Deliberação do PR realiza desconto de 1/2 salario por membro da familia que for
            # criança, pne, idoso ou egresso sistema prisional, limitando ao máximo de 2 salários
            # além de deduzir rendas que sejam classificadas como Auxílio ou Bolsa estágio
            from .services import (
                calcula_valor_deducao_por_tipo_renda_membros_familia,
                calcula_quantidade_membros_deducao_por_situacao,
                calcula_valor_deducao_por_tipo_renda_cadastro_principal,
                calcula_valor_deducao_por_situacao_cadastro_principal
            )
            membros = self.pessoa.to_dict()['membros']

            quantidade_membros_deducao_por_situacao = calcula_quantidade_membros_deducao_por_situacao(membros)
            quantidade_membros_deducao_por_situacao += calcula_valor_deducao_por_situacao_cadastro_principal(self.pessoa.id)  # noqa: E501

            valor_deducao_por_tipo_renda = calcula_valor_deducao_por_tipo_renda_membros_familia(membros)
            valor_deducao_por_tipo_renda += calcula_valor_deducao_por_tipo_renda_cadastro_principal(self.pessoa.id)

            # limita o desconto a dois salários mínimos
            if quantidade_membros_deducao_por_situacao > 0 and quantidade_membros_deducao_por_situacao < 4:
                valor_deducao_por_situacao = ((float(Salario.atual(self.pessoa.tipo).valor)/2) * quantidade_membros_deducao_por_situacao)  # noqa: E501
            elif quantidade_membros_deducao_por_situacao > 3:
                valor_deducao_por_situacao = float(Salario.atual(self.pessoa.tipo).valor) * 2

        valor_deducao = valor_deducao_por_situacao + valor_deducao_por_tipo_renda
        despesas = self.pessoa.patrimonios.ativos().filter(tipo__nome='Despesa Dedutível').aggregate(Sum('valor'))['valor__sum']  # noqa: E501

        if despesas:  # Se houver despesas, faz a dedução de valores definidos
            valor_deducao += float(despesas)
            valor_deducao = Decimal(str(valor_deducao))

        if self.numero_membros == 1:
            valor_final = float(self.ganho_mensal) - float(valor_deducao)
            return Decimal(str(valor_final))
        else:
            valor_final = float(self.ganho_mensal_membros) - float(valor_deducao)
            return Decimal(str(valor_final))

    class Meta:
        app_label = 'assistido'


class Dependente(AuditoriaAbstractMixin):

    GRAU_PARENTESCO = (
        (0, 'Cônjuge/Companheiro(a)'),
        (1, 'Pai/Mãe'),
        (2, 'Filho/Filha'),
        (3, 'Irmão/Irmã'),
        (4, 'Tio/Tia'),
        (5, 'Primo/Prima'),
        (6, 'Avó/Avô'),
        (7, 'Outro'),
    )

    CRIANCA_ADOLESCENTE = 0
    PNE = 1
    IDOSO = 2
    EGRESSO_PRISIONAL = 3

    LISTA_SITUACAO = (
        (CRIANCA_ADOLESCENTE, 'Criança ou adolescente'),
        (PNE, 'Portador de Necessidades Especiais'),
        (IDOSO, 'Idoso'),
        (EGRESSO_PRISIONAL, 'Egresso do sistema prisional'),
    )

    pessoa = models.ForeignKey(PessoaAssistida, related_name='membros', on_delete=models.DO_NOTHING)
    nome = models.CharField(max_length=256, null=False, blank=False)
    situacao = models.SmallIntegerField('Situação', choices=LISTA_SITUACAO, null=True, blank=True)  # TODO: depreciado, remover na próxima versão após copulação de foreign keys  # noqa: E501
    situacao_dependente = models.ForeignKey('Situacao', related_name='situacao', null=True, blank=True, on_delete=models.DO_NOTHING)  # noqa: E501
    tipo_renda = models.ForeignKey('TipoRenda', related_name='tipos_renda', null=True, blank=True, on_delete=models.DO_NOTHING)  # noqa: E501
    parentesco = models.SmallIntegerField('Grau de Parentesco', choices=GRAU_PARENTESCO, null=False, blank=False)
    renda = models.DecimalField('Renda Individual',
                                max_digits=16,
                                decimal_places=2,
                                default=0,
                                help_text=u'Ganhos mensais, em R$, do dependente')

    objects = AuditoriaBaseManager()

    class Meta:
        ordering = ['pessoa', 'cadastrado_em']


class Patrimonio(models.Model):
    pessoa = models.OneToOneField(Pessoa, blank=True, null=True, default=None, on_delete=models.DO_NOTHING)

    tem_imoveis = models.BooleanField(verbose_name='Possui Imóveis', default=False)
    quantidade_imoveis = models.SmallIntegerField(default=0)
    valor_imoveis = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=0,
        help_text=u'Valor total, em R$, dos bens imóveis'
    )

    tem_moveis = models.BooleanField(verbose_name='Possui Móveis', default=False)
    quantidade_moveis = models.SmallIntegerField(default=0)
    valor_moveis = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=0,
        help_text=u'Valor total, em R$, dos bens móveis'
    )

    tem_outros_bens = models.BooleanField(verbose_name='Possui Outros Bens', default=False)
    valor_outros_bens = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=0,
        help_text=u'Valor total, em R$, de outros bens e direitos'
    )

    tem_investimentos = models.BooleanField(verbose_name='Possui Aplicações ou Investimentos', default=False)
    valor_investimentos = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=0,
        help_text='Valor total, em R$, de aplicações ou investimentos financeiros'
    )

    def __str__(self):
        return self.pessoa.nome

    def valor_total_bens(self):
        return self.valor_moveis + self.valor_imoveis + self.valor_outros_bens

    @property
    def unico_bem_imovel(self):
        pass


class PatrimonialTipo(AuditoriaAbstractMixin):
    GRUPO_PATRIMONIO = 10
    GRUPO_DESPESA_DEDUTIVEL = 21
    GRUPO_DESPESA_NAO_DEDUTIVEL = 22
    GRUPO_RENDA_EXTRA = 30

    LISTA_GRUPO = (
        (GRUPO_PATRIMONIO, 'Patrimônio'),
        (GRUPO_DESPESA_DEDUTIVEL, 'Despesa Dedutível'),
        (GRUPO_DESPESA_NAO_DEDUTIVEL, 'Despesa Não Dedutível'),
        (GRUPO_RENDA_EXTRA, 'Renda Extra'),
    )

    nome = models.CharField(max_length=256, null=False, blank=False)
    grupo = models.SmallIntegerField('Grupo', choices=LISTA_GRUPO, null=False, blank=False, default=GRUPO_PATRIMONIO)

    def __str__(self):
        return self.nome


class Patrimonial(AuditoriaAbstractMixin):
    pessoa = models.ForeignKey(Pessoa, related_name='patrimonios', blank=False, null=False, default=None,
                               on_delete=models.CASCADE)
    tipo = models.ForeignKey(PatrimonialTipo, blank=False, null=False, default=None, on_delete=models.DO_NOTHING)
    valor = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    descricao = models.CharField(max_length=6000, null=True, blank=True)
    eh_bem_familia = models.BooleanField('É bem de família destinado a residência?', default=False)

    class Meta:
        app_label = 'assistido'
        verbose_name_plural = 'Patrimoniais'
        indexes = [
            models.Index(fields=['pessoa', 'tipo'], condition=Q(desativado_em=None), name='assistido_patrimonial_idx_001'),  # noqa: E501
        ]

    def __str__(self):
        return self.pessoa.nome


class Imovel(models.Model):
    PAGAMENTO_FINANCIADO = 0
    PAGAMENTO_QUITADO = 1

    LISTA_PAGAMENTO = (
        (PAGAMENTO_FINANCIADO, 'Financiado'),
        (PAGAMENTO_QUITADO, 'Quitado')
    )

    patrimonio = models.ForeignKey(Patrimonio, related_name='imoveis', on_delete=models.DO_NOTHING)

    pagamento = models.SmallIntegerField(choices=LISTA_PAGAMENTO)
    banco = models.CharField(max_length=255, blank=True, null=True, default=None)
    parcelas = models.SmallIntegerField()
    valor_parcela = models.DecimalField(max_digits=16, decimal_places=2)
    valor_total = models.DecimalField(max_digits=16, decimal_places=2)
    uso_proprio = models.BooleanField()

    class Meta:
        app_label = 'assistido'


class Movel(models.Model):
    PAGAMENTO_FINANCIADO = 0
    PAGAMENTO_QUITADO = 1

    LISTA_PAGAMENTO = (
        (PAGAMENTO_FINANCIADO, 'Financiado'),
        (PAGAMENTO_QUITADO, 'Quitado')
    )

    patrimonio = models.ForeignKey(Patrimonio, related_name='moveis', on_delete=models.DO_NOTHING)

    marca = models.CharField(max_length=255, blank=True, null=True, default=None)
    modelo = models.CharField(max_length=255, blank=True, null=True, default=None)
    pagamento = models.SmallIntegerField(choices=LISTA_PAGAMENTO)
    banco = models.CharField(max_length=255, blank=True, null=True, default=None)
    parcelas = models.SmallIntegerField()
    valor_parcela = models.DecimalField(max_digits=16, decimal_places=2)
    valor_total = models.DecimalField(max_digits=16, decimal_places=2)

    class Meta:
        app_label = 'assistido'


class Semovente(models.Model):
    TIPO_BOVINO = 1
    TIPO_OVINO = 2
    TIPO_SUINO = 3
    TIPO_CAPRINO = 4
    TIPO_EQUINO = 5

    LISTA_TIPO = (
        (TIPO_BOVINO, 'Bovino'),
        (TIPO_OVINO, 'Ovino'),
        (TIPO_SUINO, 'Suíno'),
        (TIPO_CAPRINO, 'Caprino'),
        (TIPO_EQUINO, 'Equino')
    )

    patrimonio = models.ForeignKey(Patrimonio, related_name='semoventes', on_delete=models.DO_NOTHING)

    tipo = models.SmallIntegerField(choices=LISTA_TIPO)
    quantidade = models.SmallIntegerField()
    valor_aproximado = models.DecimalField(max_digits=16, decimal_places=2)

    class Meta:
        app_label = 'assistido'


class PerfilCamposObrigatorios(models.Model):
    TIPO_TODOS = None
    TIPO_ATENDIMENTO = 1
    TIPO_PROCESSO = 2

    LISTA_PROCESSO = (
        (TIPO_TODOS, 'Todos'),
        (TIPO_ATENDIMENTO, 'Atendimento'),
        (TIPO_PROCESSO, 'Processo'),
    )

    PARTE_TODAS = None
    PARTE_REQUERENTE = 1
    PARTE_REQUERIDO = 2

    LISTA_PARTE = (
        (PARTE_TODAS, 'Todas'),
        (PARTE_REQUERENTE, 'Requerente'),
        (PARTE_REQUERIDO, 'Requerido'),
    )

    nome = models.CharField(max_length=256)
    tipo_processo = models.SmallIntegerField(
        verbose_name='Tipo Processo',
        choices=LISTA_PROCESSO,
        null=True,
        blank=True,
        default=TIPO_TODOS)
    tipo_parte = models.SmallIntegerField(
        verbose_name='Tipo Parte',
        choices=LISTA_PARTE,
        null=True,
        blank=True,
        default=PARTE_TODAS)
    parte_principal = models.BooleanField(
        verbose_name='Parte Principal?',
        null=True,
        blank=True,
        default=None)
    configuracao = models.TextField(verbose_name='Configuração', blank=False, null=False)

    tipo_pessoa = models.SmallIntegerField(
        verbose_name='Tipo de Pessoa',
        choices=constantes.LISTA_TIPO_PESSOA,
        default=constantes.TIPO_PESSOA_FISICA
    )

    class Meta:
        ordering = ['nome']
        verbose_name = u'Perfil de Campos Obrigatórios'
        verbose_name_plural = u'Perfis de Campos Obrigatórios'
        unique_together = ('tipo_processo', 'tipo_parte', 'parte_principal')

    def __str__(self):
        return self.nome

    def configuracao_to_json(self, form_name=None):

        try:
            data = simplejson.loads(self.configuracao)
        except ValueError:
            data = {}

        if data and form_name:
            if form_name in data:
                data = data[form_name]
            else:
                data = {}

        return data


class Situacao(AuditoriaAbstractMixin):
    CODIGO_IDOSO = 'IDOSO'
    CODIGO_PNE = 'PNE'
    CODIGO_FALECIDO = 'FALECIDO'
    CODIGO_PRESO = 'PRESO'

    codigo = models.CharField(max_length=255, unique=True)
    nome = models.CharField(max_length=256)
    eh_situacao_deducao = models.BooleanField('É uma situação onde que há dedução no cálculo de hipossuficiência?', default=False)  # noqa: E501
    disponivel_via_app = models.BooleanField(verbose_name='Disponível via apps (Luna, eDefensor, etc)?', default=False)

    objects = managers.SituacaoManager()

    class Meta:
        verbose_name = u'Situação'
        verbose_name_plural = u'Situações'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def pode_remover(self):
        restriction = (Situacao.CODIGO_FALECIDO, Situacao.CODIGO_IDOSO, Situacao.CODIGO_PNE, Situacao.CODIGO_PRESO)
        return self.codigo not in restriction


class TipoRenda(AuditoriaAbstractMixin):
    nome = models.CharField(max_length=256)
    eh_deducao_salario_minimo = models.BooleanField(
        'Deve ser realizada dedução máxima de 1 salário mínimo?',
        help_text=u'Caso marcado, deve-se deixar em branco o valor máximo de dedução abaixo e será utilizado o valor da tabela salários',  # noqa: E501
        default=False)

    valor_maximo_deducao = models.DecimalField(
        'Valor máximo de dedução',
        max_digits=16,
        decimal_places=2,
        default=0,
        help_text=u'Valor máximo em R$ que será deduzido para este tipo de renda (caso não seja o salário mínimo)')

    objects = managers.TipoRendaManager()

    class Meta:
        verbose_name = u'Tipo de Renda'
        verbose_name_plural = u'Tipos de renda'
        ordering = ['nome']

    def __str__(self):
        return self.nome


reversion.register(Pessoa)
reversion.register(Filiacao)
reversion.register(Profissao)
reversion.register(Bem)
reversion.register(EstruturaMoradia)
reversion.register(Moradia)
reversion.register(PessoaAssistida)
reversion.register(Documento)
reversion.register(Renda)
reversion.register(Patrimonio)
reversion.register(Imovel)
reversion.register(Movel)
reversion.register(Dependente)
reversion.register(Situacao)
reversion.register(TipoRenda)
