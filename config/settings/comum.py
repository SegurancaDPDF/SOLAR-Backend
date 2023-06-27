# -*- coding: utf-8 -*-
# from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
from collections import OrderedDict
import ldap
import os
import re

# Bibliotecas de terceiros
from dj_database_url import parse as db_url
from prettyconf import config

from core.casts import int_or_none

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Obtém a versão do sistema a partir do arquivo CHANGELOG.md
VERSION = None
with open(os.path.join(ROOT_PATH, 'CHANGELOG.md')) as changelog:
    for line in changelog:
        result = re.findall(r'\[\d+.\d+.\d+\]', line)
        if result:
            VERSION = result[0][1:-1]
            break

# Sentry Config
SENTRY_DSN = config('SENTRY_DSN', default='')
SENTRY_TRACES_SAMPLE_RATE = config('SENTRY_TRACES_SAMPLE_RATE', default=1.0, cast=float)

if SENTRY_DSN:

    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
        # By default the SDK will try to use the SENTRY_RELEASE
        # environment variable, or infer a git commit
        # SHA as release, however you may want to set
        # something more human-readable.
        release=VERSION
    )

try:
    import datetime
    # workaround to bug on python interpreter http://bugs.python.org/issue7980
    # https://gitlab.defensoria.to.def.br/defensoria/sisat/issues/792
    datetime.datetime.strptime('', '')
except Exception:  # noqa
    pass

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEBUG = config('DEBUG', default=False, cast=config.boolean)
DEBUG_TOOLBAR = config('DEBUG_TOOLBAR', default=False, cast=config.boolean)
DEBUG_VSCODE = config('DEBUG_VSCODE', default=False)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=config.list)

ADMINS = (
    ('Suporte', config('EMAIL_TO_REPORT_ERRORS', default='')),
)

MANAGERS = ADMINS

DATABASES = {
    'default': config(
        'DATABASE_URL',
        default='postgres://postgres:postgres@127.0.0.1:5432/db_solar',
        cast=db_url
    ),
}

APPLICATION_ID = config('DATABASE_APPLICATION_ID', default='A', cast=str)
APPLICATION_NAME = config('DATABASE_APPLICATION_NAME', default='solar_web', cast=str)

for nome_banco in DATABASES:

    if 'OPTIONS' not in DATABASES[nome_banco]:
        DATABASES[nome_banco].update({'OPTIONS': {}})

    DATABASES[nome_banco]['OPTIONS'].update({'application_name': APPLICATION_NAME})
    DATABASES[nome_banco]['CONN_MAX_AGE'] = config('DATABASE_CONN_MAX_AGE', default=60, cast=int)

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

TIME_ZONE = config('TIME_ZONE', default='America/Araguaina')

LANGUAGE_CODE = 'pt-br'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = False

MEDIA_ROOT = os.path.join(ROOT_PATH, 'media')

MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(ROOT_PATH, 'staticfiles_producao')

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(ROOT_PATH, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

SECRET_KEY = config('SECRET_KEY', default='wTLgzIzjngl4OkDCkog4qsuGiMWep14Q')

MIDDLEWARE = (
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'authsolar.middlewares.EgideAuthenticationMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
    # 'htmlmin.middleware.HtmlMinifyMiddleware',  # Erro! Faz o GED não salvar o conteúdo
    'htmlmin.middleware.MarkRequestMiddleware',
    'contrib.middleware.ComarcaMiddleware',
    'django_currentuser.middleware.ThreadLocalUserMiddleware',
)

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(ROOT_PATH, "templates"),
        ],
        'OPTIONS': {
            'debug': DEBUG,
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'constance.context_processors.config',
                'core.context_processors.edefensor_config',
                'core.context_processors.chronus_config',
                'core.context_processors.google_analytics',
                'core.context_processors.signo_config',
            ],
        },
    },
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.postgres',
    'minio_storage',
    'reversion',
    'contrib',
    'authsolar',
    'core',
    'assistido',
    'atendimento.atendimento',
    # 'atendimento.agendamento',
    # 'atendimento.encaminhamento',
    # 'atendimento.informacao',
    # 'atendimento.qualificacao',
    # 'atendimento.precadastro',
    'atividade_extraordinaria',
    'aceite',
    'comarca',
    'constance',
    'constance.backends.database',
    'defensor',
    'djcelery',
    # 'estatistica',
    'evento',
    'indeferimento',
    'notificacoes',
    'nucleo.nadep',
    'nucleo.nucleo',
    'nucleo.itinerante',
    # 'perfil',
    'processo.processo',
    'processo.honorarios',
    'propac',
    'relatorios',
    'api.api_v1',
    'django_celery_beat',
    'taskapp',
    'widget_tweaks',
    'braces',
    'cuser',  # depreciada (mantida por causa dos migrations)
    'cacheops',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',
    'corsheaders',
    'django_filters',
    'compressor',
    'painel',
    # Clientes API
    'clients.livre_client',
    'luna_chatbot_client',
    'procapi_client',
    'thothsigner_client',
    'scrapy_tj',
    'calc_jur',
    'meritocracia',
)

INSTALLED_APPS = INSTALLED_APPS + (
    # documentos
    # dependencies
    'luzfcb_dj_simplelock.apps.DjSimpleLockAppConfig',
    'simple_history',
    'spurl',
    'crispy_forms',
    'captcha',
    'dal',
    'dal_select2',
    'bootstrap3',
    'django_tables2',
    'django_addanother',
    'bootstrap_pagination',
    'wkhtmltopdf',
    # end dependencies
    'django_js_reverse',
    'djdocuments',

)

# documentos
WKHTMLTOPDF_CMD = os.path.join(ROOT_PATH, 'binarios_executaveis', 'wkhtmltox_0.12.5_debug', 'bin', 'wkhtmltopdf')
CAPTCHA_FOREGROUND_COLOR = '#991100'

CAPTCHA_FONT_SIZE = 50
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
# CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.word_challenge'
CAPTCHA_WORDS_DICTIONARY = '/usr/share/dict/brazilian'

# django-js-reverse
# JS_REVERSE_INCLUDE_ONLY_NAMESPACES = ['documentos']
JS_REVERSE_OUTPUT_PATH = os.path.join(ROOT_PATH, 'static', 'django_js_reverse', 'js')
# django-js-reverse
DJDOCUMENT = {
    'BACKEND': 'djdocuments_solar_backend.backend.SolarDefensoriaBackend',
    'GRUPO_ASSINANTE_MODEL': 'contrib.Defensoria',
    'SIGLA_UF': config('SIGLA_UF', default=''),
}

# end documentos

# https://docs.djangoproject.com/en/1.8/ref/settings/#email-host
EMAIL_HOST = config("EMAIL_HOST", default='')
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default='')
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default='')
EMAIL_PORT = config("EMAIL_PORT", default=25)

# https://docs.djangoproject.com/en/1.8/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = "[SOLAR]"

EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=False, cast=config.boolean)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=config.boolean)
EMAIL_SSL_CERTFILE = config("EMAIL_SSL_CERTFILE", default=None)
EMAIL_SSL_KEYFILE = config("EMAIL_SSL_KEYFILE", default=None)
EMAIL_TIMEOUT = config("EMAIL_TIMEOUT", default=None, cast=int_or_none)

# https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-DEFAULT_FROM_EMAIL
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default='')

# TODO: Unificar com configurações padrão de e-mail do django
# DPE-AM
EMAIL_DISK = config('EMAIL_DISK', default='')
EMAIL_DISK_PASSWORD = config('EMAIL_DISK_PASSWORD', default='')
EMAIL_DISK_SMTP = config('EMAIL_DISK_SMTP', default='')
EMAIL_DISK_SMTP_PORT = config('EMAIL_DISK_SMTP_PORT', default='')
EMAIL_CORREGEDORIA = config('EMAIL_CORREGEDORIA', default='', cast=config.list)

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': not DEBUG,
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console'],
        },
        'tasks': {
            'level': 'INFO',
            'handlers': ['console'],
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'djdocuments': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

CACHE_MIDDLEWARE_SECONDS = 300

CACHE_MIDDLEWARE_KEY_PREFIX = 'solar_key'

MEMCACHED_DATABASE_URL = config('MEMCACHED_DATABASE_URL', default="memcached:11211")

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': MEMCACHED_DATABASE_URL,
        'TIMEOUT': 86400
    }
}

