var tour_i18n = {
    nextBtn: 'Avançar',
    prevBtn: 'Voltar',
    doneBtn: 'Pronto!',
    skipBtn: 'Pular',
    closeTooltip: 'Fechar'};

var tours = {
    atendimento_documento_agendar: {
        id: "atendimento_documento_agendar",
        i18n: tour_i18n,
        steps: [
            {
                title: "Definir prazo de resposta p/ ofício",
                content: "Clique na aba <b>Documentos</b>",
                target: document.querySelector("a[data-toggle='tab'][href='#/documentos']"),
                placement: "top",
                nextOnTargetClick: true,
            },
            {
                title: "Definir prazo p/ resposta de ofício",
                content: "Certifique-se que o ofício já foi vinculado ao atendimento",
                target: "box-documentos",
                placement: "right",
            },
            {
                title: "Definir prazo de resposta p/ ofício",
                content: "Clique no botão <b>Agendar Resposta</b>",
                target: "btn-documento-agendar",
                placement: "right",
                yOffset: -20,
                showNextButton: false,
                nextOnTargetClick: true,
            },
            {
                title: "Definir prazo de resposta p/ ofício",
                content: "Informe o prazo de resposta",
                target: "#modal-documento-agendar.in input[name='prazo_resposta']",
                placement: "right",
                yOffset: -20,
                delay: 500,
                nextOnTargetClick: true,
            },
            {
                title: "Definir prazo de resposta p/ ofício",
                content: "Preencha este campo quando obter uma resposta para o documento. Será solicitada a inclusão do arquivo com a resposta.",
                target: "#modal-documento-agendar.in select[name='status_resposta']",
                placement: "right",
                yOffset: -20,
                delay: 500,
                nextOnTargetClick: true,
            },
            {
                title: "Definir prazo de resposta p/ ofício",
                content: "Clique em <b>Procurar</b> e localize o arquivo com a resposta do ofício.",
                target: "#modal-documento-agendar.in span.btn-file",
                placement: "right",
                yOffset: -20,
                delay: 500,
                nextOnTargetClick: true,
            },
            {
                title: "Definir prazo de resposta p/ ofício",
                content: "Clique em <b>Salvar</b>",
                target: "#modal-documento-agendar.in #btn-agendar-resposta-documento",
                placement: "right",
                yOffset: -20,
                delay: 500,
                nextOnTargetClick: true,
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
    atendimento_documento_diligencia: {
        id: "atendimento_documento_diligencia",
        i18n: tour_i18n,
        steps: [
            {
                title: "Enviar doc p/ diligência",
                content: "Clique na aba <b>Documentos</b>",
                target: document.querySelector("a[data-toggle='tab'][href='#/documentos']"),
                placement: "top",
            },
            {
                title: "Enviar doc p/ diligência",
                content: "Crie um <b class=\"text-info\"><i class=\"helper-font-16 fas fa-cloud\"></i> Novo Documento Online</b> com o Gestor de Documentos (GED), depois o assine e finalize. <i>Atenção! Imagens, documentos do Word (DOC) ou PDF não são aceitos</i>",
                target: "box-documentos",
                placement: "right",
            },
            {
                title: "Enviar doc p/ diligência",
                content: "Clique neste botão para enviar o documento ",
                target: "btn-documento-enviar-diligencia",
                placement: "right",
                yOffset: -20,
                showNextButton: false,
                nextOnTargetClick: true,
            },
            {
                title: "Enviar doc p/ diligência",
                content: "Preencha os dados solicitados e clique em <b>Enviar</b>",
                target: "btn_enviar_diligencia",
                placement: "right",
                yOffset: -20,
                delay: 500,
                nextOnTargetClick: true,
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
    atendimento_formulario_especializado: {
        id: "atendimento_formulario_especializado",
        i18n: tour_i18n,
        steps: [
            {
                title: "Preencher formulário especializado",
                content: "Clique neste botão e escolha um dos formulários disponíveis",
                target: "btn-formularios-nucleos",
                placement: "left",
                yOffset: -20,
                delay: 500,
                showNextButton: false,
            },
            {
                title: "Preencher formulário especializado",
                content: "Preencha os dados solicitados e clique em <b>Salvar</b>",
                target: "btn-modal-nucleo-salvar",
                placement: "right",
                yOffset: -20,
                delay: 500,
                nextOnTargetClick: true,
            },
        ]
    },
}
