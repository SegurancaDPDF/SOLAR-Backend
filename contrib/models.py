# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import datetime
import decimal
import json as simplejson
import logging
import re
import types
import unicodedata
from itertools import groupby

import jellyfish
import reversion
from django.conf import settings
from django.contrib.auth.models import User
from django.core import serializers
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.db.models import deletion
from django.templatetags.static import static
from django.utils import timezone
from django.utils.functional import cached_property

from model_utils import FieldTracker
from pycpfcnpj import cpfcnpj
from contrib.validators import validate_CPF_CNPJ

# Solar
from core.models import AuditoriaAbstractMixin, Documento as DocumentoCore
# Modulos locais
from . import managers
from . import constantes

__all__ = (
    'Enum',
    'Util',
    'Dados',
    'Atualizacao',
    'Telefone',
    'CEP',
    'Endereco',
    'Pais',
    'Estado',
    'Municipio',
    'Bairro',
    'Area',
    'Comarca',
    'Defensoria',
    'Documento',
    'Servidor',
    'Deficiencia',
    'Vara',
    'Salario',
    'Papel'
)

logger = logging.getLogger(__name__)


class Enum():
    STATUS_ATIVO = 1  # representam o status ativo e inativo, respectivamente
    STATUS_INATIVO = 0

    LISTA_STATUS = (  # contem valor e a descrição dos status
        (STATUS_ATIVO, 'Ativo'),
        (STATUS_INATIVO, 'Inativo'),
    )

    DIA_SEGUNDA = 0  # constantes que representam os dias da semana
    DIA_TERCA = 1
    DIA_QUARTA = 2
    DIA_QUINTA = 3
    DIA_SEXTA = 4
    DIA_SABADO = 5
    DIA_DOMINGO = 6

    LISTA_DIA = (  # contem o valor e a descrição dos dias da semana
        (DIA_SEGUNDA, 'Segunda-feira'),
        (DIA_TERCA, 'Terça-feira'),
        (DIA_QUARTA, 'Quarta-feira'),
        (DIA_QUINTA, 'Quinta-feira'),
        (DIA_SEXTA, 'Sexta-feira'),
        (DIA_SABADO, 'Sábado'),
        (DIA_DOMINGO, 'Domingo'),
    )


class Util(object):   # manipulacao de objetos
    @staticmethod
    def object_to_dict(obj, d={}, bool_to_int=False):  # converte um objeto para um dicionário

        if isinstance(obj, models.Model):

            for field in obj._meta.fields:

                attr = field.name
                d[attr] = None

                if field.is_relation:

                    d[attr] = getattr(obj, field.attname)

                else:

                    val = getattr(obj, attr)

                    if type(val) is datetime.datetime:
                        d[attr] = Util.date_to_json(val)
                    elif type(val) is datetime.date:
                        d[attr] = Util.date_to_json(val)
                    elif type(val) is datetime.time:
                        d[attr] = Util.time_to_json(val)
                    elif type(val) == bool and bool_to_int:
                        d[attr] = 1 if val else 0
                    elif type(val) is decimal.Decimal:
                        d[attr] = "%.2f" % float(val)
                    else:
                        d[attr] = val

        return d

    @staticmethod
    def json_serialize(objects):  # serializa objetos em formato JSON
        # TODO: verificar metodo - tiago
        data = simplejson.loads(serializers.serialize('json', objects))

        for i, item in enumerate(data):
            item['fields']['id'] = item['pk']
            data[i] = item['fields']

        return data

    @staticmethod
    # retorna uma string contendo uma mensagem de comentário sobre uma operação de salvamento de um objeto
    def get_comment_save(user, obj, is_new):

        model_name = obj.__class__.__name__

        if is_new:
            return "{} {} cadastrado por '{}'".format(model_name, obj.id, user.username)
        else:
            return "{} {} editado por '{}'".format(model_name, obj.id, user.username)

    @staticmethod
    # retorna uma string contendo uma mensagem de comentário sobre a exclusão de um objeto
    def get_comment_delete(user, obj):

        model_name = obj.__class__.__name__

        return "{} {} excluido por '{}'".format(model_name, obj.id, user.username)

    @staticmethod
    # realiza a conversão recursivamente para objetos relacionados
    def object_to_dict_recursive(obj):

        fields = []
        for field in obj._meta.fields:
            fields.append(field.name)

        data = {}
        for f in fields:

            val = getattr(obj, f)
            types.append({'name': f, 'type': type(val)})

            try:
                data[f] = Util.object_to_dict_recursive(val)
            except AttributeError:
                if isinstance(val, datetime.date):
                    data[f] = Util.date_to_json(val)
                elif type(val) is None:
                    data[f] = None
                else:
                    data[f] = val

        return data

    @staticmethod
    def soundex(word):
        codes = ("bfpv", "cgjkqsxz", "dt", "l", "mn", "r")
        sound_dict = dict((ch, str(ix + 1)) for ix, cod in enumerate(codes) for ch in cod)

        def cmap2(kar): return sound_dict.get(kar, '9')
        sdx = ''.join(cmap2(kar) for kar in word.lower())
        sdx2 = word[0].upper() + ''.join(k for k, g in list(groupby(sdx))[1:] if k != '9')
        sdx3 = sdx2[0:4].ljust(4, '0')
        return sdx3

    @staticmethod
    def unaccent(text):
        """Transforms a string to its unaccented version.
        This might be useful for generating "friendly" URLs
        # falha com o seguintes caracteres:
        # Æ Ð Ø Þ ß æ ð ø þ
        """

        new_text = unicodedata.normalize('NFD', text)

        return u''.join((c for c in new_text if unicodedata.category(c) != 'Mn'))

    @staticmethod
    def normalize(text):  # normaliza um texto, removendo acentos e convertendo para letras maiúsculas
        return unicodedata.normalize('NFKD', u'{}'.format(text)).encode('ASCII', 'ignore').decode('utf-8').upper()

    @staticmethod
    def text_to_soundex(word):

        ignorados = ['DO', 'DOS', 'DA', 'DAS', 'DE']
        nomes = word.upper().split(' ')
        nome_soundex = []

        for nome in nomes:
            if nome not in ignorados and len(nome) > 1:
                nome_soundex.append(jellyfish.soundex(Util.unaccent(nome)))

        return nome_soundex

    @staticmethod
    def date_to_json(value):  # converte uma data para uma representacao em formato JSON
        if type(value) is datetime.date:
            value = datetime.datetime.combine(value, datetime.time.min)
        if type(value) is datetime.datetime:
            if value.microsecond:
                return '{:.23}Z'.format(value.isoformat())
            else:
                return '{:.19}.000Z'.format(value.isoformat())

    @staticmethod
    def time_to_json(value):  # converte um objeto time para uma representacao em formato JSON.
        if type(value) is datetime.datetime:
            value = value.time()
        if type(value) is datetime.time:
            return '{:.8}'.format(value.isoformat())

    @staticmethod  # converte uma string no formato JSON para uma data no formato especificado
    def json_to_date(value, format_in='%Y-%m-%dT%H:%M:%S.%fZ', format_out='%Y-%m-%d'):
        try:
            return datetime.datetime.strptime(value, format_in).strftime(format_out)
        except Exception:
            return None

    @staticmethod
    def so_numeros(value):  # remove todos os caracteres não numéricos de uma string
        if type(value) is str:
            return ''.join(re.findall(r'\d', str(value)))

    @staticmethod
    def string_to_date(value, format):  # converte uma string em uma data
        try:
            return datetime.datetime.strptime(value, format)
        except Exception:
            return None

    @staticmethod
    def cpf_cnpj_valido(value):  # verifica se o CPF ou CNPJ é válido
        try:
            validate_CPF_CNPJ(value)
        except Exception:
            return None
        else:
            return value


