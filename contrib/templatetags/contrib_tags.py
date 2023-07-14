# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import json
import base64
import logging
import mimetypes
import os
import re
from datetime import date, datetime, time
from urllib.parse import urlencode

# Bibliotecas de terceiros
from constance import config
from django import template
from django.conf import settings
from django.db.models import Q
from django.utils.safestring import mark_safe

from contrib.models import Comarca, MenuExtra
from core.models import Documento
from contrib.models import Servidor
from core.core_utils import (
    permissao_documento_indeferimento,
    permissao_editar_sigilo_documento
)

logger = logging.getLogger(__name__)
register = template.Library()

re_only_number = re.compile(r'\d*')

@register.filter('title2')
def title2(value):
    '''
    Coloca as palavras com letra minúscula, exceto as iniciais de palavras com mais de 2 letras
    '''
    words = value.split()
    final_words = []
    for word in words:
        if len(word) <= 2:
            final_words.append(word.lower())
        else:
            final_words.append(word.capitalize())
    return ' '.join(final_words)


@register.filter('klass')
def klass(obj):  # retona o nome da clase do widget
    return obj.field.widget.__class__.__name__


@register.filter('field_class_name')
def field_class_name(obj):  # retorna o nome da classe do campo
    return obj.field.__class__.__name__


@register.filter
def form_datahora_mni(val):
    '''
    Converte string de data no formato MNI para datetime
    '''
    resposta = None

    if val:
        resposta = datetime.strptime(val, '%Y%m%d%H%M%S')

    return resposta


@register.filter
def form_datahora_json(val):
    '''
    Converte string de data no formato JSON para datetime
    '''
    resposta = None

    if val:
        resposta = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')

    return resposta


@register.filter
def form_numero_atendimento(val):  # formata número de antendimento
    val = str(val)
    return '{}.{}.{}'.format(val[0:6], val[6:9], val[9:12])


@register.filter
def form_numero_processo(val):  # formata número do processo
    from processo.processo.models import Processo
    return Processo.formatar_numero(val)


@register.filter
def form_numero_cpf_cnpj(val):  # formata número de CPF ou CNPJ
    resposta = None

    if val is not None:
        if len(val) == 11:
            resposta = '%s.%s.%s-%s' % (val[0:3], val[3:6], val[6:9], val[9:11])
        elif len(val) == 14:
            resposta = '%s.%s.%s/%s-%s' % (val[0:2], val[2:5], val[5:8], val[8:12], val[12:14])

    return resposta


@register.filter
def form_numero_cep(val):  # formata número de CEP
    resposta = val

    if len(val) == 8:
        resposta = '%s-%s' % (val[:5], val[5:])

    return resposta


@register.filter
def get_foto_servidor(user):  # obtem a foto do servidor
    return user.servidor.get_foto()


@register.simple_tag(takes_context=True)
def get_version(context):  # obtem a versão
    return settings.VERSION


@register.simple_tag(takes_context=True)
def get_application_id(context):  # obtem o id da aplicacao
    return settings.APPLICATION_ID


@register.simple_tag(takes_context=True)
def get_application_name(context):  # obtem o nome da aplicacao
    return settings.APPLICATION_NAME


@register.simple_tag(takes_context=True)
def get_comarca_servidor(context):  # obtem o nome da comarca do servidor
    if context['request'].session.get('comarca') == context['request'].user.servidor.comarca.id:
        return context['request'].user.servidor.comarca.nome
    else:
        comarca = Comarca.objects.get(id=context['request'].session.get('comarca'))
        return comarca.nome


@register.simple_tag(takes_context=True)
def get_possiveis_conversas(context):  # obtem as possíveis conversas de chat
    user = context['request'].user

    if not user:
        return json.dumps([])

    possiveis_conversas = user.servidor.possiveis_conversas_chat()

    return json.dumps(possiveis_conversas)


@register.simple_tag(takes_context=True)
def get_user_id(context):  # obter o ID do usuário
    user = context['request'].user
    return str(user.id)


@register.filter
def jsonmsg(obj):  # converter lista de mensagens em formato JSON
    import json as simplejson

    lst = []
    for msg in obj:
        lst.append({
            'msg': msg.message,
            'tag': msg.tags
        })

    return simplejson.dumps(lst)


@register.filter
def jsonify(objeto):
    return json.dumps(objeto)


