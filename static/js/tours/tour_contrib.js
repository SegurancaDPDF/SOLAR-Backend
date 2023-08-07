var tour_i18n = {
            nextBtn: 'Avançar',
            prevBtn: 'Voltar',
            doneBtn: 'Pronto!',
            skipBtn: 'Pular',
            closeTooltip: 'Fechar'};

var tours = {
    servidor_cadastrar: {
        id: "servidor_cadastrar",
        i18n: tour_i18n,
        steps: [
            {
                title: "Cadastrar novo servidor",
                content: "Clique no botão <b>Novo Servidor</b>",
                target: "btn-novo-servidor",
                placement: "left",
                yOffset: -20,
                showNextButton: false,
                nextOnTargetClick: true,
                multipage: true,
            },
            {
                title: "Cadastrar novo servidor",
                content: "Preencha o nome completo",
                target: "id_nome_completo",
                placement: "right",
                yOffset: -20,
                nextOnTargetClick: true,
            },
            {
                title: "Cadastrar novo servidor",
                content: "Preencha o cpf",
                target: "id_cpf_matricula",
                placement: "right",
                yOffset: -20,
                nextOnTargetClick: true,
            },
            {
                title: "Cadastrar novo servidor",
                content: "Clique em <b>Consultar</b>",
                target: "consultar",
                placement: "right",
                yOffset: -20,
                showNextButton: false,
                nextOnTargetClick: true,
                onNext: function(){return false;},
            },
            {
                title: "Cadastrar novo servidor",
                content: "Preencha os demais dados solicitados",
                target: "select2-id_papel-container",
                placement: "right",
                yOffset: -20,
                nextOnTargetClick: false,
            },
            {
                title: "Cadastrar novo servidor",
                content: "Clique em <b>Cadastrar</b>",
                target: "botao_cadastrar",
                placement: "right",
                yOffset: -20,
                nextOnTargetClick: true,
            }
        ]
    },
    servidor_alterar: {
        id: "servidor_alterar",
        i18n: tour_i18n,
        steps: [
            {
                title: "Alterar cadastro do servidor",
                content: "Informe um filtro para busca e clique em no botão ao lado",
                target: "btn-buscar-servidor",
                placement: "right",
                yOffset: -20,
                showNextButton: false,
                nextOnTargetClick: true,
                multipage: true,
            },
            {
                title: "Alterar cadastro do servidor",
                content: "Clique no botão <b>Editar</b> correspondente ao servidor desejado",
                target: "btn-editar-servidor-1",
                placement: "left",
                yOffset: -20,
                showNextButton: false,
                nextOnTargetClick: true,
                multipage: true,
            },
            {
                title: "Alterar cadastro do servidor",
                content: "Preencha os dados solicitados",
                target: "id_matricula",
                placement: "right",
                yOffset: -20,
                nextOnTargetClick: true,
            },
            {
                title: "Alterar cadastro do servidor",
                content: "Clique em <b>Salvar informações do Servidor</b>",
                target: "btn-salvar",
                placement: "top",
                yOffset: -20,
                nextOnTargetClick: true,
            }
        ]
    },
    servidor_nova_lotacao: {
        id: "servidor_nova_lotacao",
        i18n: tour_i18n,
        steps: [
            {
                title: "Registrar nova lotação",
                content: "Informe um filtro para busca e clique em no botão ao lado",
                target: "btn-buscar-servidor",
                placement: "right",
                yOffset: -20,
                showNextButton: false,
                nextOnTargetClick: true,
                multipage: true,
            },
            {
                title: "Registrar nova lotação",
                content: "Clique no botão <b>Editar</b> correspondente ao servidor desejado",
                target: "btn-editar-servidor-1",
                placement: "left",
                yOffset: -20,
                showNextButton: false,
                nextOnTargetClick: true,
                multipage: true,
            },
            {
                title: "Registrar nova lotação",
                content: "Clique em <b>Nova</b>",
                target: "btn-nova-lotacao",
                placement: "left",
                yOffset: -20,
                showNextButton: false,
                nextOnTargetClick: true,
            },
            {
                title: "Registrar nova lotação",
                content: "Preencha os dados solicitados e clique em <b>Salvar</b>",
                target: "btn-salvar-lotacao",
                placement: "left",
                yOffset: -20,
                delay: 500,
                nextOnTargetClick: true,
            }
        ]
    }
}