# Substituir por Piston
# https://bitbucket.org/jespern/django-piston/wiki/Documentation#!getting-started
class Dados():
    dados = []

    def __init__(self, dados, is_json=False):
        self.tratar_dados(dados, is_json)

    def tratar_dados(self, dados, is_json=False):

        if not is_json:
            try:
                dados = simplejson.loads(dados)
            except ValueError:
                dados = {}

        # trata dados recebidos via ajax
        for dado in dados:

            if isinstance(dados[dado], str):  # string
                try:
                    dados[dado] = datetime.datetime.strptime(dados[dado], '%Y-%m-%dT%H:%M:%S.000Z')
                except ValueError:
                    try:
                        dados[dado] = datetime.datetime.strptime(dados[dado], '%Y-%m-%dT%H:%M:%S-03:00')
                    except ValueError:
                        try:
                            dados[dado] = datetime.datetime.strptime(dados[dado], '%d/%m/%Y')
                        except ValueError:
                            continue

            if isinstance(dados[dado], (list, dict)):  # list/dict

                novo = []  # cria nova lista

                for item in dados[dado]:  # passa pelos itens do array
                    if item:
                        if isinstance(item, dict):
                            novo.append(item)
                        elif item.isdigit():
                            if dados[dado][item]:
                                novo.append(int(item))
                        else:
                            novo = dados[dado]
                            break

                dados[dado] = novo  # aplica nova lista

        self.dados = dados

    def __getitem__(self, key):
        try:
            return self.dados[key]
        except Exception:
            return None

    def __setitem__(self, key, value):
        self.dados[key] = value

    def get(self, key, default=None):
        try:
            return self.dados[key]
        except Exception:
            return default

    def get_all(self):
        return self.dados

    def set(self, key, value):
        self.dados[key] = value


class Atualizacao(models.Model):  # modelo do Django que representa uma atualizacao
    TIPO_IMPLEMENTACAO = 0
    TIPO_ATUALIZACAO = 1
    TIPO_CORRECAO = 2

    LISTA_TIPO = (
        (TIPO_IMPLEMENTACAO, 'Implementação'),
        (TIPO_ATUALIZACAO, 'Atualização'),
        (TIPO_CORRECAO, 'Correção'),
    )

    tipo = models.SmallIntegerField(choices=LISTA_TIPO)
    data = models.DateTimeField()
    texto = models.CharField(max_length=512)
    ativo = models.BooleanField('Ativo', default=True)

    def __str__(self):
        return self.texto

    class Meta:
        ordering = ['-ativo', '-data']
        verbose_name = u'Atualização'
        verbose_name_plural = u'Atualizações'


class Telefone(models.Model):  # modelo do django que representa um telefone

    TIPO_CELULAR = 0
    TIPO_RESIDENCIAL = 1
    TIPO_COMERCIAL = 2
    TIPO_RECADO = 3
    TIPO_WHATSAPP = 4
    TIPO_SMS = 5

    LISTA_TIPO = (
        (TIPO_CELULAR, 'Celular'),
        (TIPO_RESIDENCIAL, 'Residencial'),
        (TIPO_COMERCIAL, 'Comercial'),
        (TIPO_RECADO, 'Recado'),
        (TIPO_WHATSAPP, 'WhatsApp'),
        (TIPO_SMS, 'SMS'),
    )

    ddd = models.SmallIntegerField(null=True, blank=True)
    numero = models.CharField(u'Número', max_length=10)
    tipo = models.SmallIntegerField(choices=LISTA_TIPO)
    nome = models.CharField(max_length=256, null=True, blank=True)

    @property
    def eh_whatsapp(self):
        return self.tipo == self.TIPO_WHATSAPP

    @property
    def eh_fixo(self):
        """
        Verifica se um telefone é fixo.
        Link base: https://pt.stackoverflow.com/questions/14343/como-diferenciar-tipos-de-telefone
        """
        return int(self.numero[:1]) in range(2, 6)

    @property
    def eh_movel(self):
        """
        Verifica se um telefone é movel.
        Link base: https://pt.stackoverflow.com/questions/14343/como-diferenciar-tipos-de-telefone
        """
        return len(self.numero) == 9 or int(self.numero[:1]) in range(6, 10)

    @property
    def numero_formatado(self):
        if self.eh_movel:
            return '({}) {}-{}'.format(self.ddd, self.numero[:5], self.numero[5:])
        else:
            return '({}) {}-{}'.format(self.ddd, self.numero[:4], self.numero[4:])

    class Meta:
        verbose_name = u'Telefone'
        verbose_name_plural = u'Telefones'

    def __str__(self):
        return self.numero_formatado


class CEP(AuditoriaAbstractMixin):  # modelo do django que representa um CEP
    cep = models.CharField(max_length=8, unique=True)
    municipio = models.ForeignKey(
        'Municipio',
        null=True,
        blank=True,
        on_delete=deletion.PROTECT
    )
    bairro = models.ForeignKey('Bairro', on_delete=models.DO_NOTHING, null=True, blank=True)
    logradouro = models.CharField(max_length=256, null=True, blank=True)
    complemento = models.CharField(max_length=256, null=True, blank=True)
    eh_geral = models.BooleanField(default=False, verbose_name='É o cep geral do município (ignorar validação)?')

    @property
    def expirado(self):
        if not self.eh_geral and self.modificado_em < datetime.datetime.now() - datetime.timedelta(days=7):
            return True
        else:
            return False

    class Meta:
        verbose_name = u'CEP'
        verbose_name_plural = u'CEPs'
        ordering = ('cep',)

    def __str__(self):
        return self.cep


