# -*- coding: utf-8 -*-

# Biblioteca Padrao
from datetime import datetime

# Bibliotecas de terceiros
from cacheops import cache, CacheMiss
from constance import config
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse
from django.http import HttpResponse, Http404, JsonResponse
from django.views.generic import RedirectView
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.vary import vary_on_headers
from defensor.models import Atuacao
from processo.processo.models import Acao, Manifestacao, ManifestacaoAviso, Processo

# Bibliotecas Solar
from contrib.models import Comarca
from processo.processo.tasks import (
    procapi_atualizar_processo,
    procapi_atualizar_manifestacao,
    procapi_cadastrar_novo_processo_signal,
    procapi_distribuir_aviso
)

# Bibliotecas locais
from .services import APIAviso, APIProcesso

from .filters import (
    CompetenciaWebserviceFilter,
    ProcessoNumeroFilter,
    AvisoFilter,
    SistemaWebserviceFilter,
    ClasseWebserviceFilter,
    ComarcaWebserviceFilter,
    NumeroProcessoFilter,
    CpfDefensorFilter,
    CodigoProcapiManifestacaoFilter,
    LocalidadeFilter
)

from .services import (
    APICompetencia,
    APIClasse,
    APIAssunto
)


@login_required
def consultar_documento(request, processo_numero, numero_documento):

    atualizar_documento = request.GET.get("atualizar_documento")
    processo = APIProcesso(processo_numero, request)

    sucesso, resposta = processo.consultar_documento(
        numero_documento=numero_documento,
        atualizar_documento=atualizar_documento
    )

    if not sucesso:
        raise Http404

    # Responde com o conteúdo do documento
    if resposta['conteudo']:
        response = HttpResponse(content=resposta['conteudo'].encode('latin1'))
        response['Content-Type'] = resposta['mimetype']
    else:
        response = HttpResponse('Conteúdo não disponível para visualização!')

    return response


@login_required
def consultar_processo(request, processo_numero):

    usuario_requisicao = None
    if config.PROCAPI_ATIVAR_INFORMAR_PERFIL_PROJUDI:
        usuario_requisicao = request.user.servidor.defensor.usuario_eproc

    processo = APIProcesso(processo_numero, request)
    sucesso, resposta = processo.consultar(
        usuario_requisicao=usuario_requisicao
    )

    if sucesso:

        if resposta['classe']:

            acao = Acao.objects.filter(codigo_cnj=resposta['classe']['codigo']).first()

            if acao:
                resposta['classe']['inquerito'] = acao.inquerito
                resposta['classe']['acao_penal'] = acao.acao_penal
            else:
                resposta['classe']['inquerito'] = None
                resposta['classe']['acao_penal'] = None

        pagina = 1
        resposta['partes'] = []

        while pagina > 0:
            sucesso_partes, resposta_partes = processo.consultar_partes(pagina=pagina)
            resposta['partes'] += resposta_partes['results']
            pagina = pagina + 1 if resposta_partes['next'] else 0

        pagina = 1
        resposta['eventos'] = []

        while pagina > 0:
            sucesso_evento, resposta_evento = processo.consultar_eventos(pagina=pagina)
            resposta['eventos'] += resposta_evento['results']
            pagina = pagina + 1 if resposta_evento['next'] else 0

        resposta['existe_no_solar'] = Processo.objects.filter(numero_puro=processo_numero, ativo=True).exists()

    resposta = {
        'data': datetime.now(),
        'sucesso': sucesso,
        'mensagem': resposta if not sucesso else None,
        'processo': resposta if sucesso else None,
    }

    return JsonResponse(resposta)


