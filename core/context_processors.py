from datetime import datetime
from django.conf import settings
from django.db.models import Q
from constance import config
from contrib.models import Defensoria


def chronus_config(request):
    """
    Returns a CHRONUS_CONFIG context variable.
    """
    return {
        'CHRONUS_URL': settings.CHRONUS_URL,
        'CHRONUS_PODE_GERAR_XLSX_SEM_PAGINACAO': settings.CHRONUS_PODE_GERAR_XLSX_SEM_PAGINACAO,
    }


def google_analytics(request):
    """
    Returns a GOOGLE_ANALYTICS context variable.
    """
    return {
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
        'GOOGLE_ANALYTICS_4_ID': settings.GOOGLE_ANALYTICS_4_ID

    }


def signo_config(request):
    """
    Returns a SIGNO_CONFIG context variable.
    """
    return {
        'SIGNO_ENABLE': config.USAR_NOTIFICACOES_SIGNO,
        'SIGNO_WEBSOCKET_URL': settings.SIGNO_WEBSOCKET_URL,
        'SIGNO_REST_API_URL': settings.SIGNO_REST_API_URL
    }


def edefensor_config(request):
    """
    Returns e-Defensor context variable.
    """
    return {
        'USAR_EDEFENSOR': settings.USAR_EDEFENSOR,
        'EDEFENSOR_ADONIS_HOSTNAME': settings.EDEFENSOR_ADONIS_HOSTNAME,
        'EDEFENSOR_ADONIS_PORT': settings.EDEFENSOR_ADONIS_PORT,
    }


def permissao_acesso_propacs(request):
    """
    Retorna dicionário com dados caso o servidor tenha um defensor
    e se ele tiver acesso ao módulo de propac.
    """

    defensorias = []
    defensorias_ids = []
    acesso = False
    servidor = None

    if hasattr(request.user, 'servidor'):
        servidor = request.user.servidor

    if hasattr(servidor, 'defensor'):
        defensorias = servidor.defensor.defensorias
        defensorias_ids = list(defensorias.values_list('id', flat=True))
        acesso = len(defensorias_ids) > 0

    return {
        'acesso': acesso,
        'defensorias': defensorias_ids,
        'dados': defensorias
    }