class Endereco(AuditoriaAbstractMixin):  # modelo de django que representa um endereco
    AREA_URBANA = 0
    AREA_RURAL = 1

    LISTA_AREA = (
        (AREA_URBANA, 'Urbana'),
        (AREA_RURAL, 'Rural'),
    )

    TIPO_ENDERECO_RESIDENCIAL = 10
    TIPO_ENDERECO_COMERCIAL = 20
    TIPO_ENDERECO_CORRESPONDENCIA = 30
    TIPO_ENDERECO_ALTERNATIVO = 40

    LISTA_TIPO_ENDERECO = (
        (TIPO_ENDERECO_RESIDENCIAL, 'Residencial'),
        (TIPO_ENDERECO_COMERCIAL, 'Comercial'),
        (TIPO_ENDERECO_CORRESPONDENCIA, 'Correspondência'),
        (TIPO_ENDERECO_ALTERNATIVO, 'Alternativo')
    )

    logradouro = models.CharField(max_length=256, null=True, blank=True, default=None)
    numero = models.CharField('Número', max_length=32, null=True, blank=True, default=None)
    complemento = models.CharField('Complemento', max_length=512, null=True, blank=True, default=None)
    cep = models.CharField('CEP', max_length=10, null=True, blank=True, default=None)
    bairro = models.ForeignKey('Bairro', null=True, blank=True, default=None, on_delete=models.deletion.PROTECT)
    municipio = models.ForeignKey('Municipio', on_delete=models.deletion.PROTECT)
    tipo_area = models.SmallIntegerField(choices=LISTA_AREA, default=AREA_URBANA, null=True, blank=True)

    principal = models.BooleanField('Principal', default=False, null=False, blank=True)
    tipo = models.SmallIntegerField(
        choices=LISTA_TIPO_ENDERECO,
        default=TIPO_ENDERECO_RESIDENCIAL,
        null=False,
        blank=True
    )

    objects = managers.EnderecoManager()

    class Meta:
        ordering = ['-principal', 'logradouro']
        verbose_name = u'Endereço'
        verbose_name_plural = u'Endereços'

    def __str__(self):
        # logradouro, numero, bairro - cidade, estado

        endereco = ''

        if not settings.SIGLA_UF.upper() == 'AM':
            if self.principal:
                endereco += 'Principal -'
            else:
                endereco += 'Secundário -'

            if self.tipo:
                endereco += ' ' + self.get_tipo_display() + ' -'
            if self.tipo_area:
                endereco += ' ' + self.get_tipo_area_display()

        if self.logradouro:
            endereco += ' ' + self.logradouro

        if self.numero:
            endereco += ' ' + self.numero

        if self.bairro:
            endereco += ' ' + self.bairro.nome

        if self.municipio:
            endereco += ' ' + self.municipio.nome

            if self.municipio.estado:
                endereco += ' - ' + self.municipio.estado.uf

        if not settings.SIGLA_UF.upper() == 'AM':
            if self.cep:
                endereco += ' ' + self.cep

        return endereco

    def desativar(self, usuario, data_hora=timezone.now()):
        self.desativado_por = usuario
        self.desativado_em = data_hora
        self.save()

    @property
    def esta_completo(self):
        return (self.logradouro and self.numero and self.cep and self.municipio)

    def save(self, *args, **kwargs):

        if self.cep:
            self.cep = Util.so_numeros(self.cep)[:8]

        super().save(*args, **kwargs)


class EnderecoHistorico(models.Model):
    """Utilizado para manter o histórico de endereços"""

    endereco = models.ForeignKey(
        'Endereco',
        null=False,
        blank=False,
        related_name='historicos',
        on_delete=deletion.PROTECT
    )

    logradouro = models.CharField(max_length=256, null=True, blank=True, default=None)
    numero = models.CharField('Número', max_length=32, null=True, blank=True, default=None)
    complemento = models.CharField('Complemento', max_length=512, null=True, blank=True, default=None)
    cep = models.CharField('CEP', max_length=32, null=True, blank=True, default=None)

    bairro = models.ForeignKey('Bairro', null=True, blank=True, default=None, on_delete=deletion.PROTECT)
    municipio = models.ForeignKey('Municipio', on_delete=deletion.PROTECT)
    tipo_area = models.SmallIntegerField(choices=Endereco.LISTA_AREA, default=None, null=True, blank=True)

    principal = models.BooleanField('Principal', default=False, null=False, blank=True)
    tipo = models.SmallIntegerField(
        choices=Endereco.LISTA_TIPO_ENDERECO,
        default=None,
        null=True,
        blank=True
    )

    cadastrado_em = models.DateTimeField(null=True)
    modificado_em = models.DateTimeField(null=True)
    desativado_em = models.DateTimeField(null=True)

    cadastrado_por = models.ForeignKey(
        to='auth.User',
        on_delete=deletion.PROTECT,
        blank=True,
        null=True,
        related_name='+'
    )

    modificado_por = models.ForeignKey(
        to='auth.User',
        on_delete=deletion.PROTECT,
        blank=True,
        null=True,
        related_name='+'
    )

    desativado_por = models.ForeignKey(
        to='auth.User',
        on_delete=deletion.PROTECT,
        blank=True,
        null=True,
        related_name='+'
    )


class Pais(models.Model):  # modelo do django que representa um país
    iso = models.CharField(max_length=2)  # armazena o código ISO de duas letras do país
    iso3 = models.CharField(max_length=3)  # armazena o código ISO de três letras do país
    numero = models.CharField(max_length=3, null=True, blank=True, default=None)
    nome = models.CharField(max_length=128)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = u'País'
        verbose_name_plural = u'Países'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Estado(models.Model):  # modelo do django que representra um estado
    nome = models.CharField(max_length=32)
    uf = models.CharField(max_length=2)  # unidade federativa do estado

    class Meta:
        verbose_name = u'Estado'
        verbose_name_plural = u'Estados'
        ordering = ['uf']

    def __str__(self):  # retorna uma representacao em string utilizando o uf
        return self.uf


class Municipio(models.Model):  # modelo do django que representa um municipio
    nome = models.CharField(max_length=128)
    estado = models.ForeignKey('Estado', on_delete=deletion.PROTECT)
    comarca = models.ForeignKey('Comarca', null=True, blank=True, on_delete=deletion.PROTECT)

    class Meta:
        verbose_name = u'Município'
        verbose_name_plural = u'Municípios'
        ordering = ['nome']

    def __str__(self):  # retorna uma representacao em string utilizando o nome
        return self.nome


class Bairro(AuditoriaAbstractMixin):  # modelo do django que representa um bairro

    nome = models.CharField(max_length=128)
    nome_norm = models.CharField(max_length=128, null=False, db_index=True)
    municipio = models.ForeignKey('Municipio', null=True, blank=True, on_delete=deletion.PROTECT)

    objects = managers.BairroManager()

    # TODO excluir duplicidades e criar unique de nome_municipio

    class Meta:  
        verbose_name = u'Bairro'
        verbose_name_plural = u'Bairros'
        ordering = ['municipio__nome', 'nome_norm', '-desativado_em']

    def __str__(self):
        return self.nome

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.nome_norm = Util.normalize(self.nome)
        super(Bairro, self).save(force_insert, force_update, using, update_fields)


