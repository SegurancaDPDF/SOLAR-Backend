# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip


import six
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

import pytest
import os

# conjunto de testes usando a biblioteca PyTest e a biblioteca Selenium para realizar testes automatizados

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.desenvolvimento")

senha = ''.join(
    [unichr(ord(unicode(x)) - 1000) for x in u'\u0457\u044e\u0451\u044b\u0451\u0456\u0449\u0420\u0419\u041d\u041d'])

# mobile_emulation = {"deviceName": "Google Nexus 5"}
chrome_options = webdriver.ChromeOptions()
chrome_options.debugger_address = 'http://127.0.0.1:9222'


# chrome_options.add_experimental_option("mobileEmulation",
#                                        mobile_emulation)
# configura o webdriver do Selenium a ser usado nos testes
@pytest.fixture(scope='session')
def splinter_webdriver():
    """Override splinter webdriver name."""

    driver_name = 'firefox'
    # driver_name = 'chrome'
    # driver_name = 'remote'
    return driver_name


# @pytest.fixture(scope='session')
# def splinter_remote_url():
#     """Override splinter webdriver name."""
#     # return 'chrome'
#     return 'http://127.0.0.1:9222'
#


# @pytest.fixture(scope='session')
# def splinter_driver_kwargs():
#     """Webdriver keyword arguments, a dictionary which is passed to selenium webdriver's constructor"""
#     return {
#
#         'kwargs': {
#             'options': chrome_options
#         }
#     }


# @pytest.fixture(scope='session')
# def splinter_driver_kwargs():
#     """Webdriver keyword arguments, a dictionary which is passed to selenium webdriver's constructor"""
#     return {
#         'headless': True
#     }

# tempo de espera em segundos para aguardar a resposta do webdriver.
@pytest.fixture(scope='session')
def splinter_wait_time():
    """Webdriver kwargs."""
    return 15


@pytest.fixture(scope='session')
def session_browser(session_browser):
    url = "http://127.0.0.1:8000/login/"
    session_browser.visit(url)
    session_browser.fill('username', 'fabio.cb')
    session_browser.fill('password', senha)

    # Find and click the 'search' button
    button = session_browser.find_by_xpath('//*[@id="sign-in"]/div[4]/input')
    # Interact with elements
    button.click()
    return session_browser


# @pytest.fixture(scope='session')
# def splinter_webdriver():
#     """Override splinter webdriver name."""
#     return 'chrome'

# lista de dicionários contendo dados de pesquisa e as mensagens esperadas após a pesquisa  
dados_pesquisa = [
    # {
    #     'campos': {
    #         'nome_completo': 'Robson Carvalho da Silva Correia',
    #         'cpf_matricula': '00359964125'
    #     },
    #     'mensagens_esperadas': [
    #         'athenas+ldapa',
    #         'errors: []'
    #     ]
    # },
    {
        'campos': {
            'nome_completo': 'Fabio Caritas Barrionuevo da Luz',
            'cpf_matricula': '01129033120'
        },
        'mensagens_esperadas': [
            'já possui cadastro no sistema'
        ]
    },
    {
        'campos': {
            'nome_completo': 'THIAGO RODRIGUES DA SILVA',
            'cpf_matricula': '026.038.171-32'
        },
        'mensagens_esperadas': [
            'athenas+ldap'
        ]
    },
    {
        'campos': {
            'nome_completo': 'Danielle Lobato Maya',
            'cpf_matricula': '038.929.751-83'
        },
        'mensagens_esperadas': [
            'ldap'
        ]
    },
    {
        'campos': {
            'nome_completo': 'Edilia Mendes de Resende',
            'cpf_matricula': '052.744.621-11'
        },
        'mensagens_esperadas': [
            'já possui cadastro no sistema'
        ]
    },
    {
        'campos': {
            'nome_completo': 'Hugo Deleon Pereira Pires',
            'cpf_matricula': '031.191.261-36'
        },
        'mensagens_esperadas': [
            'já possui cadastro no sistema, mas está desativado'
        ]
    },
    {
        'campos': {
            'nome_completo': 'Alyandra de Abreu Alves Silvestre',
            'cpf_matricula': '033.709.141-23'
        },
        'mensagens_esperadas': [
            'já possui cadastro no sistema, mas está desativado'
        ]
    },
    {
        'campos': {
            'nome_completo': 'Luana Gomes de Carvalho',
            'cpf_matricula': '038.499.631-01'
        },
        'mensagens_esperadas': [
            'já possui cadastro no sistema, mas está desativado'
        ],

    },
]
# dicionário que mapeia nomes de papéis para seus respectivos valores
papeis = {
    "Estagiário": "1",
    "Corregedoria": "2",
    "Atendimento/Assistente": "Atendimento/Assistente",
    "Assessor": "4",
    "Servidor Voluntário": "5",
    "Analista jurídico": "6",
}
# lista de dicionários contendo dados para testar a funcionalidade de cadastro de usuário do site.
dados_cadastro = [
    {
        'campos': {
            'nome': 'Luana Gomes de Carvalho',
            'cpf': '038.499.631-01',
            'papel': [papeis['Atendimento/Assistente']],
            'password1': '123',
            'password2': '123',
            'matricula': '9085360',
            'defensor_supervisor': [7],
            'comarca': 11,
            'sexo': [0, ],
        },
        'mensagens_esperadas': [
            'já possui cadastro no sistema, mas está desativado'
        ],
    },
]

