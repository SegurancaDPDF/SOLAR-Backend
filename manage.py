#!/usr/bin/env python
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.desenvolvimento")

    from django.conf import settings

    if settings.DEBUG and not settings.DEBUG_VSCODE:
        if os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
            import ptvsd

            ptvsd.enable_attach(address=('0.0.0.0', 3000))
            print('Attached!')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
