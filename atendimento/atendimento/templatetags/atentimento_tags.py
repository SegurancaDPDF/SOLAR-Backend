# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django import template


register = template.Library()


@register.filter
def resposta(pergunta, atendimento):
    try:
        resposta = pergunta.resposta_set.get(atendimento=atendimento)
        return resposta.texto
    except Exception:
        return ""