class Area(models.Model):  # modelo do django que representa uma area
    nome = models.CharField(max_length=200)
    penal = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = u'Área'
        verbose_name_plural = u'Áreas'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Comarca(models.Model):  # modelo do django que representa uma comarca
    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data da última atualização', null=True, blank=False, auto_now=True)
    data_implantacao = models.DateTimeField('Data da implantação', null=True, blank=True)
    nome = models.CharField(max_length=512, null=False)
    coordenadoria = models.ForeignKey('self', null=True, blank=True, on_delete=deletion.PROTECT)
    codigo = models.CharField('Cód. Athenas', max_length=25, blank=True, null=True, default=None)
    codigo_eproc = models.CharField('Cód. E-Proc', max_length=25, blank=True, null=True, default=None)
    ativo = models.BooleanField('Ativo', default=True)

    objects = managers.ComarcaManager()

    class Meta:
        ordering = ['-ativo', 'nome']
        verbose_name = u'Comarca'
        verbose_name_plural = u'Comarcas'
        permissions = (
            ('view_all_comarcas', u'Pode ver todas comarcas'),
        )

    def __str__(self):
        return self.nome

    def comarcas(self):
        return Comarca.objects.filter(
            (Q(coordenadoria=self) | Q(id=self.id)) & Q(ativo=True)
        ).order_by('coordenadoria', 'nome')

    def defensorias(self):
        return Defensoria.objects.filter(comarca=self, ativo=True)

    @cached_property
    def municipio(self):
        return Municipio.objects.select_related('estado').filter(comarca=self, nome__iexact=self.nome).first()

    @cached_property
    def diretoria(self):
        if self.coordenadoria:
            return self.coordenadoria
        else:
            return self


class Defensoria(models.Model):  # modelo do django que representa uma defensoria
    GRAU_1 = 1
    GRAU_2 = 2

    PAINEL_PADRAO = 1
    PAINEL_SIMPLIFICADO = 2

    MODALIDADE_PRESENCIAL = 1
    MODALIDADE_REMOTO = 2

    LISTA_GRAU = (
        (GRAU_1, '1º Grau'),
        (GRAU_2, '2º Grau'),
    )

    LISTA_TIPO_PAINEL = (
        (PAINEL_PADRAO, 'Padrão'),
        (PAINEL_SIMPLIFICADO, 'Simplificado'),
    )

    LISTA_MODALIDADE = (
        (MODALIDADE_PRESENCIAL, 'Presencial'),
        (MODALIDADE_REMOTO, 'Remoto'),
    )

    AGENDAMENTO_NINGUEM = 0
    AGENDAMENTO_TODOS = 1
    AGENDAMENTO_APENAS_SETOR_AGENDAMENTO = 2
    AGENDAMENTO_APENAS_GABINENTE_DEFENSOR = 3

    LISTA_AGENDAMENTO = (
        (AGENDAMENTO_NINGUEM, 'Ninguém'),
        (AGENDAMENTO_TODOS, 'Todos'),
        (AGENDAMENTO_APENAS_SETOR_AGENDAMENTO, 'Apenas Setor de Agendamento (perm: view_129, view_recepcao)'),
        (AGENDAMENTO_APENAS_GABINENTE_DEFENSOR, 'Apenas Gabinete de Defensor (perm: view_defensor)'),
    )

    nome = models.CharField(max_length=255, db_index=True)
    codigo = models.CharField('Código', max_length=25, blank=True, null=True, default=None)
    numero = models.SmallIntegerField(null=False, blank=False, default=0)
    atuacao = models.CharField(max_length=1024, null=True, blank=True, default=None)
    comarca = models.ForeignKey(
        'Comarca',
        on_delete=deletion.PROTECT
    )
    nucleo = models.ForeignKey(
        'nucleo.Nucleo',
        null=True,
        blank=True,
        on_delete=deletion.PROTECT
    )
    predio = models.ForeignKey(
        'comarca.Predio',
        null=True,
        blank=True,
        on_delete=deletion.PROTECT
    )

    mae = models.ForeignKey(
        "Defensoria",
        related_name="filhas",
        null=True,
        blank=True,
        help_text="Defensoria responsável / supervisora",
        on_delete=deletion.PROTECT
    )

    telefone = models.CharField('Telefone da Unidade', max_length=25, blank=True, null=True, default=None)
    email = models.EmailField(max_length=128, null=True, blank=True, default=None)

    grau = models.SmallIntegerField(choices=LISTA_GRAU, default=GRAU_1, blank=True, null=True, db_index=True)
    tipo_painel_de_acompanhamento = models.SmallIntegerField(
        'Tipo do Painel de Acompanhamento',
        choices=LISTA_TIPO_PAINEL,
        default=PAINEL_PADRAO
    )
    ativo = models.BooleanField('Ativo', default=True)

    documentos = models.ManyToManyField('djdocuments.Documento',
                                        related_name='donos',
                                        blank=True)

    areas = models.ManyToManyField('Area', blank=True)
    categorias_de_agendas = models.ManyToManyField('evento.Categoria', blank=True)

    aceita_agendamento_pauta = models.SmallIntegerField(
        'Quem pode agendar na pauta?',
        choices=LISTA_AGENDAMENTO,
        default=AGENDAMENTO_TODOS
    )
    aceita_agendamento_extra = models.SmallIntegerField(
        'Quem pode agendar na extra-pauta?',
        choices=LISTA_AGENDAMENTO,
        default=AGENDAMENTO_TODOS
    )
    aceita_encaminhamento_pauta = models.SmallIntegerField(
        'Quem pode encaminhar na pauta?',
        choices=LISTA_AGENDAMENTO,
        default=AGENDAMENTO_TODOS
    )
    aceita_encaminhamento_extra = models.SmallIntegerField(
        'Quem pode encaminhar na extra-pauta?',
        choices=LISTA_AGENDAMENTO,
        default=AGENDAMENTO_TODOS
    )

    aceita_agendamento_futuro = models.BooleanField(
        'Aceita agendamento futuro?',
        default=True
    )

    aderiu_chat_edefensor = models.BooleanField('Aderiu Chat e-Defensor', default=False)

    # Flag para determinar se a Defensoria recebe distribuicao automatica
    encaminhamento_distribuido = models.BooleanField(
        verbose_name='Permite receber encaminhamento distribuido?',
        default=False,
        help_text='Flag para determinar se a Defensoria recebe distribuicao automatica'
    )
    # Flag para determinar se a Defensoria distribui automaticamente ao encaminhar agendamento
    distribuir_ao_encaminhar = models.BooleanField(
        verbose_name='Deve distribuir agendamento ao encaminhar?',
        default=False,
        help_text='Flag para determinar se a Defensoria distribui automaticamente ao encaminhar agendamento'
    )
    pode_vincular_processo_judicial = models.BooleanField(
        verbose_name="Pode vincular processo judicial?",
        default=True
    )
    pode_vincular_tarefa_de_cooperacao = models.BooleanField(
        verbose_name="Pode vincular tarefa de cooperação?",
        default=False,
        help_text='Atenção! Setores que participam do atendimento vão aparecer mesmo se esta opção estiver desmarcada'
    )
    pode_cadastrar_atividade_extraordinaria = models.BooleanField(
        default=False,
        verbose_name='Pode cadastrar Atividade Extraordinária?',
        help_text='Habilita CRUD de Atividade Extraordinária'
    )
    pode_cadastrar_peticionamento = models.BooleanField(
        default=False,
        verbose_name='Pode cadastrar Peticionamento?',
        help_text='Habilita CRUD de Peticionamentos'
    )

    varas = models.ManyToManyField('Vara', through='DefensoriaVara', through_fields=('defensoria', 'vara'),
                                   related_name='defensorias')

    # utilizado para vincular a Defensoria com os Tipos de Atividades para os relatórios estatísticos
    tipos_eventos = models.ManyToManyField(
        'core.TipoEvento',
        through='DefensoriaTipoEvento',
        through_fields=('defensoria', 'tipo_evento'),
        related_name='defensorias'
    )

    cabecalho_documento = models.TextField(
        blank=True,
        verbose_name='Cabeçalho Documento GED',
        help_text='Para utilizar formatação, utilize tags HTML'
    )
    rodape_documento = models.TextField(
        blank=True,
        verbose_name='Rodapé Documento GED',
        help_text='Para utilizar formatação, utilize tags HTML'
    )

    # DPE-AM
    triagem = models.BooleanField('Possui triagem?', default=False)
    agendamento_online = models.BooleanField('Possui agendamento online?', default=False)
    eh_mutirao = models.BooleanField(verbose_name='Unidade do Mutirão?', default=False)
    modalidade = models.SmallIntegerField(choices=LISTA_MODALIDADE, default=MODALIDADE_PRESENCIAL, blank=True, null=True)  # noqa: E501
    nivel_sigilo_indeferimento = models.SmallIntegerField('Nível de sigilo - Indeferimento',
                                                          default=DocumentoCore.SIGILO_0,
                                                          choices=DocumentoCore.LISTA_SIGILO,)
    indicador_meritocracia = models.ForeignKey('meritocracia.IndicadorMeritocracia', null=True, blank=True, on_delete=deletion.DO_NOTHING)  # noqa: E501

    objects = managers.DefensoriaManager()

    class Meta:
        ordering = ['comarca__nome', 'nome', 'numero']
        verbose_name = u'Defensoria'
        verbose_name_plural = u'Defensorias'
        permissions = (
            ('view_all_defensorias', u'Pode ver todas defensorias'),
        )

    def __str__(self):
        return self.nome

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        super(Defensoria, self).save(force_insert, force_update, using, update_fields)

        defensores = self.all_atuacoes.filter(
            ativo=True, defensor__eh_defensor=True
        ).order_by('defensor_id').values_list('defensor_id', flat=True).distinct()

        for defensor in defensores:
            cache_key = 'defensor.atuacao_listar:{}'.format(defensor)
            cache.delete(cache_key)

    @staticmethod
    def verifica_permissao_agendamento(valor_campo_aceita_agendamento, usuario):
        pode_agendar = False

        if valor_campo_aceita_agendamento == Defensoria.AGENDAMENTO_TODOS:
            pode_agendar = True
        elif (valor_campo_aceita_agendamento == Defensoria.AGENDAMENTO_APENAS_SETOR_AGENDAMENTO and
              (usuario.has_perm(perm='atendimento.view_129') or usuario.has_perm(perm='atendimento.view_recepcao'))):
            pode_agendar = True
        elif (valor_campo_aceita_agendamento == Defensoria.AGENDAMENTO_APENAS_GABINENTE_DEFENSOR and
              usuario.has_perm(perm='atendimento.view_defensor')):
            pode_agendar = True
        else:
            pode_agendar = False

        return pode_agendar