class IdentificarDocumentoView(RedirectView):
    '''
    Identifica documento pelo número do processo e número do evento
    '''
    def get_redirect_url(self, *args, **kwargs):

        # Consulta dados do evento no ProcAPI
        processo = APIProcesso(self.kwargs.get('processo_numero'), self.request)
        sucesso, evento = processo.consultar_evento(self.request.GET.get('evento'))
        documento = None

        if sucesso:
            # Se não tem documentos mas tem eventos relacionados, faz nova consulta no primeiro
            # Necessário porque o evento de intimação não possui o documento, mas sim o evento que a originou
            if not len(evento['documentos']) and len(evento['eventos']):
                sucesso, evento = processo.consultar_evento(evento['eventos'][0])
            # Se tem documentos, obtém número do primeiro
            if sucesso and len(evento['documentos']):
                documento = evento['documentos'][0]['documento']

        # Se o número do documento foi recuperado, redireciona para página de visualização
        if documento:
            return reverse('eproc_consultar_documento', args=[self.kwargs.get('processo_numero'), documento])

        # Em caso de falhas, retorna URL da busca de processo
        messages.error(self.request, 'Não foi possível indentificar o documento!')
        return self.request.META.get('HTTP_REFERER', '/')


class ProcapiCompetenciaViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    list:
    Retorna uma lista das competências existentes no PROCAPI.
    """

    permission_classes = [IsAuthenticated]
    filter_backends = (SistemaWebserviceFilter,)

    _filter_sistema_webservice = None

    @method_decorator(cache_page(86400))  # cache no navegador de 24 horas
    @method_decorator(vary_on_headers("Authorization",))
    def list(self, request, *args, **kwargs):

        self._filter_sistema_webservice = self.request.query_params.get('sistema_webservice', None) or None

        api = APICompetencia()
        competencias = api.listar_todos(params={
            'sistema_webservice': self._filter_sistema_webservice
        })

        return JsonResponse(list(competencias), safe=False)


class ProcapiClasseViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    list:
    Retorna uma lista das classes existentes no PROCAPI.
    """

    permission_classes = [IsAuthenticated]
    filter_backends = (
        SistemaWebserviceFilter,
        CompetenciaWebserviceFilter,
        LocalidadeFilter
    )

    _filter_sistema_webservice = None
    _filter_competencia = None
    _filter_codigo_localidade = None

    @method_decorator(cache_page(86400))  # cache no navegador de 24 horas
    @method_decorator(vary_on_headers("Authorization",))
    def list(self, request, *args, **kwargs):

        self._filter_sistema_webservice = self.request.query_params.get('sistema_webservice', None) or None
        self._filter_competencia = self.request.query_params.get('codigo_competencia', None) or None
        self._filter_codigo_localidade = self.request.query_params.get('codigo_localidade', None) or None

        # Usa código do TJ como valor padrão para o filtro de comarca (localidade)
        if self._filter_codigo_localidade:
            comarca = Comarca.objects.get(id=self._filter_codigo_localidade)
            if comarca.codigo_eproc:
                self._filter_codigo_localidade = comarca.codigo_eproc

        params = {
            'sistema_webservice': self._filter_sistema_webservice,
            'ativo': True
        }

        if self._filter_competencia:
            params['codigo_competencia'] = self._filter_competencia

        if self._filter_codigo_localidade:
            params['codigo_localidade'] = self._filter_codigo_localidade

        api = APIClasse()
        classes = api.listar_todos(params=params)

        return JsonResponse(list(classes), safe=False)


class ProcapiAssuntoViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    list:
    Retorna uma lista dos assuntos existentes no PROCAPI.
    """

    permission_classes = [IsAuthenticated]
    filter_backends = (
        SistemaWebserviceFilter,
        CompetenciaWebserviceFilter,
        ClasseWebserviceFilter,
        LocalidadeFilter
    )

    _filter_sistema_webservice = None
    _filter_competencia = None
    _filter_classe = None
    _filter_codigo_localidade = None

    @method_decorator(vary_on_headers("Authorization",))
    def list(self, request, *args, **kwargs):

        self._filter_sistema_webservice = self.request.query_params.get('sistema_webservice', None) or None
        self._filter_codigo_localidade = self.request.query_params.get('codigo_localidade', None) or None
        self._filter_competencia = self.request.query_params.get('codigo_competencia', None) or None
        self._filter_classe = self.request.query_params.get('codigo_classe', None) or None

        # TODO: Tentar usar estrutura para CBV: https://pypi.org/project/django-cacheops/
        cache_key = 'assunto.listar:{}-{}-{}'.format(self._filter_codigo_localidade, self._filter_competencia, self._filter_classe)  # noqa: E501

        # Usa código do TJ como valor padrão para o filtro de comarca (localidade)
        if self._filter_codigo_localidade:
            comarca = Comarca.objects.get(id=self._filter_codigo_localidade)
            if comarca.codigo_eproc:
                self._filter_codigo_localidade = comarca.codigo_eproc

        try:

            # Tenta obter dados no cache do redis
            cache_data = cache.get(cache_key)

        except CacheMiss:

            # Se não tem dados em cache, faz pesquisa no procapi
            params = {
                'sistema_webservice': self._filter_sistema_webservice,
                'ativo': True
            }

            if self._filter_competencia:
                params['codigo_competencia'] = self._filter_competencia

            if self._filter_classe:
                params['codigo_classe'] = self._filter_classe

            if self._filter_codigo_localidade:
                params['codigo_localidade'] = self._filter_codigo_localidade

            api = APIAssunto()
            assuntos = api.listar_todos(params=params)

            # Recria lista apenas com dados necessários para o frontend
            cache_data = [{
                'codigo': assunto['codigo'],
                'nome': assunto[config.PROCAPI_ASSUNTO_CAMPO_EXIBICAO],
            } for assunto in list(assuntos)]

            cache.set(cache_key, cache_data, timeout=86400)

        return JsonResponse(cache_data, safe=False)


class ProcapiSignalProcessoViewSet(GenericViewSet):

    permission_classes = [IsAuthenticated]
    filter_backends = (NumeroProcessoFilter, CpfDefensorFilter)
    _filter_numero_processo = None
    _filter_cpf_defensor = None

    @method_decorator(never_cache)
    def list(self, request, *args, **kwargs):

        self._filter_numero_processo = self.request.query_params.get('numero_processo', None) or None
        self._filter_cpf_defensor = self.request.query_params.get('cpf_defensor', None) or None
        grau = self._filter_numero_processo[20:]

        # Se processo existir chama task de atualização
        if Processo.objects.filter(
            numero_puro=self._filter_numero_processo[:20],
            grau=grau,
            tipo=Processo.TIPO_EPROC,
            pre_cadastro=False
        ).exists():

            procapi_atualizar_processo.apply_async(kwargs={
                'numero': self._filter_numero_processo[:20],
                'grau': grau
            }, queue='geral')

            return JsonResponse({'sucesso': True})
        # Caso contrario chama task para cadastrar novo processo com as partes
        else:
            procapi_cadastrar_novo_processo_signal.apply_async(kwargs={
                'numero_processo': self._filter_numero_processo[:20],
                'grau': grau,
                'cpf_defensor': self._filter_cpf_defensor
            }, queue='default')

            return JsonResponse({'sucesso': True})


class ProcapiAvisoViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    list:
    Retorna uma lista dos avisos existentes no PROCAPI.
    """

    permission_classes = [IsAuthenticated]
    filter_backends = (ProcessoNumeroFilter, SistemaWebserviceFilter)

    _filter_processo_numero = None
    _filter_sistema_webservice = None
    _filter_distribuido_cpf = None
    _filter_distribuido_defensoria = None
    _filter_manifestacao = None

    @method_decorator(vary_on_headers("Authorization",))
    def list(self, request, *args, **kwargs):

        self._filter_processo_numero = self.request.query_params.get('processo_numero', None) or None
        self._filter_sistema_webservice = self.request.query_params.get('sistema_webservice', None) or None
        self._filter_distribuido_cpf = self.request.query_params.get('distribuido_cpf', None) or None
        self._filter_distribuido_defensoria = self.request.query_params.get('distribuido_defensoria', None) or None
        self._filter_manifestacao = self.request.query_params.get('manifestacao', None) or None

        if self._filter_manifestacao:
            manifestacao = Manifestacao.objects.get(id=self._filter_manifestacao)
        else:
            manifestacao = Manifestacao(sistema_webservice=self._filter_sistema_webservice)

        prazos = []

        # Consulta no ProcAPI a lista de avisos vinculados ao processo e defensor/defensoria
        params = {
            'processo_numero': self._filter_processo_numero,
            'sistema_webservice': manifestacao.sistema_webservice,
            'ativo': True
        }

        # identifica defensorias onde o usuario está lotado
        defensorias = Atuacao.objects.vigentes(
            ajustar_horario=False
        ).filter(
            defensor=self.request.user.servidor.defensor
        )

        if not request.user.is_superuser:

            # identifica atuações dos supervisores do usuário lotado
            atuacoes_para_analise = Atuacao.objects.select_related(
                'defensor__servidor',
            ).vigentes(
                ajustar_horario=False
            ).filter(
                defensor__eh_defensor=True,
                defensoria__in=set(defensorias.values_list('defensoria_id', flat=True)),
                defensoria__pode_vincular_processo_judicial=True
            )

            if config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSOR_AUTOMATICAMENTE:
                params['distribuido_cpf'] = ','.join(set(atuacoes_para_analise.values_list('defensor__servidor__cpf', flat=True)))  # noqa: E501
            elif config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSORIA_AUTOMATICAMENTE:
                params['distribuido_defensoria'] = ','.join(map(str, set(atuacoes_para_analise.values_list('defensoria_id', flat=True))))  # noqa: E501

        avisos = APIAviso().listar_todos(params)

        # Verifica quais prazos podem ser exibidos na manifestação
        for aviso in avisos:

            aviso['selecionado'] = False

            if not aviso['esta_fechado'] or manifestacao.situacao == Manifestacao.SITUACAO_PROTOCOLADO:
                # Verifica se prazo está vinculado à manifestação
                aviso['selecionado'] = manifestacao.avisos.ativos().filter(numero=aviso['numero']).exists()

            # Verifica se prazo está vinculado à outra manifestação
            if not aviso['esta_fechado'] and not aviso['selecionado']:
                aviso['esta_fechado'] = ManifestacaoAviso.objects.ativos().filter(
                    Q(numero=aviso['numero']) &
                    (
                        ~Q(manifestacao__situacao=Manifestacao.SITUACAO_ERRO) &
                        Q(manifestacao__desativado_em=None)
                    )
                ).exists()

            # Se está selecionado ou não está encerrado, adiciona à lista de prazos disponíveis
            if aviso['selecionado'] or not aviso['esta_fechado']:
                prazos.append(aviso)

        return JsonResponse({'results': prazos}, safe=False)


