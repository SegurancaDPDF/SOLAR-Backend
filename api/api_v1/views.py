# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import json as simplejson
import base64
import requests
from datetime import datetime
from collections import OrderedDict
from constance import config
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from django.db.models import Count, F, Q, Value, IntegerField, CharField
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django_filters.rest_framework import DjangoFilterBackend
from django_celery_beat.models import PeriodicTask
from http.client import BadStatusLine
from rest_framework import generics, exceptions, status, mixins, views, filters
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework_extensions.mixins import DetailSerializerMixin, NestedViewSetMixin
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet, ViewSet

from api.api_v1.utils import restringir_qualificacao
from assistido.models import PessoaAssistida, DocumentoAssinado as DocumentoAssinadoAssistido, \
    Documento as DocumentoOriginalAssistido, Patrimonial, PatrimonialTipo, Situacao, TipoRenda
from assistido.serializers import (
    PessoaAssistidaSerializer,
    PessoaAderiuLunaChatbotSerializer,
    PatrimonialSerializer,
    PatrimonialTipoSerializer,
    SituacaoSerializer,
    TipoRendaSerializer
)
from atendimento.agendamento.utils import proximos_horarios_disponiveis
from atendimento.atendimento.filters import QualificacaoFilterBackend
from atendimento.atendimento.models import (
    Atendimento,
    Defensor as AtendimentoDefensor,
    Documento,
    FormaAtendimento,
    Pergunta,
    Encaminhamento,
    Pessoa,
    Tarefa,
    Arvore,
    Documento as DocumentoOriginalAtendimento,
    DocumentoAssinado as DocumentoAssinadoAtendimento,
    TipoColetividade,
    Qualificacao)
from atendimento.atendimento.serializers import (
    FormaAtendimentoSerializer,
    QualificacaoSerializer,
    QualificacaoDetailSerializer,
    TipoColetividadeSerializer,
    PerguntaSerializer,
    EncaminhamentoSerializer,
    ArquivarAtendimentoSerializer,
    DesarquivarAtendimentoSerializer
)
from atividade_extraordinaria.models import (
    AtividadeExtraordinaria
)
from contrib.filters import (
    DocumentoFilterBackend as ContribDocumentoFilterBackend,
    MunicipioFilterBackend,
    DefensoriaEtiquetaFilter,
    ServidorFilter
)
from contrib.models import (
    Area,
    Bairro,
    Cartorio,
    Comarca,
    Defensoria,
    Documento as ContribDocumento,
    Endereco,
    Estado,
    Etiqueta,
    DefensoriaEtiqueta,
    Municipio,
    Servidor,
    Telefone
)
from contrib.serializers import (
    AreaSerializer,
    BairroSerializer,
    CartorioSerializer,
    ComarcaSerializer,
    DocumentoSerializer as ContribDocumentoSerializer,
    EtiquetaSerializer,
    DefensoriaEtiquetaSerializer,
    MunicipioSerializer,
    ServidorSerializer
)
from contrib.services import dict_list_search
from core.exceptions import CoreBaseException
from core.models import Processo as CoreProcesso
from core.viewsets import AuditoriaModelViewSet
from defensor.models import Defensor
from evento.models import Categoria as CategoriaDeAgenda
from evento.serializers import CategoriaDeAgendaSerializer
from indeferimento.models import Indeferimento
from nucleo.nadep.models import EstabelecimentoPenal
from nucleo.nadep.serializers import EstabelecimentoPenalSerializer
from nucleo.nucleo.models import Resposta as FormularioResposta
from nucleo.nucleo.serializers import FormularioRespostaSerializer
from processo.processo.models import Processo, Manifestacao, ManifestacaoDocumento
from .filters import (
    AtendimentoDefensorFilterBackend,
    DocumentoFilterBackend,
    IndeferimentoFilterBackend,
    PessoaAssistidaFilterBackend,
    ProcessoFilterBackend,
)
from .paginators import AtendimentoResultsSetPagination, OnlyOnePerPagePaginator, StandardResultsSetPagination
from .serializers import (
    AnotacaoSerializer,
    AtendimentoHyperlinkedModelSerializer,
    AtendimentoDetailSerializer,
    CadastroAtendimentoInicialSerializer,
    CadastroAtendimentoRetornoSerializer,
    SalvarLiberarAgendamentoSerializer,
    DocumentoSerializer,
    EnderecoSerializer,
    EstadoSerializer,
    PessoaSerializer,
    PeriodicTaskSerializer,
    ProcessoSerializer,
    ProcessoAtendimentoSerializer,
    TarefaAtendimentoSerializer,
    TarefaAtendimentoDetailSerializer,
    TelefoneSerializer,
    IndeferimentoSerializer,
    IndeferimentoPrateleiraSerializer,
    AtividadeExtraordinariaSerializer,
    ManifestacaoProcessualSerializer,
    ManifestacaoProcessualDocumentoSerializer,
    ManifestacaoProcessualDocumentoBase64Serializer
)
from atendimento.atendimento.usecases import (
    arquivar_atendimento,
    desarquivar_atendimento
)
from .utils import (
    RE_CARACTERES_NUMERICOS,
    criar_agendamento,
    get_numero_atendimento_inicial,
    get_ultimo_atendimento,
)
from .permissions import EstaLotadoNoSetorDoFiltroPermission
from atendimento.atendimento.tasks import atendimento_cria_arvore


class AnotacaoViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = AtendimentoDefensor.objects.filter(
        tipo__in=[AtendimentoDefensor.TIPO_ANOTACAO, AtendimentoDefensor.TIPO_NOTIFICACAO]
    )
    serializer_class = AnotacaoSerializer
    lookup_field = 'numero'
    lookup_url_kwarg = 'numero'


class AreaViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    list:
    Retorna uma lista das áreas ativas.
    """
    queryset = Area.objects.filter(ativo=True)
    serializer_class = AreaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['penal']


# add cadastro/descadastro no chatbot via API
class AderirLunaChatBotViewSet(GenericViewSet):
    queryset = PessoaAssistida.objects.ativos()
    serializer_class = PessoaAderiuLunaChatbotSerializer

    def subscribe(self, request, *args, **kwargs):
        return self.update(request, True, args, kwargs)

    def unsubscribe(self, request, *args, **kwargs):
        return self.update(request, False, args, kwargs)

    def update(self, request, aderiu_luna_chatbot, *args, **kwargs):

        pessoa = self.get_object()
        pessoa.aderiu_luna_chatbot = aderiu_luna_chatbot
        pessoa.save()

        serializer = self.serializer_class(
            instance=pessoa,
            context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

##
# TODO: ORDENAR ESSE RETORNO PELA DATA DESC
##


class AgendamentoArvoreAPIView(APIView):
    """
    Obtém árvore de eventos do atendimento
    """

    def get(self, request, numero_inicial):

        resposta = []

        atendimento = AtendimentoDefensor.objects.filter(numero=numero_inicial, ativo=True, remarcado=None).first()

        if atendimento:

            arvore = Arvore.objects.filter(atendimento=atendimento.at_inicial, data_exclusao=None, ativo=True).first()

            if not arvore:
                arvore = atendimento_cria_arvore(atendimento.at_inicial.numero)

            resposta = simplejson.loads(arvore.conteudo)

        return Response(resposta, status=status.HTTP_200_OK)


# Viewset do django que define a lógica para criação de um novo agendamento 

class NovoAgendamentoViewSet(GenericViewSet):
    queryset = AtendimentoDefensor.objects.none()
    tipo = None

    def create(self, request, *args, **kwargs):

        commit = True if self.request.query_params.get('commit', 'true') == 'true' else False

        cad_serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )

        if cad_serializer.is_valid():

            data = cad_serializer.validated_data
            data['request'] = request
            data['usuario_criador'] = request.user
            data['commit'] = commit

            if 'pessoa_assistida_id' in data:
                data['pessoas_assistidas_ids'] = [data.pop('pessoa_assistida_id')]

            if len(data['pessoas_assistidas_ids']) == 0:
                raise exceptions.ValidationError(detail={'detail': 'Informe o ID de pelo menos um requerente'})

            if 'anotacao' not in data:
                data['anotacao'] = 'Agendado via {}'.format(request.user.get_full_name())

            if 'agenda_id' not in data:
                data['agenda_id'] = None

            if 'categoria_agenda' not in data:
                data['categoria_agenda'] = None

            if 'comarca_id' not in data:
                data['comarca_id'] = None

            if 'defensoria_id' not in data:
                data['defensoria_id'] = None

            if 'data_agendamento' not in data:
                data['data_agendamento'] = timezone.now()

            if 'processo_numero' not in data:
                data['processo_numero'] = None

            if self.tipo == AtendimentoDefensor.TIPO_RETORNO:
                data['qualificacao_id'] = None
                data['atendimento_numero'] = self.kwargs[self.lookup_field]
            else:
                data['atendimento_numero'] = None

            try:
                atendimento = criar_agendamento(**data)
            except ValidationError as e:
                raise exceptions.ValidationError(detail={'detail': str(e)})
            except ObjectDoesNotExist as e:
                raise exceptions.NotFound(detail=str(e))

            if commit:
                at_serializar = AtendimentoHyperlinkedModelSerializer(
                    instance=atendimento,
                    context={"request": request}
                )
                return Response(at_serializar.data, status=status.HTTP_200_OK)
            else:
                del data['usuario_criador']
                return Response({"detail": {'post': data}}, status=status.HTTP_400_BAD_REQUEST)

        else:

            return Response({"detail": cad_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# habilitar agendamento inicial / define permissões de acesso apenas para usuários autenticados.

class NovoAgendamentoInicialViewSet(NovoAgendamentoViewSet):
    permission_classes = [IsAuthenticated]
    tipo = AtendimentoDefensor.TIPO_INICIAL
    serializer_class = CadastroAtendimentoInicialSerializer


# agendamento de atendimento de retorno

class NovoAgendamentoRetornoViewSet(NovoAgendamentoViewSet):
    permission_classes = [IsAuthenticated]
    tipo = AtendimentoDefensor.TIPO_RETORNO
    serializer_class = CadastroAtendimentoRetornoSerializer
    lookup_field = 'numero'
    lookup_url_kwarg = 'numero'


class SalvarLiberarAgendamentoViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SalvarLiberarAgendamentoSerializer
    atendimento_id = None
    
    # recupera o número do atendimento
    def update(self, request, *args, **kwargs):
        try:
            atendimento_numero = kwargs['numero']
            atendimento = get_object_or_404(AtendimentoDefensor, numero=atendimento_numero, ativo=True)

            # Cria/atualiza atendimento da repceção somente se não tem agendamento ou agendado para hoje
            if atendimento.data_agendamento or atendimento.data_agendamento.date() == datetime.today():

                agora = datetime.now()

                atendimento_recepcao, created = Atendimento.objects.get_or_create(
                    origem=atendimento,
                    tipo=Atendimento.TIPO_RECEPCAO,
                    ativo=True
                )

                if not atendimento_recepcao.data_atendimento:
                    atendimento_recepcao.atendido_por = request.user.servidor
                    atendimento_recepcao.data_atendimento = agora

                atendimento_recepcao.modificado_por = request.user.servidor
                atendimento_recepcao.save()

                if hasattr(atendimento.at_inicial, 'arvore'):
                    atendimento.at_inicial.arvore.ativo = False
                    atendimento.at_inicial.arvore.save()

            return JsonResponse({'sucesso': True})

        except Exception as e:

            return JsonResponse({'erro': e})


# lógica para retornar os horários disponíveis para agendamento de um atendimento
class HorarioDisponivelParaAgendamentoAoAtendimentoAPIView(GenericViewSet):
    quantidade_padrao_de_horarios = 4
    queryset = AtendimentoDefensor.objects.none()

    def retrieve(self, request, numero, format=None, *args, **kwargs):
        qnt = self.request.query_params.get('qnt', self.quantidade_padrao_de_horarios) or self.quantidade_padrao_de_horarios  # noqa: E501
        dias_diferentes = self.request.query_params.get('diasdiferentes', None) or None
        forma_atendimento = self.request.query_params.get('forma_atendimento', None) or None

        numero = numero if numero else ''
        somente_numeros = RE_CARACTERES_NUMERICOS.sub('', numero)
        pode_marcar_retorno = True
        if not numero or not somente_numeros:
            return Response({"detail": "Não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        somente_numeros = int(somente_numeros)
        if qnt > 50:
            qnt = 50

        # obtem o numero do atendimento inicial, se encontrar
        # se nao, retorna None
        numero_at_inicial = get_numero_atendimento_inicial(numero)
        if not numero_at_inicial:
            return Response({"detail": "Não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # obtem o ultimo atendimento a partir do atendimento inicial
        ultimo_atendimento = get_ultimo_atendimento(numero_at_inicial)
        if not ultimo_atendimento:
            return Response({"detail": "Não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        ultima_parte_processual = None
        if not ultimo_atendimento.data_atendimento:
            # posso remarcar atendimento
            # para remarcar tenho que:
            # * marcar retorno
            # * preencher campo 'remarcado' com id do retorno marcado
            pode_marcar_retorno = False

        else:

            # obtém a última parte processual cadastrada após o último atendimento
            ultima_parte_processual = ultimo_atendimento.processo_partes.filter(
                data_cadastro__gte=ultimo_atendimento.data_atendimento,
                processo__tipo__in=[Processo.TIPO_FISICO, Processo.TIPO_EPROC],
                processo__pre_cadastro=False,
                defensoria__ativo=True
            ).order_by(
                '-data_cadastro'
            ).first()

        defensoria = None
        defensor = None
        categoria_agenda = None

        # usa defensoria da parte processual como base se for diferente que a do último atendimento
        if ultima_parte_processual and ultima_parte_processual.defensoria_id != ultimo_atendimento.defensoria_id:
            defensoria = ultima_parte_processual.defensoria
            # se nova defensoria possui várias categorias de agenda, cancela operação
            if defensoria.categorias_de_agendas.count() != 1:
                pode_marcar_retorno = False
        else:
            defensoria = ultimo_atendimento.defensoria
            defensor = ultimo_atendimento.defensor
            categoria_agenda = ultimo_atendimento.agenda_id

        horarios = []

        dt_ultimo_agendamento_nao_atendido = None
        if pode_marcar_retorno:
            horarios = proximos_horarios_disponiveis(
                defensoria=defensoria,
                defensor=defensor,
                categoria_agenda=categoria_agenda,
                forma_atendimento=forma_atendimento,
                quantidade=qnt,
                dias_diferentes=True if dias_diferentes == 'true' else False
            )
        else:
            dt_ultimo_agendamento_nao_atendido = ultimo_atendimento.data_agendamento

        dados_retorno = {
            'horarios': horarios,
            'ultimo_atendimento': ultimo_atendimento.numero,
            'ultima_parte_processual': ultima_parte_processual.id if ultima_parte_processual else None,
            'defensoria': defensoria.id if defensoria else None,
            'atendimento_pesquisado': somente_numeros,
            'atendimento_inicial': numero_at_inicial,
            'dt_ultimo_agendamento_nao_atendido': dt_ultimo_agendamento_nao_atendido,
            'pode_marcar_retorno': pode_marcar_retorno
        }

        return Response(dados_retorno)


# lógica para retornar os horários disponíveis para agendamento de uma defensoria específica

class HorarioDisponivelParaAgendamentoDefensoriaAPIView(GenericViewSet):
    quantidade_padrao_de_horarios = 4
    queryset = AtendimentoDefensor.objects.none()

    # obtenção dos horários disponíveis para agendamento.
    def retrieve(self, request, id, format=None, *args, **kwargs):

        qnt = self.request.query_params.get('qnt', self.quantidade_padrao_de_horarios) or self.quantidade_padrao_de_horarios  # noqa: E501
        dias_diferentes = self.request.query_params.get('diasdiferentes', None) or None
        categoria_agenda = self.request.query_params.get('categoria_agenda', None) or None
        forma_atendimento = self.request.query_params.get('forma_atendimento', None) or None

        defensoria = Defensoria.objects.get(id=id)

        horarios = proximos_horarios_disponiveis(
            defensoria=defensoria,
            quantidade=int(qnt),
            dias_diferentes=True if dias_diferentes == 'true' else False,
            categoria_agenda=int(categoria_agenda) if categoria_agenda else None,
            forma_atendimento=forma_atendimento,
        )

        dados_retorno = OrderedDict()
        dados_retorno['count'] = len(horarios)
        dados_retorno['next'] = None
        dados_retorno['previous'] = None
        dados_retorno['results'] = horarios

        return Response(dados_retorno)


# listar os atendimentos
class AtendimentoList(generics.ListAPIView):
    queryset = AtendimentoDefensor.objects.only(
        'id',
        'numero',
        'inicial_id'
    ).filter(
        Q(ativo=True),
        ~Q(numero=None)
    ).order_by()

    serializer_class = AtendimentoHyperlinkedModelSerializer

    pagination_class = OnlyOnePerPagePaginator
    lookup_field = 'numero'
    lookup_url_kwarg = 'numero'

    def get_serializer(self, *args, **kwargs):
        return super(AtendimentoList, self).get_serializer(*args, **kwargs)

    def get_queryset(self):
        queryset = super(AtendimentoList, self).get_queryset()
        # queryset = queryset.filter(ativo=True)
        q = Q()

        numero = self.request.query_params.get('numero', None) or None
        # apelido = self.request.query_params.get('apelido', None)
        # cpf = self.request.query_params.get('cpf', None)
        # nome_social = self.request.query_params.get('nome_social', None)
        # data_nascimento = self.request.query_params.get('data_nascimento', None)

        if numero is not None:
            q &= Q(numero=numero)
        return queryset.filter(q)

    def filter_queryset(self, queryset):
        queryset = queryset.only('pk', 'numero', 'inicial')
        return super(AtendimentoList, self).filter_queryset(queryset)


class AtendimentoTipoColetividadeList(generics.ListAPIView):
    permission_classes = [DjangoModelPermissions]
    queryset = TipoColetividade.objects.ativos().vigentes()
    serializer_class = TipoColetividadeSerializer


# ordena as pessoas por uma ordem não especificada
class PessoaList(generics.ListAPIView):
    queryset = Pessoa.objects.filter(Q(ativo=True)).order_by()
    serializer_class = PessoaSerializer


# pré-carregar os relacionamentos da pessoa com o atendimento.
class PessoaDetail(generics.ListAPIView):
    queryset = Pessoa.objects.select_related('atendimento__numero').filter(Q(ativo=True)).order_by()
    serializer_class = PessoaSerializer


class PessoaAderiuLunaChatbotViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = PessoaAssistida
    serializer_class = PessoaAderiuLunaChatbotSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'id'


class PessoaAssistidaList(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = PessoaAssistida.objects.ativos().order_by()
    serializer_class = PessoaAssistidaSerializer


class PessoaAssistida2List(generics.ListAPIView):
    queryset = PessoaAssistida.objects.ativos().order_by()
    serializer_class = PessoaAssistidaSerializer

    def get_queryset(self):
        qs = super(PessoaAssistida2List, self).get_queryset()
        numero_atendimento = self.kwargs['numero']
        q = Q(atendimentos__atendimento__numero=numero_atendimento)
        return qs.filter(q)


class PessoasAssistidasPorListaIdsList(generics.ListAPIView):
    queryset = PessoaAssistida.objects.ativos().order_by()
    serializer_class = PessoaAssistidaSerializer

    def check_permissions(self, request):

        if request.user.is_anonymous:
            raise PermissionDenied("Usuário não está logado")
            return False

        return True

    def get_queryset(self):
        try:
            qs = super(PessoasAssistidasPorListaIdsList, self).get_queryset()
            ids_assistidos = self.request.query_params.get('ids_assistidos', None) or None
            ids_assistidos_object = simplejson.loads(ids_assistidos)
            q = Q(id__in=ids_assistidos_object)
            qs = qs.filter(q)
            return qs
        except Exception:
            raise


class PessoaAssistidaDetail(generics.ListAPIView):
    queryset = PessoaAssistida.objects.ativos().order_by()
    serializer_class = PatrimonialTipoSerializer


class PessoaAssistidaPatrimonioList(generics.ListAPIView):
    permission_classes = [DjangoModelPermissions]
    queryset = Patrimonial.objects.ativos().filter(tipo__desativado_em=None).order_by('tipo__grupo', 'tipo__id', 'id')
    serializer_class = PatrimonialSerializer

    def get_queryset(self):
        qs = super(PessoaAssistidaPatrimonioList, self).get_queryset()
        qs = qs.filter(pessoa_id=self.kwargs.get('pk'))
        return qs


class PessoaAssistidaPatrimonioTipoList(generics.ListAPIView):
    permission_classes = [DjangoModelPermissions]
    queryset = PatrimonialTipo.objects.ativos().order_by('grupo', 'id')
    serializer_class = PatrimonialTipoSerializer


class TelefoneViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    """
    list:
    Retorna uma lista dos telefones ativos.

    retrieve:
    Retorna detalhes do telefone informado.

    update:
    Atualiza informações do telefone informado.

    partial_update:
    Atualiza informações do telefone informado.
    """

    queryset = Telefone.objects.filter().order_by()
    serializer_class = TelefoneSerializer


class EnderecoList(generics.ListAPIView):
    queryset = Endereco.objects.filter().order_by()
    serializer_class = EnderecoSerializer


class EnderecoDetail(generics.ListAPIView):
    queryset = Endereco.objects.filter().order_by()
    serializer_class = EnderecoSerializer


class BairroViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):  # noqa: E501
    """
    list:
    Retorna uma lista dos bairros ativos.

    retrieve:
    Retorna detalhes do bairro informado.

    create:
    Cria um novo bairro.

    update:
    Atualiza informações do bairro informado.

    partial_update:
    Atualiza informações do bairro informado.
    """

    permission_classes = [DjangoModelPermissions]
    queryset = Bairro.objects.ativos()
    serializer_class = BairroSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['nome', 'municipio']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.distinct('municipio__nome', 'nome_norm')


class MunicipioList(generics.ListAPIView):
    queryset = Municipio.objects.all()
    serializer_class = MunicipioSerializer
    filter_backends = (MunicipioFilterBackend, )
    permission_classes = [DjangoModelPermissions]

    def get_queryset(self):

        nome = self.request.query_params.get('nome', None) or None
        estado = self.request.query_params.get('estado', None) or None

        qs = super(MunicipioList, self).get_queryset()

        # filtro nome
        if nome:
            qs = qs.filter(nome__istartswith=nome)

        # filtro estado
        if estado:
            qs = qs.filter(estado=estado)

        return qs


class MunicipioDetail(generics.ListAPIView):
    queryset = Municipio.objects.filter().order_by()
    serializer_class = MunicipioSerializer
    permission_classes = [DjangoModelPermissions]


class EstadoViewSet(ReadOnlyModelViewSet):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['nome', 'uf']
    permission_classes = [DjangoModelPermissions]


class ComarcaViewSet(ReadOnlyModelViewSet):
    queryset = Comarca.objects.all()
    serializer_class = ComarcaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['coordenadoria', 'ativo']
    ordering_fields = ['nome', 'coordenadoria']
    permission_classes = [DjangoModelPermissions]


class GeraTokenChatEdefensor(views.APIView):
    """
    Gera o token para acessar o chat e-Defensor.

    * Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        """
        Gera o token para acessar o chat e-Defensor.
        """

        if request.user.is_anonymous:
            return JsonResponse([])

        url_base = settings.EDEFENSOR_CHAT_WEBSERVICE_TOKEN_URL+"/auth/"
        post_data = {
            "cpf":  settings.EDEFENSOR_CHAT_WEBSERVICE_TOKEN_USERNAME,
            "password": settings.EDEFENSOR_CHAT_WEBSERVICE_TOKEN_PASSWORD,
        }

        # Validação dos campos
        if url_base == '':
            return JsonResponse({'success': False, 'message': 'URL de obtenção do token não definida.'}, safe=False)

        if post_data["cpf"] == '':
            return JsonResponse({'success': False, 'message': 'Usuario do token não definido.'}, safe=False)

        if post_data["password"] == '':
            return JsonResponse({'success': False, 'message': 'Senha do token não definido.'}, safe=False)

        post_headers = {
            'appSystem': settings.EDEFENSOR_CHAT_WEBSERVICE_APP_SYSTEM
        }

        if settings.VERIFY_CERTFILE != '':
            path_to_certfile = False if settings.VERIFY_CERTFILE == 'False' else settings.VERIFY_CERTFILE
            response = requests.post(url_base, data=post_data, headers=post_headers, verify=path_to_certfile)
        else:
            response = requests.post(url_base, data=post_data, headers=post_headers)

        token = response.content.decode('utf-8')

        return JsonResponse(token, safe=False)


