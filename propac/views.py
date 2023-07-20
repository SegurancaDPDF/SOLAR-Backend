# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
from copy import deepcopy
from datetime import datetime
import reversion
from bulk_update.helper import bulk_update
from dal import autocomplete
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import redirect, get_object_or_404, render
import six
from django.utils.functional import cached_property
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import FormView, ListView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView, BaseCreateView
from django.core.files import File
from django_addanother.views import CreatePopupMixin
from rest_framework.permissions import DjangoModelPermissions, AllowAny
from rest_framework import viewsets, status, response, mixins
from rest_framework.decorators import action
from core.context_processors import permissao_acesso_propacs
from propac.serializer_mixin import SerializerMixin


from atendimento.atendimento.models import Atendimento, Documento
from contrib.models import Defensoria, Util
from djdocuments.views.mixins import FormActionViewMixin
from propac.exceptions import TarefaNaoEncontradaException, TarefaErroException
from relatorios.models import Local, Relatorio
from atendimento.atendimento.models import Tarefa
from propac.serializers import (TarefaListSerializer,
                                TarefaCreateSerializer,
                                TarefaDetailSerializer,
                                DocumentoPropacSerializer)
from .forms import (
    MovimentoForm,
    RemocaoMovimentoForm,
    CadastraProcedimentoForm,
    AlteraProcedimentoForm,
    EditarMovimentoForm,
    CriarDocumentoPropacForm,
    NovoMovimentoForm,
)
from .models import (
    Procedimento,
    Movimento,
    SituacaoProcedimento,
    MovimentoTipo,
    DocumentoPropac,
    TipoAnexoDocumentoPropac,
)
from defensor.models import Defensor
from propac.usecases import (responder_tarefa,
                             excluir_tarefa,
                             finalizar_tarefa,
                             listar_defensorias,
                             recupera_documentos_tarefas,
                             cria_documentos_propac)
from propac.filters import MovimentoFilterBackend


class LoginRequiredMixin(object):  # exige que o usuário esteja autenticado para acessar a view
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class AngularMixin(object):  # adiciona informações relacionadas ao angular no contexto da view
    angular_controller = None
    angular_app = None

    def get_context_data(self, **kwargs):
        context = super(AngularMixin, self).get_context_data(**kwargs)
        context['angular'] = self.angular_controller
        context['angular_app'] = self.angular_app
        return context


class PermissaoAcesso(LoginRequiredMixin, View):  # verifica a permissao de acesso a um determinado
    def dispatch(self, request, *args, **kwargs):

        if hasattr(request.user.servidor, 'defensor'):
            defensorias_list = self.defensorias_responsavel_queryset.filter(
                Q(all_atuacoes__ativo=True) &
                Q(evento=None)
            ).exists()

            if not defensorias_list:
                return redirect('atendimento_index')

        return super(PermissaoAcesso, self).dispatch(request, *args, **kwargs)

    @cached_property
    def atuacoes_vigentes_defensorias_id(self):
        defensorias_id = self.request.user.servidor.defensor.atuacoes_vigentes().values_list('defensoria_id', flat=True)
        return tuple(defensorias_id)

    @cached_property
    def defensorias_responsavel_queryset(self):
        return self.request.user.servidor.defensor.defensorias

    def defensorias_responsavel_list_id(self):
        return self.defensorias_responsavel_queryset.values_list('id', flat=True)

    @cached_property
    def defensores_responsavel_queryset(self):
        d = Defensor.objects.filter(
            Q(eh_defensor=True) &
            Q(ativo=True) &
            Q(all_atuacoes__defensoria__in=self.defensorias_responsavel_queryset) &
            (
                (
                    Q(all_atuacoes__data_inicial__lte=datetime.now()) &
                    Q(all_atuacoes__data_final=None)
                ) |
                (
                    Q(all_atuacoes__data_inicial__lte=datetime.now()) &
                    Q(all_atuacoes__data_final__gte=datetime.now())
                )
            ) &
            Q(all_atuacoes__ativo=True)
        )
        return d


class ProcedimentoDadosMixin(object):
    def get_nucleos_acesso_user(self, **kwargs):
        """
            Método que retorna uma lista de  nucleos que o user tem acesso
        """
        return self.defensorias_responsavel_list_id()

    def get_permission_user(self, **kwargs):
        """
            método que retorna um booleano que informa se o user tem acesso
            ou não a um procedimento especifico
        """

        procedimento = kwargs['procedimento']

        if procedimento.acesso == Procedimento.NIVEL_PUBLICO:
            return True

        nucleos = self.get_nucleos_acesso_user(**kwargs)

        if nucleos:
            acesso_filtro_set = set(list(nucleos))
            procedimento_defensorias_set = set(procedimento.listar_defensorias_acesso_e_responsavel_ids())
            acesso_negado_set = procedimento_defensorias_set.intersection(acesso_filtro_set)

            if len(acesso_negado_set) == 0:
                return False

        return True

    def get_context_data(self, **kwargs):
        context = super(ProcedimentoDadosMixin, self).get_context_data(**kwargs)
        context['TIPO_PROCEDIMENTO'] = Procedimento.TIPO_PROCEDIMENTO
        context['TIPO_PROPAC'] = Procedimento.TIPO_PROPAC

        context['SITUACAO_MOVIMENTO'] = Procedimento.SITUACAO_MOVIMENTO
        context['SITUACAO_ENCERRADO'] = Procedimento.SITUACAO_ENCERRADO
        context['SITUACAO_ARQUIVADO'] = Procedimento.SITUACAO_ARQUIVADO
        context['SITUACAO_DESARQUIVADO'] = Procedimento.SITUACAO_DESARQUIVADO

        context['ACESSO_NIVEL_PUBLICO'] = Procedimento.NIVEL_PUBLICO
        context['ACESSO_NIVEL_RESTRITO'] = Procedimento.NIVEL_RESTRITO
        context['ACESSO_NIVEL_PRIVADO'] = Procedimento.NIVEL_PRIVADO

        kwargs['procedimento'] = self.object
        kwargs['user'] = self.request.user

        context['user_acesso_propac'] = self.get_permission_user(**kwargs)

        return context


