# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from datetime import datetime
import json
from constance import config
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView
from contrib.models import Defensoria, Etiqueta
from contrib.utils import ip_visitante
# Solar
from procapi_client.models import HistoricoConsultaTeorComunicacao
from procapi_client.services import APIAviso, APIComunicacao, PrateleiraAvisosService
from procapi_client.exceptions import ExceptionBase
from processo.processo.models import Aviso, Fase, Processo
from defensor.models import Defensor

from .forms import BuscarIntimacaoForm


class PainelView(TemplateView):
    template_name = 'processo/intimacao/painel.html'

    def get_context_data(self, **kwargs):

        # TODO: hack para definir usuário atual como padrão na busca (não funcionou usando o inicial no form)
        data = self.request.GET.copy()
        if config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSOR_AUTOMATICAMENTE and 'responsavel' not in data and self.request.user.servidor.defensor.eh_defensor:
            data['responsavel'] = self.request.user.servidor.defensor.id

        form = BuscarIntimacaoForm(data, usuario=self.request.user)

        # Só filtra se valores de busca forem válidos
        if form.is_valid():
            data = form.cleaned_data

        prateleira = PrateleiraAvisosService(
            sistema=data['sistema_webservice'],
            defensoria=data['setor_responsavel'],
            defensor=data['responsavel'],
            usuario=self.request.user
        )

        total_geral, prateleiras = prateleira.gerar()

        context = super(PainelView, self).get_context_data(**kwargs)

        # Atualiza variáveis de contexto (visíveis no template)
        context.update({
            'total_geral': total_geral,
            'prateleiras': prateleiras,
            'form': form,
        })

        return context


