# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import os
import sys

# Bibliotecas de terceiros
from django.core.wsgi import get_wsgi_application


paths = [
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
]

for path in paths:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.producao'
application = get_wsgi_application()