REDIS_DATABASE_URL = config('REDIS_DATABASE_URL', default="redis://redis:6379")
REDIS_PROTOCOL, REDIS_HOST, REDIS_PORT = REDIS_DATABASE_URL.replace('/', '').split(':')

CACHEOPS_ENABLED = config("CACHEOPS_ENABLED", default=True)
CACHEOPS_REDIS = "{}/4".format(REDIS_DATABASE_URL)
CACHEOPS_DEGRADE_ON_FAILURE = True

CACHEOPS_UM_MINUTO = 60  # 60 * 1
CACHEOPS_UMA_HORA = 3600  # 60 * 60
CACHEOPS_UM_DIA = 86400  # 60 * 60 * 24
CACHEOPS_UMA_SEMANA = 604800  # 60 * 60 * 24 * 7

CACHEOPS = {
    # 'all' is an alias for {'get', 'fetch', 'count', 'aggregate', 'exists'}
    'agenda.categoria': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'assistido.bem': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'assistido.estruturamoradia': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'assistido.patrimonialtipo': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'assistido.perfilcamposobrigatorios': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'assistido.profissao': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'assistido.situacao': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'assistido.tiporenda': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'atendimento.assunto': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'atendimento.encaminhamento': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'atendimento.especializado': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'atendimento.formaatendimento': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'atendimento.informacao': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'atendimento.modelodocumento': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'atendimento.motivoexclusao': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'atendimento.qualificacao': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'atendimento.tipocoletividade': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'atividade_extraordinaria.atividadeextraordinariatipo': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},  # noqa: 501
    'auth.user': {'ops': 'get', 'timeout': CACHEOPS_UM_DIA, 'cache_on_save': True},
    'comarca.guiche': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'comarca.predio': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'contrib.area': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'contrib.cargo': {'ops': 'get', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'contrib.cartorio': {'ops': 'get', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'contrib.comarca': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'contrib.defensoria': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'contrib.defensoriatipoevento': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'contrib.deficiencia': {'ops': 'get', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'contrib.documento': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'contrib.estado': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'contrib.identidadegenero': {'ops': 'get', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'contrib.municipio': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'contrib.orientacaosexual': {'ops': 'get', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'contrib.pais': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'contrib.papel': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'contrib.salario': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'contrib.servidor': {'ops': 'get', 'timeout': CACHEOPS_UM_DIA, 'cache_on_save': True},
    'contrib.vara': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'core.classe': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'core.modeleodocumento': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'core.tipodocumento': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'core.tipoevento': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'defensor.atuacao': {'ops': 'all', 'timeout': CACHEOPS_UM_DIA, 'cache_on_save': True},
    'defensor.defensor': {'ops': 'all', 'timeout': CACHEOPS_UM_DIA, 'cache_on_save': True},
    'nadep.estabelecimentpenal': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'nadep.tipificacao': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'nadep.tipoestabelecimentopenal': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'nucleo.formulario': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'nucleo.nucleo': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'nucleo.pergunta': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'procapi_client.amigavel': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'procapi_client.competencia': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'procapi_client.orgaojulgador': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'procapi_client.respostatecnica': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'procapi_client.sistemawebservice': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'procapi_client.tipoarquivo': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'procapi_client.tipoevento': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'processo.acao': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'processo.assunto': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'processo.documentotipo': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'processo.fasetipo': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'processo.outroparametro': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'processo.prioridade': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'propac.movimentotipo': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'propac.tipoanexodocumentopropac': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    'relatorios.relatorio': {'ops': 'all', 'timeout': CACHEOPS_UMA_SEMANA, 'cache_on_save': True},
    '*.*': {'ops': (), 'timeout': CACHEOPS_UM_DIA},
}

SESSION_COOKIE_NAME = 'sessionid_solar'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# DURAÇÃO DA SESSÃO (EM SEGUNDOS) (PADRÃO 24 HORAS)
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=86400, cast=int)
SESSION_SAVE_EVERY_REQUEST = config('SESSION_SAVE_EVERY_REQUEST', default=False, cast=config.boolean)

# https://docs.djangoproject.com/en/1.8/ref/settings/#session-serializer
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# Celery 5 Config
# https://docs.celeryproject.org/en/stable/userguide/configuration.html
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = TIME_ZONE
CELERY_RESULT_BACKEND = "{}/2".format(REDIS_DATABASE_URL)
# https://docs.celeryproject.org/en/stable/userguide/configuration.html#broker-settings
BROKER_URL = "{}/2".format(REDIS_DATABASE_URL)
BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 300,
}

CONSTANCE_BACKEND = config('CONSTANCE_BACKEND', default="constance.backends.redisd.RedisBackend")

CONSTANCE_REDIS_CONNECTION = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'db': 3,
}

CONSTANCE_ADDITIONAL_FIELDS = {
    'atuacao_display_select': [
        'django.forms.fields.ChoiceField',
        {
            'widget': 'django.forms.Select',
            'choices': (
                ('{atuacao.defensor.nome} - {atuacao.defensoria.nome}', 'Defensor - Defensoria'),
                ('{atuacao.defensoria.nome} - {atuacao.defensor.nome}', 'Defensoria - Defensor'),
                ('{atuacao.defensoria.nome}', 'Defensoria'),
                ('{atuacao.defensoria.atuacao} - {atuacao.defensoria.nome} - {atuacao.defensor.nome}', 'Atuação - Defensoria - Defensor'),  # noqa: 501
                ('{atuacao.defensor.nome} - {atuacao.defensoria.nome} - {atuacao.defensoria.atuacao}', 'Defensor - Defensoria - Atuação'),  # noqa: 501
            )
        }
    ],
    'atendimento_acesso_select': [
        'django.forms.fields.ChoiceField',
        {
            'widget': 'django.forms.Select',
            'choices': (
                (0, 'Não Exibir'),
                (1, 'Exibir - Apenas para Iniciais'),
                (2, 'Exibir - Para todos tipos')
            )
        }
    ],
    'assistido_telefone_tipo_select': [
        'django.forms.fields.ChoiceField',
        {
            'widget': 'django.forms.Select',
            'choices': (
                (0, 'Celular'),
                (1, 'Residencial'),
                (2, 'Comercial'),
                (3, 'Recado'),
                (4, 'WhatsApp'),
                (5, 'SMS'),
            )
        }
    ],
    '129_endereco_select': [
        'django.forms.fields.ChoiceField',
        {
            'widget': 'django.forms.Select',
            'choices': (
                (0, 'Apenas Município/UF'),
                (1, 'Completo'),
            )
        }
    ],
    'processo_evento_select': [
        'django.forms.fields.ChoiceField',
        {
            'widget': 'django.forms.Select',
            'choices': (
                ('table', 'Tabela'),
                ('timeline', 'Linha do tempo')
            )
        }
    ],
    'aviso_filter_distribuido_operador_logico_select': [
        'django.forms.fields.ChoiceField',
        {
            'widget': 'django.forms.Select',
            'choices': (
                ('AND', 'CPF e Defensoria (AND)'),
                ('OR', 'CPF ou Defensoria (OR)')
            )
        }
    ],
    'procapi_assunto_campo_select': [
        'django.forms.fields.ChoiceField',
        {
            'widget': 'django.forms.Select',
            'choices': (
                ('nome', 'Nome'),
                ('descricao', 'Descrição'),
            )
        }
    ],
}

CONSTANCE_CONFIG = OrderedDict([

    # Institucional
    ('NOME_INSTITUICAO', (config('NOME_INSTITUICAO', default='', cast=str), u'Nome da Defensoria', str)),  # noqa: 501
    ('CNPJ_INSTITUICAO', (config('CNPJ_INSTITUICAO', default='', cast=str), u'CNPJ da Defensoria (somente números)', str)),  # noqa: 501

    # Frontend
    ('LOGO_MENU', (str(), 'Url da logo da defensoria', str)),
    ('LOGO_POSITION_LEFT', (False, 'Se a logo estará do lado esquerdo', bool)),
    ('NOME_INSTITUICAO_NO_HEADER', (False, 'Se o nome da instituição aparece no topo', bool)),
    ('COR_HEADER_BG', (str('#464646'), 'Altera a cor do background do header sistema', str)),
    ('COR_HEADER_FONT', (str('#FFF'), 'Altera a cor das letras do header', str)),
    ('COR_MENU_BG', (str('#464646'), 'Altera a cor do background do menu do sistema', str)),
    ('COR_MENU_ICON', (str('#CDCDCD'), 'Altera a cor das letras do menu', str)),
    ('COR_HOJE_AGENDA', (str(), 'Altera a cor do background do dia de hoje na agenda', str)),

    # Assistido
    ('EXIBIR_ALERTA_HIPOSSUFICIENCIA', (True, 'Exibir alerta de hipossuficiência no cadastro do usuário e no atendimento?', bool)),  # noqa: 501
    ('EXIBIR_ALERTA_AVALIACAO_ASSISTIDO', (config('EXIBIR_ALERTA_AVALIACAO_ASSISTIDO', default=False, cast=config.boolean), 'Exibir alerta de avaliação do assistido?', bool)),  # noqa: 501

    ('MENSAGEM_ALERTA_AVALIACAO_ASSISTIDO', (config('MENSAGEM_ALERTA_AVALIACAO_ASSISTIDO', default='', cast=str), 'Mensagem de alerta na avaliação do assistido', str)),  # noqa: 501
    ('MENSAGEM_RENDA_ASSISTIDO_INDIVIDUAL', (str(), 'Mensagem no campo "Renda Individual" no Cadastro do Assistido', str)),  # noqa: 501
    ('MENSAGEM_RENDA_ASSISTIDO_FAMILIAR', (str(), 'Mensagem no campo "Renda Familiar" no Cadastro do Assistido', str)),  # noqa: 501
    ('MENSAGEM_VALOR_SALARIO_FUNCIONARIO', (str(), 'Mensagem no campo "Salário do Funcionário" no Cadastro do Assistido', str)),  # noqa: 501
    ('MENSAGEM_VALOR_INVESTIMENTOS', (str(), 'Mensagem no campo "Investimentos" no Cadastro do Assistido', str)),

    ('EXIBIR_NAO_POSSUI_NOS_CAMPOS_OPCIONAIS', (True, 'Exibir "Não possui" nos campos opicionais do cadastro do assistido?', bool)),  # noqa: 501
    ('ATIVAR_ZAP_DEFENSORIA', (False, 'Ativa/Desativa a opção Zap Defensoria', bool)),
    ('CALCULAR_RENDA_FAMILIAR_E_MEMBROS_ASSISTIDO', (False, 'Calcular a renda familiar e número de membros no cadastro do assistido automaticamente?', bool)),  # noqa: 501
    ('SITUACOES_SIGILOSAS', (str(), 'Códigos (sem caracteres especiais) das situações do assistido onde deverá ser aplicado o sigilo caso seja selecionada. Utilize vírgula para separar caso exista mais de uma.', str)),  # noqa: E501
    ('NOTIFICACAO_SOLICITACAO_SIGILO', (False, 'Enviar email notificando usuários do pedido de solicitação de acesso? (necessário configurar DEFAULT_FROM_EMAIL no .env)', bool)),  # noqa: E501

    ('ATIVAR_BOTAO_PRE_CADASTRO', (False, 'Caso ativado, ficará disponível o botão PRE CADASTRAR REQUERIDO/REQUERENTE, que possibilita a criação e vinculação de assistido com um numero de informações resumidas', bool)),  # noqa: E501
    ('EXIBIR_ALERTA_PRE_CADASTRO', (False, 'Exibi alerta no pré cadastro do assistido?', bool)),  # noqa: E501
    ('MENSAGEM_ALERTA_PRE_CADASTRO', (str(), 'Mensagem de alerta no pré cadastro do assitido', str)),  # noqa: E501
    ('ASSISTIDO_ENDERECO_VALIDAR_CEP', (True, 'Validar CEP nos Correios (Bloqueia preenchimento da UF, município, bairro e logradouro)', bool)),  # noqa: E501
    ('ASSISTIDO_TELEFONE_TIPO_PADRAO', (0, 'Tipo de Telefone Padrão no Cadastro do Assistido', 'assistido_telefone_tipo_select')),  # noqa: E501
    ('ORDENAR_MODELO_DOCUMENTO_POR_NOME', (True, 'Ordenar o documento por nome ou ordenar por data de forma crescente', bool)),  # noqa: E501
    # 129
    ('EXIBIR_ALERTA_AVALIACAO_ASSISTIDO_129', (config('EXIBIR_ALERTA_AVALIACAO_ASSISTIDO_129', default=False, cast=config.boolean), 'Exibir alerta de avaliação do assistido no 129', bool)),  # noqa: 501
    ('MENSAGEM_ALERTA_AVALIACAO_ASSISTIDO_129', (config('MENSAGEM_ALERTA_AVALIACAO_ASSISTIDO_129', default='', cast=str), 'Mensagem de alerta na avaliação do assistido no 129', str)),  # noqa: 501

    ('MODO_EXIBICAO_ENDERECO_129', (0, 'Modo de exibição do endereço no 129', '129_endereco_select')),  # noqa: E501

    ('LEMBRETE_129_EMAIL_ENCAMINHAMENTO', (str(""), 'Template de e-mail para procedimento 129 de encaminhamento', str)),  # noqa: E501
    ('LEMBRETE_129_EMAIL_DUVIDAS', (str(""), 'Template de e-mail para procedimento 129 de dúvidas', str)),  # noqa: E501
    ('LEMBRETE_129_EMAIL_RECLAMACAO', (str(""), 'Template de e-mail para procedimento 129 de reclamação', str)),  # noqa: E501
    ('LEMBRETE_129_EMAIL_INFORMACAO', (str(""), 'Template de e-mail para procedimento 129 de informação', str)),  # noqa: E501
    ('LEMBRETE_129_EMAIL_AGENDAMENTO', (str(""), 'Template de e-mail para procedimento 129 de agendamento', str)),  # noqa: E501
    ('LEMBRETE_EMAIL_AGENDAMENTO_ONLINE', (str(""), 'Template de e-mail agendamento on-line (DPE-AM)', str)),  # noqa: E501

    ('ENVIAR_COPIA_EMAIL_DISK', (False, 'Enviar cópia para o email do disk?', bool)),
    ('EMAIL_PARA_ENVIO_DE_COPIA_DISK', (str(""), "Email do disk para envio de cópia", str)),

    # Agenda/Agendamento
    ('HORA_INICIAL_AGENDA_DEFENSOR', (str('08:00'), 'Hora padrão para cadastro de agenda de defensor', str)),
    ('SIMULTANEOS_AGENDA_DEFENSOR', (1, 'Valor padrão do campo simultâneos para cadastro de agenda de defensor', int)),

    ('MODO_EXIBICAO_ATUACAO_AO_AGENDAR', (
        '{atuacao.defensor.nome} - {atuacao.defensoria.nome}',
        'Modo de exibição defensor/defensoria no agendamento',
        'atuacao_display_select'
    )),

    ('EXIBIR_OFICIO_AGENDAMENTO', (False, 'Ativa/Desativa informações de ofício no agendamento', bool)),
    ('EXIBIR_PRESENCIAL_REMOTO_AGENDAMENTO', (False, 'Ativa/Desativa identificação Presencial/Remoto nas agendas e agendamento', bool)),  # noqa: 501
    ('EXIBIR_DATA_ATUACAO', (True, 'Ativa/Desativa informações de datas do período de atuação', bool)),
    ('EXIBIR_ATUACAO_DEFENSORIA', (False, 'Ativa/Desativa informação da atuação do ofício/defensoria', bool)),
    ('CONVERTER_PRIMEIRO_ENCAMINHAMENTO_EM_INICIAL', (False, 'Ativa/Desativa conversão do primeiro encaminhamento em inicial (multidisciplinar > defensoria)', bool)),  # noqa: 501
    ('BLOQUEAR_AGENDAMENTO_ENTRE_DEFENSORIAS', (False, 'Bloqueia o agendamento entre as defensorias. Somente quem atua na defensoria ou que faça parte do GrupoDeDefensoriasParaAgendamento podem agendar.')),  # noqa: 501
    ('SOMENTE_DEFENSORIAS_MESMA_AREA', (False, 'Filtra pelas defensorias da mesma área (família, cível etc) da qualificação selecionada ao ser feito um agendamento', bool)),  # noqa: 501
    ('WHATSAPP_INCLUIR_NOME_DEFENSOR', (True, 'Incluir nome do defensor na mensagem Whatsapp?', bool)),

    # Atendimento
    ('NOME_MODULO_ATENDIMENTO', (str('Atendimento'), 'Nome alternativo para o módulo "Atendimento"', str)),
    ('NOME_ANOTACAO_DEFENSOR', (str('Anotações do Defensor'), 'Descrição alternativa para o campo "Anotações do Defensor"', str)),  # noqa: 501

    ('LIBERAR_ATENDIMENTO_PJ_SEM_PF', (True, 'Liberar atendimentos de requerente Pessoa Jurídica sem ter Pessoa Física vinculada', bool)),  # noqa: 501

    ('REGISTRAR_ANOTACAO_EM_AGENDAMENTO', (False, 'Registrar anotação em agendamento?', bool)),  # noqa: 501
    ('REGISTRAR_VISUALIZACAO_ATENDIMENTO_SUPERUSUARIO', (True, 'Registrar visualização de tarefa se superusuário?', bool)),  # noqa: 501

    ('BUSCAR_ATENDIMENTOS_FILTRO_NOME_MIN_CARACTERES', (5, 'Mínimo de caracteres para busca de atendimentos pelo nome da pessoa', int)),  # noqa: 501
    ('BUSCAR_ATENDIMENTOS_FILTRO_NOME_MAX_PESSOAS', (200, 'Máximo de pessoas para busca de atendimentos pelo nome da pessoa', int)),  # noqa: 501
    ('BUSCAR_ATENDIMENTO_EXIBIR_COL_RESPONSAVEL', (False, 'Se True, adiciona coluna responsável pelo atendimento na Busca de Atendimentos', bool)),  # noqa: 501

    ('MODO_EXIBICAO_ACESSO_ATENDIMENTO', (1, 'Modo de exibição mensagem acesso atendimento público/privado', 'atendimento_acesso_select')),  # noqa: E501

    ('MODO_EXIBICAO_LISTA_DE_ATENDIMENTOS_DO_ASSISTIDO', (
        str('True,True,False,True'),
        'Define quais informações aparecerão sobre o atendimento: (1) Anotação da recepção, (2) Anotação do agendamento, (3) Anotação do Defensor, (4) Mensagem de "Nenhum processo vinculado"',  # noqa: E501
        str
    )),
    ('ATIVA_EXIBICAO_ANOTACAO_DEFENSOR_HISTORICO_DE_ATENDIMENTO', (
        False,
        'Se True, as anotações do defensor serão exibidas no histórico de atendimentos acima do accordion de "Mostrar/Ocultar Detalhes"',  # noqa: E501
        bool)
     ),

    ('CONTABILIZAR_ACORDO_TIPO_AMBOS', (True, 'Contabilizar como atendimento o acordo em que ambas partes não compareceram?', bool)),  # noqa: E501
    ('NOME_FORMA_ATENDIMENTO_PADRAO', (str('Presencial'), 'Nome da Forma de Atendimento Padrão', str)),
    ('URL_CONDEGE_PETICIONAMENTO', (str(), 'Link para página de Peticionamento Integrado do CONDEGE', str)),

    ('ATIVAR_BOTAO_ATENDER_AGORA', (False, 'Se ativado, exibirá na página de atendimento o botão Atender Agora, que torna a criação de atendimento do tipo retorno mais simples, no qual esse botão cria e libera o agendamento/atendimento com 1 click', bool)),  # noqa: E501
    ('ATIVAR_BOTAO_REMETER_ATENDIMENTO', (False, 'Se ativado, exibirá na página de atendimento o botão Remeter atendimento, que possibilita o encaminhamento para outra defensoria sem marcar um agendamento', bool)),  # noqa: E501
    ('ATIVAR_SIGILO_ABAS_ATENDIMENTO', (str('False,False,False,False,False'), 'Define quais abas do atendimento sigiloso ficarão restritas: (1) Documentos, (2) Tarefas / Cooperações, (3) Processos, (4) Outros e (5) Propacs', str)),  # noqa: E501
    ('ATIVAR_ORDENACAO_ATENDIMENTO_DECRESCENTE', (False, 'Ativa/Desativa ordenação de atendimentos na aba histórico forma decrescente (mais novo primeiro)', bool)),  # noqa: 501

    ('VINCULAR_PROCESSO_COM_ATENDIMENTO_EM_ANDAMENTO', (False, 'Permite adicionar processos enquanto estiver em atendimento', bool)),  # noqa: 501
    ('EXIBIR_NOME_DA_DEFENSORIA_NA_BUSCA_ATENDIMENTOS', (False, 'Exibe o nome da defensoria em vez do código na busca de atendimentos', bool)),  # noqa: 501
    ('EXIBIR_VULNERABILIDADE_DIGITAL', (
        False, 'Exibirá na paǵina de atendimento opções sobre vulnerabilidade digital', bool)),
    ('MENSAGEM_VULNERABILIDADE_DIGITAL', (str(), 'Mensagem que ficará no tooltip da vulnerabilidade digital', str)),
    ('ATIVAR_INIBICAO_RETORNO', (False, 'Caso ativado, bloqueia os botões de retorno sempre que houver a tentative de abertura de um novo retorno para um atendimento que tenha como data de registro o dia corrente (para o mesmo defensor, mesma defensoria e mesma qualificação)', bool)),  # noqa: E501
    ('MENSAGEM_INIBICAO_RETORNO', (str(), 'Mensagem que ficará no tooltip da inibição do retorno', str)),

    # Tarefas/Cooperações/Alertas
    ('HERDAR_TAREFAS_DOS_SUPERVISIONADOS', (False, 'Exibir todas tarefas de servidores supervisionados?', bool)),
    ('DIA_LIMITE_EXIBICAO_TAREFAS_CUMPRIDAS', (0, 'Dias limite para exibir tarefas cumpridas (Ex: =0 não limita, >0 dia limite exibição', int)),  # noqa: 501
    ('EXIBIR_COOPERACOES_CUMPRIDAS_PARA_RESPONSAVEL', (True, 'Exibir cooperações cumpridas para o setor responsável?', bool)),  # noqa: 501
    ('REGISTRAR_VISUALIZACAO_TAREFA_SUPERUSUARIO', (True, 'Registrar visualização de tarefa se superusuário?', bool)),  # noqa: 501
    ('PRE_FILTRAR_TAREFAS_USUARIO_LOGADO', (False, 'Pré-filtrar tarefas na tela de listagem pelo usuário logado?', bool)),  # noqa: 501
    ('NOME_STATUS_TAREFA_0', (str('Devolver - resposta anterior incompleta'), 'Nome do status para tarefa com devolução', str)),  # noqa: 501
    ('NOME_STATUS_TAREFA_1', (str('Pendente - aguardando resposta de terceiros'), 'Nome do status para tarefa pendente', str)),  # noqa: 501
    ('NOME_STATUS_TAREFA_2', (str('Cumprida - aguardando resposta do defensor'), 'Nome do status para tarefa cumprida', str)),  # noqa: 501

    # Painel de Senhas
    ('PAINEL_SENHA_LOGO_URL', (str(), 'URL da logo do painel de senhas', str)),
    ('PAINEL_SENHA_CORREGEDORIA_ID', (0, 'ID da Corregedoria', int)),

    # Atuações
    ('ATIVAR_MULTIPLAS_ATUACOES', (False, 'Ativar registro de multiplas atuações na mesma defensoria simultaneamente', bool)),  # noqa: E501
    ('QUANTIDADE_ATUACOES_ACUMULACAO', (0, 'Limitar registro de multiplas atuações de acumulação na mesma defensoria simultaneamente \n( Por padrão é Zero, não limita múltiplas acumulações. )', int)),  # noqa: E501


    # Livre
    ('ATIVAR_LIVRE_API', (False, 'Ativa/Desativa API do Livre (SEEU)', bool)),
    ('SHOW_PAINEL_LIVRE', (True, 'Mostrar novo painel do LIVRE', bool)),
    ('ID_PERGUNTA_FORMULARIO_INSPECAO_LIVRE', (0, 'ID da Pergunta o Formulário de Inspeção que contém o nome do Estabelecimento Penal', int)),  # noqa: E501

    # GED
    ('SHOW_DJDOCUMENTS', (True, 'Ativa/Desativa djdocuments (somente remove as URL nos templates)', bool)),
    ('SUPER_USER_CAN_EDIT_DOCUMENT', (False, 'Ativa/Desativa A possibilidade de um superusuario editar um documento em djdocuments', bool)),  # noqa: 501
    ('SUPER_USER_CAN_EXCLUDE_DOCUMENT', (False, 'Ativa/Desativa A possibilidade de um superusuario excluir um documento em djdocuments', bool)),  # noqa: 501
    ('GED_PODE_INCLUIR_IMAGENS_EXTERNAS', (True, 'Permite incluir imagens externas. Se habilitado, as imagens externas serão baixadas ao liberar documento para assinatura.', bool)),  # noqa: 501
    ('GED_PODE_BAIXAR_DOCUMENTO_NAO_ASSINADO', (False, 'Permite baixar documentos do GED sem a necessidade da assinatura', bool)),  # noqa: 501
    ('BLOQUEAR_TELA_AO_CRIAR_EDITAR_GED', (True, 'Bloqueia a tela de atendimento-documentos ao criar ou editar um GED (caso false, GED será aberto em nova aba)', bool)),  # noqa: 501
    ('ATIVAR_PETICAO_SIMPLIFICADA', (False, 'Ativa a função de criação simples da petição(GED). A funcionalidade estará disponível na tab de documentos do Processo', bool)),  # noqa: 501
    ('GED_EXIBIR_FORMULAS_MODELO', (True, 'Exibir fórmulas GED ao editar modelo de documento', bool)),

    # Processos
    ('NOME_PROCESSO_TJ', (str(), 'Nome do sistema de processos judiciais', str)),
    ('URL_PROCESSO_TJ', (str(), 'Link para consulta pública processual', str)),
    ('MODO_EXIBICAO_EVENTOS_PROCESSO_TJ', ('table', 'Modo de exibição dos eventos de processos na aba TJ', 'processo_evento_select')),  # noqa: 501
    ('SHOW_SIDEBAR_PROCESSOS_PENDENTES', (False, 'Mostrar caixa de processos pendentes?', bool)),
    ('DIA_LIMITE_CADASTRO_FASE', (5, 'Dia limite para cadastro de fase do mês anterior (Ex: =0 não corrige, >0 dia limite alteração)', int)),  # noqa: 501
    ('EXIBIR_DATA_HORA_TERMINO_CADASTRO_AUDIENCIA', (True, 'Exibir campo data/hora término no cadastro de audiências', bool)),  # noqa: 501
    ('VERIFICA_ATUALIZACAO_HONORARIOS', (False, 'Gerar alertas de honorarios para cada movimentacao do eproc', bool)),
    ('PROCESSO_CALCULADORA_CALCULO_URL', (str(), 'URL da Calculadora Judicial (Cálculo)', str)),
    ('PROCESSO_CALCULADORA_CONSULTA_URL', (str(), 'URL da Calculadora Judicial (Consulta)', str)),
    ('BUSCAR_PROCESSO_DIGITAL_AUTOMATICAMENTE', (True, 'Habilita na tela de cadastro de processo a busca automática no PROCAPI caso seja digitado os 20 digitos de um processo', bool)),  # noqa: E501
    ('PERMITE_CADASTRAR_PROCESSO_NAO_LOCALIZADO_OU_COM_ERRO_WEBSERVICE_DO_TJ', (False, 'Habilita a possibilidade de deixar usuário cadastrar processo caso a defensoria não esteja habilitado em processo sigiloso ou o webservice do tribunal de justiça apresente erro de conexão no PROCAPI', bool)),  # noqa: E501
    ('PERMITE_CADASTRAR_PROCESSO_NAO_LOCALIZADO_COMO_FISICO', (False, 'Habilita a possibilidade de deixar usuário cadastrar processo não localizado como físico', bool)),  # noqa: E501
    ('VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSORIA_AUTOMATICAMENTE', (False, 'Habilita na tela de distribuição de processos a sugestão de defensoria responsável ao aviso automaticamente', bool)),  # noqa: E501
    ('VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSOR_AUTOMATICAMENTE', (True, 'Habilita na tela de distribuição de processos a  a sugestão de defensor responsável ao aviso automaticamente', bool)),  # noqa: E501
    ('VINCULAR_NA_DISTRIBUICAO_AVISO_A_PROCESSO_CADASTRADO', (True, 'Habilita na tela de distribuição de processos a sugestão a partir de processo previamente cadastrado', bool)),  # noqa: E501
    ('AVISOS_FILTER_DISTRIBUIDO_OPERADOR_LOGICO', ('AND', 'AND para filtrar por cpf e defensoria (Padrão); OR para filtrar por cpf ou defensoria.', 'aviso_filter_distribuido_operador_logico_select')),  # noqa: E501

    ('SUGERIR_DEFENSORIA_E_DEFENSOR_NA_DISTRIBUICAO', (True, 'Habilita na tela de distribuição a sugestão de defensoria ou defensor de acordo com a distribuição usada.(por defensoria e/ou defensor)', bool)),  # noqa: E501
    ('HABILITAR_LISTAGEM_GERAL_DE_AVISOS', (True, 'Habilita na tela de distribuição a listagem de todos os avisos, pendentes e abertos, quando todos os filtros de busca não forem selecionados.', bool)),  # noqa: E501
    ('LISTA_TIPOS_DOCUMENTOS_EMENDA_INICIAL', (str(), 'Tipos de documentos correspondentes a emenda à inicial', str)),  # noqa: E501
    ('MAXIMO_DE_RETRY_CELERY', (3, 'Define numero máximo de tentativas de execução de um task do celery', int)),  # noqa: E501
    ('ATIVAR_ACOMPANHAMENTO_PROCESSO', (False, 'Ativar acompanhamento processual (status parte do processo)', bool)),
    ('DIAS_ACOMPANHAMENTO_PROCESSO', (0, 'Período para acompanhar a situação do processo a partir de sua última atualização. Não será listado caso seja 0.', int)),  # noqa: E501
    ('PROCAPI_PERMITE_CADASTRAR_PROCESSO_SIGILOSO', (False, 'Se Habilitado, SOLAR irá cadastrar processos não localizados no PROCAPI, presumindo que eles existem e estão sigilosos no TJ', bool)),  # noqa: E501
    # Honorários
    ('HONORARIO_VINCULAR_AO_TITULAR_DO_SETOR', (False, 'True: vincula honorário ao titular do setor de honorários; False: vincula ao defensor que cadastrou a sentença', bool)),  # noqa: E501

    # Eventos
    ('AREA_NO_CADASTRO_ATIVIDADE_EXTRAORDINARIA', (False, 'Insere/Remove o campo Área do cadastro de atividades extraordinárias', bool)),  # noqa: 501

    # Procedimentos
    ('AREA_NO_CADASTRO_PROCEDIMENTOS', (False, 'Insere/Remove o campo Área do cadastro de procedimentos/propacs', bool)),  # noqa: 501

    # Aceite
    ('ATIVA_FUNCIONALIDADE_ACEITE', (False, 'Ativa a funcionalidade de aceite de termos.', bool)),

    # Serviços
    ('ATIVAR_PROCAPI', (False, 'Ativa/Desativa consulta na API de processos', bool)),
    ('PROCAPI_ASSUNTO_CAMPO_EXIBICAO', ('nome', 'Campo usado para exibição dos assuntos no peticionamento inicial', 'procapi_assunto_campo_select')),  # noqa: E501

    ('ATIVAR_ESAJ', (False, 'Ativa/Desativa modificações para utilização do eSAJ', bool)),
    ('PROCAPI_ATIVAR_INFORMAR_PERFIL_PROJUDI', (False, 'Habilita opção informar nome de usuário do Projudi na edição de perfil de usuário', bool)),  # noqa: E501

    ('USAR_API_EGIDE_AUTH', (False, 'Ativa/Desativa a consulta a API do ÉGIDE para autenticar usuário', bool)),
    ('EGIDE_MENSAGEM_USUARIO_NAO_CADASTRADO', (str('<p>Contate o administrador do sistema</p>'), 'Mensagem exibida quando um usuário do ÉGIDE não está cadastrado no SOLAR', str)),  # noqa: E501
    ('EGIDE_URL_ALTERAR_SENHA', (str(''), 'Link para redirecionamento quando usuário tentar alterar a senha pelo SOLAR', str)),  # noqa: E501

    ('USAR_API_ATHENAS', (False, 'Ativa/Desativa a consulta a API do ATHENAS no momento de cadastro de novos usuario', bool)),  # noqa: 501
    ('USAR_API_LDAP', (False, 'Ativa/Desativa a consulta a API ao LDAP (Active Directory) no momento de cadastro de novos usuario', bool)),  # noqa: 501
    ('SHOW_INSCRICAO_PLANTAO', (False, 'Ativa/Desativa acesso ao módulo de inscrição a edital de concorrência de plantões', bool)),  # noqa: 501

    # Serviços: Metabase
    ('METABASE_SITE_URL', (str(""), 'URL do Metabase', str)),
    ('METABASE_SECRET_KEY', (str(""), 'Chave Secreta do Metabase', str)),
    ('METABASE_EXPIRATION_IN_MINUTES', (10, 'Tempo de expiração dos links gerados pelo Metabase (em minutos)', int)),
    ('METABASE_DISPLAY_IN_IFRAME', (False, 'Ativa/Desativa exibição embutida no SOLAR. Se desativado exibe em uma nova aba', bool)),  # noqa: 501

    # Serviços: SIGNO (Notificações)
    ('USAR_NOTIFICACOES_SIGNO', (False, 'Ativa/Desativa utilização do SIGNO para notificações no sistema', bool)),

    ('NOTIFICAR_ALTERACAO_CADASTRO_ASSISTIDO', (False, 'Ativa/Desativa notificação do sistema ao alterar cadastro do assistido', bool)),  # noqa: 501
    ('NOTIFICAR_LIBERACAO_ATENDIMENTO_RECEPCAO', (False, 'Ativa/Desativa notificação do sistema ao liberar atendimento pela recepção', bool)),  # noqa: 501
    ('NOTIFICAR_DOCUMENTO_PRONTO_PARA_ASSINAR', (False, 'Ativa/Desativa notificação do sistema quando documento for marcado como pronto para assinar', bool)),  # noqa: 501
    ('NOTIFICAR_DOCUMENTO_FINALIZADO', (False, 'Ativa/Desativa notificação do sistema quando documento for marcado como finalizado', bool)),  # noqa: 501
    ('NOTIFICAR_DOCUMENTO_ASSINATURA_PENDENTE', (False, 'Ativa/Desativa notificação do sistema ao adicionar nova pendência de assinatura', bool)),  # noqa: 501
    ('NOTIFICAR_MANIFESTACAO_EM_ANALISE', (False, 'Ativa/Desativa notificação do sistema ao ser criado uma petição para analise pelo módulo peticionamento', bool)),  # noqa: 501
    ('NOTIFICAR_MANIFESTACAO_PROTOCOLADA', (False, 'Ativa/Desativa notificação do sistema ao ser protocolado uma petição pelo módulo peticionamento', bool)),  # noqa: 501
    ('NOTIFICAR_PROCESSO_DE_INDEFERIMENTO', (False, 'Ativa/Desativa notificação do sistema ao ser tramitado um processo de indeferimento/impedimento/suspeição', bool)),  # noqa: 501

    # Serviços: LUNA (Notificações Chatbot)
    ('USAR_NOTIFICACOES_ASSISTIDO_VIA_CHATBOT', (False, 'Ativa/Desativa utilização de notificações via Luna Chatbot', bool)),  # noqa: 501

    ('LUNA_MENSAGEM_AGENDAMENTO_INICIAL', (str(""), 'Mensagem a ser enviada ao assistido via Luna ao realizar agendamento inicial', str)),  # noqa: E501
    ('LUNA_MENSAGEM_AGENDAMENTO_RETORNO', (str(""), 'Mensagem a ser enviada ao assistido via Luna ao realizar agendamento de retorno', str)),  # noqa: E501
    ('LUNA_MENSAGEM_AGENDAMENTO_REMARCACAO', (str(""), 'Mensagem a ser enviada ao assistido via Luna ao remarcar agendamento', str)),  # noqa: E501
    ('LUNA_MENSAGEM_AGENDAMENTO_EXCLUSAO', (str(""), 'Mensagem a ser enviada ao assistido via Luna ao excluir agendamento', str)),  # noqa: E501
    ('LUNA_MENSAGEM_ANOTACAO', (str(""), 'Mensagem a ser enviada ao assistido via Luna ao fazer uma anotação', str)),  # noqa: E501
    ('LUNA_MENSAGEM_DOCUMENTO_PENDENTE', (str(""), 'Mensagem a ser enviada ao assistido via Luna ao registrar um documento pendente', str)),  # noqa: E501
    ('LUNA_MENSAGEM_ENCAMINHAMENTO_EXTERNO', (str(""), 'Mensagem a ser enviada ao assistido via Luna ao encaminhar p/ órgão externo', str)),  # noqa: E501

    # Serviços: E-mails:
    ('EMAIL_PROCESSO_MANIFESTACAO_PROTOCOLO', (str(""), 'Mensagem a ser enviada ao assistido via e-mail ao protocolar manifestação', str)),  # noqa: E501

    # Serviços: Whatsapp
    ('WHATSAPP_PROCESSO_MANIFESTACAO_PROTOCOLO', (str(""), 'Mensagem a ser enviada ao assistido via whatsapp ao protocolar manifestação', str)),  # noqa: E501

    # Serviços: Movile SMS (Notificações SMS)
    ('ATENDIMENTO_HORARIO_UNICO_POR_TURNO', (False, 'Exibe um unico horário nas informações dos atendimentos para os assistidos, independente do horário que tenha sido selecionado no agendamento.', bool)),  # noqa: E501
    ('HORARIO_FIXO_MANHA', (str(' as 8:00h da manha'), 'Texto a substituir as palavras-chave de horário (como SMS_HORA) no caso da manhã quando ATENDIMENTO_HORARIO_UNICO_POR_TURNO=True.', str)),  # noqa: E501
    ('HORARIO_FIXO_TARDE', (str(' as 13:00h da tarde'), 'Texto a substituir as palavras-chave de horário (como SMS_HORA) no caso da tarde quando ATENDIMENTO_HORARIO_UNICO_POR_TURNO=True.', str)),  # noqa: E501

    # Serviços: Facilita SMS (Notificações SMS)
    ('FACILITA_SMS_AUTH', (False, 'Ativar o envio de sms por meio da plataforma facilita móvel', bool)),  # noqa: E501
    ('FACILITA_SMS_API_URL', (str(), 'URL', str)),
    ('FACILITA_SMS_AUTH_USER', (str(), 'USER', str)),
    ('FACILITA_SMS_AUTH_TOKEN', (str(), 'TOKEN', str)),

    ('ATENDIMENTO_EXTRA_PAUTA_HORARIO_UNICO', (False, 'Exibe um unico horário nas informações do SMS para os assistidos, no caso de agendamento marcado como extra-pauta', bool)),  # noqa: E501
    ('HORARIO_FIXO_EXTRA_PAUTA', (str('7h às 11h'), 'Texto a substituir as palavras-chave de horário (como SMS_HORA) no caso de ATENDIMENTO_EXTRA_PAUTA_HORARIO_UNICO=True.', str)),  # noqa: E501

    ('USAR_SMS', (False, 'Usar o envio de SMS', bool)),
    ('SERVICO_SMS_DISPONIVEL', (False, 'Habilitar o serviço de envio de SMS', bool)),

    ('MENSAGEM_SMS_AGENDAMENTO_INICIAL', (str("[SMS_DEF_SIGLA]\nO seu atendimento de numero SMS_NUMERO_ATENDIMENTO com o(a) Defensor(a) SMS_DEFENSOR foi marcado para o dia SMS_DIA as SMS_HORA."), 'Mensagem de SMS a ser enviada ao assistido ao realizar agendamento inicial', str)),  # noqa: E501
    ('MENSAGEM_SMS_AGENDAMENTO_RETORNO', (str("[SMS_DEF_SIGLA]\nO retorno do seu atendimento de numero SMS_NUMERO_ATENDIMENTO com o(a) Defensor(a) SMS_DEFENSOR foi marcado para o dia SMS_DIA as SMS_HORA."), 'Mensagem de SMS a ser enviada ao assistido ao realizar agendamento de retorno', str)),  # noqa: E501
    ('MENSAGEM_SMS_AGENDAMENTO_REMARCACAO', (str("[SMS_DEF_SIGLA]\nO seu atendimento de numero SMS_NUMERO_ATENDIMENTO com o(a) Defensor(a) SMS_DEFENSOR foi remarcado para o dia SMS_DIA as SMS_HORA."), 'Mensagem de SMS a ser enviada ao assistido ao realizar remarcação de agendamento', str)),  # noqa: E501
    ('MENSAGEM_SMS_AGENDAMENTO_EXCLUSAO', (str("[SMS_DEF_SIGLA]\nO seu atendimento de numero SMS_NUMERO_ATENDIMENTO foi negado."), 'Mensagem de SMS a ser enviada ao assistido ao excluir agendamento', str)),  # noqa: E501
    ('MENSAGEM_SMS_ANOTACAO', (str("[SMS_DEF_SIGLA]\nSMS_CONTEUDO_ANOTACAO"), 'Mensagem de SMS a ser enviada ao assistido ao fazer uma anotação de qualificação SMS', str)),  # noqa: E501

    ('SMS_REMOVER_ACENTOS', (True, 'Remover os acentos dos textos ao digitar SMS enquanto a qualificação for SMS', bool)),  # noqa: E501

    # Serviço: Notificação E-mail SMTP
    ('USAR_EMAIL', (False, 'Usar o envio de e-mail', bool)),
    ('ASSUNTO_EMAIL_NOTIFICACAO', (str(""), 'Assunto do e-mail de notificação', str)),  # noqa: E501
    ('MENSAGEM_EMAIL_AGENDAMENTO_INICIAL', (str(""), 'Mensagem de e-mail a ser enviada ao assistido ao realizar agendamento inicial', str)),  # noqa: E501
    ('MENSAGEM_EMAIL_AGENDAMENTO_RETORNO', (str(""), 'Mensagem de e-mail a ser enviada ao assistido ao realizar agendamento de retorno', str)),  # noqa: E501
    ('MENSAGEM_EMAIL_AGENDAMENTO_REMARCACAO', (str(""), 'Mensagem de e-mail a ser enviada ao assistido ao realizar remarcação de agendamento', str)),  # noqa: E501
    ('MENSAGEM_EMAIL_AGENDAMENTO_EXCLUSAO', (str(""), 'Mensagem de e-mail a ser enviada ao assistido ao excluir agendamento', str)),  # noqa: E501

    # Sistema
    ('PORTA_DO_ASSINADOR', (49153, 'Numero da Porta da Aplicação Desktop do Assinador que esteja escutando requisições', int)),  # noqa: E501
    ('URL_DO_ASSINADOR', (str('http://localhost'), 'URL da Aplicação Desktop do Assinador que esteja escutando requisições', str)),  # noqa: E501
    ('URL_THOTH_SIGNER', (str('http://localhost:9001/'), 'URL do assinador Thoth Signer, ex: http://ipouhostname:9001/', str)),  # noqa: E501
    ('ID_FASE_PROCESSUAL_PADRAO_NA_ABERTURA_DE_PRAZOS', (str(''), 'Se preenchido, ao ser aberto o prazo de um aviso pelo SOLAR será criado uma fase processual no processo com ID especificado (auditoria) ', str)),  # noqa: E501
    ('FORMATO_SUPORTADO_UPLOADS', (str('.pdf,.doc,.docx,.mp3,.ogg,.wav,.mp4,.mov,.avi,.jpeg,.jpg,.jfif,.png,.gif'), '[DEPRECIADO] Define o formato de arquivos aceito no upload dos formulários, utilizar o padrão: .pdf,.mp3,.mp4,.ogg,.doc,.docx etc...', str)),  # noqa: E501
    ('JSVERSION', (0, 'Versão dos arquivos .js (Formato: AAAAMMDDHHmm)', int)),
    ('ATIVAR_ETIQUETA_SIMPLIFICADA', (False, 'Ativa a função de criação simplificada de etiquetas', bool)),  # noqa: 501

    # Usuários
    ('ENVIAR_EMAIL_AO_CADASTRAR_SERVIDOR', (False, 'Enviar email com token para criação de senha ao cadastrar usuário', bool)),  # noqa: 501

    # Calculadora
    ('ATIVAR_CALCULADORA', (False, 'Ativar calculadora jurídica na defensoria', bool)),  # noqa: 501
    ('URL_CARTILHA_EXEC_PENAL', (str(''), 'URL para cartilha de execução penal utilizado na calculadora', str)),
])

# LDAP CONFIGURATIONS
PYTHON_LDAP_CONFIG = {
    'LDAP_AUTH_BIND_DN': config('LDAP_AUTH_BIND_DN', default='', cast=str),
    'LDAP_AUTH_BIND_PASSWORD': config('LDAP_AUTH_BIND_PASSWORD', default='', cast=str),
    'LDAP_AUTH_BIND_SUFFIX': config('LDAP_AUTH_BIND_SUFFIX', default='', cast=str),
    'LDAP_AUTH_SERVER_URI': config('LDAP_AUTH_SERVER_URI', default='', cast=str),
    'LDAP_AUTH_GLOBAL_OPTIONS': {
        ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER,
        ldap.OPT_REFERRALS: 0
    }

}
# END LDAP

# EGIDE
AUTHENTICATION_BACKENDS = (
    'authsolar.backends.EgideAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_EXEMPT_URLS = [
    r'^api/',
    r'^favicon.ico',
    # logincallback
    r'^login/callback/$',

    # django-simple-captcha
    r'^captcha/',

    # documentos:validar
    r'^docs/d/validar/$',

    # documentos:validar-detail
    r'^docs/d/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/validar-detail/$',

    # documentos:validar_detail_pdf
    r'^docs/d/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/validar-detail/pdf$',
]

EGIDE_CLIENT_ID = config('EGIDE_CLIENT_ID', default='', cast=str)
EGIDE_CLIENT_SECRET = config('EGIDE_CLIENT_SECRET', default='', cast=str)

EGIDE_URL = config('EGIDE_URL', default='', cast=str)
EGIDE_API = '{}/api/v1/me'.format(EGIDE_URL)
EGIDE_REDIRECT_URI = config('EGIDE_REDIRECT_URI', default='http://localhost:8000/login/callback/')
EGIDE_LOGOUT_URL = '{}/logout'.format(EGIDE_URL)
EGIDE_AUTHORIZE_URL = config(
    'EGIDE_AUTHORIZE_URL',
    default='{}/oauth/authorize/?client_id={}&response_type=code&redirect_uri={}'.format(
        EGIDE_URL,
        EGIDE_CLIENT_ID,
        EGIDE_REDIRECT_URI))
EGIDE_TOKEN_URL = config(
    'EGIDE_TOKEN_URL',
    default='{}/oauth/token'.format(EGIDE_URL)
)


# END EGIDE

# SIGNO
SIGNO_REST_API_URL = config('SIGNO_REST_API_URL', default='', cast=str)
SIGNO_WEBSOCKET_URL = config('SIGNO_WEBSOCKET_URL', default='', cast=str)
# END SIGNO

# CHATBOT
CHATBOT_LUNA_USERNAME = config('CHATBOT_LUNA_USERNAME', default='', cast=str)
CHATBOT_USERNAME = config('CHATBOT_USERNAME', default='lunachatbot', cast=str)

# no maximo 30 caracteres
CHATBOT_FULL_NAME = config('CHATBOT_FULL_NAME', default='Luna Chatbot DPE', cast=str)

CHATBOT_LUNA_API_TOKEN = config('CHATBOT_LUNA_API_TOKEN', default='', cast=str)
CHATBOT_LUNA_WEBHOOK_URL = config('CHATBOT_LUNA_WEBHOOK_URL', default='', cast=config.list)
CHATBOT_LUNA_VERIFY_CERTFILE = config('CHATBOT_LUNA_VERIFY_CERTFILE', default=True, cast=config.boolean)

# END CHATBOT

# MOVILE SMS

MOVILE_API_URL = config('MOVILE_API_URL', default='', cast=str)
MOVILE_AUTH_TOKEN = config('MOVILE_AUTH_TOKEN', default='', cast=str)
MOVILE_AUTH_USER = config('MOVILE_AUTH_USER', default='', cast=str)

# END MOVILE SMS

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'api.api_v1.permissions.IsAdminUserOrIsServidorUsoInterno',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_xml.renderers.XMLRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework_xml.parsers.XMLParser',
    ),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
}

