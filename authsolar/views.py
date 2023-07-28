import json
import logging


from constance import config
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import View, TemplateView
from requests_oauthlib import OAuth2Session
from django.conf import settings
from django.contrib.auth import login
from .backends import EgideAuthBackend, EgideSolarUserDoesNotExist

from .auth_views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView,
    PasswordChangeDoneView,
)

__all__ = [
    'SolarLoginView',
    'SolarLogoutView',
    'SolarPasswordResetView',
    'SolarPasswordResetDoneView',
    'SolarPasswordResetConfirmView',
    'SolarPasswordResetCompleteView',
    'SolarPasswordChangeView',
    'SolarPasswordChangeDoneView',
    'SolarEgideProcessCallback',
    'SolarEgideUsuarioNaoCadastrado',
]


logger = logging.getLogger(__name__)


# classe de visualização para exibir uma página quando o usuário não está cadastrado no sistema
class SolarEgideUsuarioNaoCadastrado(TemplateView):
    template_name = '500_usuario_nao_cadastrado.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # adiciona a mensagem de usuário não cadastrado ao contexto da página
        context['EGIDE_MENSAGEM_USUARIO_NAO_CADASTRADO'] = config.EGIDE_MENSAGEM_USUARIO_NAO_CADASTRADO
        return context


# classe de visualização para processar o retorno de chamada após a autenticação com o serviço de terceiros (EGIDE)
class SolarEgideProcessCallback(View):
    http_method_names = ['get']

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        if config.USAR_API_EGIDE_AUTH and (not request.user or not request.user.is_authenticated):
            try:
                response_code = request.GET.get('code')

                oauth = OAuth2Session(
                    settings.EGIDE_CLIENT_ID,
                    redirect_uri=settings.EGIDE_REDIRECT_URI)

                if response_code:
                    token = oauth.fetch_token(
                        verify=False,
                        code=response_code,
                        token_url=settings.EGIDE_TOKEN_URL,
                        client_secret=settings.EGIDE_CLIENT_SECRET)

                    # persiste o token de autenticacao na sessao
                    request.session['access_token'] = token

                    oauth = OAuth2Session(token=token)
                    text = oauth.get(settings.EGIDE_API, verify=False).text

                    user_data = json.loads(text)

                    user = EgideAuthBackend(user_data).authenticate(request)
                    user.backend = 'authsolar.backends.EgideAuthBackend'
                    # autentica usuario no django
                    login(request, user)
            except EgideSolarUserDoesNotExist:
                return redirect(reverse('login_usuario_nao_cadastrado'))
            except Exception as e:
                print("erro")
                logger.exception(e)

        return redirect(reverse('index'))


class SolarLoginView(LoginView):
    pass


class SolarLogoutView(LogoutView):

    def dispatch(self, request, *args, **kwargs):
        # faz logout da sessao no django
        original_response = super(SolarLogoutView, self).dispatch(request, *args, **kwargs)
        if config.USAR_API_EGIDE_AUTH:
            # redireciona para a pagina de logout do EGIDE
            return redirect(settings.EGIDE_LOGOUT_URL)
        return original_response


class SolarPasswordResetView(PasswordResetView):
    pass


class SolarPasswordResetDoneView(PasswordResetDoneView):
    pass


class SolarPasswordResetConfirmView(PasswordResetConfirmView):
    pass


class SolarPasswordResetCompleteView(PasswordResetCompleteView):
    pass


class SolarPasswordChangeView(PasswordChangeView):
    pass


class SolarPasswordChangeDoneView(PasswordChangeDoneView):
    pass
