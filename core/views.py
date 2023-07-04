# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging
import json
from typing import Optional

# Bibliotecas de terceiros
import reversion
from constance import config
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.forms import HiddenInput, ChoiceField, Select
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from django.utils import timezone
from django.views.generic.base import RedirectView
from django.views.generic.edit import BaseCreateView, DeleteView, UpdateView
from django.templatetags.static import static

from djdocuments.models import Documento as DocumentoGED
from djdocuments.views.documentos import DocumentoCriar

# Solar
from contrib.models import Util
from notificacoes.tasks import (
    notificar_processo_de_indeferimento
)
# Modulos locais
from .models import Processo, Evento, Documento, TipoDocumento, TipoEvento, Classe
from . import forms
from core.core_utils import permissao_editar_sigilo_documento
from contrib.models import HistoricoLogin
from contrib.utils import ip_visitante
logger = logging.getLogger(__name__)


@login_required
def index(request):

    if request.session.get('auditoria_login', True):
        info_navegador = '{} - {}'.format(request.META.get('HTTP_USER_AGENT', ''), request.META.get('REMOTE_HOST', ''))
        historico = HistoricoLogin.objects.create(
            endereco_ip=ip_visitante(request),
            info_navegador=info_navegador,
        )
        request.session['auditoria_login'] = False
        request.session['auditoria_login_id'] = historico.id

    servidor = request.user.servidor
    request.session['comarca'] = servidor.comarca.id

    if request.user.is_superuser:
        return redirect('perfil_comarcas')
    elif request.user.has_perm(perm='atendimento.view_defensor'):
        return redirect('atendimento_perfil')
    elif request.user.has_perm(perm='atendimento.view_recepcao'):
        return redirect('recepcao_index')
    elif request.user.has_perm(perm='atendimento.view_129'):
        return redirect('precadastro_index')
    elif request.user.has_perm(perm='relatorios.view_relatorios'):
        return redirect('relatorios:index')
    else:
        return redirect('atualizacoes_perfil')


@login_required
def home(request):
    return render(request=request, template_name="index.html", context=locals())


def senhasucesso(request):
    messages.info(request, u'Senha alterada com sucesso!')
    return redirect('login')