class BuscarView(TemplateView):

    template_name = 'processo/intimacao/buscar.html'

    def get_context_data(self, **kwargs):
        '''
        CITAÇÕES/INTIMAÇÕES
        - Processos com prazo em aberto
        - Processos pendentes de citação/intimação - Urgentes
        - Processos pendentes de citação/intimação
        - Processos pendentes de intimação de homologação de acordo
        - Processos pendentes de citação - art 334 CPC
        - Decursos de prazo nos últimos 30 dias
        '''

        totais = []
        avisos = []
        prioridades = []

        # Permissões
        pode_abrir_prazo = self.request.user.is_superuser or self.request.user.servidor.defensor.eh_defensor
        pode_ver_todas_etiquetas = config.ATIVAR_ETIQUETA_SIMPLIFICADA or (self.request.user.is_superuser or self.request.user.servidor.defensor.eh_defensor)

        lista_defensores = []
        lista_defensorias = self.request.user.servidor.defensor.defensorias
        lista_todas_defensorias = Defensoria.objects.ativos()

        defensorias_codigos = {}
        defensorias_nomes = {}
        for defensoria in Defensoria.objects.ativos():
            defensorias_codigos[str(defensoria.id)] = defensoria.codigo
            defensorias_nomes[str(defensoria.id)] = defensoria.nome

        for defensor in self.request.user.servidor.defensor.lista_supervisores:
            lista_defensores.append({'nome': defensor.nome, 'cpf': defensor.servidor.cpf})

        # Lista de etiquetas disponíveis para as defensorias da lotação do usuário
        etiquetas = Etiqueta.objects.ativos().order_by('nome').distinct()

        if pode_ver_todas_etiquetas:
            etiquetas = etiquetas.filter(
                defensoriaetiqueta__desativado_em=None,
                defensoriaetiqueta__defensoria__in=lista_defensorias,
            )
        else:
            etiquetas = etiquetas.filter(
                defensoriaetiqueta__desativado_em=None,
                defensoriaetiqueta__defensoria__in=lista_defensorias,
                defensoriaetiqueta__usuarios_autorizados=self.request.user
            )

        etiquetas_id = list(etiquetas.values_list('id', flat=True))
        etiquetas_nome = dict(list(etiquetas.values_list('id', 'nome')))
        etiquetas_cor = dict(list(etiquetas.values_list('id', 'cor')))

        # Filtros
        situacao = self.request.GET.get('situacao')

        # TODO: hack para definir usuário atual como padrão na busca (não funcionou usando o inicial no form)
        data = self.request.GET.copy()
        if config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSOR_AUTOMATICAMENTE and 'responsavel' not in data and self.request.user.servidor.defensor.eh_defensor:
            data['responsavel'] = self.request.user.servidor.defensor.id

        form = BuscarIntimacaoForm(data, usuario=self.request.user)

        # Só filtra se valores de busca forem válidos
        if form.is_valid():

            data = form.cleaned_data

            data['curadoria'] = None
            if 'curadoria' in self.request.GET:
                if self.request.GET['curadoria'] in ['true']:
                    data['curadoria'] = True
                else:
                    data['curadoria'] = False

            data['prioridade'] = None
            if 'prioridade' in self.request.GET:
                data['prioridade'] = self.request.GET['prioridade']

            data['etiqueta'] = None
            if 'etiqueta' in self.request.GET:
                if self.request.GET['etiqueta'].isnumeric():
                    data['etiqueta'] = int(self.request.GET['etiqueta'])
                else:
                    data['etiqueta'] = self.request.GET['etiqueta']

            if data['responsavel'] is None and data['setor_responsavel'] is None and not self.request.user.is_superuser:
                data['responsavel'] = self.request.user.servidor.defensor

            # Só consulta se responsável foi informado ou o usuário é superusuário e tem permissão pra ver a etiqueta informada
            if (data['responsavel'] or data['setor_responsavel'] or self.request.user.is_superuser) and (pode_ver_todas_etiquetas or data['etiqueta'] in etiquetas_id):

                distribuido_cpf = None
                distribuido_defensoria = None

                if data['responsavel']:

                    if config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSOR_AUTOMATICAMENTE:
                        distribuido_cpf = data['responsavel'].servidor.cpf
                    else:
                        distribuido_defensoria = ','.join(map(str, list(data['responsavel'].defensorias.values_list('id', flat=True))))

                    if config.AVISOS_FILTER_DISTRIBUIDO_OPERADOR_LOGICO == 'OR':
                        distribuido_cpf = data['responsavel'].servidor.cpf

                if data['setor_responsavel']:
                    distribuido_defensoria = data['setor_responsavel'].id

                api = APIAviso()
                # Consulta no ProcAPI o total de avisos pendentes
                _, totais = api.consultar_totais(params={
                    'sistema_webservice': data['sistema_webservice'].nome if data['sistema_webservice'] else None,
                    'distribuido_cpf': distribuido_cpf,
                    'distribuido_defensoria': distribuido_defensoria,
                    'distribuido_operador_logico': config.AVISOS_FILTER_DISTRIBUIDO_OPERADOR_LOGICO,
                    'tipo': data['tipo'],
                    'curadoria': data['curadoria'],
                    'prioridade': data['prioridade'],
                    'etiqueta': data['etiqueta'],
                    'ativo': True,
                })
                # Consulta no ProcAPI a lista de avisos pendentes
                avisos = api.listar_todos(params={
                    'sistema_webservice': data['sistema_webservice'].nome if data['sistema_webservice'] else None,
                    'distribuido': True,
                    'distribuido_cpf': distribuido_cpf,
                    'distribuido_defensoria': distribuido_defensoria,
                    'distribuido_operador_logico': config.AVISOS_FILTER_DISTRIBUIDO_OPERADOR_LOGICO,
                    'tipo': data['tipo'],
                    'situacao': data['situacao'],
                    'curadoria': data['curadoria'],
                    'prioridade': data['prioridade'],
                    'etiqueta': data['etiqueta'],
                    'ativo': True,
                    'ordering': 'prazo_final',
                })

                for aviso in avisos:
                    if aviso['prioridades']:
                        prioridades += aviso['prioridades']
                    if aviso['prazo_final']:
                        aviso['prazo_final'] = datetime.strptime(aviso['prazo_final'], '%Y-%m-%dT%H:%M:%S')
                    if aviso['prazo_ciencia']:
                        aviso['prazo_ciencia'] = datetime.strptime(aviso['prazo_ciencia'], '%Y-%m-%dT%H:%M:%S')
                        

        situacoes = {}
        for situacao_id, situacao_nome in Aviso.LISTA_SITUACAO:
            # procura por total de itens vinculados a situação
            total_situacao = 0
            for total in totais:
                if total['_id']['situacao'] == situacao_id:
                    total_situacao += total['count']

            situacoes[situacao_id] = {
                'nome': situacao_nome,
                'total': total_situacao
            }

        filtros = self.request.GET.copy()
        if 'situacao' in filtros:
            del filtros['situacao']
        filtros = filtros.urlencode()

        # Dados do painel de totais
        dados_painel_totais = [
            {
                'texto': situacoes[Aviso.SITUACAO_PENDENTE]['nome'],
                'valor': situacoes[Aviso.SITUACAO_PENDENTE]['total'],
                'icone': 'fas fa-exclamation-circle',
                'cor': 'bg-red',
                'url': '?situacao={}&{}'.format(Aviso.SITUACAO_PENDENTE, filtros),
                'selecionado': situacao == str(Aviso.SITUACAO_PENDENTE),
            },
            {
                'texto': situacoes[Aviso.SITUACAO_ABERTO]['nome'],
                'valor': situacoes[Aviso.SITUACAO_ABERTO]['total'],
                'icone': 'fas fa-clock',
                'cor': 'bg-yellow',
                'url': '?situacao={}&{}'.format(Aviso.SITUACAO_ABERTO, filtros),
                'selecionado': situacao == str(Aviso.SITUACAO_ABERTO),
            },
            {
                'texto': situacoes[Aviso.SITUACAO_FECHADO]['nome'],
                'valor': situacoes[Aviso.SITUACAO_FECHADO]['total'],
                'icone': 'fas fa-check-circle',
                'cor': 'bg-green',
                'url': '?situacao={}&{}'.format(Aviso.SITUACAO_FECHADO, filtros),
                'selecionado': situacao == str(Aviso.SITUACAO_FECHADO),
            },
            {
                'texto': situacoes[Aviso.SITUACAO_EXPIRADO]['nome'],
                'valor': situacoes[Aviso.SITUACAO_EXPIRADO]['total'],
                'icone': 'fas fa-times-circle',
                'cor': 'bg-blue',
                'url': '?situacao={}&{}'.format(Aviso.SITUACAO_EXPIRADO, filtros),
                'selecionado': situacao == str(Aviso.SITUACAO_EXPIRADO),
            },
        ]

        context = super(BuscarView, self).get_context_data(**kwargs)

        # Atualiza variáveis de contexto (visíveis no template)
        context.update({
            # Só pode abrir prazo se for defensor ou superusuário
            'agora': datetime.now(),
            'pode_abrir_prazo': pode_abrir_prazo,
            'pode_ver_todas_etiquetas': pode_ver_todas_etiquetas,
            'eh_defensor': self.request.user.servidor.defensor.eh_defensor,
            'lista_defensores': json.dumps(lista_defensores),
            'lista_defensorias': lista_defensorias,
            'defensorias_codigos': defensorias_codigos,
            'defensorias_nomes': defensorias_nomes,
            'lista_todas_defensorias': lista_todas_defensorias,
            'prioridades': set(prioridades),
            'etiquetas': etiquetas_nome,
            'etiquetas_cor': etiquetas_cor,
            'cpf_usuario': self.request.user.servidor.cpf,
            'totais': dados_painel_totais,
            'object_list': avisos,
            'form': form,
            'angular': 'BuscarIntimacoesCtrl',
        })

        return context