class DefensoriaEtiqueta(AuditoriaAbstractMixin):
    defensoria = models.ForeignKey('Defensoria', on_delete=models.PROTECT)
    etiqueta = models.ForeignKey('Etiqueta', on_delete=models.PROTECT)
    usuarios_autorizados = models.ManyToManyField('auth.User', blank=True)

    class Meta:
        db_table = 'contrib_defensoria_etiquetas'  # padrão m2m django (model principal + nome_do_campo m2m)
        ordering = ['defensoria', 'etiqueta']

    def __str__(self):
        return f'{self.defensoria.nome} - {self.etiqueta.nome}'


class DefensoriaVara(AuditoriaAbstractMixin):
    PARIDADE_QUALQUER = 0
    PARIDADE_IMPARES = 1
    PARIDADE_PARES = 2

    LISTA_PARIDADE = (
        (PARIDADE_QUALQUER, 'Qualquer'),
        (PARIDADE_IMPARES, 'Processos Ímpares'),
        (PARIDADE_PARES, 'Processos Pares'),
    )

    defensoria = models.ForeignKey('Defensoria', on_delete=models.PROTECT)
    vara = models.ForeignKey('Vara', on_delete=models.PROTECT)

    paridade = models.SmallIntegerField(choices=LISTA_PARIDADE, default=PARIDADE_QUALQUER)
    regex = models.CharField(verbose_name='Expressão regular da regra de distribuição (regex)', max_length=80, blank=True, null=True)  # noqa: E501
    usuario_webservice = models.CharField(verbose_name='Nome do usuário webservice', max_length=80, blank=True, null=True)  # noqa: E501

    principal = models.BooleanField(
        verbose_name='Principal',
        help_text='É o valor default?',
        blank=False,
        null=False,
        default=False)
    distribuicao_automatica = models.BooleanField(
        verbose_name='Distribuir Automaticamente',
        blank=False,
        null=False,
        default=False)
    distribuir_por_polo = models.ManyToManyField(
        'processo.ProcessoPoloDestinatario',
        verbose_name='Distribuir Avisos Por Determinado Polo do Destinatário',
        blank=True,
        default=None)
    distribuir_por_competencia = models.ManyToManyField(
        'procapi_client.Competencia',
        verbose_name='Distribuir Avisos Por Determinada Competência',
        blank=True,
        default=None
    )

    class Meta:
        db_table = 'contrib_defensoria_varas'  # padrão m2m django (model principal + nome_do_campo m2m)
        ordering = ['defensoria', 'vara']
        verbose_name = u'Defensoria / Vara'
        verbose_name_plural = u'Defensorias / Varas'


class DefensoriaTipoEvento(models.Model):
    defensoria = models.ForeignKey('Defensoria', on_delete=models.PROTECT)
    tipo_evento = models.ForeignKey('core.TipoEvento', on_delete=models.PROTECT)
    conta_estatistica = models.BooleanField(help_text='Conta Estatísticas?', default=True, null=False)

    class Meta:
        db_table = 'contrib_defensoria_tipos_eventos'  # padrão m2m django (model principal + nome_do_campo m2m)
        ordering = ['defensoria', 'tipo_evento']
        unique_together = ('defensoria', 'tipo_evento')
        verbose_name = u'Defensoria / Tipos de Evento'
        verbose_name_plural = u'Defensorias / Tipos de Evento'