class MovimentoMixin(object):  # classe mixin para lidar com os movimentos do procedimento
    movimento_url_kwarg = 'pk_movimento'
    movimento_field = 'pk'
    movimento_model = Movimento

    def get_movimento_field(self):
        return self.movimento_field

    def get_movimento_url_kwarg(self):
        return self.movimento_url_kwarg

    def dispatch(self, request, *args, **kwargs):
        self.movimento_object = self.get_movimento_object()
        return super(MovimentoMixin, self).dispatch(request, *args, **kwargs)

    def get_movimento_object(self):
        uuid_procedimento = self.kwargs.get(self.get_movimento_url_kwarg(), None)
        parans = {self.get_movimento_field(): uuid_procedimento}
        return self.movimento_model.objects.get(**parans)


class ProcedimentoMixin(object):  # classe mixin para lidar com os procedimentos
    procedimento_url_kwarg = 'uuid'
    procedimento_field = 'uuid'
    procedimento_model = Procedimento

    def get_procedimento_field(self):
        return self.procedimento_field

    def get_procedimento_url_kwarg(self):
        return self.procedimento_url_kwarg

    def dispatch(self, request, *args, **kwargs):
        self.procedimento_object = self.get_procedimento_object()
        return super(ProcedimentoMixin, self).dispatch(request, *args, **kwargs)

    def get_procedimento_object(self):
        uuid_procedimento = self.kwargs.get(self.get_procedimento_url_kwarg(), None)
        parans = {self.get_procedimento_field(): uuid_procedimento}
        return self.procedimento_model.objects.get(**parans)


class ProcedimentoHomeView(PermissaoAcesso, FormView, ListView):  # view principal de procedimentos
    template_name = 'propac/procedimento_index.html'
    model = Procedimento
    context_object_name = 'procedimentos_list'
    form_class = CadastraProcedimentoForm
    paginate_by = 15

    def get_queryset(self):
        return Procedimento.objects.filter(ativo=True, tipo=Procedimento.TIPO_PROCEDIMENTO) \
            .order_by('-data_ultima_movimentacao')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['defensorias_responsavel_queryset'] = self.defensorias_responsavel_queryset
        kwargs['defensores_responsavel_queryset'] = self.defensores_responsavel_queryset
        return kwargs

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['angular'] = 'PropacsDefaultCtrl'
        context['propacs_acesso'] = permissao_acesso_propacs(self.request)

        if 'form' not in kwargs:
            context['form'] = self.get_form()

        return context


class PropacHomeView(ProcedimentoHomeView):  # view principal do procap
    template_name = 'propac/propac_index.html'
    context_object_name = 'propac_list'

    def get_queryset(self):
        return Procedimento.objects.filter(ativo=True, tipo=Procedimento.TIPO_PROPAC) \
            .order_by('-data_ultima_movimentacao')


class PropacPerfilHomeView(ProcedimentoHomeView, ProcedimentoDadosMixin):  # view do perfil do procap
    template_name = 'propac/procedimento_propac_inicio.html'
    context_object_name = 'procedimentos_list'

    def get_queryset(self):
        kwargs = {'user': self.request.user}
        nucleos = self.get_nucleos_acesso_user(**kwargs)

        data_list = Procedimento.objects.filter(
            Q(ativo=True) &
            (
                Q(defensoria_responsavel__id__in=nucleos) |
                Q(defensorias_acesso__id__in=nucleos)
            )
        )

        return data_list.order_by('-data_ultima_movimentacao').distinct()


class PesquisarPropacProcedimentoHomeView(ProcedimentoHomeView):  # view de pesquisa e procedimentos do procap
    template_name = 'propac/buscar_procedimentos_propacs_index.html'

    def get_context_data(self, **kwargs):
        context = super(PesquisarPropacProcedimentoHomeView, self).get_context_data(**kwargs)
        context['angular'] = 'PropacsBuscarCtrl'
        return context


