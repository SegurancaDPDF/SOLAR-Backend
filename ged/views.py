# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip
from datetime import date, datetime

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.shortcuts import redirect
from django.utils import timezone
from django.db import Error
from django.db.models import Q, Sum, Case, When, Value, IntegerField
from django.views.generic.edit import UpdateView
from djdocuments.models import Documento
from djdocuments.views.documentos import (
    DocumentoPainelGeralPorGrupoView,
    AssinaturasPendentesGrupo,
    AssinaturasRealizadasPorGrupo,
    DocumentosProntosParaFinalizarGrupo,
    DocumentosEmEdicaoGrupo,
    DocumentosFinalizadosGrupo,
    DocumentoModeloPainelGeralView,
)
from djdocuments_solar_backend.backend import SolarDefensoriaBackend

from atendimento.atendimento.models import Atendimento
from contrib.models import Comarca, Defensoria
from constance import config
import logging

logger = logging.getLogger(__name__)


class GEDPainelGeralView(DocumentoPainelGeralPorGrupoView):
    mostrar_ultimas = None

    def get_ultimos_modelos_queryset(self):

        queryset = super(GEDPainelGeralView, self).get_ultimos_modelos_queryset()

        # remove modelos publicos da lista de modelos do usuário
        queryset = queryset.exclude(modelo_publico=True, grupo_dono__isnull=False)

        if not self.request.user.is_superuser:
            queryset = queryset.exclude(grupo_dono=None)

        return queryset

    def get_context_data(self, **kwargs):

        grupos_id_list = tuple(self.djdocuments_backend.get_grupos_usuario(self.request.user).values_list('pk', flat=True))  # noqa: E501

        context = super(GEDPainelGeralView, self).get_context_data(**kwargs)
        context['pastas'] = [
            {
                'nome': 'Modelos',
                'descricao': 'Modelos utilizados para gerar documentos',
                'url': reverse('ged:painel_geral_modelos'),
                'total': context['ultimos_modelos_count'],
            },
            {
                'nome': 'Modelos Públicos',
                'descricao': 'Modelos de outros setores utilizados para gerar documentos',
                'url': reverse('ged:painel_geral_modelos_publicos'),
                'total': Documento.admin_objects.filter(
                    eh_modelo=True,
                    modelo_publico=True,
                    esta_ativo=True,
                    grupo_dono__isnull=False
                ).count(),
            },
            {
                'nome': 'Em Edição',
                'descricao': 'Documentos sendo editados',
                'url': reverse('ged:painel_geral_documentos_em_edicao'),
                'total': context['ultimos_documentos_em_edicao_count'],
            },
            {
                'nome': 'Prontos para Assinar',
                'descricao': 'Documentos aguardando assinatura',
                'url': reverse('ged:painel_geral_assinaturas_pendentes'),
                'total': context['ultimas_assinaturas_pendentes_count'],
            },
            {
                'nome': 'Assinados',
                'descricao': 'Documentos assinados',
                'url': reverse('ged:painel_geral_assinaturas_realizadas'),
                'total': context['ultimas_assinaturas_realizadas_count'],
            },
            {
                'nome': 'Prontos para Finalizar',
                'descricao': 'Documentos aguardando conclusão',
                'url': reverse('ged:painel_geral_documentos_nao_finalizados'),
                'total': context['ultimos_documentos_nao_finalizados_count'],
            },
            {
                'nome': 'Finalizados',
                'descricao': 'Documentos concluídos e publicados',
                'url': reverse('ged:painel_geral_documentos_finalizados'),
                'total': context['ultimos_documentos_finalizados_count'],
            },
            {
                'nome': 'De Hoje',
                'descricao': 'Documentos criados hoje',
                'url': '{}?data_inicial={:%d/%m/%Y}'.format(
                    reverse('ged:painel_geral_documentos'),
                    date.today()
                ),
                'total': Documento.objects.filter(
                    criado_em__date=date.today()
                ).from_groups(
                    grupos_ids=grupos_id_list,
                    is_superuser=self.request.user.is_superuser
                ).count(),
            },
        ]

        return context


class GEDFiltroMixin:
    def clean_filters(self):
        filtros = self.request.GET.copy()

        if filtros.get('numero_documento'):

            numero_documento = filtros.get('numero_documento').lower().split('v')[0]

            if numero_documento.isdigit():
                filtros['numero_documento'] = int(numero_documento)
            else:
                filtros['numero_documento'] = None

        return filtros