class Documento(models.Model):
    nome = models.CharField(max_length=256)

    exibir_em_documento_assistido = models.BooleanField(default=True)
    exibir_em_documento_atendimento = models.BooleanField(default=False)

    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = u'Documento'
        verbose_name_plural = u'Documentos'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def nome_norm(self):
        return Util.normalize(self.nome)


class Papel(models.Model):

    LISTA_CSS_LABEL_CLASS = (
        ('', 'Default'),
        ('label-success', 'Success'),
        ('label-warning', 'Warning'),
        ('label-important', 'Important'),
        ('label-info', 'Info'),
        ('label-inverse', 'Inverse'),
    )

    nome = models.CharField(max_length=256)

    grupos = models.ManyToManyField("auth.Group")

    requer_supervisor = models.BooleanField(
        default=False,
        help_text="Exige informar um supervisor no cadastro do servidor?")

    requer_matricula = models.BooleanField(
        default=True,
        help_text="Exige informar a matrícula no cadastro do servidor?")

    requer_superusuario = models.BooleanField(
        default=False,
        help_text="Disponível apenas para superusuários?")

    marcar_usuario_como_defensor = models.BooleanField(
        default=False,
        help_text="Marcar usuário como defensor?")

    css_label_class = models.CharField(
        verbose_name='CSS Label Class',
        max_length=25,
        choices=LISTA_CSS_LABEL_CLASS,
        blank=True,
        default='',
        help_text="Usado para definir a cor de labels")

    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Papel'
        verbose_name_plural = 'Papéis'
        ordering = ['-ativo', 'nome']


def limitar_choices_papel():
    q = Q(ativo=True)
    return q


def servidor_photo_name(instance, filename):
    import uuid

    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)

    return '/'.join(['servidor', instance.usuario.username, filename])


def get_foto_redimensionada(foto):
    from PIL import Image
    from django.core.files import File
    import hashlib
    import time

    foto_redimensionada = None

    if foto:  # se foto existe confere tamanho
        with Image.open(foto) as img:
            (width, height) = img.size
            max_size = 480

            if width > max_size or height > max_size:  # só redimensiona se tamanho maior que o tamanho máximo

                if width > height:
                    wsize = max_size
                    wpercent = (wsize/float(width))
                    hsize = int((float(height)*float(wpercent)))
                else:
                    hsize = max_size
                    hpercent = (hsize/float(height))
                    wsize = int((float(width)*float(hpercent)))

                foto_redimensionada = img.resize((wsize, hsize))

                path_arquivo_temporario = "/tmp/%s.jpeg" % hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()

                foto_redimensionada.save(path_arquivo_temporario, format='JPEG', quality=90)
                return File(open(path_arquivo_temporario, 'rb'))
            else:
                return foto


class Servidor(models.Model):
    LISTA_SEXO = (
        (0, 'Masculino'),
        (1, 'Feminino')
    )
    papel = models.ForeignKey(
        "Papel",
        related_name="servidores",
        null=True,
        help_text="Conjunto de Permisssões do usuário",
        limit_choices_to=limitar_choices_papel,
        on_delete=deletion.PROTECT
    )
    nome = models.CharField(max_length=256, blank=True, db_index=True)
    usuario = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    comarca = models.ForeignKey(
        'Comarca',
        on_delete=deletion.PROTECT
    )
    cpf = models.CharField(max_length=32)
    data_nascimento = models.DateField(null=True, blank=True, default=None)
    data_nascimento.system_check_deprecated_details = dict(
        msg='O campo Servidor.data_nascimento foi depreciado.',
        hint='Retire as referências ao campo dos seus relatórios antes que ele seja removido',
        id='fields.CS001'
    )

    sexo = models.SmallIntegerField(choices=LISTA_SEXO, null=True, blank=True, default=None)
    matricula = models.CharField(max_length=256, blank=True)

    ativo = models.BooleanField(default=True)

    uso_interno = models.BooleanField(default=False, help_text='Define que este servidor é de uso interno do sistema')

    telefones = models.ManyToManyField('contrib.Telefone', blank=True, default=None)
    foto = models.ImageField("Foto", upload_to=servidor_photo_name, null=True, blank=True, default=None)

    data_atualizacao = models.DateTimeField(null=True, blank=True, default=None)

    _monitor_de_modificacoes = FieldTracker(fields=['papel_id'])

    class Meta:
        verbose_name = u'Servidor'
        verbose_name_plural = u'Servidores'
        ordering = ['nome']

    def get_foto(self):

        if not self.foto:
            return static('img/default_person.jpg')

        return '{}'.format(self.foto.url)

    def in_group(self, group_name):
        return self.usuario.groups.filter(name=group_name).exists()

    def coordenadoria(self):
        return self.comarca.coordenadoria or self.comarca

    @cached_property
    def proximo_itinerante(self):
        proximo = self.evento_set.filter(
            ativo=True,
            data_final__gte=datetime.date.today()
        ).order_by('data_inicial').first()
        return proximo

    def possiveis_conversas_chat(self):
        from defensor.models import Atuacao

        # Pega todas as defensorias em que o usuário logado tem atuações vigentes
        initial_user_atuacoes_vigentes = self.defensor.atuacoes_vigentes().values_list('defensoria_id', flat=True)

        # Pega todas as lotações do usuário logado nestas defensorias
        # Obtém todas as lotações do usuário em que está habilitado para utilizar o chat
        query_atuacoes = Atuacao.objects.filter(
            habilitado_chat_edefensor=True,
            visualiza_chat_edefensor=True,
            defensoria__id__in=initial_user_atuacoes_vigentes,
        ).vigentes_por_defensor(
            self.defensor
        )

        # Se for defensor, mostra apenas as atuações dele
        if self.defensor.eh_defensor:
            query_atuacoes = query_atuacoes.filter(defensor=self.defensor)

        possiveis_conversas = []

        # Para cada atuação, salva em uma string contendo a id da defensoria e a id do titular separados por um "#"
        # e adiciona no array "conversas"
        for a in query_atuacoes:

            # Se a Defensoria da atuação não aderiu o chat
            if not a.defensoria.aderiu_chat_edefensor:
                continue

            conversa = {
                'defensoria': str(a.defensoria.id)
            }

            defensor_titular = None

            # No caso de substituição, o titular é a propriedade "titular"
            if a.tipo == Atuacao.TIPO_SUBSTITUICAO:
                defensor_titular = a.titular
            # No caso de acumulação ou titularidade, o titular é a propridade "defensor"
            elif a.tipo in [Atuacao.TIPO_ACUMULACAO, Atuacao.TIPO_TITULARIDADE]:
                defensor_titular = a.defensor
            # No caso de lotação, o titular é o defensor da atuação do tipo titularidade relacionado àquela defensoria
            elif a.tipo == Atuacao.TIPO_LOTACAO:
                atuacoes_titular = Atuacao.objects.filter(
                    tipo__in=[Atuacao.TIPO_TITULARIDADE, Atuacao.TIPO_ACUMULACAO],
                    defensoria=a.defensoria,
                    ativo=True).first()
                if atuacoes_titular:
                    defensor_titular = atuacoes_titular.defensor

            if defensor_titular:

                from api.api_v1.serializers import ServidorBasicSerializer

                servidor_serializado = ServidorBasicSerializer(defensor_titular.servidor)

                conversa['titular'] = defensor_titular.id
                conversa['titular_dados'] = {
                    'id': defensor_titular.id,
                    'servidor': servidor_serializado.data
                }
                possiveis_conversas.append(conversa)

        return possiveis_conversas

    def __str__(self):
        return self.nome

    def possui_acesso_administracao_em_assistido(self, acessos):

        # verifica se o usuário possui acesso do tipo administração
        if self.usuario.is_superuser:
            return True
        else:
            lista_id_defensorias = self.defensor.defensorias.values_list('id', flat=True)
            for acesso in acessos:
                if acesso['concessao']['id'] in lista_id_defensorias and acesso['dono']:
                    return True

        return False

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        from defensor.models import Defensor

        if self.usuario:
            self.nome = self.usuario.get_full_name()

        # Redimensiona tamanho da foto antes de salvar
        foto_redimensionada = get_foto_redimensionada(self.foto)
        if foto_redimensionada:
            self.foto = foto_redimensionada

        super(Servidor, self).save(force_insert, force_update, using, update_fields)

        # Remove grupos de permissão do papel anterior
        self.usuario.groups.clear()
        # Adiciona grupos de permissão do novo papel
        novos_grupos = tuple(self.papel.grupos.all())
        self.usuario.groups.add(*novos_grupos)
        self.usuario.nao_salvar_servidor = True
        self.usuario.save()

        # Ativa cadastro de defensor de acordo com o papel
        defensor_ativo = self.papel.marcar_usuario_como_defensor
        if not self.papel.marcar_usuario_como_defensor and hasattr(self, 'defensor'):
            defensor_ativo = self.defensor.ativo

        # TODO: Avaliar impacto nas atuações ativas
        Defensor.objects.update_or_create(
            servidor=self,
            defaults={
                'eh_defensor': self.papel.marcar_usuario_como_defensor,
                'ativo': defensor_ativo
            }
        )

    def desativar(self, usuario, data_hora=None):
        self.usuario.is_active = False
        self.usuario.save()

    def reativar(self, usuario, data_hora=None):
        self.usuario.is_active = True
        self.usuario.save()