class ProcedimentoDetailView(PermissaoAcesso, ProcedimentoDadosMixin, DetailView):  # view de detalhe do procedimento
    model = Procedimento
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    template_name = 'propac/procedimento_dados.html'
    context_object_name = 'procedimento'

    def get_movimento_form_kwargs(self):
        ret = {}
        instance = self.object.movimentos_ativos().filter(eh_precadastro=True).last()
        if instance:
            ret['instance'] = instance

        ret['initial'] = {'procedimento': self.object}
        return ret

    def get_movimento_form(self):
        return MovimentoForm(**self.get_movimento_form_kwargs())

    def get_permission_user_editar(self, **kwargs):
        permissao = False

        procedimento = self.object

        if procedimento.defensoria_responsavel_id in self.atuacoes_vigentes_defensorias_id:
            permissao = True
        else:
            for d in procedimento.defensorias_acesso.all():
                if d.id in self.atuacoes_vigentes_defensorias_id:
                    permissao = True

        return permissao

    def get_context_data(self, **kwargs):
        context = super(ProcedimentoDetailView, self).get_context_data(**kwargs)
        context['angular'] = 'ImprimirCtrl'
        context['movimento_form'] = self.get_movimento_form()
        context['movimento_form_modal_url'] = reverse('procedimentos:procedimento_novo_movimento_modal_html',
                                                      kwargs={'uuid': self.object.uuid})
        context['movimento_form_action'] = reverse('procedimentos:procedimento_cadastrar_movimento',
                                                   kwargs={'uuid': self.object.uuid})

        context['user_acesso_propac_editar'] = self.get_permission_user_editar()

        context['relatorios'] = Relatorio.objects.filter(
            papeis=self.request.user.servidor.papel,
            locais__pagina=Local.PAG_PROPAC_DETALHES
        ).ativos()

        return context


class ProcedimentoNovoMovimentoModalHtml(ProcedimentoDetailView):
    # view do modal de criacao de novo movimento do procedimento
    template_name = 'propac/procedimento_modal_criar_movimento_content.html'


class CadastraMovimentacaoProcedimentoView(LoginRequiredMixin, FormActionViewMixin, ProcedimentoMixin, BaseCreateView):
    # view de cadastro de uma nova movimentacao no procedimento
    model = Movimento
    form_class = NovoMovimentoForm
    template_name = 'propac/cadastrar_movimentacao.html'
    ja_existe = False

    def get_form_action(self):
        kwargs = {'uuid': self.procedimento_object.uuid}
        return reverse('procedimentos:procedimento_cadastrar_movimento', kwargs=kwargs)

    def form_valid(self, form):
        movimento = form.save(commit=False)
        movimento.cadastrado_por = self.request.user.servidor
        movimento.procedimento = self.procedimento_object
        movimento.volume = movimento.numero_ultimo_volume()
        movimento.ordem_volume = movimento.ordem_ultimo_volume()
        with reversion.create_revision(atomic=False):
            ret = super(CadastraMovimentacaoProcedimentoView, self).form_valid(form)
            reversion.set_user(self.request.user)
            reversion.set_comment(Util.get_comment_save(self.request.user, movimento, True))
        if self.request.is_ajax():
            ret = JsonResponse({'sucess': True}, status=200)

        return ret

    def get_success_url(self):
        kwargs = {'uuid': self.procedimento_object.uuid, 'pk': self.object.pk}
        return reverse('procedimentos:editar_movimento', kwargs=kwargs)

    def form_invalid(self, form):
        ret = super(CadastraMovimentacaoProcedimentoView, self).form_invalid(form)
        if self.request.is_ajax():
            ret = JsonResponse({'error': form.errors}, status=403)
        return ret


class CadastraProcedimentoView(FormActionViewMixin, BaseCreateView):  # view de cadastro de um novo procedimento
    form_class = CadastraProcedimentoForm
    model = Procedimento
    template_name = 'propac/cadastrar_movimentacao.html'

    def get_form_action(self):
        return reverse('procedimentos:novo_procedimento')

    def get_success_url(self):
        kwargs = {'uuid': self.object.uuid}
        return reverse('procedimentos:editar_procedimento', kwargs=kwargs)

    def form_valid(self, form):
        procedimento = form.save(commit=False)
        procedimento.cadastrado_por = self.request.user.servidor
        procedimento.defensor_responsavel_nome = procedimento.defensor_responsavel.servidor.nome
        procedimento.defensoria_responsavel_nome = procedimento.defensoria_responsavel.nome
        with reversion.create_revision(atomic=False):
            ret = super(CadastraProcedimentoView, self).form_valid(form)
            reversion.set_user(self.request.user)
            reversion.set_comment(Util.get_comment_save(self.request.user, procedimento, True))

        if self.request.is_ajax():
            # todo: success
            ret = JsonResponse({'success': True}, status=200)

        return ret

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        ret = super(CadastraProcedimentoView, self).form_invalid(form)
        if self.request.is_ajax():
            ret = JsonResponse({'error': form.errors}, status=403)
            # redirect('procedimentos:procedimento_index')
        return ret