class AjaxableResponseMixin(object):
    """
    https://docs.djangoproject.com/en/1.8/topics/class-based-views/generic-editing/#ajax-example
    https://docs.djangoproject.com/en/1.8/topics/class-based-views/mixins/#more-than-just-html
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'success': True,
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


class ReversionMixin(object):

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        # armazena dados de auditoria ao desativar registro
        with reversion.create_revision(atomic=False):
            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_delete(request.user, self.object))
            self.object.desativar(usuario=request.user)

        return redirect(self.get_success_url())

    def form_valid(self, form):

        eh_novo = True

        if self.object and self.object.id:
            eh_novo = False

        # armazena dados de auditoria ao criar/editar registro
        with reversion.create_revision(atomic=False):
            resposta = super(ReversionMixin, self).form_valid(form)
            reversion.set_user(self.request.user)
            reversion.set_comment(Util.get_comment_save(self.request.user, self.object, eh_novo))

        return resposta


class SoftDeleteView(DeleteView):
    template_name = 'core/excluir_evento.html'

    def get_context_data(self, **kwargs):
        context = super(SoftDeleteView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next')

        return context

    def get_success_url(self):
        if self.request.POST.get('next'):
            return self.request.POST.get('next')
        else:
            return reverse('index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.desativar(usuario=request.user)
        return redirect(self.get_success_url())


class ProcessoDeleteView(SoftDeleteView):
    slug_field = 'uuid'
    model = Processo


class EventoCreateView(BaseCreateView):
    model = Evento
    form_class = forms.NovoEventoForm
    incluir_documentos = True

    def post(self, request, *args, **kwargs):

        processo = get_object_or_404(Processo, uuid=self.kwargs['processo_uuid'], desativado_em=None)
        tipo = self.kwargs['tipo']

        # captura flag para verificar se deve ou não incluir documentos
        self.incluir_documentos = eval(request.POST.get('incluir_documentos', 'True'))

        self.object = Evento(
            processo=processo,
            numero=processo.eventos.count() + 1,
            data_referencia=timezone.now(),
            em_edicao=self.incluir_documentos,  # só vai ficar em edição se precisar incluir documentos
        )

        form = self.form_class(request.POST, instance=self.object)

        if tipo == TipoEvento.TIPO_ENCAMINHAMENTO:
            form.fields['setor_encaminhado'].required = True

        if form.is_valid():

            self.object = form.save()

            # se não está em edição, registra encaminhamento do processo
            if not self.object.em_edicao and self.object.setor_encaminhado:
                self.object.processo.setor_encaminhado = self.object.setor_encaminhado
                self.object.processo.save()
                if config.NOTIFICAR_PROCESSO_DE_INDEFERIMENTO:
                    notificar_processo_de_indeferimento.apply_async(
                        kwargs={
                            'user_remetente_id': request.user.id,
                            'processo_id': processo.id
                        },
                        queue='sobdemanda'
                    )
            return redirect(self.get_success_url())

        else:
            messages.error(request, form.errors)
            return redirect(request.POST.get('next'))

    def get_success_url(self):
        if self.object.em_edicao:
            kwargs = {'processo_uuid': self.kwargs['processo_uuid'], 'pk': self.object.pk}
            return reverse('core:evento_editar', kwargs=kwargs)
        else:
            return self.request.POST.get('next')


class EventoDeleteView(SoftDeleteView):
    model = Evento

    def delete(self, request, *args, **kwargs):

        evento = self.get_object()
        processo = evento.processo

        if evento.setor_encaminhado == processo.setor_encaminhado:
            processo.setor_encaminhado = None
            processo.save()

        return super().delete(request, *args, **kwargs)


class EventoUpdateView(AjaxableResponseMixin, UpdateView):
    """
    Atualiza informações do evento sem encerrar edição
    """
    context_object_name = 'evento'
    form_class = forms.EditarEventoForm
    model = Evento
    slug_field = 'id'
    slug_url_kwarg = 'pk'
    template_name = 'core/novo_evento.html'
    minimo_documentos = 0

    def form_invalid(self, form):
        return super(EventoUpdateView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(EventoUpdateView, self).get_context_data(**kwargs)
        context['minimo_documentos'] = self.minimo_documentos
        context['form'] = self.get_form(self.form_class)
        context['Processo'] = Processo
        context['TipoEvento'] = TipoEvento

        if self.object.processo:
            context['processo'] = self.object.processo
            context['setor'] = self.object.processo.setor_atual

        return context

    def get_queryset(self):
        queryset = super(EventoUpdateView, self).get_queryset()
        queryset = queryset.filter(em_edicao=True, desativado_em=None)
        return queryset

    def get_success_url(self):
        if self.request.POST.get('next'):
            return self.request.POST.get('next')
        else:
            kwargs = {'pk': self.object.pk}
            return reverse('core:evento_editar', kwargs=kwargs)


class EventoUpdateAndCloseView(EventoUpdateView):
    """
    Atualiza informações do evento e encerra edição
    """

    def get_success_url(self):
        return self.request.POST.get('next')

    def form_valid(self, form):

        evento = form.save(commit=False)
        evento.data_referencia = timezone.now()
        evento.em_edicao = False
        evento.save()

        if evento.setor_encaminhado:
            evento.processo.setor_encaminhado = evento.setor_encaminhado
            evento.processo.save()

            if config.NOTIFICAR_PROCESSO_DE_INDEFERIMENTO:
                notificar_processo_de_indeferimento.apply_async(
                    kwargs={
                        'user_remetente_id': self.request.user.id,
                        'processo_id': self.object.processo.id
                        },
                    queue='sobdemanda'
                    )

        self.object = evento

        return super(EventoUpdateAndCloseView, self).form_valid(form)


class DocumentoRenameView(UpdateView):
    """
    Atualiza nome do documento
    """
    model = Documento
    form_class = forms.RenomearDocumentoForm

    def get_success_url(self):
        return self.request.POST.get('next')

    def form_valid(self, form):

        documento = form.save(commit=False)
        documento.save()

        if documento.documento:
            documento.documento.assunto = documento.nome
            documento.documento.save()

        self.object = documento

        return super(DocumentoRenameView, self).form_valid(form)

    def form_invalid(self, form):
        for k, v in form.errors.items():
            messages.error(self.request, u'{0}: {1}'.format(k, v))
        return redirect(self.request.META.get('HTTP_REFERER', '/'))


@login_required
def encaminhar_processo(request, processo_uuid):
    pass


@login_required
def vincular_documento_evento(request, pk, document_pk):

    evento = Evento.objects.ativos().filter(pk=pk).first()
    documento = DocumentoGED.objects.filter(pk=document_pk).first()

    if evento and documento:
        Documento.objects.create(
            processo=evento.processo,
            evento=evento,
            tipo=TipoDocumento.objects.first(),  # todo: tipo padrao,
            documento=documento,
            nome=documento.assunto,
        )

    return redirect('core:evento_editar', evento_numero=evento.numero)


@login_required
def upload_documento(request, pk):

    def get_nivel_sigilo() -> int:
        post_request = request.POST
        return (
            int(post_request.get('nivel_sigilo'))
            if post_request.get('nivel_sigilo')
            else 0
        )

    evento = Evento.objects.ativos().get(pk=pk)

    if request.POST.get('id'):
        documento = Documento.objects.get(id=request.POST.get('id'))
    else:
        documento = Documento(
            processo=evento.processo,
            evento=evento,
            tipo=TipoDocumento.objects.first(),  # todo: tipo padrao
            nome=request.POST.get('nome'),
            nivel_sigilo=get_nivel_sigilo()
        )

    form_arquivo = forms.DocumentoUploadForm(
        request.POST,
        request.FILES,
        instance=documento
    )

    if form_arquivo.is_valid():
        documento = form_arquivo.save()

    if request.POST.get('next'):
        return redirect(request.POST.get('next'))
    else:
        return redirect('core:evento_editar', pk=evento.pk)


@login_required
def excluir_documento(request, pk):

    documento = get_object_or_404(
        Documento,
        id=request.POST.get('id'),
        evento__pk=pk,
        evento__em_edicao=True
    )

    documento.desativar(usuario=request.user)
    messages.success(request, u'Documento excluído com sucesso!')

    if request.POST.get('next'):
        return redirect(request.POST.get('next'))
    else:
        return redirect('core:evento_editar', pk=pk)


@login_required
def listar_classes(request):

    if request.method == 'POST' and request.is_ajax():
        data = json.loads(request.body)
    else:
        data = request.GET.dict()

    classes = Classe.objects.ativos().order_by(
        'nome_norm'
    ).distinct(
        'nome_norm'
    ).values(
        'id', 'nome', 'tipo'
    )

    for key, value in iter(data.items()):
        classes = classes.filter(**{key: value})

    return JsonResponse(list(classes), safe=False)


class DocumentoCriarParaEvento(DocumentoCriar):

    def dispatch(self, request, *args, **kwargs):

        # carrega evento que será vinculado a partir dos parametros da url
        self.evento = Evento.objects.get(
            pk=self.kwargs.get('pk')
        )

        return super(DocumentoCriarParaEvento, self).dispatch(request, *args, **kwargs)

    def get_form_action(self):
        return reverse(
            'core:criar_documento',
            kwargs={
                'pk': self.kwargs.get('pk'),
            }
        )

    def _filtra_sigilo(self) -> tuple:
        PUBLICO = Documento.SIGILO_0
        PRIVADO = Documento.SIGILO_1
        return tuple(
            filter(
                lambda sigilo: sigilo[0] == PUBLICO or sigilo[0] == PRIVADO,
                Documento.LISTA_SIGILO
            )
        )

    def get_form(self, form_class=None):

        form = super(DocumentoCriarParaEvento, self).get_form(form_class=form_class)

        # impede escolha do grupo dono do documento na interface
        form.fields['grupo'].widget = HiddenInput()
        form.fields['nivel_sigilo'] = ChoiceField(
            initial=Documento.SIGILO_0,
            choices=((None, '< Selecione um nível de sigilo >'),) + self._filtra_sigilo(),
            required=False,
            widget=Select(
                attrs={'class': 'span1 ativar-select2'}))

        return form

    def get_initial(self):

        result = super(DocumentoCriarParaEvento, self).get_initial()

        # define setor criacao como grupo dono do documento
        result['grupo'] = self.evento.setor_criacao

        return result

    def form_valid(self, form):

        result = super(DocumentoCriarParaEvento, self).form_valid(form)

        nivel_sigilo = int(form['nivel_sigilo'].value()) if form['nivel_sigilo'].value() else 0
        Documento.objects.create(
            processo=self.evento.processo,
            evento=self.evento,
            tipo=TipoDocumento.objects.first(),  # todo: tipo padrao
            documento=self.object,
            nome=self.object.assunto,
            nivel_sigilo=nivel_sigilo
        )

        return result


class FaviconView(RedirectView):
    url = static('img/favicon.ico')
    permanent = True


favicon_view = FaviconView.as_view()


def _is_nivel_sigilo_valido(nivel_sigilo: Optional[int]):
    return nivel_sigilo in [item_nivel[0] for item_nivel in Documento.LISTA_SIGILO]


@login_required
def altera_sigilo_documento(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        nivel_sigilo = request_data.get('nivel_sigilo', None)
        if not nivel_sigilo or not _is_nivel_sigilo_valido(int(nivel_sigilo)):
            return JsonResponse({"message": "Nível de sigilo inválido."},
                                safe=False, status=400)
        documento = Documento.objects.filter(id=int(request_data.get('id', 0))).first()
        if not documento:
            return JsonResponse({"message": "O documento informado não existe."},
                                safe=False, status=404)
        if not permissao_editar_sigilo_documento(documento, request.user.servidor):
            return JsonResponse({"message": "Você não tem permissão para alterar o nível de sigilo deste documento."},
                                safe=False, status=403)
        documento.nivel_sigilo = nivel_sigilo
        documento.save()
        return JsonResponse({"message": "Nível de sigilo alterado com sucesso."},
                            safe=False, status=200)
    return JsonResponse({"message": "Método não permitido."}, safe=False, status=405)