class Cargo(AuditoriaAbstractMixin):
    nome = models.CharField(max_length=512, null=False, db_index=True)
    nome_norm = models.CharField(max_length=512, null=False, db_index=True)
    codigo = models.CharField(max_length=512, null=False, db_index=True)

    def __str__(self):
        if self.codigo:
            return '{0} - {1}'.format(self.nome, self.codigo)
        else:
            return self.nome


class Deficiencia(models.Model):
    nome = models.CharField(max_length=512, null=False)
    ativo = models.BooleanField('Ativo', default=False)

    class Meta:
        verbose_name = u'Deficiência'
        verbose_name_plural = u'Deficiências'


class Vara(models.Model):

    GRAU_1 = 1
    GRAU_2 = 2
    GRAU_3 = 3

    LISTA_GRAU = (
        (GRAU_1, '1º Grau'),
        (GRAU_2, '2º Grau'),
        (GRAU_3, 'STF/STJ'),
    )

    data_cadastro = models.DateField('Data de Cadastro', null=True, blank=False, default=None)
    data_atualizacao = models.DateField('Data da última atualização', null=True, blank=False, default=None)
    comarca = models.ForeignKey(
        'Comarca',
        on_delete=deletion.PROTECT
    )
    nome = models.CharField(max_length=512, null=False)
    codigo_eproc = models.CharField(max_length=25, blank=True, null=True, default=None)
    ativo = models.BooleanField('Ativo', default=False)
    grau = models.SmallIntegerField(choices=LISTA_GRAU, default=GRAU_1)

    class Meta:
        ordering = ['-ativo', 'nome']
        verbose_name = u'Vara'
        verbose_name_plural = u'Varas'

    def __str__(self):
        return self.nome


class Salario(models.Model):

    vigencia = models.DateField()
    valor = models.DecimalField(max_digits=16, decimal_places=2)

    indice_renda_individual = models.DecimalField('Índice de renda individual',
                                                  max_digits=16,
                                                  decimal_places=2,
                                                  default=0)
    indice_renda_familiar = models.DecimalField('Índice de renda familiar',
                                                max_digits=16,
                                                decimal_places=2,
                                                default=0)
    indice_renda_per_capita = models.DecimalField('Índice de renda per capita',
                                                  max_digits=16,
                                                  decimal_places=2,
                                                  default=0)
    indice_valor_bens = models.DecimalField('Índice de valor em bens', max_digits=16, decimal_places=2, default=0)
    indice_valor_investimentos = models.DecimalField('Índice de valor em investimentos',
                                                     max_digits=16,
                                                     decimal_places=2,
                                                     default=0)
    tipo_pessoa = models.SmallIntegerField('Tipo de pessoa',
                                           choices=constantes.LISTA_TIPO_PESSOA,
                                           null=True,
                                           blank=False,
                                           default=constantes.TIPO_PESSOA_FISICA)
    indice_valor_salario_funcionario = models.DecimalField('Índice de salário do funcionário',
                                                           max_digits=16,
                                                           decimal_places=2,
                                                           default=0)

    @staticmethod
    def atual(tipo_pessoa=constantes.TIPO_PESSOA_FISICA):
        """Retorna o salário vigente conforme o tipo de pessoa (Física ou Jurídica)."""

        try:
            salario = Salario.objects.filter(tipo_pessoa=tipo_pessoa).latest('vigencia')
        except ObjectDoesNotExist as e:
            logger.error('Não existe Salário cadastrado para tipo_pessoa=%s. %s' % (tipo_pessoa, e))
            salario = None

        return salario

    def validar_renda_individual(self, renda_individual):
        """
        Faz validação da renda individual.
        Caso o índice seja zero a validação é desconsiderada.
        """

        validacao = True
        if renda_individual is not None and self.indice_renda_individual > 0:
            validacao = renda_individual <= self.valor * self.indice_renda_individual

        return validacao

    def validar_renda_familiar(self, renda_familiar):
        """
        Faz validação da renda familiar.
        Caso o índice seja zero a validação é desconsiderada.
        """

        validacao = True
        if renda_familiar is not None and self.indice_renda_familiar > 0:
            validacao = renda_familiar <= self.valor * self.indice_renda_familiar

        return validacao

    def validar_renda_per_capita(self, renda_per_capita):
        """
        Faz validação da renda per capita.
        Caso o índice seja zero a validação é desconsiderada.
        """

        validacao = True
        if renda_per_capita is not None and self.indice_renda_per_capita > 0:
            validacao = renda_per_capita <= self.valor * self.indice_renda_per_capita

        return validacao

    def validar_valor_bens(self, valor_bens):
        """
        Faz validação do valor dos bens, conforme o tipo de pessoa (Física ou Jurídica).
        Caso o índice seja zero a validação é desconsiderada.
        """

        validacao = True
        if valor_bens is not None and self.indice_valor_bens > 0:
            validacao = valor_bens <= self.valor * self.indice_valor_bens

        return validacao

    def validar_valor_investimentos(self, valor_investimentos):
        """
        Faz validação do valor de investimentos.
        Caso o índice seja zero a validação é desconsiderada.
        """

        validacao = True
        if valor_investimentos is not None and self.indice_valor_investimentos > 0:
            validacao = valor_investimentos <= self.valor * self.indice_valor_investimentos

        return validacao

    def validar_valor_salario_funcionario(self, valor_salario_funcionario):
        """
        Faz validação do valor do salário do funcionário.
        Caso o índice seja zero a validação é desconsiderada.
        """

        validacao = True

        if valor_salario_funcionario is not None and self.indice_valor_salario_funcionario > 0:
            validacao = valor_salario_funcionario <= self.valor * self.indice_valor_salario_funcionario
        return validacao