class ProcapiSignalManifestacaoViewSet(GenericViewSet):

    permission_classes = [IsAuthenticated]
    filter_backends = (CodigoProcapiManifestacaoFilter,)
    _filter_codigo_procapi = None

    @method_decorator(never_cache)
    def list(self, request, *args, **kwargs):

        self._filter_codigo_procapi = self.request.query_params.get('codigo_procapi', None) or None

        manifestacao = Manifestacao.objects.filter(codigo_procapi=self._filter_codigo_procapi)

        if manifestacao.exists():
            procapi_atualizar_manifestacao.apply_async(kwargs={
                'id': manifestacao.first().id
            }, queue='sobdemanda')
            return JsonResponse({'sucesso': True})
        else:
            return JsonResponse({'sucesso': False})


class ProcapiSignalAvisoViewSet(GenericViewSet):

    permission_classes = [IsAuthenticated]
    filter_backends = (
        AvisoFilter,
        SistemaWebserviceFilter
    )
    _filter_numero_aviso = None
    _filter_sistema_webservice = None
    _filter_orgao_julgador = None

    @method_decorator(never_cache)
    def list(self, request, *args, **kwargs):

        self._filter_numero_aviso = self.request.query_params.get('numero_aviso', None) or None
        self._filter_sistema_webservice = self.request.query_params.get('sistema_webservice', None) or None
        self._filter_orgao_julgador = self.request.query_params.get('codigo_orgao_julgador', None) or None

        if self._filter_numero_aviso and self._filter_sistema_webservice:
            procapi_distribuir_aviso.apply_async(kwargs={
                'aviso_numero': self._filter_numero_aviso,
                'sistema_webservice': self._filter_sistema_webservice
            }, queue='sobdemanda')

            return JsonResponse({'sucesso': True})
        else:
            return JsonResponse({'sucesso': False})
