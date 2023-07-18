# -*- coding: utf-8 -*-
# Importações necessárias

from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import os

from celery import Celery
from django.apps import AppConfig, apps
from django.conf import settings

# verifica se as configurações do Django já foram configuradas

__all__ = [
    'app',
    'TaskAppConfig'
]

if not settings.configured:
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.producao')  # pragma: no cover

app = Celery('solar_tasks')


class TaskAppConfig(AppConfig):
    name = 'taskapp'
    verbose_name = 'Celery Config'

    def ready(self):
        app.config_from_object('django.conf.settings')
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        app.autodiscover_tasks(lambda: installed_apps, force=True)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))  # pragma: no cover