class GEDPainelGeralDocumentoMixin(GEDFiltroMixin):
    STATUS_TODOS = 0
    STATUS_EM_EDICAO = 1
    STATUS_PRONTOS_PARA_ASSINAR = 2
    STATUS_ASSINADOS = 3
    STATUS_PRONTOS_PARA_FINALIZAR = 4
    STATUS_FINALIZADOS = 5

    LISTA_STATUS = (
        (STATUS_TODOS, 'Todos'),
        (STATUS_EM_EDICAO, 'Em edição'),
        (STATUS_PRONTOS_PARA_ASSINAR, 'Prontos para assinar'),
        (STATUS_ASSINADOS, 'Assinados'),
        (STATUS_PRONTOS_PARA_FINALIZAR, 'Prontos para finalizar'),
        (STATUS_FINALIZADOS, 'Finalizados'),
    )

    def get_context_data(self, **kwargs):

        context = super(GEDPainelGeralDocumentoMixin, self).get_context_data(**kwargs)
        context['ged_atual'] = None
        context['assinatura_atual'] = None
        context['assinatura_atual_url'] = None

        context['filtros'] = self.request.GET
        context["LISTA_STATUS"] = self.LISTA_STATUS

        if self.request.user.has_perm(perm='atendimento.view_all_atendimentos'):
            context['lista_defensorias'] = Defensoria.objects.all()
        else:
            # Se usuário não tem permissão, restringe informações de acordo com suas lotações
            context['lista_defensorias'] = self.request.user.servidor.defensor.defensorias

        if self.request.GET.get('doc'):

            ged_atual = Documento.admin_objects.get(pk_uuid=self.request.GET.get('doc'))

            if ged_atual.esta_pronto_para_assinar and self.request.GET.get('assinatura'):

                assinaturas_pendentes = ged_atual.assinaturas.filter(
                    esta_assinado=False,
                    ativo=True
                )

                assinatura_atual = assinaturas_pendentes.filter(
                    id=self.request.GET.get('assinatura')
                ).first()

                existem_outras_assinaturas_pendentes = assinaturas_pendentes.exclude(
                    id=self.request.GET.get('assinatura')
                ).exists()

                if assinatura_atual:
                    context['assinatura_atual'] = assinatura_atual
                    if existem_outras_assinaturas_pendentes:
                        context['assinatura_atual_url'] = assinatura_atual.get_url_para_assinar
                    else:
                        context['assinatura_atual_url'] = assinatura_atual.get_url_para_assinar_e_finalizar

            # define variável de permissão para editar GED
            pode_editar = ged_atual.pode_editar(self.request.user)

            context['ged_atual_pode_editar'] = pode_editar[0]
            context['ged_atual_pode_editar_msg'] = pode_editar[1]

            # define variável de permissão para excluir GED
            pode_excluir = SolarDefensoriaBackend().pode_excluir_documento(
                document=ged_atual,
                usuario=self.request.user
            )
            context['ged_atual_pode_excluir'] = pode_excluir[0]
            context['ged_atual_pode_excluir_msg'] = pode_excluir[1]

            # define variável de permissão para revogar assinatura do GED
            pode_revogar_assinatura = SolarDefensoriaBackend().pode_revogar_assinatura(
                document=ged_atual,
                usuario=self.request.user
            )

            context['ged_atual_pode_revogar_assinatura'] = pode_revogar_assinatura[0]
            context['ged_atual_pode_revogar_assinatura_msg'] = pode_revogar_assinatura[1]

            # Carrega informacoes dos atendimentos vinculados ao ged selecionado
            ged_atual_documentos = ged_atual.documento_set.ativos().atendimento_ativo().values(
                'id',
                'atendimento__tipo',
                'atendimento__numero',
                'atendimento__origem__numero')

            # Trata informacoes dos atendimentos vinculados ao ged selecionado
            atendimentos = []
            for documento in ged_atual_documentos:

                atendimento_atividade = documento['atendimento__tipo'] == Atendimento.TIPO_ATIVIDADE

                if atendimento_atividade:
                    atendimento_numero = documento['atendimento__origem__numero']
                else:
                    atendimento_numero = documento['atendimento__numero']

                atendimentos.append({
                    'numero': atendimento_numero,
                    'atividade': atendimento_atividade,
                    'url': reverse('atendimento_atender', args=[atendimento_numero]),
                    'documento_id': documento['id']
                })

            context['ged_atual'] = ged_atual
            context['ged_atual_atendimentos'] = atendimentos

            # Carrega informacoes dos propacs vinculados ao ged selecionado
            context['ged_atual_documento_propac'] = ged_atual.documentopropac_set.filter(ativo=True).first()

        return context


