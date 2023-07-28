# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import re

from requests_oauthlib import OAuth2Session

from constance import config
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin

EXEMPT_URLS = [re.compile(settings.LOGIN_URL.lstrip('/'))]

if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [re.compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]


class EgideAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):

        if config.USAR_API_EGIDE_AUTH and (not request.user or not request.user.is_authenticated):
            path = request.path_info.lstrip('/')
            urls_autorizadas = [m.match(path) for m in EXEMPT_URLS]
            # skip for non-required authentication urls
            if not any(urls_autorizadas):
                oauth = OAuth2Session(
                    settings.EGIDE_CLIENT_ID,
                    redirect_uri=settings.EGIDE_REDIRECT_URI)

                # obtem da API do EGIDE, dados relativos ao usuario atual
                egide_response = oauth.authorization_url(settings.EGIDE_AUTHORIZE_URL)
                authorize_url = egide_response[0]

                return HttpResponseRedirect(authorize_url)
