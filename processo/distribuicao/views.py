# -*- coding: utf-8 -*-
# Create your views here.
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView, View
from constance import config

from contrib.models import Defensoria
from defensor.models import Defensor
from procapi_client.models import OrgaoJulgador
from procapi_client.services import APIAviso
from processo.processo.models import Aviso

from processo.processo.services import AvisoService

from . import forms


class DistribuirListView(TemplateView):
    template_name = 'processo/distribuicao/distribuir.html'

    def get_context_data(self, **kwargs):

        avisos = []
        defensor = None
        defensoria = None

        form = forms.BuscarIntimacaoForm(self.request.GET)
        page = int(self.request.GET.get('page', 1))

        if form.is_valid():

            data = form.cleaned_data
            defensor = data['defensor']
            defensoria = data['defensoria']

            # Se deativada a flag HABILITAR_LISTAGEM_GERAL_DE_AVISOS
            # Não irá consultar os avisos de os filtros
            # do campo de busca estiverem vazios.
            campus_estao_vazios = bool(
                not data['sistema_webservice']
                and not data['comarca']
                and not data['vara']
                and not data['paridade']
                and not data['defensor']
                and not data['defensoria']
            )

            if not config.HABILITAR_LISTAGEM_GERAL_DE_AVISOS and campus_estao_vazios:

                context = super(DistribuirListView, self).get_context_data(**kwargs)
                context.update({
                    'object_list': [],
                    'form': form,
                })

                return context

            municipio = None
            orgaos_julgadores = []

            if data['comarca']:
                if data['comarca'].municipio:
                    municipio = data['comarca'].municipio.id
                else:
                    orgaos_julgadores = OrgaoJulgador.objects.ativos().filter(
                        vara__comarca=data['comarca']
                    ).values_list('codigo_mni', flat=True)

            if data['vara']:
                orgaos_julgadores = data['vara'].orgaojulgador_set.ativos().values_list('codigo_mni', flat=True)

            api = APIAviso()
            # Consulta no ProcAPI a lista de avisos pendentes
            sucesso, resposta = api.listar(pagina=page, params={
                'sistema_webservice': data['sistema_webservice'].nome if data['sistema_webservice'] else None,
                'municipio': municipio,
                'orgao_julgador': ','.join(orgaos_julgadores) if orgaos_julgadores else None,
                'paridade': data['paridade'] if data['paridade'] else None,
                'distribuido_cpf': data['defensor'].servidor.cpf if data['defensor'] else None,
                'distribuido_defensoria': data['defensoria'].id if data['defensoria'] else None,
                'distribuido': True if data['defensor'] or data['defensoria'] else False,
                'situacao': ','.join([str(Aviso.SITUACAO_PENDENTE), str(Aviso.SITUACAO_ABERTO)]),
                'ativo': True
            })

            page_obj = api.get_page_obj()
            avisos = []

            if sucesso:

                avisos = resposta['results']
                service = AvisoService()

                # Passa por todos avisos e faz a sugestão de distribuição automaticamente
                for aviso in avisos:
                    service.distribuir(aviso)

        context = super(DistribuirListView, self).get_context_data(**kwargs)

        pode_sugerir_defensor_defensoria = (
            config.SUGERIR_DEFENSORIA_E_DEFENSOR_NA_DISTRIBUICAO
            or (defensor or defensoria)
        )
        # Atualiza variáveis de contexto (visíveis no template)
        context.update({
            'object_list': avisos,
            'defensor_filtrado': defensor,
            'defensoria_filtrada': defensoria,
            'defensores': Defensor.objects.filter(ativo=True, eh_defensor=True),
            'defensorias': Defensoria.objects.filter(ativo=True),
            'form': form,
            'angular': 'DistribuirListCtrl',
            'page_obj': page_obj,
            'pode_sugerir_defensor_defensoria': pode_sugerir_defensor_defensoria
        })

        return context

    def post(self, request, *args, **kwargs):

        data = self.request.POST
        avisos = data.getlist('avisos')
        total_erros = 0
        total_sucessos = 0

        service = AvisoService()

        for aviso in avisos:

            defensorForm = data.get('defensor-{}'.format(aviso))
            defensoriaForm = data.get('defensoria-{}'.format(aviso))

            if defensoriaForm or defensorForm:

                # Caso não seja selecionado defensor ou defensoria na página de distribuição o valor do form é 0
                defensor = Defensor.objects.get(id=defensorForm) if len(defensorForm) > 0 else None
                defensoria = Defensoria.objects.get(id=defensoriaForm) if len(defensoriaForm) > 0 else None

                # Atualiza aviso, vinculando defensoria e/ou defensor de acordo a distribuição
                sucesso, resposta = service.salvar_distribuicao(
                    aviso,
                    defensoria,
                    defensor,
                    eh_redistribuicao=data.get('eh_redistribuicao', False)
                )

                # Soma total de erros e sucessos na vinculação
                if sucesso:
                    total_sucessos += 1
                else:
                    total_erros += 1

        # Se houveram erros na vinculação, exibe mensagem com total
        if total_erros:
            messages.error(self.request, u'Erro ao distribuir {} aviso(s)!'.format(resposta))

        # Se as vinculações deram certo, exibe mensagem com total
        if total_sucessos:
            messages.success(self.request, u'{} aviso(s) distribuído(s) com sucesso!'.format(total_sucessos))

        return redirect('distribuicao:distribuir')


class RedistribuirAvisoView(View):
    def post(self, request, *args, **kwargs):

        data = self.request.POST
        service = AvisoService()

        aviso = data.get('aviso')
        defensoria = Defensoria.objects.get(id=data.get('defensoria'))

        # Atualiza aviso, vinculando defensoria e/ou defensor de acordo a redistribuição
        # TODO: Adicionar redistribuição por defensor na redistribuição de um único aviso
        sucesso, resposta = service.salvar_distribuicao(
            aviso,
            defensoria,
            None,
            eh_redistribuicao=True
            )

        if sucesso:
            messages.success(self.request, 'Aviso redistribuído com sucesso!')
        else:
            messages.error(self.request, 'Erro ao redistribuir aviso!')

        return redirect(request.META.get('HTTP_REFERER', '/'))
