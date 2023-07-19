# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from collections import OrderedDict

# Bibliotecas de terceiros
from constance import config
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

# Solar
from core.views import ReversionMixin, SoftDeleteView

# Modulos locais
from .models import Local, Relatorio
from . import forms


@never_cache
@login_required
def index(request):

    return render(
        request=request,
        template_name="relatorios/index.html",
        context={
            'config': config,
            'angular': 'RelatorioIndexCtrl'
        }
    )


@never_cache
@login_required
def listar(request):

    grupos = Local.objects.filter(
        pagina=Local.PAGINA_RELATORIO_LISTAR
    ).order_by('posicao', 'titulo')

    lista = []

    for grupo in grupos:

        relatorios = []
        for relatorio in grupo.relatorios.filter(papeis=request.user.servidor.papel).ativos():
            relatorios.append(relatorio.to_dict())

        lista.append({
            'nome': grupo.titulo,
            'classe_css': grupo.classe_css,
            'itens': relatorios
        })

    return JsonResponse(lista, safe=False)


class RelatorioListView(ListView):
    queryset = Relatorio.objects.ativos().select_related(
        'cadastrado_por',
        'modificado_por'
    ).prefetch_related(
        'locais',
        'papeis'
    )
    model = Relatorio
    paginate_by = 50
    template_name = "relatorios/buscar.html"

    def get_context_data(self, **kwargs):
        context = super(RelatorioListView, self).get_context_data(**kwargs)
        context.update({
            'form': forms.BuscarRelatorioForm(self.request.GET)
        })
        return context

    def get_queryset(self):

        queryset = super(RelatorioListView, self).get_queryset()
        q = Q()

        if self.request.GET.get('tipo'):
            q &= Q(tipo=self.request.GET.get('tipo'))

        if self.request.GET.get('local'):
            q &= Q(locais=self.request.GET.get('local'))

        if self.request.GET.get('papel'):
            q &= Q(papeis=self.request.GET.get('papel'))

        if self.request.GET.get('filtro'):
            q &= Q(titulo__icontains=self.request.GET.get('filtro'))

        return queryset.filter(q)


class RelatorioMixin(ReversionMixin, SuccessMessageMixin):
    model = Relatorio
    success_message = '%(titulo)s salvo com sucesso!'

    def get_parametros_ordenados(self, parametros):

        parametros = dict(parametros)
        parametros.pop('extra', None)  # remove parametros extra
        parametros.pop('aliases', None)  # remove parametros de aliases

        for param in parametros:
            parametros[param] = self.object.parametros.get(param, False)

        # reordena parâmetros
        ordenado = OrderedDict()

        # inclui parâmetros de data no início
        for param in ['ano', 'mes', 'data_inicial', 'data_final']:
            if param in parametros:
                ordenado[param] = parametros.pop(param)

        # inclui demais parâmetros em ordem alfabética
        for param in sorted(parametros.keys()):
            ordenado[param] = parametros[param]

        return ordenado

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            titulo=self.object.titulo,
        )


class RelatorioCreateMixin(RelatorioMixin):
    template_name = 'relatorios/cadastrar.html'

    def form_valid(self, form):

        self.object = form.save(commit=False)
        parametros = {}

        # mantém parâmetros personalizados
        for param in ['aliases', 'defaults', 'extra']:
            if param in self.object.parametros:
                parametros[param] = self.object.parametros[param]

        # inclui parâmetros disponíveis dos locais escolhidos no relatório
        locais = Local.objects.filter(id__in=self.request.POST.getlist('locais'))
        for local in locais:
            for param in local.parametros:
                parametros[param] = self.object.parametros.get(param, False)

        self.object.parametros = parametros

        return super(RelatorioCreateMixin, self).form_valid(form)

    def get_context_data(self, **kwargs):

        context = super(RelatorioCreateMixin, self).get_context_data(**kwargs)

        parametros = {}
        parametrizavel = False

        if self.object:

            # verifica se relatório é parametrizável
            parametrizavel = self.object.locais.parametrizaveis().exists()

            # recupera lista de parâmetros do relatório
            if isinstance(self.object.parametros, dict):
                parametros = self.object.parametros

        # esconde parâmetros de controle
        parametros.pop('aliases', None)
        parametros_extra = parametros.pop('extra', None)

        # reordena parâmetros de forma amigável
        parametros = self.get_parametros_ordenados(parametros)

        context.update({
            'parametros': parametros,
            'parametros_extra': parametros_extra if isinstance(parametros_extra, list) else {},
            'parametrizavel': parametrizavel,
        })

        return context

    def get_success_url(self):

        kwargs = {'pk': self.object.pk}

        # se relatório parametrizável, direciona para página de parametrização
        if self.object.tipo == Relatorio.TIPO_JASPER and self.object.locais.parametrizaveis().exists():
            return reverse('relatorios:parametrizar', kwargs=kwargs)
        else:
            return reverse('relatorios:editar', kwargs=kwargs)