class AlteraProcedimentoView(ProcedimentoDetailView, UpdateView):  # view de edicao de um procedimento
    form_class = AlteraProcedimentoForm
    template_name = 'propac/procedimento_dados_editar.html'

    def get_context_data(self, **kwargs):
        context = super(AlteraProcedimentoView, self).get_context_data(**kwargs)
        context['form'] = self.get_form(self.form_class)
        context['angular'] = 'PropacsCtrl'
        context['defensorias_acesso_ids'] = list(self.object.defensorias_acesso.all().values_list('id', flat=True))

        return context

    def get_form_kwargs(self):
        kwargs = super(AlteraProcedimentoView, self).get_form_kwargs()
        kwargs['defensorias_responsavel_queryset'] = self.defensorias_responsavel_queryset
        kwargs['defensores_responsavel_queryset'] = self.defensores_responsavel_queryset
        return kwargs

    def post(self, request, *args, **kwargs):
        """
            Altera o procedimento ou propac carregado pela referencia de uuid.
        """
        procedimento = get_object_or_404(Procedimento, uuid=self.kwargs['uuid'])
        form = self.form_class(request.POST, instance=procedimento)
        if form.is_valid():
            procedimento = form.save(commit=False)
            procedimento.defensor_responsavel_nome = procedimento.defensor_responsavel.servidor.nome
            procedimento.defensoria_responsavel_nome = procedimento.defensoria_responsavel.nome

            procedimento.remover_defensorias_acesso()

            if procedimento.acesso == Procedimento.NIVEL_RESTRITO:
                for nucleo in Defensoria.objects.filter(id__in=request.POST.getlist('defensorias_acesso')):
                    procedimento.defensorias_acesso.add(nucleo)

            with reversion.create_revision(atomic=False):
                procedimento.save()
                reversion.set_user(request.user)
                reversion.set_comment(Util.get_comment_save(request.user, procedimento, False))
            return redirect('procedimentos:procedimento_uuid', uuid=procedimento.uuid)

        else:
            messages.error(request, form.errors)
            return redirect('procedimentos:procedimento_index')


class CadastraRemocaoMovimentacaoView(LoginRequiredMixin, View):
    form_class = RemocaoMovimentoForm

    def post(self, request, *args, **kwargs):
        """ Cria a remocao da movimentação aplicando o motivo, data remocao e quem a realizou"""
        form = self.form_class(request.POST)
        movimentacao = Movimento.objects.get(pk=self.kwargs['pk'])

        if form.is_valid():
            movimento_form = form.save(commit=False)
            movimentacao.motivo_remocao = movimento_form.motivo_remocao
            movimentacao.data_remocao = datetime.now()
            movimentacao.removido_por = request.user.servidor

            with reversion.create_revision(atomic=False):
                movimentacao.save()
                reversion.set_user(request.user)
                reversion.set_comment('Remoção ' + Util.get_comment_save(request.user, movimentacao, False))
        else:
            messages.error(request, form.errors)

        return redirect('procedimentos:procedimento_uuid', uuid=movimentacao.procedimento.uuid)


class AlteraSituacaoProcedimentoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        """ Altera a situacao do procedimento e cria a instancia de modificacao para fiz de registro dos dados."""
        procedimento = get_object_or_404(Procedimento, uuid=self.kwargs['uuid'])
        if procedimento:
            procedimento.situacao = request.POST['situacao']
            with reversion.create_revision(atomic=False):
                procedimento.save()
                reversion.set_user(request.user)
                reversion.set_comment('Altera Situação ' + Util.get_comment_save(request.user, procedimento, False))

            SituacaoProcedimento.objects.create(
                procedimento=procedimento,
                situacao=procedimento.situacao,
                motivo=request.POST['motivo'],
                cadastrado_por=request.user.servidor
            )

            return redirect('procedimentos:procedimento_uuid', uuid=procedimento.uuid)
        else:
            return redirect('procedimentos:procedimento_index')


class AlteraAssuntoProcedimentoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        """ Altera o assunto do procedimento """
        procedimento = get_object_or_404(Procedimento, uuid=self.kwargs['uuid'])
        if procedimento:
            procedimento.assunto = request.POST['assunto']
            with reversion.create_revision(atomic=False):
                procedimento.save()
                reversion.set_user(request.user)
                reversion.set_comment('Altera Assunto ' + Util.get_comment_save(request.user, procedimento, False))

            return redirect('procedimentos:procedimento_uuid', uuid=procedimento.uuid)
        else:
            return redirect('procedimentos:procedimento_index')


class JSONProcedimentoSearchView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        filtro = json.loads(request.body)
        response = {'procedimentos': []}

        if filtro:

            data_list = Procedimento.objects.filter(
                Q(ativo=True) & (
                    Q(numero__icontains=filtro['filtro']) |
                    Q(uuid__icontains=filtro['filtro']) |
                    Q(assunto__icontains=filtro['filtro']))
            )

            if 'acesso' in filtro:
                data_list = data_list.filter(
                    Q(acesso=Procedimento.NIVEL_PUBLICO) |
                    (
                        Q(acesso=Procedimento.NIVEL_PRIVADO) &
                        Q(defensoria_responsavel__id__in=filtro['acesso'])
                    ) |
                    (
                        Q(acesso=Procedimento.NIVEL_RESTRITO) &
                        (
                            Q(defensoria_responsavel__id__in=filtro['acesso']) |
                            Q(defensorias_acesso__id__in=filtro['acesso'])
                        )
                    )
                )

            if 'atendimento' in filtro:
                atendimento_filtro = Atendimento.objects.get(
                    Q(numero=filtro['atendimento']) &
                    Q(remarcado=None) &
                    Q(ativo=True)
                )
                if atendimento_filtro.inicial:
                    atendimento_filtro = atendimento_filtro.inicial

                data_list = data_list.filter().exclude(
                    pk__in=atendimento_filtro.procedimentos.all(
                    ).values_list('id', flat=True)
                )

            data = data_list.distinct().values()
            response = dict(procedimentos=list(data))

        return JsonResponse(response)


