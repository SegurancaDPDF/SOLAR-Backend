import requests
import time
from bs4 import BeautifulSoup


# percorre as tags '<td>' e armazena seus textos limpos em dados
def movimentos(soup):
    dados = []
    lista_movimento = []
    lista_data = []
    ob_json = []

    for th in soup.findAll('td'):
        dados.append(th.text.replace('\n', ' ').replace('\t', ' ').strip())

    for i in range(len(dados)):
        if dados[i] != '':
            lista_data.append(dados[i])
    dados = lista_data
    lista_data = []

    for i in range(len(dados)):
        if i % 2 == 0:
            lista_data.append(dados[i])
        else:
            lista_movimento.append(" ".join(dados[i].split()))

    for i in range(len(lista_data)):
        ob_json.append({'data': lista_data[i], 'movimentacoes': lista_movimento[i]})

    return ob_json


# retorna um formato JSON contendo informações sobre datas e tipos de petições diversas.
def peticoes_divercas(soup):
    dados = []
    lista_movimento = []
    lista_data = []
    ob_json = []

    for th in soup.findAll('td'):
        dados.append(th.text.replace('\n', ' ').replace('\t', ' ').strip())

    for i in range(len(dados)):
        if dados[i] != '':
            lista_data.append(dados[i])
    dados = lista_data
    lista_data = []

    for i in range(len(dados)):
        if i % 2 == 0:
            lista_data.append(dados[i])
        else:
            lista_movimento.append(" ".join(dados[i].split()))

    for i in range(len(lista_data)):
        ob_json.append({'data': lista_data[i], 'tipo': lista_movimento[i]})

    return ob_json


# extrai dados de datas, audiências, situações e quantidade de pessoas presentes em audiências
def audiencias(soup):
    dados = []
    lista_movimento = []
    lista_data = []
    ob_json = []

    for th in soup.findAll('td'):
        dados.append(th.text.replace('\n', ' ').replace('\t', ' ').strip())

    for i in range(len(dados)):
        if dados[i] != '':
            lista_data.append(dados[i])
    dados = lista_data
    lista_data = []
    index = 0
    for i in range(int(len(dados)/4)):
        lista_data.append(
            {
                'data': dados[index+0],
                'audiencia': dados[index+1],
                'situacao': dados[index+2],
                'qtd_pessoas': dados[index+3]
             })
    return lista_data

# extrai informações de datas, tipos de processo, classes, áreas e motivos de um histórico de classes
def historico_classes(soup):
    dados = []
    lista_movimento = []
    lista_data = []
    ob_json = []

    for th in soup.findAll('td'):
        dados.append(th.text.replace('\n', ' ').replace('\t', ' ').strip())

    for i in range(len(dados)):
        if dados[i] != '' :
            lista_data.append(dados[i])
    dados = lista_data
    index = 0
    for i in range(int(len(dados)/5)):
        ob_json.append(
            {
                'data': dados[index+0],
                'tipo': dados[index+1],
                'classe': dados[index+2],
                'area': dados[index+3],
                'motivo': dados[index+4]
            })
    return ob_json


def partes_do_processo(partes_processo):
    lista_partes_processo = []
    list_dic = []
    for child in partes_processo:
        lista_partes_processo.append( " ".join(child.text.strip().split() ))
    dados = lista_partes_processo
    lista_partes_processo = []
    for i in range(len(dados)):
        if dados[i] != '':
            lista_partes_processo.append(dados[i])
    list_dic.append({'requerente': lista_partes_processo[0], 'requerida': lista_partes_processo[1]})
    return list_dic


def extracao_dados(soup):
    consulta_processo = []

    # Partes do processo
    partes_processo = soup.find(string='Partes do processo').parent.find_next('table')
    consulta_processo.append(partes_do_processo(partes_processo))

    # Movimentações
    movimentacoes = soup.find(string='Movimentações').parent.find_next('table')
    consulta_processo.append(movimentos(movimentacoes))

    # Petições Diversas
    peticoes_diversas = soup.find(string='Petições diversas').parent.find_next('table')
    consulta_processo.append(peticoes_divercas(peticoes_diversas))

    audiencia = soup.find(string='Audiências').parent.find_next('table')

    if audiencia.text.strip() == 'Não há Audiências futuras vinculadas a este processo.':
        consulta_processo.append([
            {
                'data': 'Nenhum',
                'audiencia': 'Não há Audiências futuras vinculadas a este processo.'
            }])
    else:
        consulta_processo.append( audiencias(audiencia))

    # Historico de Classes
    if soup.find(string='Histórico de classes'):
        historico_classe = soup.find(string='Histórico de classes').parent.find_next('table')
    else:
        historico_classe = []

    if historico_classe:
        consulta_processo.append(historico_classes(historico_classe))
    return consulta_processo


# incidentes = soup.find_all('table')[3]

# apensos = soup.find_all('table')[4]
def consulta_tjam(numero_processo):
    documento = ''

    tentativas = 0
    sucesso = False
    while tentativas < 4 and (not sucesso):
        url_tj = 'https://consultasaj.tjam.jus.br/' \
                 'cpopg/searchMobile.do?tipoConsulta=%2Fcpopg%2FopenMobile.do&' \
                 'localPesquisa.cdLocal=-1&cbPesquisa=NUMPROC&dePesquisa=' + numero_processo + ' '

        response = requests.get(url_tj,timeout=2)
        new_url = str(response.url).replace('Mobile', '')
        work_page = requests.get(new_url, timeout=4)
        soup = BeautifulSoup(work_page.text, 'html.parser')

        try:
            if soup.find(string='Partes do processo').parent is not None:
                documento = extracao_dados(soup)
                sucesso = True
            else:
                sucesso = False
                time.sleep(2)
                print('acessou')
        except AttributeError as error:
            print('Algo aconteceu')
            time.sleep(2)
        print('tentativas: ' + str(tentativas))
        tentativas += 1
    if documento == '':
        return [{
            'link':
                new_url+'&numeroDigitoAnoUnificado='+numero_processo[:13]+'&foroNumeroUnificado='+numero_processo[16:],
            'messagem':
                'Não existem informações disponíveis para os parâmetros informados.', 'error': True}]
    return documento
