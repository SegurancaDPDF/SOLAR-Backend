# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import re

import six
from django.contrib.auth.models import User

from contrib.models import Util
import contrib.forms
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


def letras_iniciais(partes_nome_list):
    letras = ''
    for parte in partes_nome_list:
        letras = '{}{}'.format(letras, parte[:2])

    return letras


algoritmo_segunda_parte = {
    'letras_iniciais': letras_iniciais
}


def criar_username_de_nome(nome_completo, alg_segunda_parte='letras_iniciais'):
    def _gerencia_sufixo(sufixo, caso=1):
        if caso == 1:
            return sufixo[0:3:2]
        elif caso == 2:
            return '{}{}'.format(sufixo[0], sufixo[-2])
        else:
            return sufixo[:2]

    def _monta_username(prefixo, sufixo, caso=1):
        username = '{}.{}'.format(prefixo, _gerencia_sufixo(sufixo, caso))
        if User.objects.filter(username=username).exists():
            caso += 1
            if caso > 3:
                return username
            return _monta_username(prefixo, sufixo, caso)
        return username

    nome_completo = six.text_type(nome_completo)
    nome_completo = Util.unaccent(nome_completo).lower()

    ignorados = ['do', 'dos', 'da', 'das', 'de']
    partes_nome_list = [palavra for palavra in nome_completo.split() if palavra not in ignorados]

    username = ''
    if partes_nome_list:
        username = partes_nome_list.pop(0)
        if partes_nome_list:
            prefixo = '{}'.format(username)
            sufixo = algoritmo_segunda_parte.get(alg_segunda_parte)(partes_nome_list)
            username = _monta_username(prefixo, sufixo)

    return username


def validar_cpf(cpf):
    """
    Valida CPFs, retornando apenas a string de números válida.
    """

    cpf = ''.join(re.findall(r'\d', str(cpf)))

    if (not cpf) or (len(cpf) < 11):
        return False

    # Pega apenas os 9 primeiros dígitos do CPF e gera os 2 dígitos que faltam
    inteiros = list(map(int, cpf))
    novo = inteiros[:9]

    while len(novo) < 11:
        r = sum([(len(novo)+1-i)*v for i, v in enumerate(novo)]) % 11

        if r > 1:
            f = 11 - r
        else:
            f = 0
        novo.append(f)

    # Se o número gerado coincidir com o número original, é válido
    if novo == inteiros:
        return cpf
    return False


def validar_cnpj(cnpj):
    """
    Valida CNPJs, retornando apenas a string de números válida.
    """

    cnpj = ''.join(re.findall(r'\d', str(cnpj)))

    if (not cnpj) or (len(cnpj) < 14):
        return False

    # Pega apenas os 12 primeiros dígitos do CNPJ e gera os 2 dígitos que faltam
    inteiros = list(map(int, cnpj))
    novo = inteiros[:12]

    prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    while len(novo) < 14:
        r = sum([x*y for (x, y) in zip(novo, prod)]) % 11
        if r > 1:
            f = 11 - r
        else:
            f = 0
        novo.append(f)
        prod.insert(0, 6)

    # Se o número gerado coincidir com o número original, é válido
    if novo == inteiros:
        return cnpj

    return False


def ip_visitante(request):

    if request:

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        return ip


@never_cache
@login_required
def email_info_acesso(request):
    form_password_reset = contrib.forms.CustomPasswordResetForm(request.POST)
    if form_password_reset.is_valid():
        form_password_reset.save()
    return JsonResponse({'error': False})