class CPF:
    def __init__(self):
        """
        Class to interact with CPF numbers
        """
        pass

    @staticmethod
    def format(cpf):
        """
        Method that formats a brazilian CPF
        """
        return "%s.%s.%s-%s" % (cpf[0:3], cpf[3:6], cpf[6:9], cpf[9:11])

    @staticmethod
    def validate(cpf):
        """
        Method to validate a brazilian CPF number
        Based on Pedro Werneck source avaiable at
        www.PythonBrasil.com.br
        """

        if cpf is None:
            return False

        cpf_invalidos = [11 * str(i) for i in range(10)]
        if cpf in cpf_invalidos:
            return False

        if not cpf.isdigit():
            """ Verifica se o CPF contem pontos e hifens """
            cpf = cpf.replace(".", "")
            cpf = cpf.replace("-", "")

        if len(cpf) < 11:
            """ Verifica se o CPF tem 11 digitos """
            return False

        if len(cpf) > 11:
            """ CPF tem que ter 11 digitos """
            return False

        selfcpf = [int(x) for x in cpf]

        cpf = selfcpf[:9]

        while len(cpf) < 11:

            r = sum([(len(cpf) + 1 - i) * v for i, v in [(x, cpf[x]) for x in range(len(cpf))]]) % 11

            if r > 1:
                f = 11 - r
            else:
                f = 0
            cpf.append(f)

        return bool(cpf == selfcpf)

    # TODO: chamar metodo validate da classe CNPJ
    @staticmethod
    def is_cpf(cpf):
        return cpfcnpj.validate(cpf)


class CNPJ:
    def __init__(self):
        """
        Class to interact with CNPJ numbers
        """
        pass

    @staticmethod
    def validate(cnpj):
        return cpfcnpj.validate(cnpj)

    # TODO: chamar metodo validate da classe CNPJ
    @staticmethod
    def is_cnpj(cnpj):
        return cpfcnpj.validate(cnpj)


class MenuExtra(AuditoriaAbstractMixin):

    LOCAL_ROOT = 'root'
    LOCAL_AJUDA = 'ajuda'
    LOCAL_CONVENIO = 'convenios'

    LOCAIS = (
        (LOCAL_ROOT, u'Root'),
        (LOCAL_AJUDA, u'Ajuda'),
        (LOCAL_CONVENIO, u'Convênios'),
    )

    local = models.CharField(
        choices=LOCAIS,
        default=LOCAL_AJUDA,
        max_length=255
    )

    posicao = models.PositiveSmallIntegerField()
    nome = models.CharField(max_length=255)
    descricao = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    icone = models.CharField(max_length=255)

    objects = managers.MenuExtraManager()

    class Meta:
        verbose_name = u'Menu Extra'
        verbose_name_plural = u'Menus Extra'
        ordering = ['local', 'posicao']

    def __str__(self):
        return self.nome


class OrientacaoSexual(AuditoriaAbstractMixin):
    nome = models.CharField(max_length=256)

    objects = managers.OrientacaoSexualManager()

    class Meta:
        verbose_name = u'Orientação Sexual'
        verbose_name_plural = u'Orientações Sexuais'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class IdentidadeGenero(AuditoriaAbstractMixin):
    nome = models.CharField(max_length=256)

    objects = managers.IdentidadeGeneroManager()

    class Meta:
        verbose_name = u'Identidade de Gênero'
        verbose_name_plural = u'Identidades de Gênero'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class GeneroPessoa(AuditoriaAbstractMixin):
    nome = models.CharField(max_length=256)

    objects = managers.GeneroPessoaManager()

    class Meta:
        verbose_name = u'Gênero'
        verbose_name_plural = u'Gêneros'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Cartorio(AuditoriaAbstractMixin):
    cns = models.CharField(max_length=6, unique=True, help_text='Código Nacional da Serventia')
    nome = models.CharField(max_length=255)
    municipio = models.ForeignKey('Municipio', on_delete=models.deletion.PROTECT)

    def __str__(self):
        return self.nome


class Etiqueta(AuditoriaAbstractMixin):
    nome = models.CharField(max_length=255)
    cor = models.CharField(max_length=7, blank=True, default='')
    defensorias = models.ManyToManyField(
        'Defensoria',
        through='DefensoriaEtiqueta',
        through_fields=('etiqueta', 'defensoria')
    )

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class HistoricoLogin(AuditoriaAbstractMixin):
    endereco_ip = models.CharField(max_length=255)
    info_navegador = models.CharField(max_length=255, null=True)
    logout = models.DateTimeField(null=True)

    class Meta:
        verbose_name = u'Histórico Login'

    def __str__(self):
        return self.endereco_ip

    def save(self, *args, **kwargs):
        if args:
            self.cadastrado_por = args[0]

        super(HistoricoLogin, self).save(*args, **kwargs)


reversion.register(Telefone)
reversion.register(CEP)
reversion.register(Endereco)
reversion.register(EnderecoHistorico)
reversion.register(Pais)
reversion.register(Estado)
reversion.register(Municipio)
reversion.register(Bairro)
reversion.register(Area)
reversion.register(Comarca)
reversion.register(Defensoria)
reversion.register(Documento)
reversion.register(Servidor)
reversion.register(Deficiencia)
reversion.register(Vara)
reversion.register(Salario)
reversion.register(Cargo)
reversion.register(OrientacaoSexual)
reversion.register(IdentidadeGenero)
