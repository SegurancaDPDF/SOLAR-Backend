# third-party
from rest_framework import routers

# application
from . import viewsets

router = routers.SimpleRouter()
router.register(r'areas', viewsets.AreaViewSet)
router.register(r'atualizacoes', viewsets.AtualizacaoViewSet)
router.register(r'bairros', viewsets.BairroViewSet)
router.register(r'cargos', viewsets.CargoViewSet)
router.register(r'ceps', viewsets.CEPViewSet)
router.register(r'comarcas', viewsets.ComarcaViewSet)
router.register(r'contrib-documentos', viewsets.DocumentoViewSet)
router.register(r'defensorias-tipos-evento', viewsets.DefensoriaTipoEventoViewSet)
router.register(r'defensorias-varas', viewsets.DefensoriaVaraViewSet)
router.register(r'defensorias', viewsets.DefensoriaViewSet)
router.register(r'deficiencias', viewsets.DeficienciaViewSet)
router.register(r'endereco-historicos', viewsets.EnderecoHistoricoViewSet)
router.register(r'enderecos', viewsets.EnderecoViewSet)
router.register(r'estados', viewsets.EstadoViewSet)
router.register(r'etiquetas', viewsets.EtiquetaViewSet)
router.register(r'identidades-genero', viewsets.IdentidadeGeneroViewSet)
router.register(r'login-historicos', viewsets.HistoricoLoginViewSet)
router.register(r'menus-extras', viewsets.MenuExtraViewSet)
router.register(r'municipios', viewsets.MunicipioViewSet)
router.register(r'orientacoes-sexuais', viewsets.OrientacaoSexualViewSet)
router.register(r'paises', viewsets.PaisViewSet)
router.register(r'papeis', viewsets.PapelViewSet)
router.register(r'salarios', viewsets.SalarioViewSet)
router.register(r'telefones', viewsets.TelefoneViewSet)
router.register(r'varas', viewsets.VaraViewSet)
router.register(r'servidores', viewsets.ServidorViewSet)