class RenovaTokenChatEdefensor(views.APIView):
    """
    Renova o token para acessar o chat e-Defensor.

    * Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        """
        Renova o token para acessar o chat e-Defensor.
        """

        if request.user.is_anonymous:
            return JsonResponse([])

        url_base = settings.EDEFENSOR_CHAT_WEBSERVICE_TOKEN_URL
        post_data = {
            "refreshToken":  request.POST.get('refresh_token'),
        }

        # Validação dos campos
        if url_base == '':
            return JsonResponse({'success': False, 'message': 'URL de obtenção do token não definida.'}, safe=False)

        post_headers = {
            'appSystem': settings.EDEFENSOR_CHAT_WEBSERVICE_APP_SYSTEM
        }

        response = None
        token = None

        try:
            if settings.VERIFY_CERTFILE != '':
                path_to_certfile = False if settings.VERIFY_CERTFILE == 'False' else settings.VERIFY_CERTFILE
                response = requests.post(url_base, data=post_data, headers=post_headers, verify=path_to_certfile)
            else:
                response = requests.post(url_base, data=post_data, headers=post_headers)
            token = response.content.decode('utf-8')
        except BadStatusLine:
            return JsonResponse({
                'success': 'false',
                'message': 'Deu erro de BadStatusLine, provavelmente o servidor remoto responde com um código de status que python não consegue entender.'  # noqa: E501
            }, safe=False)

        return JsonResponse(token, safe=False)


class PossiveisConversasChat(GenericViewSet):

    authentication_classes = [SessionAuthentication]

    def check_permissions(self, request):

        if request.user.is_anonymous:
            raise PermissionDenied("Usuário não está logado")
            return False

        return True

    def retrieve(self, request, format=None, *args, **kwargs):

        possiveis_conversas = request.user.servidor.possiveis_conversas_chat()

        return JsonResponse(possiveis_conversas, safe=False)


class AtendimentosComDocumentoPendente(GenericViewSet):

    authentication_classes = [SessionAuthentication]

    queryset = AtendimentoDefensor.objects.ativos()

    def check_permissions(self, request):

        if request.user.is_anonymous:
            raise PermissionDenied("Usuário não está logado")

        return True

    def retrieve(self, request, defensor_id, format=None, *args, **kwargs):

        assistido_id = self.request.query_params.get('assistido_id', None) or None

        # Cria o array vazio dos números de atendimentos
        ats_com_documento_pendente = []

        try:

            defensor = Defensor.objects.get(id=defensor_id)
            assistido = PessoaAssistida.objects.get(id=assistido_id)

            # Obtém documentos sem arquivo de atendimentos do defensor informado
            documentos_pendentes = Documento.objects.filter(atendimento__defensor__defensor=defensor, arquivo="")

            # Itera sobre os documentos pendentes
            for dp in documentos_pendentes:

                # Se o atendimento já consta na lista
                if dict_list_search(ats_com_documento_pendente, "numero", dp.atendimento.numero):
                    continue  # Pula para o proóximo documento

                # Pega o atendimento
                at = dp.atendimento

                # Itera sobre os requerentes do atendimento
                for rq in at.requerentes:
                    # Se o requerente é o que procuramos
                    if rq.pessoa.id == assistido.id:
                        # Pega o número do atendimento
                        numero = dp.atendimento.numero
                        # Se o número do atendimento não existia na lista
                        if not dict_list_search(ats_com_documento_pendente, "numero", at.numero):
                            # Pega o documento pendente principal
                            doc_rel = at.documentos_pendentes.filter(ativo=True).order_by('-id')
                            # Se na verdade, não tem nenhum documento pendente ativo neste atendimento
                            if doc_rel.count() == 0:
                                # Para de iterar sobre os assistidos deste atendimento
                                break
                            doc_rel = doc_rel.first()
                            # Cria o objeto a ser associado
                            objeto = {
                                'numero': numero,
                                'tit_doc': doc_rel.nome,
                                'id_doc': doc_rel.id
                            }
                            # Adiciona o objeto
                            ats_com_documento_pendente.append(objeto)
                            # Para de iterar sobre os assistidos deste atendimento
                            break
        except Defensor.DoesNotExist:
            """ qs = self.queryset.none() """
            return JsonResponse({
                'erro': 'Defensor não existe com id '+defensor_id
            }, safe=False)
        except Exception:
            raise

        return JsonResponse(ats_com_documento_pendente, safe=False)


class AtendimentoViewSet(NestedViewSetMixin, DetailSerializerMixin, ReadOnlyModelViewSet):

    filter_backends = (
        AtendimentoDefensorFilterBackend,
    )

    queryset = AtendimentoDefensor.objects.prefetch_related(
        'partes'
    ).filter(
        ~Q(numero=None)
    ).order_by().order_by('-data_agendamento')

    queryset_detail = AtendimentoDefensor.objects.prefetch_related(
        'partes'
    ).filter(
        ~Q(numero=None)
    ).order_by().order_by('-data_agendamento')  # noqa: E501

    serializer_class = AtendimentoHyperlinkedModelSerializer
    serializer_detail_class = AtendimentoDetailSerializer

    pagination_class = AtendimentoResultsSetPagination
    lookup_field = 'numero'
    lookup_url_kwarg = 'numero'

    def get_serializer(self, *args, **kwargs):
        return super(AtendimentoViewSet, self).get_serializer(*args, **kwargs)

    def get_queryset(self):
        queryset = super(AtendimentoViewSet, self).get_queryset()
        q = Q()

        numero = self.request.query_params.get('numero', None) or None
        pessoa_parte = self.request.query_params.get('partes__pessoa', None) or None

        if 'soagendamentos' in self.request.query_params:
            q &= Q(data_atendimento=None)
            if 'soagendamentosfuturos' in self.request.query_params:
                datahora_agora = timezone.now()
                q &= Q(data_atendimento_gte=datahora_agora)

        if 'incluirprecadastro' not in self.request.query_params and not self.kwargs.get('numero'):
            q &= ~Q(tipo=AtendimentoDefensor.TIPO_LIGACAO)

        data_inicial = self.request.query_params.get('data_inicial', None) or None
        data_final = self.request.query_params.get('data_final', None) or None
        defensoria_id = self.request.query_params.get('defensoria_id', None) or None

        if data_inicial:
            q &= Q(data_agendamento__date__gte=data_inicial)

        if data_final:
            q &= Q(data_agendamento__date__lte=data_final)

        if defensoria_id:
            q &= Q(defensoria_id=defensoria_id)

        ativo = self.request.query_params.get('ativo', None) or None

        if ativo is not None:
            q &= Q(ativo=(ativo == 'true'))

        if numero is not None:
            q &= Q(numero=numero)
        if pessoa_parte is not None:
            q &= Q(partes__pessoa=pessoa_parte)
        return queryset.filter(q)

    def filter_queryset(self, queryset):
        # queryset = queryset.only('pk', 'numero', 'inicial')
        queryset = queryset
        return super(AtendimentoViewSet, self).filter_queryset(queryset)

    @transaction.atomic
    @action(detail=True, methods=("post",), permission_classes=(IsAuthenticated,))
    def arquivar(self, request, numero=None):
        serializer = ArquivarAtendimentoSerializer(data=request.data,
                                                   context={'request': request})
        serializer.is_valid(raise_exception=True)
        try:
            atendimento_arquivado = arquivar_atendimento(
                request.user,
                numero,
                serializer.validated_data
            )
            response_data = ArquivarAtendimentoSerializer(atendimento_arquivado).data
            return JsonResponse(response_data, status=status.HTTP_201_CREATED)
        except CoreBaseException as exception:
            return JsonResponse({"erro": exception.message}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=("post",), permission_classes=(IsAuthenticated,))
    @transaction.atomic
    def desarquivar(self, request, numero=None):
        serializer = DesarquivarAtendimentoSerializer(
                        data=request.data,
                        context={'request': request})
        serializer.is_valid(raise_exception=True)
        try:
            atendimento_desarquivado = desarquivar_atendimento(
                request.user,
                numero,
                serializer.validated_data
            )
            response_data = DesarquivarAtendimentoSerializer(atendimento_desarquivado).data
            return JsonResponse(response_data, status=status.HTTP_201_CREATED)
        except CoreBaseException as exception:
            return JsonResponse({"erro": exception.message}, status=status.HTTP_403_FORBIDDEN)


class ProcessosAtendimentoViewSet(mixins.ListModelMixin, GenericViewSet):
    lookup_field = 'numero'
    lookup_url_kwarg = 'numero'
    pagination_class = StandardResultsSetPagination
    filter_backends = (ProcessoFilterBackend, )
    serializer_class = ProcessoAtendimentoSerializer
    atendimento_instance = None

    def list(self, request, numero=None, *args, **kwargs):
        self.atendimento_instance = AtendimentoDefensor.objects.filter(numero=numero).first()

        ret = super(ProcessosAtendimentoViewSet, self).list(request, *args, **kwargs)
        if not self.atendimento_instance:
            ret.status_code = status.HTTP_404_NOT_FOUND
            ret.data['detail'] = "Atendimento não encontrado"
        return ret

    def get_queryset(self):
        if self.atendimento_instance:
            processos_queryset = self.atendimento_instance.get_processos().filter(
                data_exclusao=None,
                pre_cadastro=False
            ).order_by().order_by('-ultima_modificacao')
        else:
            processos_queryset = Processo.objects.none()
        return processos_queryset


class DocumentosAtendimentoViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):  # noqa: E501
    permission_classes = [DjangoModelPermissions]
    filter_backends = (
        DocumentoFilterBackend,
    )

    queryset = Documento.objects.ativos()
    queryset_detail = Documento.objects.ativos()

    serializer_class = DocumentoSerializer
    serializer_detail_class = DocumentoSerializer

    def get_queryset(self):

        atendimento_numero = self.kwargs.get('parent_lookup_atendimento__numero')
        pendentes = self.request.query_params.get('pendentes', None) or None

        # obtém lista de documentos do atendimento

        try:
            atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)
        except AtendimentoDefensor.DoesNotExist:
            qs = self.queryset.none()
        else:
            qs = atendimento.documentos

        # documentos pendentes
        if pendentes == 'true':
            qs = qs.pendentes()
        elif pendentes == 'false':
            qs = qs.nao_pendentes()

        return qs


class TarefasAtendimentoViewSet(NestedViewSetMixin, DetailSerializerMixin, ReadOnlyModelViewSet):
    permission_classes = [DjangoModelPermissions]

    queryset = Tarefa.objects.ativos().order_by(
        '-data_finalizado',
        '-status',
        'prioridade',
        'data_inicial',
        'data_final',
        'id'
    )
    serializer_class = TarefaAtendimentoSerializer
    serializer_detail_class = TarefaAtendimentoDetailSerializer

    # todo: encontrar forma de usar a lista definida em "parents_query_lookups" na definição da url
    def get_queryset(self):

        atendimento_numero = self.kwargs.get('parent_lookup_atendimento__numero')

        if atendimento_numero:
            return self.queryset.filter(
                Q(atendimento__numero=atendimento_numero) |
                Q(atendimento__inicial__numero=atendimento_numero)
            )
        else:
            return self.queryset.none()


class PessoaAssistidaViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):  # noqa: E501
    queryset = PessoaAssistida.objects.ativos().order_by()
    queryset_detail = PessoaAssistida.objects.ativos().order_by()
    filter_backends = (
        PessoaAssistidaFilterBackend,
    )
    serializer_class = PessoaAssistidaSerializer
    serializer_detail_class = PessoaAssistidaSerializer

    pagination_class = AtendimentoResultsSetPagination

    def get_queryset(self):
        queryset = super(PessoaAssistidaViewSet, self).get_queryset()
        q = Q()
        nome = self.request.query_params.get('nome', None) or None
        apelido = self.request.query_params.get('apelido', None) or None
        cpf = self.request.query_params.get('cpf', None) or None
        nome_social = self.request.query_params.get('nome_social', None) or None
        data_nascimento = self.request.query_params.get('data_nascimento', None) or None

        if nome is not None and nome:
            q &= Q(nome__icontains=nome)
        if apelido is not None and apelido:
            q &= Q(apelido__icontains=apelido)
        if cpf is not None and cpf:
            q &= Q(cpf=cpf)
        if nome_social is not None and nome_social:
            q &= Q(nome_social__icontains=nome_social)
        if data_nascimento is not None and data_nascimento:
            dt_nascimento = parse_date(data_nascimento)
            q &= Q(data_nascimento=dt_nascimento)

        return queryset.filter(q)


class ReadOnlyAtendimentosPessoaAssistida(ReadOnlyModelViewSet):
    filter_backends = (
        AtendimentoDefensorFilterBackend,
    )
    queryset = AtendimentoDefensor.objects.prefetch_related('partes').filter(
        Q(remarcado=None),
        ~Q(numero=None),
        tipo__in=[
            AtendimentoDefensor.TIPO_LIGACAO,
            AtendimentoDefensor.TIPO_INICIAL,
            AtendimentoDefensor.TIPO_RETORNO,
            AtendimentoDefensor.TIPO_ENCAMINHAMENTO,
            AtendimentoDefensor.TIPO_ANOTACAO
        ]
    ).order_by().order_by('-data_agendamento').only(
        'id',
        'numero',
        'inicial',
        'defensor',
        'substituto',
        'defensoria',
        'qualificacao',
        'data_agendamento',
    )
    serializer_class = AtendimentoHyperlinkedModelSerializer

    pagination_class = AtendimentoResultsSetPagination
    lookup_field = 'numero'
    lookup_url_kwarg = 'numero'

    def get_serializer(self, *args, **kwargs):
        return super(ReadOnlyAtendimentosPessoaAssistida, self).get_serializer(*args, **kwargs)

    def get_queryset(self):
        queryset = super(ReadOnlyAtendimentosPessoaAssistida, self).get_queryset()

        id_pessoa_assistida = self.kwargs.get('parent_lookup_partes__pessoa')

        # filtro para mostrar apenas atendimentos onde a pessoa é requerente (0) ou requerido (1)
        parte_tipo = self.request.query_params.get('partes__tipo', None) or None

        q = Q(partes__pessoa_id=id_pessoa_assistida)
        q &= Q(partes__ativo=True)

        if parte_tipo is not None:
            q &= Q(partes__tipo=parte_tipo)

        ids_iniciais = AtendimentoDefensor.objects.filter(q).values_list('id', flat=True)

        queryset = queryset.filter(Q(inicial_id__in=ids_iniciais) | Q(id__in=ids_iniciais))

        numero = self.request.query_params.get('numero', None) or None
        pessoa_parte = self.request.query_params.get('partes__pessoa', None) or None

        q = Q()
        if 'soagendamentos' in self.request.query_params:
            q &= Q(data_atendimento=None)
            if 'soagendamentosfuturos' in self.request.query_params:
                datahora_agora = timezone.now()
                q &= Q(data_atendimento_gte=datahora_agora)

        if 'incluirprecadastro' not in self.request.query_params and not self.kwargs.get('numero'):
            q &= ~Q(tipo=AtendimentoDefensor.TIPO_LIGACAO)

        if 'incluiranotacao' not in self.request.query_params and not self.kwargs.get('numero'):
            q &= ~Q(tipo=AtendimentoDefensor.TIPO_ANOTACAO)

        ativo = self.request.query_params.get('ativo', None) or None

        if ativo is not None:
            q &= Q(ativo=(ativo == 'true'))

        if numero is not None:
            q &= Q(numero=numero)
        if pessoa_parte is not None:
            q &= Q(partes__pessoa=pessoa_parte)

        return queryset.filter(q)


class ProcessoComAtualizacaoPendentesReadOnlyViewSet(ReadOnlyModelViewSet):
    queryset = Processo.objects.filter(
            ativo=True,
            atualizando=False,
            atualizado=False,
            tipo=Processo.TIPO_EPROC
        )

    serializer_class = ProcessoSerializer
    pagination_class = AtendimentoResultsSetPagination
    lookup_field = 'numero_puro'
    lookup_url_kwarg = 'numero_puro'


class IndeferimentoList(generics.ListAPIView):
    permission_classes = (EstaLotadoNoSetorDoFiltroPermission,)
    serializer_class = IndeferimentoSerializer
    filter_backends = (IndeferimentoFilterBackend,)
    filterset_fields = ('resultado', 'tipo_baixa')

    def get_queryset(self):

        setor = self.request.query_params.get('setor', None) or None
        prateleira = self.request.query_params.get('prateleira', None) or None
        classe = self.request.query_params.get('classe', None) or None

        queryset = Indeferimento.objects.select_related(
            'processo__classe',
            'processo__setor_criacao',
            'processo__setor_atual',
            'processo__setor_encaminhado',
            'defensor',
            'pessoa',
        ).ativos().exclude(
            processo__situacao=CoreProcesso.SITUACAO_PETICIONAMENTO
        ).annotate_prateleiras(
            setor=setor
        )

        if prateleira is not None:
            queryset = queryset.filter(
                prateleira=prateleira
            )

        if classe is not None:
            queryset = queryset.filter(
                processo__classe=classe
            )

        queryset = queryset.order_by('processo__cadastrado_em')

        return queryset


class IndeferimentoPrateleiraList(generics.ListAPIView):
    permission_classes = (EstaLotadoNoSetorDoFiltroPermission,)
    serializer_class = IndeferimentoPrateleiraSerializer
    filter_backends = (IndeferimentoFilterBackend,)
    filterset_fields = ('resultado', 'tipo_baixa')

    def get_queryset(self):

        setor = Defensoria.objects.get(id=self.request.query_params.get('setor'))
        prateleira = self.request.query_params.get('prateleira', None) or None

        queryset = Indeferimento.objects.ativos().annotate_prateleiras(
            setor=setor
        )

        if prateleira:
            queryset = queryset.annotate(
                classe=F('processo__classe_id'),
                classe_nome=F('processo__classe__nome'),
                classe_tipo=F('processo__classe__tipo'),
            ).order_by(
                'prateleira',
                'classe_tipo',
                'classe_nome',
            )
        else:
            queryset = queryset.annotate(
                classe=Value(None, IntegerField()),
                classe_nome=Value(None, CharField()),
                classe_tipo=Value(None, IntegerField()),
            ).order_by(
                'prateleira',
            )

        queryset = queryset.values(
            'prateleira',
            'classe',
            'classe_nome',
        ).annotate(
            total=Count('id')
        )

        # remove processos em peticionamento e baixados (se setor não puder baixar)
        if setor.nucleo.indeferimento_pode_registrar_baixa:
            queryset = queryset.exclude(processo__situacao=CoreProcesso.SITUACAO_PETICIONAMENTO)
        else:
            queryset = queryset.exclude(processo__situacao__in=[
                CoreProcesso.SITUACAO_PETICIONAMENTO,
                CoreProcesso.SITUACAO_BAIXADO
            ])

        return queryset

    def filter_queryset(self, queryset):

        queryset = super(IndeferimentoPrateleiraList, self).filter_queryset(queryset)

        prateleira = self.request.query_params.get('prateleira', None) or None

        if prateleira is None:
            queryset = queryset.filter(
                prateleira__isnull=False
            )
        else:
            queryset = queryset.filter(
                prateleira=prateleira
            )

        return queryset


class AtividadeExtraordinariaViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = AtividadeExtraordinaria.objects.filter().order_by()
    serializer_class = AtividadeExtraordinariaSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'id'


class PeriodicTaskViewSet(ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = PeriodicTask.objects.filter(crontab__isnull=False)
    serializer_class = PeriodicTaskSerializer


class SettingViewSet(ViewSet):
    # https://stackoverflow.com/questions/51360970/how-to-expose-django-constance-settings-via-django-rest-framework
    permission_classes = (IsAdminUser,)

    def create(self, request, format=None):

        for key, options in getattr(settings, 'CONSTANCE_CONFIG', {}).items():
            if key in request.data:
                setattr(config, key, request.data[key])

        self.salvar_no_storage()

        return self.list(request, format)

    def salvar_no_storage(self):
        """
        Salva configurações do constance no storage
        """

        data = {}
        for key, _ in getattr(settings, 'CONSTANCE_CONFIG', {}).items():
            data[key] = getattr(config, key)

        arquivo = 'constance.json'

        if default_storage.exists(arquivo):
            default_storage.delete(arquivo)

        conteudo = simplejson.dumps(data, indent=4)
        arquivo = default_storage.save(arquivo, ContentFile(conteudo.encode()))

    @action(methods=['get'], detail=False, permission_classes=[IsAdminUser], url_path='recuperar', url_name='recuperar')
    def recuperar_do_storage(self, request, format=None):
        """
        Recupera configurações do constance salvas no storage
        """

        arquivo = 'constance.json'

        if default_storage.exists(arquivo):
            conteudo = default_storage.open(arquivo)
            json_object = simplejson.load(conteudo)

            for key, _ in getattr(settings, 'CONSTANCE_CONFIG', {}).items():
                if key in json_object:
                    setattr(config, key, json_object[key])
        else:
            raise exceptions.NotFound()

        return self.list(request, format)

    def list(self, request, format=None):

        data = []
        for key, options in getattr(settings, 'CONSTANCE_CONFIG', {}).items():
            data.append({
                'key': key,
                'value': getattr(config, key),
                'default': options[0],
                'help_text': options[1]
            })

        result = OrderedDict()
        result['count'] = len(data)
        result['next'] = None
        result['previous'] = None
        result['results'] = data

        return Response(data=result)


class ManifestacaoProcessualViewSet(NestedViewSetMixin, DetailSerializerMixin, ReadOnlyModelViewSet):

    permission_classes = [IsAuthenticated]

    queryset = Manifestacao.objects.all()
    serializer_class = ManifestacaoProcessualSerializer
    serializer_detail_class = ManifestacaoProcessualSerializer


class ManifestacaoProcessualDocumentosViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):  # noqa: E501

    permission_classes = [IsAuthenticated]
    queryset = ManifestacaoDocumento.objects.all()

    def get_queryset(self):

        manifestacao_id = self.kwargs.get('parent_lookup_manifestacao_id')

        qs = super().get_queryset().filter(manifestacao_id=manifestacao_id)

        return qs

    def get_serializer_class(self):
        if self.request.GET.get('incluir_conteudo_em_base64'):
            return ManifestacaoProcessualDocumentoBase64Serializer
        return ManifestacaoProcessualDocumentoSerializer

    def create(self, request, *args, **kwargs):

        documento = ManifestacaoDocumento.objects.filter(
            manifestacao=request.data['manifestacao'],
            origem_id=request.data['origem_id'],
            origem=request.data['origem'],
        ).first()

        if documento:

            if not documento.ativo:
                documento.reativar(request.user)

            serializer = self.get_serializer_class()(documento)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return super().create(request, *args, **kwargs)

    #  implementação personalizada para atualizar `ManifestacaoProcessual`.
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        manifestacao_processual = self.get_object()
        if 'documento_assinado' in request.data:
            arquivo_temporario_em_memoria_do_base_64 = ContentFile(base64.b64decode(request.data.get('documento_assinado')))  # noqa: E501
            arquivo_temporario_em_memoria_do_base_64.name = 'nomealeatorio.p7s'
            if manifestacao_processual.origem == ManifestacaoDocumento.ORIGEM_PESSOA:
                documento_original_assistido = DocumentoOriginalAssistido.objects.get(
                    id=manifestacao_processual.origem_id
                )
                documento_assinado_salvo_em_storage = DocumentoAssinadoAssistido.objects.create(
                    arquivo=arquivo_temporario_em_memoria_do_base_64
                )
                documento_original_assistido.documento_assinado = documento_assinado_salvo_em_storage
                documento_original_assistido.save()
            elif manifestacao_processual.origem == ManifestacaoDocumento.ORIGEM_ATENDIMENTO:
                documento_original_atendimento = DocumentoOriginalAtendimento.objects.get(
                    id=manifestacao_processual.origem_id
                )
                documento_assinado_salvo_em_storage = DocumentoAssinadoAtendimento.objects.create(
                    atendimento=documento_original_atendimento.atendimento,
                    arquivo=arquivo_temporario_em_memoria_do_base_64
                )
                documento_original_atendimento.documento_assinado = documento_assinado_salvo_em_storage
                documento_original_atendimento.save()
            else:
                raise Exception('Não foi possível determinar a origem do documento enviado')
        serializer = self.get_serializer(manifestacao_processual, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class QualificacaoViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, DetailSerializerMixin, GenericViewSet):
    permission_classes = [DjangoModelPermissions]
    filter_backends = (
        QualificacaoFilterBackend,
    )

    queryset = Qualificacao.objects.select_related(
        'area',
        'nucleo',
        'especializado'
    ).ativos()

    serializer_class = QualificacaoSerializer
    serializer_detail_class = QualificacaoDetailSerializer

    def get_queryset(self):

        disponivel_para_agendamento_via_app = self.request.query_params.get('disponivel_para_agendamento_via_app', None) or None  # noqa: E501
        exibir_em_atendimentos = self.request.query_params.get('exibir_em_atendimentos', None) or None  # noqa: E501
        tipo = self.request.query_params.get('tipo', None) or None  # noqa: E501
        penal = self.request.query_params.get('penal', None) or None
        orgao_encaminhamento = self.request.query_params.get('orgao_encaminhamento', None) or None
        possui_orgao_encaminhamento = self.request.query_params.get('possui_orgao_encaminhamento', None) or None
        qs = super(QualificacaoViewSet, self).get_queryset()

        # filtro status
        if disponivel_para_agendamento_via_app == 'true':
            qs = qs.filter(disponivel_para_agendamento_via_app=True)
        elif disponivel_para_agendamento_via_app == 'false':
            qs = qs.filter(disponivel_para_agendamento_via_app=False)

        # filtro status
        if exibir_em_atendimentos == 'true':
            qs = qs.filter(exibir_em_atendimentos=True)

        # filtro tipo
        if tipo:
            qs = qs.filter(tipo__in=tipo.split(","))

        # filtro áreas penais
        if penal == 'true':
            qs = qs.filter(area__penal=True)

        # filtro orgao_encaminhamento
        if orgao_encaminhamento:
            qs = qs.filter(orgao_encaminhamento=orgao_encaminhamento)

        if possui_orgao_encaminhamento == 'true':
            qs = qs.filter(orgao_encaminhamento__isnull=False)
        if possui_orgao_encaminhamento == 'false':
            qs = qs.filter(orgao_encaminhamento__isnull=True)

        qs = restringir_qualificacao(qs, self.defensorias_ids)

        return qs

    @property
    def defensorias_ids(self):
        ids = []
        if hasattr(self.request.user, 'servidor'):
            ids = list(self.request.user.servidor.defensor.defensorias.values_list('id', flat=True))
        return ids


class ContribDocumentoViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    permission_classes = [DjangoModelPermissions]
    filter_backends = (
        ContribDocumentoFilterBackend,
    )

    queryset = ContribDocumento.objects.all()

    serializer_class = ContribDocumentoSerializer

    def get_queryset(self):

        ativo = self.request.query_params.get('ativo', None) or None  # noqa: E501
        exibir_em_documento_assistido = self.request.query_params.get('exibir_em_documento_assistido', None) or None  # noqa: E501
        exibir_em_documento_atendimento = self.request.query_params.get('exibir_em_documento_atendimento', None) or None  # noqa: E501

        qs = super(ContribDocumentoViewSet, self).get_queryset()

        # filtro exibir_em_documento_assisitido
        if exibir_em_documento_assistido == 'true':
            qs = qs.filter(exibir_em_documento_assistido=True)
        elif ativo == 'false':
            qs = qs.filter(exibir_em_documento_assistido=False)

        # filtro exibir_em_documento_atendimento
        if exibir_em_documento_atendimento == 'true':
            qs = qs.filter(exibir_em_documento_atendimento=True)
        elif ativo == 'false':
            qs = qs.filter(exibir_em_documento_atendimento=False)

        # filtro status
        if ativo == 'true':
            qs = qs.filter(ativo=True)
        elif ativo == 'false':
            qs = qs.filter(ativo=False)

        return qs


class CartorioViewSet(ReadOnlyModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = Cartorio.objects.ativos()
    serializer_class = CartorioSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['municipio']


class FormaAtendimentoViewSet(ReadOnlyModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = FormaAtendimento.objects.ativos()
    serializer_class = FormaAtendimentoSerializer


class EstabelecimentoPenalViewSet(ReadOnlyModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = EstabelecimentoPenal.objects.filter(ativo=True)
    serializer_class = EstabelecimentoPenalSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome']


class FormularioRespostaViewSet(ReadOnlyModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = FormularioResposta.objects.ativos().distinct('texto')
    serializer_class = FormularioRespostaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['pergunta']
    search_fields = ['texto']


class CategoriaDeAgendaViewSet(ReadOnlyModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = CategoriaDeAgenda.objects.ativos()
    serializer_class = CategoriaDeAgendaSerializer
    filterset_fields = ['eh_categoria_crc']


class PerguntaViewSet(ReadOnlyModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = Pergunta.objects.order_by("slug")
    serializer_class = PerguntaSerializer
    filterset_fields = ['qualificacao', 'slug', 'texto']


class EncaminhamentoViewSet(ReadOnlyModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = Encaminhamento.objects.filter(ativo=True)
    serializer_class = EncaminhamentoSerializer
    filterset_fields = ['nome']


class SituacaoViewSet(ReadOnlyModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = Situacao.objects.all()
    serializer_class = SituacaoSerializer
    filterset_fields = ['nome', 'eh_situacao_deducao', 'disponivel_via_app']


class TipoRendaViewSet(ReadOnlyModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = TipoRenda.objects.all()
    serializer_class = TipoRendaSerializer
    filterset_fields = ['nome', 'eh_deducao_salario_minimo', 'valor_maximo_deducao']


class EtiquetaViewSet(AuditoriaModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = Etiqueta.objects.ativos()
    serializer_class = EtiquetaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['nome', 'defensorias']

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Recupera dados da requisição
        defensorias = request.data.pop('lista_defensorias', [])
        for defensoria in defensorias:
            # Vincula defensoria à etiqueta
            if defensoria.get('sel'):
                DefensoriaEtiqueta.objects.update_or_create(
                    etiqueta=instance,
                    defensoria_id=defensoria.get('id'),
                    defaults={
                        'desativado_por': None,
                        'desativado_em': None,
                    }
                )
            # Desativa vínculo da defensoria à etiqueta
            else:
                etiqueta_defensoria = DefensoriaEtiqueta.objects.filter(
                    etiqueta=instance,
                    defensoria_id=defensoria.get('id')
                ).first()

                if etiqueta_defensoria:
                    etiqueta_defensoria.desativar(request.user)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # # Se 'prefetch_related' foi aplicado a uma queryset, precisamos invalidar forçadamente o
            # cache de pré-carregamento no objeto.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class DefensoriaEtiquetaViewSet(ModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = DefensoriaEtiqueta.objects.ativos().filter(etiqueta__desativado_em=None)
    serializer_class = DefensoriaEtiquetaSerializer
    filter_class = DefensoriaEtiquetaFilter


class ServidorViewSet(AuditoriaModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = Servidor.objects.all()
    serializer_class = ServidorSerializer
    filter_class = ServidorFilter
