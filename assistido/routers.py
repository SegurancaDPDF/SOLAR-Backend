# third-party
from rest_framework import routers

# application
from . import viewsets

router = routers.SimpleRouter()
router.register(r'assistidos', viewsets.PessoaAssistidaViewSet)
router.register(r'assistidos-documentos', viewsets.DocumentoViewSet)
router.register(r'dependentes', viewsets.DependenteViewSet)
router.register(r'estruturas-moradia', viewsets.EstruturaMoradiaViewSet)
router.register(r'filiacoes', viewsets.FiliacaoViewSet)
router.register(r'imoveis', viewsets.ImovelViewSet)
router.register(r'moveis', viewsets.MovelViewSet)
router.register(r'patrimoniais', viewsets.PatrimonialViewSet)
router.register(r'patrimonios', viewsets.PatrimonioViewSet)
router.register(r'perfis-campos-obrigatorios', viewsets.PerfilCamposObrigatoriosViewSet)
router.register(r'profissoes', viewsets.ProfissaoViewSet)
router.register(r'rendas', viewsets.RendaViewSet)
router.register(r'semoventes', viewsets.SemoventeViewSet)
router.register(r'situacoes', viewsets.SituacaoViewSet)
router.register(r'tipos-patrimonial', viewsets.PatrimonialTipoViewSet)
router.register(r'tipos-renda', viewsets.TipoRendaViewSet)