SWAGGER_SETTINGS = {
   'SECURITY_DEFINITIONS': {
      'Basic': {
            'type': 'basic'
      },
      'TokenAuth': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Token-based authentication with required prefix "Token"'
      }
   }
}

SIMPLE_JWT = {
    'SIGNING_KEY': config('SIMPLE_JWT_SIGNING_KEY', default=SECRET_KEY),
    'USER_ID_FIELD': 'username',
    'USER_ID_CLAIM': 'username',
    'TOKEN_TYPE_CLAIM': None,
    'JTI_CLAIM': None,
    "TOKEN_OBTAIN_SERIALIZER": "authsolar.serializers.CustomTokenObtainPairSerializer",
}

# END API REST

# DADOS PROCEDIMENTOS
PROCEDIMENTO_NUMERO_MAXIMO_POR_VOLUME = 20
PROCEDIMENTO_SIGLA_PROCEDIMENTO = 'PA'
PROCEDIMENTO_SIGLA_PROPAC = 'PP'

GOOGLE_ANALYTICS_ID = config('GOOGLE_ANALYTICS_ID', default='')
GOOGLE_ANALYTICS_4_ID = config('GOOGLE_ANALYTICS_4_ID', default='')

# APIs
ATHENAS_API_URL = config('ATHENAS_API_URL', default='')
PLANTAO_API_URL = config('PLANTAO_API_URL', default='')