class GEDFiltroAssinaturaMixin(GEDFiltroMixin):
    def get_queryset(self):

        queryset = super().get_queryset()
        filtros = self.clean_filters()

        q = Q()
        if filtros.get("titulo_documento"):
            q &= Q(documento__assunto__icontains=filtros.get("titulo_documento"))

        if filtros.get("numero_documento"):
            q &= Q(documento__id=filtros.get("numero_documento"))

        if filtros.get("defensoria"):
            q &= Q(grupo_assinante=filtros.get("defensoria"))

        if filtros.get("numero_atendimento"):
            q &= Q(documento__documento__atendimento__numero__icontains=filtros.get("numero_atendimento"))

        if filtros.get("data_inicial"):
            q &= Q(documento__criado_em__date__gte=datetime.strptime(filtros.get("data_inicial"), '%d/%m/%Y'))

        if filtros.get("data_final"):
            q &= Q(documento__criado_em__date__lte=datetime.strptime(filtros.get("data_final"), '%d/%m/%Y'))

        return queryset.filter(q)


class GEDFiltroDocumentoMixin(GEDFiltroMixin):
    def get_queryset(self):

        queryset = super().get_queryset()
        filtros = self.clean_filters()

        q = Q()
        if filtros.get("titulo_documento"):
            q &= Q(assunto__icontains=filtros.get("titulo_documento"))

        if filtros.get("numero_documento"):
            q &= Q(id=filtros.get("numero_documento"))

        if filtros.get("defensoria"):
            q &= Q(grupo_dono=filtros.get("defensoria"))

        if filtros.get("numero_atendimento"):
            q &= Q(documento__atendimento__numero__icontains=filtros.get("numero_atendimento"))

        if filtros.get("data_inicial"):
            q &= Q(criado_em__date__gte=datetime.strptime(filtros.get("data_inicial"), '%d/%m/%Y'))

        if filtros.get("data_final"):
            q &= Q(criado_em__date__lte=datetime.strptime(filtros.get("data_final"), '%d/%m/%Y'))

        return queryset.filter(q)


class GEDFiltroModeloMixin(GEDFiltroMixin):
    def get_queryset(self):

        queryset = super().get_queryset()
        filtros = self.clean_filters()

        q = Q()
        if filtros.get("titulo_documento"):
            q &= Q(modelo_descricao__icontains=filtros.get("titulo_documento"))

        if filtros.get("numero_documento"):
            q &= Q(id=filtros.get("numero_documento"))

        if filtros.get("data_inicial"):
            q &= Q(criado_em__date__gte=datetime.strptime(filtros.get("data_inicial"), '%d/%m/%Y'))

        if filtros.get("data_final"):
            q &= Q(criado_em__date__lte=datetime.strptime(filtros.get("data_final"), '%d/%m/%Y'))

        return queryset.filter(q)


