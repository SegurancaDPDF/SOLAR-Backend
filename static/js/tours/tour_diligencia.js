var tour_i18n = {
            nextBtn: 'Avançar',
            prevBtn: 'Voltar',
            doneBtn: 'Pronto!',
            skipBtn: 'Pular',
            closeTooltip: 'Fechar'};

var tours = {
    diligencia_visao_geral: {
        id: "diligencia_visao_geral",
        i18n: tour_i18n,
        steps: [
            {
                title: "Bem vindo!",
                content: "Esta é a página dos oficiais de diligência. Vou te mostrar o que é possível fazer por aqui... Vamos lá!?",
                target: document.querySelector(".content-header"),
                placement: "bottom",
                xOffset: 20,
                multipage: true,
                onNext: function(){
                    window.location="/nucleo/diligencia/";
                },
            },
            {
                title: "Visão geral - Calendário",
                content: "Neste calendário você pode acompanhar quantos prazos de resposta vencem em cada dia do mês corrente",
                target: document.querySelector(".calendario"),
                placement: "right",
            },
            {
                title: "Visão geral - Dados Gerais",
                content: "Aqui você pode acompanhar o total de solicitações agendadas, em andamento e as finalizadas nos últimos 30 dias",
                target: "box-dados-gerais",
                placement: "left",
            },
            {
                title: "Visão geral - Todas Atividades",
                content: "Nesta lista você visualiza os detalhes das solicitações agendadas, em andamento e as finalizadas nos últimos 30 dias",
                target: "box-todas-atividades",
                placement: "top",
            },
            {
                title: "Visão geral - Minhas atividades recentes",
                content: "E nesta outra lista você visualiza suas últimas atividades registradas",
                target: "box-minhas-atividades",
                placement: "top",
            },
            {
                title: "Até mais!",
                content: "A qualquer momento você pode clicar neste botão para obter mais ajuda!",
                target: "btn-ajuda",
                placement: "left",
                yOffset: -20,
            },
        ]
    },
    diligencia_agendada: {
        id: "diligencia_agendada",
        i18n: tour_i18n,
        steps: [
            {
                title: "Atender nova diligência",
                content: "Clique no botão <b>Atender</b>",
                target: "btn-atender-diligencia-1",
                placement: "right",
                yOffset: -20,
                showNextButton: false,
                nextOnTargetClick: true,
                multipage: true,
            },
            {
                title: "Atender nova diligência",
                content: "Confirme os dados e clique em <b>Sim</b>",
                target: "btn-modal-distribuir-nucleo-diligencia-sim",
                placement: "right",
                yOffset: -20,
                delay: 500,
                showNextButton: false,
                nextOnTargetClick: true,
                multipage: true,
            },
            {
                title: "Atender nova diligência",
                content: "Nesta seção encontram-se as solicitações em andamento",
                target: "box-solicitacoes-andamento",
                placement: "right",
            },
            {
                title: "Atender nova diligência",
                content: "Para ver o conteúdo do documento clique neste botão",
                target: "btn-ver-documento-1",
                placement: "right",
                yOffset: -20,
            },
            {
                title: "Atender nova diligência",
                content: "Nesta seção encontram-se as solicitações já finalizadas",
                target: "box-solicitacoes-finalizadas",
                placement: "right",
            },
            {
                title: "Atender nova diligência",
                content: "Nesta seção é possível ver as atividades já registradas e incluir novas",
                target: "box-atividades",
                placement: "top",
            },
            {
                title: "Até mais!",
                content: "A qualquer momento você pode clicar neste botão para obter mais ajuda!",
                target: "btn-ajuda",
                placement: "left",
                yOffset: -20,
            },
        ]
    },
    diligencia_nova_atividade: {
        id: "diligencia_nova_atividade",
        i18n: tour_i18n,
        steps: [
            {
                title: "Registrar nova atividade",
                content: "Clique neste botão",
                target: "btn-nova-atividade",
                placement: "left",
                yOffset: -20,
                showNextButton: false,
                nextOnTargetClick: true,
            },
            {
                title: "Registrar nova atividade",
                content: "Preencha as informações solicitadas e clique em <b>Salvar</b>",
                target: "btn-modal-cadastrar-atividade-salvar",
                placement: "left",
                yOffset: -20,
                delay: 500,
                nextOnTargetClick: true,
            }
        ]
    },
    diligencia_excluir_atividade: {
        id: "diligencia_excluir_atividade",
        i18n: tour_i18n,
        steps: [
            {
                title: "Excluir atividade",
                content: "Clique neste botão",
                target: "btn-atividade-excluir-1",
                placement: "left",
                yOffset: -20,
                showNextButton: false,
                nextOnTargetClick: true,
            },
            {
                title: "Excluir atividade",
                content: "Para confirmar a exclusão clique em <b>Salvar</b>",
                target: "btn-modal-excluir-atividade-excluir",
                placement: "left",
                yOffset: -20,
                delay: 500,
                nextOnTargetClick: true,
            }
        ]
    },
    diligencia_novo_documento: {
        id: "diligencia_novo_documento",
        i18n: tour_i18n,
        steps: [
            {
                title: "Incluir nova certidão",
                content: "Clique neste botão",
                target: "btn-atividade-novo-documento-1",
                placement: "left",
                yOffset: -20,
                showNextButton: false,
                nextOnTargetClick: true,
            },
            {
                title: "Incluir nova certidão",
                content: "Preencha as informações solicitadas e clique em <b>Anexar Arquivo</b>",
                target: "btn-modal-documentos-atividade-anexar",
                placement: "left",
                yOffset: -20,
                delay: 500,
                nextOnTargetClick: true,
            }
        ]
    },
    diligencia_finalizar: {
        id: "diligencia_finalizar",
        i18n: tour_i18n,
        steps: [
            {
                title: "Finalizar diligência",
                content: "Clique neste botão",
                target: "btn-finalizar",
                placement: "left",
                yOffset: -20,
                showNextButton: false,
                nextOnTargetClick: true,
            },
            {
                title: "Finalizar diligência",
                content: "Preencha as informações solicitadas e clique em <b>Salvar</b>",
                target: "btn-modal-finalizar-atividade-finalizar",
                placement: "left",
                yOffset: -20,
                delay: 500,
                nextOnTargetClick: true,
            }
        ]
    },
}