# @pytest.fixture(scope="class")
# def browser_login_ativo(browser):
#     do_login(browser)
#     return browser
clear_selector = '.select2-selection__clear'
container_selector = '.select2-container'
dropdown_selector = '.select2-dropdown'
input_selector = '.select2-search__field'
label_selector = '.select2-selection__rendered'
labels_selector = \
    '.select2-selection__rendered .select2-selection__choice'
option_selector = '.select2-results__option[aria-selected]'
widget_selector = '.select2-selection'


# interage com o navegador
def click(b, selector):
    b.find_by_css(selector).first.click()


# def toggle_autocomplete(b):
#     click(b, )
#
# def select_option(self, b, text):
#     """Assert that selecting option "text" sets input's value."""
#     dropdown = browser.find_by_css(dropdown_selector)
#     if not len(dropdown) or not dropdown.visible:
#         toggle_autocomplete()
#
#     case.assert_visible(self.dropdown_selector)
#     case.enter_text(self.input_selector, text)
#     find_option(text).click()
#

def verificar_pesquisa(navegador, botao_de_acao, campos, mensagens_esperadas):
    url = "http://127.0.0.1:8000/servidor/criar-usuario/"
    navegador.visit(url)
    for chave, valor in six.iteritems(campos):
        if isinstance(valor, (list, tuple)):
            navegador.find_by_name(chave)
            navegador.execute_script('$("#id_{}").select2("open")'.format(chave))
            # navegador.fill(chave, 'Select2 list value')
            search_input = navegador.find_by_css('.select2-results__option[aria-selected]').first
            search_input.fill(valor[0])
            search_input.send_keys(Keys.RETURN)
            # elem = navegador.driver.find_element_by_name("chave")
            # elem.send_keys(Keys.RETURN)

        #     select.mouse_over()
        #     select.click()
        #
        #
        #     select.click()
        #     navegador.select(chave, valor[0])
        else:
            navegador.fill(chave, valor)

    button = navegador.find_by_name(botao_de_acao)
    # Interage com os elementos
    button.click()

    for mensagem in mensagens_esperadas:
        se_erro = (campos, mensagens_esperadas)
        assert navegador.is_text_present(mensagem), se_erro


def test_mensagens_erro(session_browser):
    """Test using real browser."""
    for dado in dados_pesquisa:
        verificar_pesquisa(session_browser, 'consultar', dado['campos'], dado['mensagens_esperadas'])

        # error_msg = "erro"
        # assert browser.is_text_present('já possui cadastro no sistema'), error_msg


def test_foobar(session_browser):
    session_browser.visit("https://twitter.com/hackebrot/status/883051377966149633")
    assert True

# def test_cadastro_novo_usuario(browser):
#     # browser = browser_login_ativo
#     login(browser)
#
#     url = "http://127.0.0.1:8000/servidor/criar-usuario/"
#     browser.visit(url)
#     for dado in dados_cadastro:
#         verificar_pesquisa(browser, 'botao_cadastrar', dado['campos'], dado['mensagens_esperadas'])