class GEDDocumentoListView(GEDPainelGeralDocumentoMixin, GEDFiltroDocumentoMixin, DocumentosEmEdicaoGrupo):
    template_name = 'luzfcb_djdocuments/painel_geral.html'
    search_fields = [('pk', 'icontains'), ('assunto', 'icontains')]

    def get_queryset(self):

        queryset = self.model.objects.get_queryset()
        filtros = self.clean_filters()

        q = Q()
        if filtros.get("titulo_documento"):
            q &= Q(assunto__icontains=filtros.get("titulo_documento"))

        if filtros.get("numero_documento"):
            q &= Q(id=filtros.get("numero_documento"))

        if filtros.get("defensoria"):
            q &= Q(grupo_dono=filtros.get("defensoria"))

        if filtros.get("numero_atendimento"):
            q &= Q(documento__atendimento__numero__icontains=filtros.get("numero_atendimento"))

        if filtros.get("data_inicial"):
            q &= Q(criado_em__date__gte=datetime.strptime(filtros.get("data_inicial"), '%d/%m/%Y'))

        if filtros.get("data_final"):
            q &= Q(criado_em__date__lte=datetime.strptime(filtros.get("data_final"), '%d/%m/%Y'))

        grupos_id_list = tuple(self.djdocuments_backend.get_grupos_usuario(self.request.user).values_list('pk', flat=True))  # noqa: E501

        queryset = queryset.from_groups(
            grupos_ids=grupos_id_list,
            is_superuser=self.request.user.is_superuser
        )
        queryset = queryset.only(
            'pk',
            'pk_uuid',
            'eh_modelo',
            'esta_ativo',
            'versao_numero',
            'assunto',
            'criado_por_nome',
            'criado_por__username',
            'criado_em',
            'esta_assinado',
            'data_assinado',
            'finalizado_por_nome',
            'finalizado_por__username',
            'modificado_por__username',
            'modificado_por_nome',
        ).select_related(
            'finalizado_por',
            'modificado_por',
            'criado_por'
        )

        return queryset.filter(q)

    def get_context_data(self, **kwargs):

        context = super(GEDDocumentoListView, self).get_context_data(**kwargs)
        context['search_url'] = reverse('ged:painel_geral_documentos')
        context['q'] = self.request.GET.get('q')

        context['documentos'] = True
        context['caminho'] = [
            {
                'url': context['search_url'],
                'nome': 'Todos Documentos'
            }]

        return context


class GEDPainelAssinaturasPendentesView(GEDPainelGeralDocumentoMixin, GEDFiltroAssinaturaMixin, AssinaturasPendentesGrupo):  # noqa: E501

    template_name = 'luzfcb_djdocuments/painel_geral.html'
    search_fields = [('documento_identificador_versao', 'icontains'), ('documento_assunto', 'icontains')]

    def get_context_data(self, **kwargs):

        context = super(GEDPainelAssinaturasPendentesView, self).get_context_data(**kwargs)
        context['search_url'] = reverse('ged:painel_geral_assinaturas_pendentes')

        context['assinaturas'] = True
        context['caminho'] = [
            {
                'url': context['search_url'],
                'nome': 'Assinaturas Pendentes'
            }]

        return context


class GEDAssinaturasRealizadasView(GEDPainelGeralDocumentoMixin, GEDFiltroAssinaturaMixin, AssinaturasRealizadasPorGrupo):  # noqa: E501
    template_name = 'luzfcb_djdocuments/painel_geral.html'
    search_fields = [('documento_identificador_versao', 'icontains'), ('documento_assunto', 'icontains')]

    def get_context_data(self, **kwargs):

        context = super(GEDAssinaturasRealizadasView, self).get_context_data(**kwargs)
        context['search_url'] = reverse('ged:painel_geral_assinaturas_realizadas')
        context['q'] = self.request.GET.get('q')

        context['assinaturas'] = True
        context['caminho'] = [
            {
                'url': context['search_url'],
                'nome': 'Assinaturas Realizadas'
            }]

        return context


class GEDPainelDocumentosNaoFinalizadosView(GEDPainelGeralDocumentoMixin, GEDFiltroDocumentoMixin, DocumentosProntosParaFinalizarGrupo):  # noqa: E501
    template_name = 'luzfcb_djdocuments/painel_geral.html'
    search_fields = [('pk', 'icontains'), ('assunto', 'icontains')]

    def get_context_data(self, **kwargs):

        context = super(GEDPainelDocumentosNaoFinalizadosView, self).get_context_data(**kwargs)
        context['search_url'] = reverse('ged:painel_geral_documentos_nao_finalizados')
        context['q'] = self.request.GET.get('q')

        context['documentos'] = True
        context['caminho'] = [
            {
                'url': context['search_url'],
                'nome': 'Documentos não finalizados'
            }]

        return context


class GEDPainelDocumentosEmEdicaoView(GEDPainelGeralDocumentoMixin, GEDFiltroDocumentoMixin, DocumentosEmEdicaoGrupo):
    template_name = 'luzfcb_djdocuments/painel_geral.html'
    search_fields = [('pk', 'icontains'), ('assunto', 'icontains')]

    def get_context_data(self, **kwargs):

        context = super(GEDPainelDocumentosEmEdicaoView, self).get_context_data(**kwargs)
        context['search_url'] = reverse('ged:painel_geral_documentos_em_edicao')
        context['q'] = self.request.GET.get('q')

        context['documentos'] = True
        context['caminho'] = [
            {
                'url': context['search_url'],
                'nome': 'Documentos em edição'
            }]

        return context


