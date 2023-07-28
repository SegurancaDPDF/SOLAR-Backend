# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
# Modulos locais
from . import views


urlpatterns = [
    url(r'^$', login_required(views.InicialView.as_view()), name='agendamento_index'),
    url(r'^agendar/$', login_required(views.AgendarInicialView.as_view()), name='agendamento_agendar'),
    url(r'^calendario/$', login_required(views.CalendarioView.as_view()), name='agendamento_calendario'),
    url(r'^conflitos/', include([
        url(r'^$', views.conflitos, name='agendamento_conflitos'),
        url(r'^corrigir/$', views.conflitos_corrigir, name='agendamento_conflitos_corrigir'),
        url(r'^corrigidos/$', views.conflitos_corrigidos, name='agendamento_conflitos_corrigidos'),
        url(r'^defensor/([0-9]+)/$', views.conflitos, name='agendamento_conflitos_defensor'),
        url(r'^defensor/([0-9]+)/total/$', views.conflitos_total, name='agendamento_conflitos_total'),
        url(r'^defensor/([0-9]+)/total/([0-9]+)/([0-9]+)/$', views.conflitos_mensal, name='agendamento_conflitos_mensal'),  # noqa: E501
    ])),
    url(r'^justificar/$', views.justificar, name='agendamento_justificar'),
    url(r'^(?P<atendimento_numero>[0-9]+)/', include([
        url(r'^nucleo/$', views.nucleo, name='agendamento_nucleo'),
        url(r'^nucleo/agendar/$', login_required(views.AgendarNucleoView.as_view()), name='agendamento_agendar_nucleo'),
        url(r'^nucleo/confirmar/$', views.nucleo_confirmar, name='agendamento_nucleo_confirmar'),
        url(r'^processo/$', views.processo, name='agendamento_processo'),
        url(r'^retorno/$', login_required(views.RetornoView.as_view()), name='agendamento_retorno'),
        url(r'^retorno/agendar/$', login_required(views.AgendarRetornoView.as_view()), name='agendamento_agendar_retorno'),  # noqa: E501
        url(r'^remarcar/$', login_required(views.RemarcarView.as_view()), name='agendamento_remarcar'),
        url(r'^remarcar/agendar/$', login_required(views.AgendarRemarcarView.as_view()), name='agendamento_agendar_remarcar'),  # noqa: E501
    ])),
]