PROCAPI_URL = config('PROCAPI_URL', default='')
PROCAPI_TOKEN = config('PROCAPI_TOKEN', default='')
PROCAPI_VERSAO_MIN = '23.04.3'

LIVRE_API_URL = config('LIVRE_API_URL', default='')
LIVRE_API_TOKEN = config('LIVRE_API_TOKEN', default='')

CHRONUS_URL = config('CHRONUS_URL', default='')
CHRONUS_PODE_GERAR_XLSX_SEM_PAGINACAO = config(
    'CHRONUS_PODE_GERAR_XLSX_SEM_PAGINACAO',
    default=False,
    cast=config.boolean)

SIGLA_UF = config('SIGLA_UF', default='')
SIGLA_INSTITUICAO = config('SIGLA_INSTITUICAO', default='', cast=str)

# E-DEFENSOR
USAR_EDEFENSOR = config('USAR_EDEFENSOR', default=False, cast=config.boolean)
EDEFENSOR_CATEGORIA_AGENDA_ID = config('EDEFENSOR_CATEGORIA_AGENDA_ID', default=None, cast=int_or_none)
EDEFENSOR_CHAT_WEBSERVICE_TOKEN_URL = config(
    'EDEFENSOR_CHAT_WEBSERVICE_TOKEN_URL',
    default='',
    cast=str)
