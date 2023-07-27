from django.conf import settings

from clients.base.services import APIBase
from clients.livre_client.models import HistoricoConsulta
from contrib.utils import ip_visitante


# APILivre que herda de APIBase para interagir com a API Livre
class APILivre(APIBase):
    api_url = settings.LIVRE_API_URL
    api_token = settings.LIVRE_API_TOKEN

    def __init__(self, request=None):
        self.request = request

    # método 'action' que realiza uma ação na API e registra o histórico da consulta.
    def action(self, *args, **kwargs):

        sucesso, resposta = super().action(*args, **kwargs)
        # registro do histórico da consulta no banco de dados
        HistoricoConsulta.objects.create(
            servico='_'.join(args[0]),
            parametros=kwargs['params'] if 'params' in kwargs else None,
            ip=ip_visitante(self.request) if self.request else None,
            sucesso=sucesso,
            resposta=resposta if not sucesso else None
        )

        return sucesso, resposta

    def esta_ativado(self):  # verifica se a API está ativada através da presença do token
        return self.api_token is not None

    def get_mensagem_conexao_indisponivel(self):  # retorna uma mensagem de conexão indisponível
        return 'Conexão com SEEU temporariamente indisponível!'

    def get_page_size(self):
        return 100

    def verificar_disponibilidade(self):  # verifica a disponibilidade do serviço
        return self.action(['seeu', 'verificar-disponibilidade-web-service_list'])


class APIRelatorio(APILivre):  # herda de APILivre e adiciona funcionalidades específicas de relatórios
    # constantes para tipos de relatórios
    RELATORIO_SITUACAO_CARCERARIA = 1
    RELATORIO_ATESTADO_DE_PENA = 2
    RELATORIO_LINHA_DO_TEMPO = 3
    
    # realiza a consulta de um relatório através do número do processo e tipo de relatório
    def consultar(self, numero_processo, tipo_relatorio):
        return self.action(['seeu', 'obter-relatorio_read'], params={
            'numero_processo': numero_processo,
            'tipo_relatorio': tipo_relatorio
        })


class APILeiArtigoParagrafo(APILivre):
    def consultar(self):
        return self.action(['seeu', 'consultar-todos-leis-artigo-paragrafo-inciso-alinea_list'])
