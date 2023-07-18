# django
from django.http import JsonResponse

# third-party
from constance import config
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

# project
from contrib.models import Defensoria
from defensor.models import Defensor
from processo.processo.models import Aviso
from processo.processo.services import AvisoService

# application
from . import forms
from . import models
from . import serializers
from .services import APIAviso, PrateleiraAvisosService
from .filters import (
    ComarcaWebserviceFilter,
    DefensorFilter,
    DefensoriaFilter,
    PageFilter,
    ParidadeFilter,
    ResponsavelFilter,
    SistemaWebserviceFilter,
    VaraFilter
)


class CompentenciaViewSet(ModelViewSet):
    queryset = models.Competencia.objects.all()
    serializer_class = serializers.SistemaWebServiceSerializer
    permission_classes = [DjangoModelPermissions]


class ListDistribuirAvisosViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = (
        ComarcaWebserviceFilter,
        DefensorFilter,
        DefensoriaFilter,
        ParidadeFilter,
        SistemaWebserviceFilter,
        VaraFilter,
        PageFilter
    )

    def list(self, request, *args, **kwargs):

        form = forms.ListDistribuirAvisosForm(request.query_params)

        if not form.is_valid():
            return Response({k: v[0] for k, v in form.errors.items()}, status=status.HTTP_400_BAD_REQUEST)

        data = form.cleaned_data
        sistema = data['sistema_webservice']
        comarca = data['comarca']
        vara = data['vara']
        defensoria = data['defensoria']
        defensor = data['defensor']
        paridade = data['paridade']
        page = data['page']

        campos_estao_vazios = bool(
            not sistema
            and not comarca
            and not vara
            and not defensoria
            and not defensor
            and not paridade
        )

        campos_estao_vazios = False
        if not config.HABILITAR_LISTAGEM_GERAL_DE_AVISOS and campos_estao_vazios:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        municipio = None
        orgaos_julgadores = []

        if comarca:
            if comarca.municipio:
                municipio = comarca.municipio.id
            else:
                orgaos_julgadores = models.OrgaoJulgador.objects.ativos().filter(
                    vara__comarca=comarca
                ).values_list('codigo_mni', flat=True)

        if vara:
            orgaos_julgadores = vara.orgaojulgador_set.ativos().values_list('codigo_mni', flat=True)

        sucesso, resposta = APIAviso().listar(pagina=page, params={
            'sistema_webservice': sistema.nome if sistema else None,
            'municipio': municipio,
            'orgao_julgador': ','.join(orgaos_julgadores) if orgaos_julgadores else None,
            'paridade': paridade if paridade else None,
            'distribuido_cpf': defensor.servidor.cpf if defensor else None,
            'distribuido_defensoria': defensoria.id if defensoria else None,
            'distribuido': True if defensor or defensoria else False,
            'situacao': ','.join([str(Aviso.SITUACAO_PENDENTE), str(Aviso.SITUACAO_ABERTO)]),
            'ativo': True
        })

        avisos = []
        if sucesso:
            avisos = resposta['results']
            service = AvisoService()
            for aviso in avisos:
                service.distribuir(aviso)

        return JsonResponse(resposta, safe=False)

    def create(self, request):
        avisos = request.data['objects']
        service = AvisoService()
        total_erros = 0
        total_sucessos = 0
        aviso_distribuido_sucesso = []
        aviso_distribuido_erro = []

        for aviso in avisos:

            defensor = Defensor.objects.get(servidor__cpf=aviso['defensor']) if len(aviso['defensor']) > 0 else None
            defensoria = Defensoria.objects.get(id=aviso['defensoria']) if aviso['defensoria'] > 0 else None

            aviso_numero = aviso['aviso_numero']
            sucesso, resposta = service.salvar_distribuicao(
                    aviso_numero,
                    defensoria,
                    defensor,
                    eh_redistribuicao=False
                )

            if sucesso:
                total_sucessos += 1
                aviso_distribuido_sucesso.append(aviso)
            else:
                total_erros += 1
                aviso_distribuido_erro.append(resposta)

        if total_sucessos:
            return Response({'objects': aviso_distribuido_sucesso}, status=status.HTTP_201_CREATED)
        else:
            return Response(f'Erro ao distribuir {aviso_distribuido_erro} aviso(s) ou já foram distribúidos!',
                            status=status.HTTP_400_BAD_REQUEST)


class PainelDeAvisosViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = (
        DefensoriaFilter,
        ResponsavelFilter,
        SistemaWebserviceFilter,
    )

    @swagger_auto_schema(responses={200: serializers.PainelDeAvisoSerializer()})
    def list(self, request, *args, **kwargs):

        form = forms.PainelDeAvisosForm(request.query_params)

        if not form.is_valid():
            return Response({k: v[0] for k, v in form.errors.items()}, status=status.HTTP_400_BAD_REQUEST)

        data = form.cleaned_data

        prateleira = PrateleiraAvisosService(
            sistema=data['sistema_webservice'],
            defensoria=data['defensoria'],
            defensor=data['responsavel'],
            usuario=self.request.user
        )

        total_geral, prateleiras = prateleira.gerar()

        serializer = serializers.PainelDeAvisoSerializer({
            'total_geral': total_geral,
            'prateleiras': prateleiras
        })

        return Response(serializer.data)


class SistemasWebServiceViewSet(ModelViewSet):
    queryset = models.SistemaWebService.objects.all()
    serializer_class = serializers.SistemaWebServiceSerializer
    permission_classes = [DjangoModelPermissions]
