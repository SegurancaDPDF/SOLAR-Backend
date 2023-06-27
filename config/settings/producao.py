# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Modulos locais
from .comum import *  # noqa: F403

TEMPLATES[0]['OPTIONS']['loaders'] = [  # noqa: F405
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]
