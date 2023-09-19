# -*- coding: utf-8 -*-
from django.db.models import Case, IntegerField, Max, Q, Sum, Value, When
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from contrib.models import DefensoriaVara
from procapi_client.models import SistemaWebService, TipoEvento
from processo.processo.models import FaseTipo

from . import forms


class DefensoriaVaraListView(ListView):
    model = DefensoriaVara
    paginate_by = 50
    template_name = 'processo/associacao/defensoria_vara_buscar.html'

    def get_context_data(self, **kwargs):

        context = super(DefensoriaVaraListView, self).get_context_data(**kwargs)

        context.update({
            'form': forms.BuscarDefensoriaVaraForm(self.request.GET),
        })

        return context

    def get_queryset(self):

        queryset = super(DefensoriaVaraListView, self).get_queryset().ativos()
        q = Q()

        form = forms.BuscarDefensoriaVaraForm(self.request.GET)

        if form.is_valid():

            data = form.cleaned_data

            # Filtro por defensoria
            if data.get('defensoria'):
                q &= Q(defensoria=data.get('defensoria'))

            # Filtro por vara
            if data.get('vara'):
                q &= Q(vara=data.get('vara'))

            # Filtro por paridade
            if data.get('paridade') is not None:
                q &= Q(paridade=data.get('paridade'))

        return queryset.filter(q)


class DefensoriaVaraCreateView(CreateView):
    # form_class = forms.BuscarDefensoriaVaraForm
    model = DefensoriaVara
    # fields = ['defensoria', 'vara', 'paridade']
    form_class = forms.CadastrarDefensoriaVaraForm
    template_name = "processo/associacao/defensoria_vara_cadastrar.html"
    success_url = reverse_lazy('associacao:defensoria_vara_listar')

    # def get_success_url(self):
    #     return self.request.META.get('HTTP_REFERER', '/')


class FaseTipoListView(ListView):
    model = FaseTipo
    queryset = FaseTipo.objects.prefetch_related(
        'tipos_de_evento'
    ).select_related(
        'modificado_por',
    ).annotate(
        total_associacoes=Max(
            Case(
                When(tipos_de_evento__id__isnull=False, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ),
        disponivel_para_peticao=Sum(
            Case(
                When(
                    Q(tipos_de_evento__disponivel_em_peticao_avulsa=True) |
                    Q(tipos_de_evento__disponivel_em_peticao_com_aviso=True),
                    then=Value(1)
                ),
                default=Value(0),
                output_field=IntegerField()
            )
        ),
    ).ativos().filter(
        judicial=True
    ).order_by(
        'total_associacoes', 'nome'
    )
    paginate_by = 50
    template_name = 'processo/associacao/fase_tipo_buscar.html'

    def get_context_data(self, **kwargs):

        context = super(FaseTipoListView, self).get_context_data(**kwargs)

        context.update({
            'form': forms.BuscarFaseTipoForm(self.request.GET),
        })

        return context

    def get_queryset(self):

        queryset = super(FaseTipoListView, self).get_queryset()
        q = Q()

        form = forms.BuscarFaseTipoForm(self.request.GET)

        if form.is_valid():

            data = form.cleaned_data

            # Filtro por sistema webservice
            if data.get('sistema'):
                q &= Q(tipos_de_evento__sistema_webservice=data.get('sistema'))

            # Filtro por nome
            if data.get('filtro'):
                q &= Q(nome__icontains=data.get('filtro'))

        return queryset.filter(q)


class FaseTipoDetailView(DetailView):
    model = FaseTipo
    template_name = 'processo/associacao/fase_tipo_visualizar.html'

    def get_context_data(self, **kwargs):

        context = super(FaseTipoDetailView, self).get_context_data(**kwargs)
        sistemas = SistemaWebService.objects.ativos()

        associacoes = []

        for sistema in sistemas:
            associacoes.append({
                'sistema': sistema,
                'tipos_evento': sistema.tipoevento_set.ativos(),
                'tipo_evento': self.object.tipos_de_evento.filter(
                    sistema_webservice=sistema
                ).first()
            })

        context.update({
            'associacoes': associacoes
        })

        return context

    def post(self, request, *args, **kwargs):

        data = request.POST
        sistemas = SistemaWebService.objects.ativos()

        tipo_fase = self.model.objects.get(id=kwargs.get('pk'))

        # Desativa qualquer associação anterior do tipo de fase ao sistema
        tipo_fase.tipos_de_evento.clear()

        # Passa por todos sistemas
        for sistema in sistemas:

            # Se foi escolhido um tipo de evento cria associação
            if data.get(sistema.nome):
                tipo_evento = TipoEvento.objects.get(id=data.get(sistema.nome))
                tipo_fase.tipos_de_evento.add(tipo_evento)

        # atualiza dados da fase (inclui dados de auditoria)
        tipo_fase.save()

        return redirect('associacao:fase_tipo_buscar')