@register.filter
def bs_label(index):
    if index == 0:
        return 'label-important'
    elif index == 1:
        return 'label-warning'
    elif index == 2:
        return 'label-info'
    else:
        return ''


@register.filter
def get_value_by_key(lst, key):  # obtem o valor correspondente a uma chave em um dicionário
    if key in lst:
        return lst[key]


@register.simple_tag(takes_context=True)
def get_total_atualizacoes(context):
    from contrib.models import Atualizacao, Servidor

    servidor = Servidor.objects.get(usuario_id=context['request'].user.id)

    if servidor.data_atualizacao is None:
        total = Atualizacao.objects.filter(ativo=True).count()
    else:
        total = Atualizacao.objects.filter(ativo=True, data__gt=servidor.data_atualizacao).count()

    if total:
        return total
    else:
        return ''


@register.simple_tag(takes_context=True)
def get_total_atendimentos_recepcao(context):
    from atendimento.atendimento.models import Atendimento, Defensor as AtendimentoDefensor
    from comarca.models import Predio
    from nucleo.itinerante.models import Evento

    inicio = date.today()
    termino = datetime.combine(inicio, time.max)

    # Se servidor vinculado a um itinerante ativo, redireciona
    evento = Evento.objects.filter(
        data_inicial__lte=date.today(),
        data_final__gte=date.today(),
        participantes=context['request'].user.servidor,
        ativo=True).first()

    if evento:

        atendimentos = AtendimentoDefensor.objects.filter(
            Q(defensoria=evento.defensoria) &
            Q(tipo__in=[1, 2, 4]) &
            Q(data_agendamento__range=[inicio, termino]) &
            Q(data_atendimento=None) &
            Q(remarcado=None) &
            Q(ativo=True) &
            (
                Q(filhos__id=None) |
                (
                    ~Q(
                        Q(filhos__tipo=Atendimento.TIPO_RECEPCAO) &
                        Q(filhos__ativo=True)
                    )
                )
            )
        )

    else:

        comarca = context['request'].session.get('comarca')
        predio = context['request'].session.get('predio')

        atendimentos = AtendimentoDefensor.objects.filter(
            Q(defensoria__comarca_id=comarca) &
            Q(tipo__in=[1, 2, 4]) &
            Q(data_agendamento__range=[inicio, termino]) &
            Q(data_atendimento=None) &
            Q(remarcado=None) &
            Q(ativo=True) &
            (
                Q(filhos__id=None) |
                (
                    ~Q(
                        Q(filhos__tipo=Atendimento.TIPO_RECEPCAO) &
                        Q(filhos__ativo=True)
                    )
                )
            )
        )

        if predio:

            predio = Predio.objects.get(id=predio)

            if not predio.visao_comarca:
                atendimentos = atendimentos.filter(defensoria__predio=predio)

    total = atendimentos.count()

    if total:
        return total
    else:
        return ''


@register.filter
def get_total_atendimentos_nucleo(defensor, nucleo):  # obter o total de atendimentos de um defensor em um núcleo
    from atendimento.atendimento.models import Defensor as Atendimento
    from defensor.models import Atuacao

    inicio = date.today()
    termino = datetime.combine(inicio, time.max)

    total = Atendimento.objects.filter(
        (
            Q(data_agendamento__range=[inicio, termino]) | (
                Q(data_agendamento=None) &
                Q(tipo=Atendimento.TIPO_NUCLEO)
            )
        ),
        (
            Q(defensor=defensor) |
            Q(substituto=defensor)
        ),
        defensoria__in=Atuacao.objects.filter(
            defensor=defensor,
            defensoria__nucleo=nucleo,
            ativo=True
        ).values(
            'defensoria'
        ),
        data_atendimento=None,
        remarcado=None,
        ativo=True,
    ).count()

    if total:
        return total
    else:
        return ''


@register.simple_tag(takes_context=True)
def get_total_atendimentos_nucleos(context):
    from atendimento.atendimento.models import Defensor as Atendimento
    from defensor.models import Atuacao

    if hasattr(context['request'].user.servidor, 'defensor'):
        defensor = context['request'].user.servidor.defensor
    else:
        defensor = None

    inicio = date.today()
    termino = datetime.combine(inicio, time.max)

    total = Atendimento.objects.filter(
        (
            Q(data_agendamento__range=[inicio, termino]) |
            (
                Q(data_agendamento=None) &
                Q(tipo=Atendimento.TIPO_NUCLEO)
            )
        ),
        (
            Q(defensor=defensor) |
            Q(substituto=defensor)
        ),
        defensoria__in=Atuacao.objects.filter(
            defensor=defensor,
            ativo=True
        ).exclude(
            defensoria__nucleo=None
        ).values(
            'defensoria'
        ),
        data_atendimento=None,
        remarcado=None,
        ativo=True
    ).count()

    if total:
        return total
    else:
        return ''