class GEDPainelDocumentosFinalizadosView(GEDPainelGeralDocumentoMixin, GEDFiltroDocumentoMixin, DocumentosFinalizadosGrupo):  # noqa: E501
    template_name = 'luzfcb_djdocuments/painel_geral.html'
    search_fields = [('pk', 'icontains'), ('assunto', 'icontains')]

    def get_context_data(self, **kwargs):

        context = super(GEDPainelDocumentosFinalizadosView, self).get_context_data(**kwargs)
        context['search_url'] = reverse('ged:painel_geral_documentos_finalizados')
        context['q'] = self.request.GET.get('q')

        context['documentos'] = True
        context['caminho'] = [
            {
                'url': context['search_url'],
                'nome': 'Documentos Finalizados'
            }]

        return context


class GEDPainelModelos(GEDPainelGeralDocumentoMixin, GEDFiltroModeloMixin, DocumentoModeloPainelGeralView):
    template_name = 'luzfcb_djdocuments/painel_geral.html'
    ordering = ('-modelo_pronto_para_utilizacao', 'modelo_descricao')
    modelos_publicos = False

    def get_context_data(self, **kwargs):

        context = super(GEDPainelModelos, self).get_context_data(**kwargs)
        context['search_url'] = reverse('ged:painel_geral_modelos')
        context['q'] = self.request.GET.get('q')

        context['documentos'] = True
        context['modelos'] = True
        context['caminho'] = [
            {
                'url': context['search_url'],
                'nome': 'Modelos'
            }]

        return context

    def get_queryset(self):

        if config.ORDENAR_MODELO_DOCUMENTO_POR_NOME:
            queryset = super(GEDPainelModelos, self).get_queryset()
        else:
            queryset = super(GEDPainelModelos, self).get_queryset().order_by('-modificado_em')

        if not self.request.user.is_superuser:
            queryset = queryset.exclude(grupo_dono=None)

        filtros = self.clean_filters()
        q = Q()

        # Filtrar por defensoria
        if filtros.get("defensoria"):
            q &= Q(grupo_dono=filtros.get("defensoria"))

        return queryset.filter(q)