class VinculaProcedimentoAtendimentoView(PermissaoAcesso, View):
    def vincular_procedimento_ao_atendimento(self, request, adicionar=True):

        filtro = json.loads(request.body)
        response = {'sucesso': False}

        atendimento_filtro = filtro['atendimento'] if 'atendimento' in filtro else None
        uuid_filtro = filtro['uuid'] if 'uuid' in filtro else None

        if uuid_filtro and atendimento_filtro:

            procedimento = Procedimento.objects.get(uuid=uuid_filtro)
            acesso_filtro = filtro['acesso'] if 'acesso' in filtro else None

            # Certificar de desvincular apenas a se estiver na defensoria responsavel ou nas defensorias de acesso
            if acesso_filtro:
                acesso_filtro_set = set(list(acesso_filtro))
                procedimento_defensorias_set = set(procedimento.listar_defensorias_acesso_e_responsavel_ids())
                acesso_negado_set = procedimento_defensorias_set.intersection(acesso_filtro_set)

                if len(acesso_negado_set) == 0:
                    return response

            # Certificar de vincular apenas a um atendimento inicial
            atendimento_filtro = Atendimento.objects.get(
                Q(numero=filtro['atendimento']) &
                Q(remarcado=None) &
                Q(ativo=True)
            )
            if atendimento_filtro.inicial:
                atendimento_filtro = atendimento_filtro.inicial

            procedimento = Procedimento.objects.get(uuid=uuid_filtro)
            with reversion.create_revision(atomic=False):
                reversion.set_user(request.user)
                if adicionar:
                    procedimento.atendimentos.add(atendimento_filtro)
                    reversion.set_comment(
                        'Adicionado atendimento {0} ao vinculo ' + Util.get_comment_save(request.user, procedimento,
                                                                                         True).format(
                            atendimento_filtro))
                else:
                    procedimento.atendimentos.remove(atendimento_filtro)
                    reversion.set_comment(
                        'Removendo atendimento {0} do vinculo ' + Util.get_comment_save(request.user, procedimento,
                                                                                        False).format(
                            atendimento_filtro))
            response = {'sucesso': True}

        return response

    def post(self, request, *args, **kwargs):
        """
            View que recebe por post um numero de atendimento inicial e o uuid de um Procedimento
            e faz o vínculo entre os dois.
        """
        return JsonResponse(self.vincular_procedimento_ao_atendimento(request))


class DesvinculaProcedimentoAtendimentoView(VinculaProcedimentoAtendimentoView):
    def post(self, request, *args, **kwargs):
        """
            View que recebe por post um numero de atendimento inicial e o uuid de um Procedimento
            e realiza o desvinculo de um ao outro.
        """

        return JsonResponse(
            super(DesvinculaProcedimentoAtendimentoView, self).vincular_procedimento_ao_atendimento(request, False))


def get_dados_documento(documento):
    doc = False
    if documento and documento.esta_ativo:
        doc = {
            'pk': documento.pk,
            'pk_uuid': documento.pk_uuid,
            'assunto': documento.assunto,
            'numero': documento.identificador_versao,
            'edit_url': reverse('documentos:editar', kwargs={'slug': documento.pk_uuid}),
        }
    return doc