@register.simple_tag(takes_context=True)
def get_total_progressoes_proximas(context):  # obtem o total de progressoes proximas
    from nucleo.nadep.services import Prisao as ServicesPrisao

    if hasattr(context['request'].user.servidor, 'defensor'):  # obtem o total de progressoes do defensor atual
        total = ServicesPrisao.list_progressao_defensor(context['request'].user.servidor.defensor).count()
    else:
        total = None

    if total:
        return total
    else:
        return ''


@register.simple_tag
def get_current_time(format_string):  # hora atual formatada
    return datetime.now().strftime(format_string)


def default_menu_extra(context):  # retorna o menu extra
    return {
        'request': context['request'],
        'menus': MenuExtra.objects.ativos().filter(local=MenuExtra.LOCAL_ROOT).order_by('posicao')
    }


def default_menu_ajuda(context):  # retorna o menu de ajuda
    return {
        'request': context['request'],
        'menus': MenuExtra.objects.ativos().filter(local=MenuExtra.LOCAL_AJUDA).order_by('posicao')
    }


def default_menu_convenio(context):  # retorna o menu de convenio
    return {
        'request': context['request'],
        'menus': MenuExtra.objects.ativos().filter(local=MenuExtra.LOCAL_CONVENIO).order_by('posicao'),
        'quantidade_itens':  MenuExtra.objects.ativos().filter(local=MenuExtra.LOCAL_CONVENIO).count()
    }


def default_menu_nucleos(context):  # retorna o menu de nucleos
    from nucleo.nucleo.models import Nucleo

    nucleos = None
    servidor = context['request'].user.servidor

    if hasattr(servidor, 'defensor'):
        nucleos_list = Nucleo.objects.menu(servidor.defensor)
        nucleos = nucleos_list.values()

    return {
        'request': context['request'],
        'nucleos': nucleos,
        'perms': context['perms']
    }


def default_menu_plantao(context):  # retorna o menu de plantao
    from nucleo.nucleo.models import Nucleo

    if hasattr(context['request'].user.servidor, 'defensor'):
        defensor = context['request'].user.servidor.defensor
        plantao = Nucleo.objects.menu_plantao(defensor).values_list('id', 'nome')
    else:
        defensor = None
        plantao = None

    return {
        'request': context['request'],
        'defensor': defensor,
        'plantao': plantao,
        'perms': context['perms']
    }


def default_menu_comarcas(context):  # retorna o menu de comarcas

    if hasattr(context['request'].user.servidor, 'defensor'):
        defensor = context['request'].user.servidor.defensor
        comarcas = Comarca.objects.menu(defensor).values_list('id', 'nome')
    else:
        defensor = None
        comarcas = None

    return {
        'request': context['request'],
        'defensor': defensor,
        'comarcas': comarcas,
        'perms': context['perms'],
        'config': context['config']
    }


def default_menu_nadep(context):  # retorna o menu nadep
    return default_menu_comarcas(context)


def mensagem_producao(context):
    from django.conf import settings

    return {
        'request': context['request'],
        'debug': settings.DEBUG,
        'databases': settings.DATABASES
    }


@register.simple_tag(takes_context=True)
def get_total_honorarios_encaminhados(context):
    from processo.honorarios.models import Honorario, Movimento
    from django.db.models import Max
    total_transitados_encaminhado = None
    # TODO otimizar esse contador, se for o caso com sql puro
    if hasattr(context['request'].user.servidor, 'defensor'):
        if context['request'].user.servidor.defensor.eh_defensor:
            total_transitados_geral = Honorario.objects.filter(movimentos_honorario__ativo=True).annotate(
                max=Max('movimentos_honorario__tipo'))
            total_transitados_encaminhado = total_transitados_geral.filter(
                defensor__id=context['request'].user.servidor.defensor.id, max=Movimento.TIPO_ENCAMINHADO_DEF).count()

    if total_transitados_encaminhado:
        return total_transitados_encaminhado
    else:
        return ''


