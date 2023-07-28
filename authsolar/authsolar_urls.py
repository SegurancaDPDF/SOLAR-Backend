# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from django.conf.urls import url
from django.urls import path

from .views import (
    SolarLoginView,
    SolarLogoutView,
    SolarPasswordResetView,
    SolarPasswordResetDoneView,
    SolarPasswordResetConfirmView,
    SolarPasswordResetCompleteView,
    SolarPasswordChangeView,
    SolarPasswordChangeDoneView,
    SolarEgideProcessCallback,
    SolarEgideUsuarioNaoCadastrado,
)

urlpatterns = [
    url(r'^login/$',
        view=SolarLoginView.as_view(template_name='login.html'),
        name='login'
        ),
    url(r'^login/usuario-nao-cadastrado/$',
        view=SolarEgideUsuarioNaoCadastrado.as_view(),
        name='login_usuario_nao_cadastrado'
        ),
    url(r'^login/callback/$',
        view=SolarEgideProcessCallback.as_view(),
        name='logincallback'
        ),
    url(r'^logout/$',
        view=SolarLogoutView.as_view(next_page='/'),
        name='logout'
        ),
    url(r'^password_change/$',
        view=SolarPasswordChangeView.as_view(),
        name='password_change',
        ),
    url(r'^password_change/done/$',
        view=SolarPasswordChangeDoneView.as_view(),
        name='password_change_done',
        ),
    url(r'^password_reset/$',
        view=SolarPasswordResetView.as_view(),
        name='password_reset',
        ),
    url(r'^password_reset/done/$',
        view=SolarPasswordResetDoneView.as_view(),
        name='password_reset_done',
        ),
    path('reset/<uidb64>/<token>/',
        view=SolarPasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
        ),
    url(r'^reset/done/$',
        view=SolarPasswordResetCompleteView.as_view(),
        name='password_reset_complete',
        ),
]