class MovimentoUpdateView(FormActionViewMixin, AngularMixin, ProcedimentoMixin, UpdateView):
    # representa a view para atualizar um movimento
    model = Movimento
    form_class = EditarMovimentoForm
    template_name = 'propac/editar_movimento.html'
    angular_app = 'novoMovimentoApp'
    angular_controller = 'NovoMovimentoCtrl'
    procedimento_object = None

    def get_queryset(self):
        # obtem o conjunto de dados do modelo movimento
        q = super(MovimentoUpdateView, self).get_queryset()
        q = q.filter(Q(procedimento=self.procedimento_object))
        return q

    def get(self, request, *args, **kwargs):
        ret = super(MovimentoUpdateView, self).get(request, *args, **kwargs)
        # if not self.object.eh_precadastro or self.object.ativo is False:
        if not self.object.eh_precadastro:
            ret = redirect(self.get_success_url())
        return ret

    def get_success_url(self):
        # obtem a url de redirecionamento após o sucesso da atualizacao
        kwargs = {
            'uuid': self.procedimento_object.uuid,
        }

        return reverse_lazy('procedimentos:procedimento_uuid', kwargs=kwargs)

    def get_initial(self):
        # retorna os dados iniciais para o formulario
        initial = super(MovimentoUpdateView, self).get_initial()
        initial['procedimento'] = self.procedimento_object
        return initial

    def get_form_action(self):
        # obtem a url de acao do formulario
        kwargs = {
            'uuid': self.procedimento_object.uuid,
            'pk': self.object.pk
        }
        return reverse('procedimentos:editar_movimento',
                       kwargs=kwargs)

    def get_context_data(self, **kwargs):
        # obtem os dados de contexto para a renderizacao do template
        context = super(MovimentoUpdateView, self).get_context_data(**kwargs)
        context['procedimento_object'] = self.procedimento_object
        context['documento_propac_form'] = CriarDocumentoPropacForm()
        movimento = self.object

        # criacao dos dados de documentos
        criar_documento_propac_url_kwargs = {
            'uuid': self.procedimento_object.uuid,
            'pk': movimento.pk
        }
        context['documento_propac_form_action'] = reverse('procedimentos:procedimento_criar_documento_propac',
                                                          kwargs=criar_documento_propac_url_kwargs)
        context['cancelar_movimento_form_action'] = reverse('procedimentos:cancelar_movimento',
                                                            kwargs=criar_documento_propac_url_kwargs)
        dados = self.object.documentos.select_related('documento').order_by('pk').filter(ativo=True)

        dados = [
            {
                'documento_propac_pk': d.pk,
                'cancelar_doc_propac_url': reverse('procedimentos:cancelar_documentopropac',
                                                   kwargs={
                                                       'uuid': self.procedimento_object.uuid,
                                                       'pk_movimento': movimento.pk,
                                                       'pk_docpropac': d.pk
                                                   }),

                'anexo': d.anexo_original_nome_arquivo if d.anexo and d.anexo_original_nome_arquivo else False,
                'tipo_anexo': d.tipo_anexo.nome if d.tipo_anexo else None,
                'novo_doc': False,
                'documento': get_dados_documento(d.documento)

            }
            for d in dados]
        # obtem os tipos de anexo
        tipos_anexo = dict(TipoAnexoDocumentoPropac.objects.all().filter(ativo=True).order_by('nome').values_list('pk', 'nome'))  # noqa
        atendimentos = []  # obtem os atendimentos relacionados ao procedimento
        for atendimento in self.procedimento_object.atendimentos.all().order_by('numero'):
            for documento in atendimento.documentos:
                if documento.ativo:
                    doc = {
                        'id_documento': documento.pk,
                        'numero': atendimento.numero,
                        'ativo': True,
                        'modo': "atendimento",
                        'novo_doc': False,
                        'tipo_anexo': '',
                        'status': {},
                    }
                    if documento.documento_online and (documento.documento_online and
                                                       documento.documento_online.eh_modelo is False and
                                                       documento.documento_online.esta_ativo is True):
                        doc['documento'] = str(documento.documento_online_id)
                        doc['anexo_str'] = '{}v{} - {}'.format(
                            documento.documento_online.document_number,
                            documento.documento_online.document_version_number,
                            documento.documento_online.assunto
                        )
                        atendimentos.append(doc)
                    else:
                        doc['anexo_str'] = documento.nome
                        doc['anexo'] = documento.arquivo.path

                        atendimentos.append(doc)

        documentos_tarefas = recupera_documentos_tarefas(movimento)
        # monta o json com os dados necessarios
        resultr = json.dumps(
            {
                'documentos': list(dados),
                'tipos_anexo': tipos_anexo,
                'atendimentos': list(atendimentos),
                'documentos_tarefas': list(documentos_tarefas)
            }, cls=DjangoJSONEncoder
        )

        context['documentos_json'] = resultr
        return context

    def form_invalid(self, form):  # lida com o caso de um formulario invalido
        if not self.object.eh_precadastro or self.object.ativo is False:
            return redirect(self.get_success_url())
        return super(MovimentoUpdateView, self).form_invalid(form)

    def form_valid(self, form):  # lida com um formulario valido
        if not self.object.eh_precadastro or self.object.ativo is False:
            return redirect(self.get_success_url())

        movimentacao = form.save(commit=False)
        movimentacao.cadastrado_por = self.request.user.servidor
        movimentacao.eh_precadastro = False
        movimentacao.volume = movimentacao.numero_ultimo_volume()
        movimentacao.ordem_volume = movimentacao.ordem_ultimo_volume()
        documentos_propac_list = movimentacao.documentos.select_related('tipo_anexo').order_by('pk').filter(ativo=True)
        for index, doc_propac in enumerate(documentos_propac_list, 1):
            doc_propac.nome = '{}{}'.format(doc_propac.tipo_anexo.nome, index)

        bulk_update(documentos_propac_list, update_fields=['nome'], batch_size=1000)

        with reversion.create_revision(atomic=False):
            ret = super(MovimentoUpdateView, self).form_valid(form)
            reversion.set_user(self.request.user)
            reversion.set_comment(Util.get_comment_save(self.request.user, movimentacao, True))
        return ret


