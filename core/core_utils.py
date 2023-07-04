# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from constance import config
from functools import wraps
from core.models import Documento
from contrib.models import Servidor


def executar_se_constance_ativo(constance_variable_name):
    def decorate(funcao):
        @wraps(funcao)
        def wrapper(*args, **kwargs):
            if getattr(config, constance_variable_name):
                return funcao(*args, **kwargs)
            else:
                return 'Nao executado - Opcao {} do constance esta desativado no admin'.format(constance_variable_name)

        return wrapper

    return decorate


def _is_documento_valido(documento):
    return True if documento else False


def _is_documento_publico(documento):
    PUBLICO = Documento.SIGILO_0
    return documento.nivel_sigilo == PUBLICO


def _is_servidor_cadastrou_documento(documento: Documento, servidor: Servidor) -> bool:
    return documento.cadastrado_por_id == servidor.usuario_id


def _is_servidor_relacionado_documento(documento: Documento, servidor: Servidor) -> bool:
    return documento.processo.indeferimento.defensor.servidor_id == servidor.id


def _is_servidor_lotado_defensoria_permissao(servidor: Servidor) -> bool:
    tem_permissao_por_lotacao = servidor.defensor.defensorias.filter(
            nivel_sigilo_indeferimento__gt=Documento.SIGILO_0,
            nucleo__indeferimento_pode_registrar_decisao=True).exists()
    return tem_permissao_por_lotacao


def permissao_documento_indeferimento(documento: Documento, servidor: Servidor) -> bool:
    """
        Retorna se o usuário tem permissão para visualizar o documento \n
        1 - Verifica se o documento não é nulo (necessário pois há alto nível de complexidade em alguns templates) ou
        2 - Verifica se o documento tem algum nível de sigilo restritivo ou \n
        3 - Verifica se o usuário é o servidor que cadastrou o documento ou \n
        4 - Verifica se o usuário é o servidor relacionado ao indeferimento ou \n
        5 - Verifica se o usuário está lotado em alguma defensoria com permissão
            para visualizar arquivos sigilosos ex.: corregedoria \n
        Parameters:
                documento (Documento): documento a ser acessado
                servidor (Servidor): servidor que deseja acessar o documento
        Returns:
                permissão (bool): Se o usuário tem permissão para visualizar o documento
    """
    return (
        not _is_documento_valido(documento) or
        _is_documento_publico(documento) or
        _is_servidor_cadastrou_documento(documento, servidor) or
        _is_servidor_relacionado_documento(documento, servidor) or
        _is_servidor_lotado_defensoria_permissao(servidor)
    )


def permissao_editar_sigilo_documento(documento: Documento, servidor: Servidor) -> bool:
    """
        Retorna se o usuário tem permissão para editar o documento \n
        1 - Verifica se o documento não é nulo (necessário pois há alto nível de complexidade em alguns templates) ou
        2 - Verifica se o usuário é o servidor que cadastrou o documento ou \n
        3 - Verifica se o usuário é o servidor relacionado ao indeferimento ou \n
        4 - Verifica se o usuário está lotado em alguma defensoria com permissão
            para visualizar arquivos sigilosos ex.: corregedoria \n
        Parameters:
                documento (Documento): documento a ser acessado
                servidor (Servidor): servidor que deseja acessar o documento
        Returns:
                permissão (bool): Se o usuário tem permissão para visualizar o documento
    """
    return (
        not _is_documento_valido(documento) or
        _is_servidor_cadastrou_documento(documento, servidor) or
        _is_servidor_relacionado_documento(documento, servidor) or
        _is_servidor_lotado_defensoria_permissao(servidor)
    )