class RelatorioCreateView(RelatorioCreateMixin, CreateView):
    form_class = forms.EditarRelatorioNaoParametrizavelForm


class RelatorioParametrizavelCreateView(RelatorioCreateMixin, CreateView):
    form_class = forms.EditarRelatorioParametrizavelForm


class RelatorioUpdateView(RelatorioCreateMixin, UpdateView):
    def get_form(self, form_class=None):
        if self.get_object().tipo == Relatorio.TIPO_METABASE:
            form_class = forms.EditarRelatorioMetabaseForm
        elif self.get_object().locais.parametrizaveis().exists():
            form_class = forms.EditarRelatorioParametrizavelForm
        else:
            form_class = forms.EditarRelatorioNaoParametrizavelForm

        return form_class(**self.get_form_kwargs())


class RelatorioParametrosUpdateView(RelatorioMixin, UpdateView):
    form_class = forms.ParametrizarRelatorioForm
    template_name = 'relatorios/parametrizar.html'

    def form_valid(self, form):

        self.object = form.save(commit=False)

        # recupera parâmetros armazenados no banco
        parametros = self.get_object().parametros

        # recupera nome dos parametros marcados no template
        marcados = self.request.POST.getlist('parametro', {})

        # atualiza lista de parâmetros de acordo com os parâmetros marcados
        for param in self.get_parametros_ordenados(self.object.locais.first().parametros):
            if param in marcados:
                parametros[param] = True
            else:
                parametros[param] = False

        # se ano ou mês, marca ano e desmarca data_inicial e data_final
        if parametros.get('ano') or parametros.get('mes'):
            parametros['ano'] = True
            parametros['data_inicial'] = False
            parametros['data_final'] = False

        # se data inicial ou data final, força a marcação dos dois
        if parametros.get('data_inicial') or parametros.get('data_final'):
            parametros['data_inicial'] = True
            parametros['data_final'] = True

        # atualiza valores do relatório
        self.object.parametros = parametros

        return super(RelatorioParametrosUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(RelatorioParametrosUpdateView, self).get_context_data(**kwargs)

        local = self.object.locais.first()
        parametros = self.get_parametros_ordenados(local.parametros)  # todos campos disponíveis no local
        parametros_extra = self.object.parametros.get('extra')  # campos personalizados do relatório

        context.update({
            'local': local,
            'parametros': parametros,
            'parametros_extra': parametros_extra if isinstance(parametros_extra, list) else {},
        })

        return context

    def get_success_url(self):
        kwargs = {'pk': self.object.pk}
        return reverse('relatorios:parametrizar', kwargs=kwargs)


class RelatorioDeleteView(ReversionMixin, SoftDeleteView):
    model = Relatorio
    template_name = 'core/excluir_evento.html'

    def get_success_url(self):
        return reverse('relatorios:buscar')


class RelatorioVisualizarView(DetailView):
    model = Relatorio
    template_name = "relatorios/visualizar.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context.update({
            'iframeUrl': self.get_object().get_metabase_url()
        })

        return context


class RelatorioMetabaseCreateView(RelatorioCreateMixin, CreateView):
    form_class = forms.EditarRelatorioMetabaseForm

    def form_valid(self, form):
        object = form.save(commit=False)
        object.tipo = Relatorio.TIPO_METABASE
        object.save()

        return super().form_valid(form)