class CancelarMovimento(ProcedimentoMixin, DeleteView):  # view para cancelar um movimento
    model = Movimento
    template_name = 'propac/movimento_confirm_delete.html'

    def get_queryset(self):  # obtem o conjunto de dados do modelo movimento
        q = super(CancelarMovimento, self).get_queryset()
        q = q.filter(Q(procedimento=self.procedimento_object))
        return q

    def get_success_url(self):  # obtem a url de redirecionamento após o sucesso do cancelamento
        kwargs = {
            'uuid': self.procedimento_object.uuid,
        }

        return reverse_lazy('procedimentos:procedimento_uuid', kwargs=kwargs)

    def get_object(self, queryset=None):  # obtem o objeto movimento a ser cancelado
        obj = super(CancelarMovimento, self).get_object(queryset=queryset)
        return obj

    def delete(self, request, *args, **kwargs):  # funcao para lidar com a solicitacao de exclusao
        movimentacao = self.get_object()
        movimentacao_pk = movimentacao.pk
        if movimentacao:
            if movimentacao.ativo:
                if movimentacao.eh_precadastro:
                    movimentacao.cancelar_movimentacao('movimentacao cancelada', request.user)
                if request.is_ajax():
                    return JsonResponse({'success': 'ok', 'pk_movimento': movimentacao_pk})

        success_url = self.get_success_url()

        return HttpResponseRedirect(success_url)


class CancelarDocumentoPropac(ProcedimentoMixin, MovimentoMixin, DeleteView):
    # representa a view para cancelar um Documentoprocap
    pk_url_kwarg = 'pk_docpropac'
    model = DocumentoPropac
    template_name = 'propac/documentopropac_confirm_delete.html'

    def get_queryset(self):  # obtem o conjunto de dados do modelo
        q = super(CancelarDocumentoPropac, self).get_queryset()
        q = q.filter(Q(movimento=self.movimento_object.pk))
        return q

    def get_success_url(self):  # obtem a url de redirecionamento após o sucesso do cancelamento
        kwargs = {
            'uuid': self.procedimento_object.uuid,
            'pk': self.movimento_object.pk
        }

        return reverse_lazy('procedimentos:editar_movimento', kwargs=kwargs)

    def delete(self, request, *args, **kwargs):  # funcao para lidar com a solicitacao de exclusao
        documentopropac = self.get_object()
        pk_deletado = documentopropac.pk
        if documentopropac.ativo:
            if Documento.objects.filter(documento_online=documentopropac.documento).exists():
                documentopropac.documento = None
                documentopropac.save()
            documentopropac.delete()
        if request.is_ajax():
            return JsonResponse({'success': 'ok', 'pk': pk_deletado})

        success_url = self.get_success_url()

        return HttpResponseRedirect(success_url)


class CriarDocumentoPropac(CreatePopupMixin, ProcedimentoMixin, BaseCreateView):
    # representa a view para criar um documentopropac
    model = DocumentoPropac
    form_class = CriarDocumentoPropacForm
    success_url = '/'
    procedimento_object = None
    movimento_object = None

    def get_movimento_object(self):
        # obtem o objeto movimento relacionado ao documento propac
        movimento_pk = self.kwargs.get('pk', None)
        return Movimento.objects.get(pk=movimento_pk)

    def dispatch(self, request, *args, **kwargs):
        # funcao para lidar com a solicitacao antes de ser tratada pela view
        self.movimento_object = self.get_movimento_object()
        if request.POST.get('anexo') and isinstance(request.POST.get('anexo'), str):
            f = open(request.POST.get('anexo'), 'rb')
            request.FILES['anexo'] = File(f, name=os.path.basename('{}.{}'.format(request.POST.get('anexo_str'),
                                                                                  f.name.split('.')[-1])))

        return super(CriarDocumentoPropac, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):  # obtem os dados de contexto para a renderizacao do template
        context = super(CriarDocumentoPropac, self).get_context_data(**kwargs)
        context['documento_propac_form'] = context['form']
        criar_documento_propac_url_kwargs = {
            'uuid': self.procedimento_object.uuid,
            'pk': self.movimento_object.pk
        }
        context['documento_propac_form_action'] = reverse('procedimentos:procedimento_criar_documento_propac',
                                                          kwargs=criar_documento_propac_url_kwargs)
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.movimento = self.movimento_object
        instance.cadastrado_por = self.request.user.servidor

        # ignora a resposta e responde via Ajax
        super(CriarDocumentoPropac, self).form_valid(form)
        # if self.request.is_ajax():
        anexo = False
        if form.instance.anexo and form.instance.anexo_original_nome_arquivo:
            anexo = form.instance.anexo_original_nome_arquivo

        data = {
            'success': True,
            'documento_propac_pk': getattr(form.instance, 'pk'),
            'cancelar_doc_propac_url': reverse('procedimentos:cancelar_documentopropac',
                                               kwargs={
                                                   'uuid': self.procedimento_object.uuid,
                                                   'pk_movimento': self.movimento_object.pk,
                                                   'pk_docpropac': getattr(form.instance, 'pk')
                                               }),
            'anexo': anexo,
            'tipo_anexo': form.instance.tipo_anexo.nome if form.instance.tipo_anexo else None,
            'novo_doc': True,
            'documento': get_dados_documento(form.instance.documento) if form.instance.documento else False

        }

        return JsonResponse(data, status=200)
        # return response

    def form_invalid(self, form):
        # ignora a resposta e responde via Ajax
        super(CriarDocumentoPropac, self).form_invalid(form)
        # if self.request.is_ajax():
        return JsonResponse({'errors': form.errors}, status=403)
        # return response


