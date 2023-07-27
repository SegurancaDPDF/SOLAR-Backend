# third-party
from rest_framework import routers

# application
from . import viewsets

router = routers.SimpleRouter()
router.register(r'aprisionamentos', viewsets.AprisionamentoViewSet)
router.register(r'calculos-de-execucao-penal', viewsets.CalculoExecucaoPenalViewSet)
router.register(r'estabelecimentos-penais', viewsets.EstabelecimentoPenalViewSet)
router.register(r'faltas', viewsets.FaltaViewSet)
router.register(r'historicos', viewsets.HistoricoViewSet)
router.register(r'interrupcoes', viewsets.InterrupcaoViewSet)
router.register(r'motivos-para-baixa-prisao', viewsets.MotivoBaixaPrisaoViewSet)
router.register(r'mudancas-de-regime', viewsets.MudancaRegimeViewSet)
router.register(r'penas-restritivas', viewsets.PenaRestritivaViewSet)
router.register(r'prisoes', viewsets.PrisaoViewSet)
router.register(r'remicoes', viewsets.RemissaoViewSet)
router.register(r'restricoes-prestacao-de-servico', viewsets.RestricaoPrestacaoServicoViewSet)
router.register(r'solturas', viewsets.SolturaViewSet)
router.register(r'tipificacoes', viewsets.TipificacaoViewSet)
router.register(r'tipos-estabelecimento-penal', viewsets.TipoEstabelecimentoPenalViewSet)