EDEFENSOR_CHAT_WEBSERVICE_TOKEN_USERNAME = config(
    'EDEFENSOR_CHAT_WEBSERVICE_TOKEN_USERNAME',
    default='',
    cast=str)
EDEFENSOR_CHAT_WEBSERVICE_TOKEN_PASSWORD = config(
    'EDEFENSOR_CHAT_WEBSERVICE_TOKEN_PASSWORD',
    default='',
    cast=str)
EDEFENSOR_CHAT_WEBSERVICE_APP_SYSTEM = config(
    'EDEFENSOR_CHAT_WEBSERVICE_APP_SYSTEM',
    default='',
    cast=str)
EDEFENSOR_USERNAME = config('EDEFENSOR_USERNAME', default='edefensor', cast=str)
# no maximo 30 caracteres
EDEFENSOR_FULL_NAME = config('EDEFENSOR_FULL_NAME', default='eDefensor APP', cast=str)
EDEFENSOR_ADONIS_HOSTNAME = config('EDEFENSOR_ADONIS_HOSTNAME', default='', cast=str)
EDEFENSOR_ADONIS_PORT = config('EDEFENSOR_ADONIS_PORT', default='', cast=str)

VERIFY_CERTFILE = config('VERIFY_CERTFILE', default='', cast=str)
CORS_ORIGIN_ALLOW_ALL = config('CORS_ORIGIN_ALLOW_ALL', default=False, cast=config.boolean)

