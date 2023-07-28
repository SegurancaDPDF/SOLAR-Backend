# third-party
from rest_framework import routers

# application
from . import viewsets

router = routers.SimpleRouter()
router.register(r'acordos', viewsets.AcordoViewSet)
router.register(r'assuntos', viewsets.AssuntoViewSet)
router.register(r'atendimentos', viewsets.AtendimentoDefensorViewSet)
router.register(r'atendimentos-coletivos', viewsets.ColetivoViewSet)
router.register(r'atendimentos-documentos', viewsets.DocumentoViewSet)
router.register(r'atendimentos-gerais', viewsets.AtendimentoViewSet)
router.register(r'atendimentos-partes', viewsets.PessoaViewSet)
router.register(r'atendimentos-participantes', viewsets.AtendimentoParticipanteViewSet)
router.register(r'encaminhamentos', viewsets.EncaminhamentoViewSet)
router.register(r'especializados', viewsets.EspecializadoViewSet)
router.register(r'formas-atendimento', viewsets.FormaAtendimentoViewSet)
router.register(r'grupos-agendamento', viewsets.GrupoDeDefensoriasParaAgendamentoViewSet)
router.register(r'impedimentos', viewsets.ImpedimentoViewSet)
router.register(r'informacoes', viewsets.InformacaoViewSet)
router.register(r'justificativas', viewsets.JustificativaViewSet)
router.register(r'modelos-documento', viewsets.ModeloDocumentoViewSet)
router.register(r'motivos-exclusao', viewsets.MotivoExclusaoViewSet)
router.register(r'pastas-documentos', viewsets.PastaDocumentoViewSet)
router.register(r'perguntas', viewsets.PerguntaViewSet)
router.register(r'procedimentos', viewsets.ProcedimentoViewSet)
router.register(r'qualificacoes', viewsets.QualificacaoViewSet)
router.register(r'qualificacoes-assuntos', viewsets.QualificacaoAssuntoViewSet)
router.register(r'tarefas', viewsets.TarefaViewSet)
router.register(r'tipos-coletividade', viewsets.TipoColetividadeViewSet)
router.register(r'tipos-vulnerabilidade-digital', viewsets.TipoVulnerabilidadeViewSet)