class GEDPainelModelosPublicos(GEDPainelGeralDocumentoMixin, DocumentoModeloPainelGeralView):
    template_name = 'luzfcb_djdocuments/painel_geral.html'
    ordering = ('-modelo_pronto_para_utilizacao', 'modelo_descricao')
    modelos_publicos = True

    def get_context_data(self, **kwargs):

        context = super(GEDPainelModelosPublicos, self).get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q')

        comarca_id = self.kwargs.get('comarca_id')
        defensoria_id = self.kwargs.get('defensoria_id')
        atendimento_numero = self.request.GET.get('atendimento_numero', '')

        comarca = None
        defensoria = None

        if not comarca_id and not defensoria_id:
            context['comarcas'] = Comarca.objects.annotate(
                total=Sum(Case(
                    When
                    (
                        defensoria__djdocuments_documento_donos__eh_modelo=True,
                        defensoria__djdocuments_documento_donos__esta_ativo=True,
                        defensoria__djdocuments_documento_donos__modelo_publico=True,
                        then=Value(1)
                    ),
                    default=Value(0),
                    output_field=IntegerField())
                )
            ).filter(
                total__gt=0,
                ativo=True
            )

        if comarca_id and not defensoria_id:

            comarca = Comarca.objects.get(id=comarca_id)

            context['defensorias'] = Defensoria.objects.annotate(
                total=Sum(Case(
                    When
                    (
                        djdocuments_documento_donos__eh_modelo=True,
                        djdocuments_documento_donos__esta_ativo=True,
                        djdocuments_documento_donos__modelo_publico=True,
                        then=Value(1)
                    ),
                    default=Value(0),
                    output_field=IntegerField())
                )
            ).filter(
                comarca_id=comarca_id,
                total__gt=0,
                ativo=True
            )

        if defensoria_id:

            defensoria = Defensoria.objects.select_related('comarca').get(id=defensoria_id)
            comarca = defensoria.comarca

        context['desabilitar_consulta_defensoria'] = True
        context['defensoria_id'] = defensoria_id
        context['documentos'] = True
        context['modelos'] = True
        context['caminho'] = [
            {
                'url': reverse('ged:painel_geral_modelos_publicos'),
                'nome': 'Modelos Públicos'
            }]

        if comarca:
            context['caminho'].append(
                {
                    'url': reverse('ged:painel_geral_modelos_publicos_comarca', kwargs={
                        'comarca_id': comarca.id
                    }),
                    'nome': comarca.nome
                }
            )

        if defensoria:
            context['caminho'].append(
                {
                    'url': reverse('ged:painel_geral_modelos_publicos_defensoria', kwargs={
                        'defensoria_id': defensoria.id
                    }),
                    'nome': defensoria.nome
                }
            )

        # Acrescenta número do atendimento às URLs do menu superior
        if atendimento_numero:
            for caminho in context['caminho']:
                caminho['url'] = '{}?atendimento_numero={}'.format(caminho['url'], atendimento_numero)

        # Url de busca deve ser a última pasta do caminho
        context['search_url'] = context['caminho'][-1]['url']
        context['atendimento_numero'] = atendimento_numero

        return context

    def get_queryset(self):

        defensoria_id = self.kwargs.get('defensoria_id')

        if defensoria_id:
            queryset = self.model.admin_objects.filter(
                eh_modelo=True,
                esta_ativo=True,
                modelo_publico=True,
                grupo_dono_id=defensoria_id
            )
        else:
            queryset = self.model.objects.none()

        filtros = self.clean_filters()

        q = Q()
        if filtros.get("titulo_documento"):
            q &= Q(modelo_descricao__icontains=filtros.get("titulo_documento"))

        if filtros.get("numero_documento"):
            q &= Q(id=filtros.get("numero_documento"))

        if filtros.get("data_inicial"):
            q &= Q(criado_em__date__gte=datetime.strptime(filtros.get("data_inicial"), '%d/%m/%Y'))

        if filtros.get("data_final"):
            q &= Q(criado_em__date__lte=datetime.strptime(filtros.get("data_final"), '%d/%m/%Y'))

        return queryset.filter(q)


class GEDPainelExcluirDocumento(UpdateView):
    model = Documento
    fields = ['documento-id']

    # def get_success_url(self):
    #     return reverse('ged:painel_geral')

    '''Define a URL de retorno'''
    def get_url(self):
        url_referer = self.request.environ['HTTP_REFERER']
        url = 'ged:painel_geral'

        if 'documentos-em-edicao' in url_referer:
            url = 'ged:painel_geral_documentos_em_edicao'

        elif 'documentos-nao-finalizados' in url_referer:
            url = 'ged:painel_geral_documentos_nao_finalizados'

        elif 'assinaturas-realizadas' in url_referer:
            url = 'ged:painel_geral_assinaturas_realizadas'

        elif 'assinaturas-pendentes' in url_referer:
            url = 'ged:painel_geral_assinaturas_pendentes'

        return url

    def post(self, request, *args, **kwargs):
        ged = self.request.POST.get('documento')

        try:
            ged = Documento.admin_objects.get(pk=ged)
        except ObjectDoesNotExist as e:
            logger.exception(e)
            messages.error(self.request, u'Erro ao excluir documento!')
        else:
            usuario = self.request.user

            # verifica se o usuário tem permissão para excluir o GED desejado
            if SolarDefensoriaBackend().pode_excluir_documento(document=ged, usuario=usuario)[0]:

                agora = timezone.now()

                try:
                    # desabilita o relacionamento com Documento(Atendimento)
                    for doc in ged.documento_set.all():
                        doc.excluir(
                            excluido_por=usuario.servidor,
                            agora=agora
                        )
                    # desabilita o relacionamento com Documento(Core)
                    for doc in ged.core_documentos.all():
                        doc.desativar(
                            usuario=usuario,
                            data_hora=agora
                        )
                    # desabilita o GED e as Assinaturas vinculadas
                    ged.delete(current_user=usuario, agora=agora)
                except Error as e:
                    logger.exception(e)
                    messages.error(self.request, u'Erro ao excluir documento!')
                else:
                    messages.success(self.request, u'Documento excluído com sucesso!')
            else:
                messages.error(self.request, u'Sem permissão para excluir este documento!')

        return redirect(self.get_url())