class AbrirPrazoView(TemplateView):

    def post(self, request, *args, **kwargs):

        avisos = []
        comunicacoes = []
        data = json.loads(self.request.body)

        form = BuscarIntimacaoForm(data, usuario=self.request.user)

        if form.is_valid():

            avisos = data['avisos']

            for aviso in avisos:

                # Consulta no ProcAPI a lista de avisos pendentes
                api = APIComunicacao()
                comunicacao = None

                processo, aviso = aviso.split(',')
                existe, resposta = api.consultar(aviso)

                if existe:
                    # Recupera registro salvo
                    comunicacao = resposta
                else:
                    # Registra a comunicação do aviso
                    sucesso, resposta = api.criar(
                        # O CPF deve ser enviado para identificar um consultante específico, caso o sistema onde está o aviso exigir  # noqa: E501
                        consultante_cpf=data['cpf_responsavel'],
                        processo=processo,
                        numero=aviso,
                    )

                    # Primeiro verifica erros deconexão com tribunal de justiça
                    for erro in ExceptionBase.ERROS_DE_CONEXAO:
                        if erro in resposta:
                            comunicacao = {
                                'error': 'Erro, sistema do tribunal de justiça offline, por favor tente mais tarde ou verifique com suporte técnico',
                                'numero': aviso,
                                'processo': processo
                                }

                    # Aviso Já Fechado PJe
                    if "PJEAvisoJaFechadoException" in resposta:
                        comunicacao = {
                            'error': 'Não foi possível abrir o aviso {} pois já está fechado/respondido no PJe'.format(aviso),
                            'numero': aviso,
                            'processo': processo
                            }

                    if sucesso:
                        # Cria uma fase processual para fins de auditoria de quem abriu o prazo do aviso
                        # Caso habilitado no CONFIG
                        if (config.ID_FASE_PROCESSUAL_PADRAO_NA_ABERTURA_DE_PRAZOS and
                           config.ID_FASE_PROCESSUAL_PADRAO_NA_ABERTURA_DE_PRAZOS != '' and
                           Processo.objects.filter(numero_puro=processo).exists()):
                            Fase.objects.create(
                                processo=Processo.objects.filter(numero_puro=processo).first(),
                                tipo_id=int(config.ID_FASE_PROCESSUAL_PADRAO_NA_ABERTURA_DE_PRAZOS),
                                data_cadastro=datetime.now(),
                                data_protocolo=datetime.now(),
                                cadastrado_por=self.request.user.servidor,
                                defensor_cadastro=Defensor.objects.filter(servidor__cpf=data['cpf_responsavel'], ativo=True).first(),
                                automatico=True,
                                ativo=True
                            )
                        # Cria log para fins de Auditoria
                        HistoricoConsultaTeorComunicacao.objects.create(
                            processo=processo,
                            aviso=aviso,
                            ip=ip_visitante(request)
                        )
                        comunicacao = resposta

                comunicacoes.append(comunicacao)

        return JsonResponse({'comunicacoes': comunicacoes})


class EtiquetarPrazoView(TemplateView):

    def post(self, request, *args, **kwargs):

        data = request.POST
        etiquetas = data.getlist('etiqueta')

        for aviso_numero in data.getlist('aviso'):
            APIAviso().atualizar(**{
                'numero': aviso_numero,
                'etiquetas': etiquetas
            })

        return redirect(request.META.get('HTTP_REFERER', '/'))