# HABILITA COMPRESSÃO CSS E JS PELO DJANGO-COMPRESS
COMPRESS_ENABLED = not DEBUG
COMPRESS_OFFLINE = not DEBUG
COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter', 'compressor.filters.cssmin.CSSMinFilter']

# HABILITA HTML MINIFY
HTML_MINIFY = not DEBUG

# Adicionado temporariamente
SILENCED_SYSTEM_CHECKS = ['models.E006']

# BigAutoField para django 3.2
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Tamanho máximo de uploads no GED (Padrão do Django 2.5 MB)
# https://docs.djangoproject.com/en/3.2/ref/settings/#data-upload-max-memory-size
DATA_UPLOAD_MAX_MEMORY_SIZE = config('DATA_UPLOAD_MAX_MEMORY_SIZE', default=2621440, cast=int)


# Minio Storage
# https://django-minio-storage.readthedocs.io/en/latest/usage/#installation
MINIO_STORAGE_ENDPOINT = config("MINIO_STORAGE_ENDPOINT", default=None)
MINIO_STORAGE_ACCESS_KEY = config("MINIO_STORAGE_ACCESS_KEY", default=None)
MINIO_STORAGE_SECRET_KEY = config("MINIO_STORAGE_SECRET_KEY", default=None)
MINIO_STORAGE_USE_HTTPS = False
MINIO_STORAGE_MEDIA_BUCKET_NAME = config("MINIO_STORAGE_MEDIA_BUCKET_NAME", default=None)
MINIO_STORAGE_STATIC_BUCKET_NAME = config("MINIO_STORAGE_STATIC_BUCKET_NAME", default=None)
MINIO_STORAGE_MEDIA_USE_PRESIGNED = True
if MINIO_STORAGE_MEDIA_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"
if MINIO_STORAGE_STATIC_BUCKET_NAME:
    STATICFILES_STORAGE = "minio_storage.storage.MinioStaticStorage"
