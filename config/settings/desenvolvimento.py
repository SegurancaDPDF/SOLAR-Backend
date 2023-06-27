# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Modulos locais
from .comum import *  # noqa: F403

ALLOWED_HOSTS = set(ALLOWED_HOSTS + ['127.0.0.1', 'localhost'])  # noqa: F405

INSTALLED_APPS = INSTALLED_APPS + (  # noqa: F405
    'django_extensions',
)

try:
    import debug_toolbar  # noqa
except ImportError:
    debug_toolbar = None
else:
    if DEBUG_TOOLBAR:  # noqa: F405
        INSTALLED_APPS = INSTALLED_APPS + (
            'debug_toolbar',
        )
        MIDDLEWARE = MIDDLEWARE + ('debug_toolbar.middleware.DebugToolbarMiddleware', )  # noqa: F405
        INTERNAL_IPS = ['127.0.0.1', '10.0.2.2', ]
        DEBUG_TOOLBAR_CONFIG = {
            'DISABLE_PANELS': [
                'debug_toolbar.panels.redirects.RedirectsPanel',
                'debug_toolbar.panels.versions.VersionsPanel',
            ],
            'SHOW_TEMPLATE_CONTEXT': True,
        }


TEMPLATES[0]['OPTIONS']['debug'] = DEBUG  # noqa: F405
TEMPLATES[0]['OPTIONS']['loaders'] = [  # noqa: F405
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]

DJANGO_LIVE_TEST_SERVER_ADDRESS = 'localhost:8000-8010,8080,9200-9300'

# Habilita o uso do jupyter notebook via docker
# https://stackoverflow.com/questions/62193187/django-shell-plus-how-to-access-jupyter-notebook-in-docker-container
SHELL_PLUS = "ipython"

SHELL_PLUS_PRINT_SQL = True

NOTEBOOK_ARGUMENTS = [
    "--ip",
    "0.0.0.0",
    "--port",
    "8888",
    "--allow-root",
    "--no-browser",
]

IPYTHON_ARGUMENTS = [
    "--ext",
    "django_extensions.management.notebook_extension",
    "--debug",
]

IPYTHON_KERNEL_DISPLAY_NAME = "Django Shell-Plus"

SHELL_PLUS_POST_IMPORTS = [  # extra things to import in notebook
    ("module1.submodule", ("func1", "func2", "class1", "etc")),
    ("module2.submodule", ("func1", "func2", "class1", "etc"))
]

# https://docs.djangoproject.com/en/3.2/topics/async/#async-safety
if DEBUG:
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"  # only use in development
