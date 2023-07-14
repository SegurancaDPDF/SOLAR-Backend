# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from lettuce import step, world


@step(u'Dado que eu logo com o usuário "([^"]*)"')
def dado_que_eu_logo_com_o_usuario_value1(step, value1):
    world.browser.find_element_by_id('username').send_keys(value1)
    world.browser.find_element_by_id('password').send_keys(value1)
    world.browser.find_element_by_xpath("//input[@value='Autenticar']").click()
    world.browser.implicitly_wait(300)
    assert value1 == world.browser.find_element_by_css_selector('h2').text, "Ops! Textos nao sao iguais!"


@step(u'Dado que eu entro na pagina "([^"]*)"')
def dado_que_eu_entro_na_pagina_value1(step, value1):
    world.browser.get(world.base_url + "/")


@step(u'Quando eu digito o texto "([^"]*)" no campo "([^"]*)"')
def quando_eu_digito_o_texto_value1_no_campo_field1(step, value1, field1):
    world.browser.find_element_by_id(field1).send_keys(value1)


@step(u'E digito o texto "([^"]*)" no campo "([^"]*)"')
def e_digito_o_texto_value1_no_campo_field1(step, value1, field1):
    world.browser.find_element_by_id(field1).send_keys(value1)


@step(u'E clico no botao "([^"]*)"')
def e_clico_no_botao_field1(step, field1):
    world.browser.find_element_by_xpath("//input[@value='" + field1 + "']").click()


@step(u'E aguardo ([^"]*) segundos')
def e_aguardo_value1_segundos(step, value1):
    world.browser.implicitly_wait(value1)


@step(u'Eu vejo o título "([^"]*)"')
def eu_vejo_o_titulo_value1(step, value1):
    world.browser.implicitly_wait(300)
    assert value1 == world.browser.find_element_by_css_selector('h2').text, "Ops! Textos nao sao iguais!"
