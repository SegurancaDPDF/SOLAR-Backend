# third-party
from constance import config

# django
from django.contrib.auth.models import User
from django.urls import reverse

# project
from contrib.models import Comarca
from nucleo.nucleo.models import Nucleo

# Criando o menu com base nas permissões do usuário


class MenuService:
    menu: dict = None
    user = None

    def __init__(self, user: User) -> None:
        self.user = user

    def gerar(self):

        self.menu = []
        self._gerar_menu_buscar()
        self._gerar_menu_129()
        self._gerar_menu_reclamacoes()
        self._gerar_menu_crc()
        self._gerar_menu_recepcao()
        self._gerar_menu_ged()
        self._gerar_menu_comarcas()
        self._gerar_menu_nucleos()
        self._gerar_menu_processos()
        self._gerar_menu_honorarios()
        self._gerar_menu_nucleo()
        self._gerar_menu_plantao()
        self._gerar_menu_processos()
        self._gerar_menu_honorarios()
        self._gerar_menu_livre()
        self._gerar_menu_relatorios()
        self._gerar_menu_inscricoes()
        self._gerar_menu_admin()

        return self.menu

    def _gerar_menu_buscar(self):

        submenus = []

        if self.user.has_perm('atendimento.view_atendimento'):
            submenus.append({
                'nome': 'Calendário de Agendamentos',
                'url': reverse('agendamento_calendario'),
                'icon': 'fas fa-calendar-alt'
            })
            submenus.append({
                'nome': f'{config.NOME_MODULO_ATENDIMENTO}s',
                'url': reverse('atendimento_buscar'),
                'icon': 'fas fa-calendar-alt'
            })

        if self.user.has_perm('processo.view_processo'):
            submenus.append({
                'nome': 'Processos',
                'url': reverse('processo_listar'),
                'icon': 'fas fa-folder'
            })

        if self.user.has_perm('assistido.add_pessoa'):
            submenus.append({
                'nome': 'Assistidos',
                'url': reverse('assistido_buscar'),
                'icon': 'fas fa-users'
            })

        if self.user.has_perm('atendimento.add_tarefa'):
            submenus.append({
                'nome': 'Tarefas',
                'url': reverse('atendimento_tarefas_buscar'),
                'icon': 'far fa-check-square'
            })

        if self.user.has_perm('atividade_extraordinaria.view_atividade_extraordinaria'):
            submenus.append({
                'nome': 'Tarefas',
                'url': reverse('atividade_extraordinaria:buscar'),
                'icon': 'fas fa-list'
            })

        if len(submenus):
            self.menu.append({
                'nome': 'Buscar',
                'url': '#',
                'icon': 'fas fa-search',
                'submenus': submenus
            })

    def _gerar_menu_129(self):
        if self.user.has_perm('atendimento.view_129'):
            self.menu.append({
                'nome': '129',
                'url': reverse('precadastro_index'),
                'icon': 'fas fa-phone'
            })

    def _gerar_menu_reclamacoes(self):
        if self.user.has_perm('atendimento.view_reclamacao'):
            self.menu.append({
                'nome': 'Reclamações',
                'url': reverse('painel_acompanhar_reclamacao', kwargs={'painel': 'todos'}),
                'icon': 'far fa-thumbs-down'
            })

    def _gerar_menu_crc(self):
        if self.user.has_perm('atendimento.view_129') and config.USAR_NOTIFICACOES_ASSISTIDO_VIA_CHATBOT:
            self.menu.append({
                'nome': 'CRC',
                'url': reverse('precadastro_painel'),
                'icon': 'fas fa-headset'
            })

    def _gerar_menu_recepcao(self):

        submenus = []

        if self.user.has_perm('atendimento.view_recepcao'):
            submenus.append({
                'nome': 'Calendário de Agendamentos',
                'url': reverse('agendamento_calendario'),
                'icon': 'fas fa-calendar-alt'
            })
            submenus.append({
                'nome': 'Novo Agendamento',
                'url': reverse('assistido_buscar'),
                'icon': 'fas fa-calendar-plus'
            })
            submenus.append({
                'nome': 'Doc. Pendentes',
                'url': reverse('atendimento_documentos_pendentes'),
                'icon': 'fas fa-file-upload'
            })

        if len(submenus):
            self.menu.append({
                'nome': 'Recepção',
                'url': reverse('recepcao_index'),
                'icon': 'fas fa-book',
                'submenus': submenus
            })

    def _gerar_menu_ged(self):
        if config.SHOW_DJDOCUMENTS and self.user.has_perm('djdocuments.add_documento'):
            self.menu.append({
                'nome': 'GED',
                'title': 'Gestor de Documentos',
                'url': reverse('ged:painel_geral'),
                'icon': 'fas fa-book'
            })

    def _gerar_menu_comarcas(self):

        submenus = []

        if self.user.has_perm('atendimento.view_defensor'):

            comarcas = Comarca.objects.menu(self.user.servidor.defensor)

            for comarca in comarcas:
                submenus.append({
                    'nome': comarca.nome,
                    'url': reverse('comarca_index', args=[comarca.id]),
                    'icon': 'fas fa-comments'
                })

        if len(submenus):
            self.menu.append({
                'nome': 'Defensor',
                'url': reverse('atendimento_perfil'),
                'icon': 'fas fa-comments',
                'submenus': submenus
            })

    def _gerar_menu_nucleos(self):

        submenus = []

        if self.user.has_perm('atendimento.view_distribuicao'):
            submenus.append({
                'nome': 'Distribuir',
                'url': reverse('atendimento_distribuir'),
                'icon': 'fas fa-share-alt'
            })

        if self.user.has_perms(['atendimento.add_assunto', 'atendimento.change_assunto', 'atendimento.delete_assunto']):
            submenus.append({
                'nome': 'Assuntos',
                'url': reverse('atendimento_assuntos_listar'),
                'icon': 'fas fa-clipboard-list'
            })

        if submenus:
            self.menu.append({
                'nome': 'Núcleos',
                'url': reverse('atendimento_perfil'),
                'icon': 'fas fa-briefcase',
                'submenus': submenus
            })

    def _gerar_menu_nucleo(self):
        for nucleo in Nucleo.objects.menu(self.user.servidor.defensor):
            self._gerar_menu_nucleo_item(nucleo)

    def _gerar_menu_nucleo_item(self, nucleo: Nucleo):

        submenus = []

        if nucleo.agendamento and nucleo.indeferimento:
            submenus.append({
                'nome': 'Atendimentos',
                'url': reverse('nucleo_index', args=[nucleo.id]),
                'icon': 'fas fa-comments'
            })
            submenus.append({
                'nome': 'Indeferimentos',
                'url': reverse('indeferimento:index', kwargs={'nucleo_id': nucleo.id}),
                'icon': 'fas fa-life-ring'
            })

        icon = 'fas fa-briefcase'

        if nucleo.diligencia:
            icon = 'fas fa-envelope'

        self.menu.append({
            'nome': nucleo.nome,
            'url': reverse('nucleo_index', args=[nucleo.id]),
            'icon': icon,
            'submenus': submenus
        })

    def _gerar_menu_plantao(self):
        if self.user.has_perm('atendimento.view_distribuicao'):
            for nucleo in Nucleo.objects.menu_plantao(self.user.servidor.defensor)[:1]:
                self.menu.append({
                    'nome': 'Plantão',
                    'url': reverse('nucleo_index', args=[nucleo.id]),
                    'icon': 'fas fa-fire',
                })

    def _gerar_menu_processos(self):

        submenus = []

        if self.user.has_perm('processo.view_processo'):
            submenus.append({
                'nome': 'Processos',
                'url': reverse('processo_listar'),
                'icon': 'fas fa-folder'
            })
            submenus.append({
                'nome': 'Peticionamentos',
                'url': reverse('peticionamento:buscar'),
                'icon': 'fas fa-university'
            })
            submenus.append({
                'nome': 'Avisos Pendentes',
                'url': reverse('intimacao:painel'),
                'icon': 'fas fas fa-bell'
            })
            submenus.append({
                'nome': 'Audiências',
                'url': reverse('processo_audiencias'),
                'icon': 'fas fa-gavel'
            })

        if self.user.has_perm('processo.view_distribuicao'):
            submenus.append({
                'nome': 'Distribuir',
                'url': reverse('distribuicao:distribuir'),
                'icon': 'fas fa-sitemap'
            })

        if self.user.has_perm('propac.view_procedimento'):
            submenus.append({
                'nome': 'Propacs',
                'url': reverse('procedimentos:inicio_index'),
                'icon': 'fas fa-folder-open color-yellow'
            })

        if submenus:
            self.menu.append({
                'nome': 'Processos',
                'url': '#',
                'icon': 'fas fa-folder',
                'submenus': submenus
            })

    def _gerar_menu_honorarios(self):
        if self.user.has_perm('honorarios.view_honorario'):
            self.menu.append({
                'nome': 'Honorários',
                'url': reverse('honorarios_index'),
                'icon': 'fas fa-donate',
            })

    def _gerar_menu_livre(self):

        submenus = []

        if self.user.has_perm('atendimento.view_defensor'):

            comarcas = Comarca.objects.menu(self.user.servidor.defensor)

            for comarca in comarcas:
                submenus.append({
                    'nome': comarca.nome,
                    'url': reverse('comarca_index', args=[comarca.id]),
                    'icon': 'fas fa-comments'
                })

        if len(submenus):
            self.menu.append({
                'nome': 'Livre',
                'url': reverse('nadep_index'),
                'icon': 'fas fa-leaf',
                'submenus': submenus
            })

    def _gerar_menu_relatorios(self):
        if self.user.has_perm('relatorios.view_relatorios'):
            self.menu.append({
                'nome': 'Relatórios',
                'url': reverse('relatorios:index'),
                'icon': 'fas fa-chart-bar',
            })

    def _gerar_menu_inscricoes(self):
        if config.SHOW_INSCRICAO_PLANTAO and self.user.has_perm('defensor.view_inscricao_plantao'):
            self.menu.append({
                'nome': 'Inscrição Plantão',
                'url': reverse('defensor_plantao_listar'),
                'icon': 'fas fa-user-plus',
            })

    def _gerar_menu_admin(self):

        submenus = []

        if self.user.has_perm('evento.add_evento') or self.user.has_perm('evento.add_agenda'):
            submenus.append({
                'nome': 'Agendas',
                'url': reverse('evento_index'),
                'icon': 'fas fa-calendar-alt'
            })

        if self.user.has_perm('evento.add_atuacao'):
            submenus.append({
                'nome': 'Defensores',
                'url': reverse('defensor_atuacao'),
                'icon': 'fas fa-user-tie'
            })

        if self.user.has_perm('contrib.change_servidor'):
            submenus.append({
                'nome': 'Servidores',
                'url': reverse('listar_servidor'),
                'icon': 'fas fa-user-friends'
            })

        if self.user.has_perm('itinerante.view_evento'):
            submenus.append({
                'nome': 'Itinerante',
                'url': reverse('itinerante_index'),
                'icon': 'fas fa-truck'
            })

        if self.user.has_perm('comarca.change_predio'):
            submenus.append({
                'nome': 'Prédios',
                'url': reverse('itinerante_index'),
                'icon': 'fas fa-building'
            })

        if self.user.has_perm('comarca.change_defensoria'):
            submenus.append({
                'nome': 'Defensorias',
                'url': reverse('defensoria_buscar'),
                'icon': 'fas fa-house-user'
            })

        if self.user.has_perm('assistido.change_perfilcamposobrigatorios'):
            submenus.append({
                'nome': 'Campos',
                'url': reverse('campos_obrigatorios_index'),
                'icon': 'fas fa-tasks'
            })

        if self.user.is_superuser:
            submenus.append({
                'nome': 'Avançado',
                'url': reverse('perfil_admin'),
                'icon': 'fas fa-puzzle-piece'
            })
            submenus.append({
                'nome': 'Django',
                'url': reverse('admin:index'),
                'icon': 'fas fa-tools'
            })

        if len(submenus):
            self.menu.append({
                'nome': 'Admin',
                'url': '#',
                'icon': 'fas fa-cogs',
                'submenus': submenus
            })