@register.simple_tag(takes_context=True)
def get_url_processo_tj(context, numero, grau=None, chave=None):

    if grau is None:
        grau = ''

    if chave is None:
        chave = ''

    url_formatada = config.URL_PROCESSO_TJ.format(
        numero=numero,
        grau=grau,
        chave=chave
    )
    return url_formatada


@register.simple_tag
def get_perms_honorarios_by_defensor(user):
    from processo.honorarios.models import Movimento
    # TODO otimizar essa permissao
    if hasattr(user.servidor, 'defensor'):
        if user.servidor.defensor and user.servidor.defensor.eh_defensor:
            if Movimento.objects.filter(ativo=True, defensor__id=user.servidor.defensor.id,
                                        tipo=Movimento.TIPO_ENCAMINHADO_DEF).count():
                return True
    return False


@register.filter(name='has_group')
def has_group(user, group_name):  # verifica se o usuario possui grupo especifico
    return user.groups.filter(name=group_name).exists()


@register.filter
def filename(value):  # nome do arquivo
    return os.path.basename(value)


@register.filter
def filetype(value):  # tipo do arquivo
    type, encoding = mimetypes.guess_type(value, strict=True)
    return type


@register.filter
def fileextension(value):  # extensao do arquivo
    name, extension = os.path.splitext(value)
    return extension[1:]


@register.filter('base64encode')
def do_base64encode(value):
    encoded = base64.b64encode(value.encode('ascii')).decode('ascii')
    encoded = encoded.replace('\n', '')
    return mark_safe(encoded)


@register.filter('cpf_servidor')
def do_cpf_servidor(user):
    cpf = ''
    if user and hasattr(user, 'servidor'):
        if user.servidor and user.servidor.cpf:
            cpf = re_only_number.sub(user.servidor.cpf, '')
    return cpf


@register.filter()
def divide(n1, n2):
    try:
        return n1 / n2
    except ZeroDivisionError:
        return None


@register.filter()
def percentof(amount, total):
    try:
        return '{:.1f}%'.format(amount / total * 100)
    except ZeroDivisionError:
        return None


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)


# TODO Avaliar possíveis impactos nas demais telas que utilizam a tag url_replace
#      e substituir por esta tag renomeando-a para url_replace
@register.simple_tag(takes_context=True)
def url_replace_tarefas(context, **kwargs):
    query = dict(context['request'].GET)
    query.update(kwargs)

    return urlencode(query, doseq=True)


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.

    It also removes any empty parameters to keep things neat,
    so you can remove a parm by setting it to ``""``.

    For example, if you're on the page ``/things/?with_frosting=true&page=5``, then

    <a href="/things/?{% param_replace page=3 %}">Page 3</a>

    would expand to

    <a href="/things/?with_frosting=true&page=3">Page 3</a>

    Based on
    https://stackoverflow.com/questions/22734695/next-and-before-links-for-a-django-paginated-query/22735278#22735278
    https://www.caktusgroup.com/blog/2018/10/18/filtering-and-pagination-django/
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()


@register.simple_tag(takes_context=False)
def permissao_visualizar_documento_indeferimento_tag(documento: Documento, servidor: Servidor) -> bool:
    return permissao_documento_indeferimento(documento, servidor)


@register.simple_tag(takes_context=False)
def permissao_editar_sigilo_documento_indeferimento_tag(documento: Documento, servidor: Servidor) -> bool:
    return permissao_editar_sigilo_documento(documento, servidor)


register.inclusion_tag("default_menu_extra.html", takes_context=True)(default_menu_extra)
register.inclusion_tag("default_menu_ajuda.html", takes_context=True)(default_menu_ajuda)
register.inclusion_tag("default_menu_convenio.html", takes_context=True)(default_menu_convenio)
register.inclusion_tag("default_menu_comarcas.html", takes_context=True)(default_menu_comarcas)
register.inclusion_tag("default_menu_nucleos.html", takes_context=True)(default_menu_nucleos)
register.inclusion_tag("default_menu_plantao.html", takes_context=True)(default_menu_plantao)
register.inclusion_tag("mensagem_producao.html", takes_context=True)(mensagem_producao)
register.inclusion_tag("default_menu_nadep.html", takes_context=True)(default_menu_nadep)