class MovimentoTipoAutocomplete(autocomplete.Select2QuerySetView):
    # representa a view para autocompletar o tipo do Movimento
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(MovimentoTipoAutocomplete, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return MovimentoTipo.none()

        qs = MovimentoTipo.objects.all()

        if self.q:
            # qs = qs.filter(Q(titulo__unaccent__icontains=self.q.upper()))
            qs = qs.filter(Q(nome__icontains=self.q) | Q(codigo=self.q))

            # qs = qs.annotate(full_name=Concat('first_name', Value(' '), 'last_name', output_field=CharField()))
            # qs = qs.filter(full_name__icontains=self.q)
        return qs

    def get_result_label(self, result):
        # obtem o rotulo do resultado do autocompletar
        a = result.nome
        return six.text_type(a)


class TarefasPropacViewSet(SerializerMixin,
                           mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    # representa a view para manipulacao das tarefas do propac                          
    permission_classes = (DjangoModelPermissions,)
    filter_backends = (MovimentoFilterBackend,)
    serializer_class = None
    serializer_classes = {
        "retrieve": TarefaDetailSerializer,
        "list": TarefaListSerializer,
        "create": TarefaCreateSerializer
    }

    queryset = Tarefa.objects.ativos().order_by(
        '-data_finalizado',
        '-status',
        'prioridade',
        'data_inicial',
        'data_final',
        'id'
    )

    @action(methods=['post'], detail=True, permission_classes=(DjangoModelPermissions,))
    def finalizar_tarefa(self, request, pk=None):
        try:
            tarefa = finalizar_tarefa(request.user.servidor, int(pk))
            return JsonResponse({'success': True, 'id': tarefa.pk})
        except (TarefaNaoEncontradaException, TarefaErroException) as error:
            return JsonResponse({'success': False, 'message': error})

    def destroy(self, request, *args, **kwargs):
        # funcao para exlcuir uma tarefa
        try:
            obj = self.get_object()
            excluir_tarefa(obj, request.user.servidor)

            return response.Response({}, status.HTTP_204_NO_CONTENT)

        except (TarefaNaoEncontradaException, TarefaErroException) as error:
            return response.Response({'success': False, 'message': error}, status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def defensorias(self, request):
        # obter defensorias
        defensorias = listar_defensorias(request.user)
        return response.Response(defensorias)

    def perform_create(self, serializer):
        # executar a criacao de uma tarefa
        serializer.save(cadastrado_por=self.request.user.servidor)


@login_required
def responder_tarefa_view(request, *args, **kwargs):
    # responder uma tarefa
    user = request.user
    tarefa_id = request.POST.get('tarefa')
    resposta = request.POST.get('resposta')
    status = int(request.POST.get('status'))

    resposta = responder_tarefa(user, tarefa_id, resposta, status,
                                request.POST, request.FILES)

    if resposta:
        return redirect(request.POST['next'])

    raise Http404


@login_required
def movimento_tarefas_view(request, *args, **kwargs):
    # visualizar as tarefas de um movimento
    atendimento_permissao = True
    acesso_concedido = True
    angular = "PropacTarefaCtrl"

    propac = kwargs.get("uuid")
    movimento = kwargs.get("pk")

    return render(request=request, template_name="propac/tarefas_propac.html", context=locals())


class DocumentoPropacViewset(mixins.CreateModelMixin,
                             viewsets.GenericViewSet):
    # classe que representa a view para criar um documentopropac                             
    permission_classes = (AllowAny,)
    serializer_class = DocumentoPropacSerializer
    queryset = DocumentoPropac.objects.all()

    def create(self, request, *args, **kwargs):
        # funcao para criar um documentopropac
        request_data = deepcopy(request.data)
        documentos = cria_documentos_propac(request_data, request.user.servidor)
        serializer = DocumentoPropacSerializer(documentos, many=True)

        return response.Response(serializer.data, status=status.HTTP_201_CREATED)


@never_cache
@login_required
def get_movimento_documentos(request, pk):
    """
        Busca os documentos do movimento
        Deixar desabilitado a opção de associar documentos GED as tarefas propac
    """
    print('apagar movimento documentos')
    documentos = Tarefa.objects.get(pk=pk).documento

    if not documentos:
        return JsonResponse({'documentos': tuple()})

    documentos = documentos.select_related(
        'documento_online',
        'cadastrado_por__usuario',
        'enviado_por__usuario',
    )

    documentos_list = []

    for documento in documentos:
        documentos_list.append({
            'id': documento.id,
            'nome': documento.nome,
            'arquivo': documento.arquivo.url if documento.arquivo else '',
            'data_cadastro': documento.data_cadastro,
            'cadastrado_por_nome': documento.cadastrado_por.nome if documento.cadastrado_por else None,
            'cadastrado_por_username': documento.cadastrado_por.usuario.username if documento.cadastrado_por else None,
            'data_enviado': documento.data_enviado,
            'enviado_por_nome': documento.enviado_por.nome if documento.enviado_por else None,
            'enviado_por_username': documento.enviado_por.usuario.username if documento.enviado_por else None,
            'documento_online': {
                'id': documento.documento_online_id,
                'assunto': documento.documento_online.assunto,
                'identificador_versao': documento.documento_online.identificador_versao
            } if documento.documento_online else None,
            'pendente': documento.pendente,
        })

    return JsonResponse({'documentos': documentos_list})
