(function($) {

    $(document).ready(function() {

        ADONIS_HOSTNAME = document.getElementById("EDEFENSOR_ADONIS_HOSTNAME").value;
        ADONIS_PORT = document.getElementById("EDEFENSOR_ADONIS_PORT").value;

        WS_PROTOCOL = 'ws:';
        HTTP_PROTOCOL = 'http:';

        // Muda para protocolos seguros se porta 443 (https)
        if(ADONIS_PORT=='443'){
            WS_PROTOCOL = 'wss:';
            HTTP_PROTOCOL = 'https:';
        }

        const KENNEDY_API_DOMAIN_HOMOLOGACAO = `${HTTP_PROTOCOL}://${ADONIS_HOSTNAME}:${ADONIS_PORT}`,
              KENNEDY_API_ROUTE = '/api/v1/messages',
              KENNEDY_API_BASE = KENNEDY_API_DOMAIN_HOMOLOGACAO+KENNEDY_API_ROUTE,
              SOLAR_API_PATHNAME = '/api/v1',
              SOLAR_GERA_TOKEN_PATHNAME = SOLAR_API_PATHNAME+'/edefensor/gera-token/',
              SOLAR_RENOVA_TOKEN_PATHNAME = SOLAR_API_PATHNAME+'/edefensor/renova-token/',
              SOLAR_POSSIVEIS_CONVERSAS_PATHNAME = SOLAR_API_PATHNAME+'/edefensor/possiveis-conversas-chat/',
              SOLAR_ATENDIMENTOS_COM_DOC_PENDENTE = SOLAR_API_PATHNAME+'/atendimentos/com-documento-pendente/{defensor_id}/?assistido_id={assistido_solar_id}',
              SOLAR_INFORMACOES_DE_DOCUMENTO = SOLAR_API_PATHNAME+'/atendimentos/{atendimento_numero}/documentos/{documento_id}/'

              UDL_HEIGHT = 37,
              MAIN_TICKER_MILISSECONDS = 4000,
              TEMPO_ENTRE_NOTIFICACOES_SONORAS_EDEFENSOR = 3000,
              APENAS_TEMPO_REAL_NOTIFICACOES_SONORAS_EDEFENSOR = true,

              GERA_TOKEN_DIRETO_URL = `${KENNEDY_API_DOMAIN_HOMOLOGACAO}/api/v1`,

              ADONIS_CONNECTION_URI = WS_PROTOCOL+'//'+ADONIS_HOSTNAME+':'+ADONIS_PORT;
              ADONIS_BASE_PATH = '/api/v1',
              ADONIS_HTTPS_BASE = HTTP_PROTOCOL+'//'+ADONIS_HOSTNAME+':'+ADONIS_PORT+ADONIS_BASE_PATH,
              ADONIS_AUTH_URL = ADONIS_HTTPS_BASE+'/auth',
              ADONIS_BUSCA_CONVERSAS = ADONIS_HTTPS_BASE+'/chat/{defensor_id}/messages/solar',
              ADONIS_BUSCA_INFO_CONVERSAS = ADONIS_HTTPS_BASE+'/chat/conversations/{defensor_id}/{assistido_id}',
              ADONIS_BUSCA_NUMERO_DE_MENSAGENS_NAO_LIDAS = ADONIS_HTTPS_BASE+'/chat/{defensor_id}/notreceived/',
              ADONIS_MARCA_TODAS_COMO_LIDAS = ADONIS_HTTPS_BASE+'/chat/{defensor_id}/{assistido_id}/read',
              ADONIS_ENCERRA_ATENDIMENTO = ADONIS_HTTPS_BASE+'/chat/conversation/{defensor_id}/{assistido_id}/finish',

              END_CONVERSATION_INFO = "Finalizando conversa (Protocolo {protocolo})",
              START_CONVERSATION_INFO = "Iniciando conversa (Protocolo {protocolo})";

        var codigos = {};
            Object.defineProperty( codigos, "GABINETE", {
                value: "0",
                writable: false,
                enumerable: true,
                configurable: true
            });
            Object.defineProperty( codigos, "ASSISTIDO", {
                value: "1",
                writable: false,
                enumerable: true,
                configurable: true
            });
            Object.defineProperty( codigos, "INFORMACAO", {
                value: "2",
                writable: false,
                enumerable: true,
                configurable: true
            });

        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        function getCsrfToken(){
            return getCookie('csrftoken');
        }

        niceDownloadFile = function (file_path) {

            let filename = file_path.substr(file_path.lastIndexOf('/') + 1);

            /* var file_path = 'host/path/file.ext'; */
            var a = document.createElement('A');
            a.href = file_path;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }

        function seedHexColor(seed){

            let halfHex = function(hexa){ return (Math.floor(parseInt(hexa, 16)/2)).toString(16)};
            let cor = Math.floor((Math.abs(Math.sin(seed) * 16777215)) % 16777215).toString(16);
            let corMeia = halfHex(cor.substring(0,2))+halfHex(cor.substring(2,4))+halfHex(cor.substring(4,6));
            return '#'+corMeia;

        }

        function formata_data(data) {

            let dia;

            try {
                dia  = data.getDate().toString().padStart(2, '0'),
                mes  = (data.getMonth()+1).toString().padStart(2, '0'), //+1 pois no getMonth Janeiro começa com zero.
                ano  = data.getFullYear(),
                hora = data.getHours().toString().padStart(2, '0'),
                minuto = data.getMinutes().toString().padStart(2, '0');
                segundo = data.getSeconds().toString().padStart(2, '0');
            } catch (err) {
                return false;
            }

            return ano+'-'+mes+'-'+dia+' '+hora+':'+minuto+':'+segundo;

        }

        function removeNewlinewBeginEnd(value) {
            if(typeof(value)!='string'){
                return false;
            }
            return value.replace(/^\s+|\s+$/g, '');
        }

        function get_container_offset(obj) {

            var childPos = obj.offset();
            var parentPos = obj.parent().offset();
            var childOffset = {
                top: childPos.top - parentPos.top,
                left: childPos.left - parentPos.left
            }

            return childOffset;
        }

        let chatbox_get_body = function(chatbox) {

            return chatbox.find(".chatbox__body").first();

        },
        chatbox_get_title = function(chatbox) {

            return chatbox.find(".chatbox__title").first();

        },
        chatbox_get_title_close = function(chatbox) {

            return chatbox.find(".chatbox__title__close").first();

        },
        chatbox_get_new_messagens_icon = function(chatbox) {

            return chatbox.find(".new_messages_icon").first();

        },
        chatbox_get_input = function(chatbox) {

            return chatbox.find(".chat_set_height").first();

        },
        // Pega o botão "enviar" de um chatbox
        chatbox_get_file_button = function(chatbox) {

            return chatbox.find(".btn-file").first();

        },
        chatbox_get_loading_button = function(chatbox) {

            return chatbox.find(".btn-file-loading").first();

        },
        chatbox_get_send_icon = function(chatbox) {

            return chatbox.find(".img_attach").first();

        },
        chatbox_get_atendimento_modal = function(chatbox) {

            return chatbox.find(".chatbox__atendimento__modal").first();

        },
        chatbox_get_atendimento_modal_select = function(chatbox) {

            return chatbox.find(".chatbox__atendimento__modal_select").first();

        },
        chatbox_get_atendimento_modal_close = function(chatbox) {

            return chatbox.find(".chatbox__atendimento__modal_close").first();

        },
        chatbox_get_atendimento_modal_close_button = function(chatbox) {

            return chatbox.find(".chatbox__atendimento__modal_close_button").first();

        },
        chatbox_get_atendimento_modal_info = function(chatbox) {

            return chatbox.find(".chatbox__atendimento__modal_info").first();

        },
        chatbox_get_atendimento_modal_footer = function(chatbox) {

            return chatbox.find(".chatbox__atendimento__modal_footer").first();

        },
        chatbox_get_botao_enviar_da_modal_atendimento = function(chatbox) {

            return chatbox.find(".chatbox__atendimento__modal_send_button").first();

        },
        desabilita_enviar_da_modal_atendimento = function(chatbox, invert_action) {

            // Valor padrão de invert_action
            if(typeof(invert_action) == 'undefined') invert_action = false;

            let botao_enviar_da_modal_atendimento = chatbox_get_botao_enviar_da_modal_atendimento(chatbox);

            if(!invert_action){
                botao_enviar_da_modal_atendimento.attr('disabled', 'disabled');
                botao_enviar_da_modal_atendimento.addClass('disabled');
            }else{
                botao_enviar_da_modal_atendimento.removeAttr('disabled');
                botao_enviar_da_modal_atendimento.removeClass('disabled');
            }

        },
        associa_evento_solicitar_documento = function(channel, tit_doc, id_doc, numero_atendimento) {

            let chatbox = chatbox_get_opened_chat(channel.channel_string);
            let botao_enviar = chatbox_get_botao_enviar_da_modal_atendimento(chatbox);

            botao_enviar.off('click'); // Desassocia o evento

            // Se os parâmetros foram passados, associa o evento
            if(typeof(tit_doc) != 'undefined' && typeof(id_doc) != 'undefined' && typeof(numero_atendimento) != 'undefined'){
                botao_enviar.on('click', function(event){

                    let informacao = `Você solicitou o documento ${tit_doc} do atendimento ${numero_atendimento}`;
                    let unread_info = true; // Diz que a informação não foi lida ainda

                    let atendimento_modal = chatbox_get_atendimento_modal(chatbox);

                    if(typeof chatbox == 'undefined'){
                        return false;
                    }

                    // Esconde a modal
                    atendimento_modal.css('display', 'none');

                    // TODO: Descomentar esse código
                    channel.subscription.emit('sendFile', {
                        atendimento: numero_atendimento,
                        documento_id: id_doc
                    })

                    // Tenta desfazer o listner
                    try {
                        channel.subscription.off("sendfilepermited");
                    } catch (er) {
                        console.warn('O evento sendfilepermited não existia.')
                    }

                    channel.subscription.on("sendfilepermited", function(data){

                        cria_informacao_adonis(chatbox, informacao, unread_info);

                    });
                });
            }

        },
        modal_atendimento_mostra_icone_carregando = function(chatbox, invert_action, custom_title) {

            let loading_color = '#494082';

            // Valor padrão de invert_action
            if(typeof(invert_action) == 'undefined'){
                invert_action = false;
            }

            if(typeof(custom_title) == 'undefined'){
                custom_title = '';
            }

            let chatbox_file_button = chatbox_get_file_button(chatbox);
            let chatbox_loading_button = chatbox_get_loading_button(chatbox);
            let chatbox_send_icon = chatbox_get_send_icon(chatbox);

            // O botão habilita novamente
            chatbox_file_button.css('background-color', (invert_action)?'':loading_color);
            chatbox_file_button.attr('disabled', !invert_action);
            if(custom_title != ''){
                chatbox_file_button.attr('title', custom_title);
            }else{
                chatbox_file_button.attr('title', (invert_action)?'':'Procurando atendimentos com documento pendente...');
            }

            // Troca o loading pelo ícone
            chatbox_loading_button.css('display', (invert_action)?'none':'inline');
            chatbox_send_icon.css('display', (!invert_action)?'none':'inline');

        },
        chatbox_get_chats = function() {

            return get_chats_container().children('div.chatbox');

        },
        get_chats_container = function() {

            return $("#chats-container");

        },
        chatbox_get_opened_chat = function (channel_string){

            let chats = chatbox_get_chats(),
                return_element = undefined;
            let objeto_channel = get_object_from_channel_string(channel_string);
            let assistido_solar_id = objeto_channel.assistido_solar_id;
            let defensor_id = objeto_channel.defensor_id;

            chats.each(function(idx, chatbox){

                chatbox = $(chatbox);

                let chat_defensor = chatbox.data('defensor'),
                    chat_user_solar_id = chatbox.data('assistido_solar_id');

                if(chat_defensor==defensor_id && chat_user_solar_id==assistido_solar_id){
                    return_element = chatbox;
                    return return_element;
                }
            });

            return return_element;

        },
        chatbox_get_list = function(chatbox) {
            return chatbox.data('chat_list');
        },
        chatbox_get_assistido_solar_id = function(chatbox) {

            return chatbox.data('assistido_solar_id');

        },
        chatbox_get_assistido = function(chatbox) {

            let chat_list = chatbox_get_list(chatbox);
            let assistido_solar_id = chatbox_get_assistido_solar_id(chatbox);
            let asisstido = chat_list_get_assistido(chat_list, assistido_solar_id);

            return asisstido;

        },
        chatbox_get_sended_by_info = function(chatbox, sended_by){

            let assistido = chatbox_get_assistido(chatbox);
            let sended_by_info = [];

            sended_by_info[codigos.GABINETE] = {
                classe: 'chatbox__body__message--right',
                descricao: "Você"
            };

            sended_by_info[codigos.ASSISTIDO] = {
                classe: 'chatbox__body__message--left',
                descricao: assistido.dados.nome
            };

            sended_by_info[codigos.INFORMACAO] = {
                classe: 'chatbox__body__message--center',
                descricao: assistido.dados.nome
            };

            return sended_by_info[sended_by];

        },
        // Pega a lista de wrappers de um chatbox
        get_wrapper_list = function(chatbox){

            return chatbox_get_body(chatbox).children('.chat_message_wrapper');

        },
        chatbox_posiciona_cursor = function(chatbox) {

            let input = chatbox_get_input(chatbox);

            input.focus();

        },
        shine_element = function(element) {

            let unshiner = undefined;

            // Se o elemento já estava brilhando
            if(element.hasClass('shining')){

                // Pega o temporizador que ia fazer ele para de brilhar logo logo e impede ele de fazer isto
                unshiner = element.data('unshiner');
                clearTimeout(unshiner);

            // Se o elemento não estava brilhando
            }else{

                // Faz ele brilhar
                element.addClass('shining');

            }

            // Programa o temporizador que vai fazer o elemento parar de brilhar
            unshiner = setTimeout(function(){

                element.removeClass('shining');

            }, 3000);

            element.data('unshiner', unshiner);

        },
        shine_chat = function(chatbox) {

            // Pega o título
            let title = chatbox_get_title(chatbox);

            // Faz o título brilhar
            shine_element(title);

        },
        shine_message = function(mensagem) {

            let ul_section_full = mensagem.find('.ul_section_full').first();

            shine_element(ul_section_full);

        }
        normalize_wrappers = function(chatbox){

            // Para cada grupo de mensagens
            get_wrapper_list(chatbox).each(function(idx, wrapper){

                wrapper = $(wrapper);

                // Se o tipo do grupo de mensagens ainda não foi definido
                if(!wrapper.hasClass('wrapper_left') && !wrapper.hasClass('wrapper_right')  && !wrapper.hasClass('wrapper_center')){

                    // TODO: Verifica se é info


                    // Pega a primeira mensagem do grupo
                    first_message = wrapper.children('.chatbox__body__message').first();

                    // Se a primeira mensagem está do lado esquerdo
                    if(first_message.hasClass('chatbox__body__message--left')){

                        // O grupo é de mensagens de defensor
                        wrapper.data('sended_by', 0);
                        wrapper.addClass('wrapper_left');

                    }else{

                        // Se não, o grupo é de mensagens de assistido
                        wrapper.data('sended_by', 1);
                        wrapper.addClass('wrapper_right');

                    }

                }

            });

        },
        normalize_input_height = function(chatbox) {

            setTimeout(function(){

                let input = chatbox_get_input(chatbox);

                input.attr('rows', 1);

                let lines_limit = 10,
                    lineHeight = input.css('lineHeight'),
                    lines = Math.floor(input[0].scrollHeight / parseInt(lineHeight,10));

                if (lines > lines_limit) { lines = lines_limit; }

                input.attr('rows', lines);

            }, 100);

        },
        normaliza_posicoes_chats = function() {

            let chats_container = get_chats_container(),
                qtd_chats = chats_container.children('div.chatbox').length;

            for (let i = 0; i < qtd_chats; i++) {

                let chatbox = chats_container.children('div.chatbox:eq('+(i)+')');
                chatbox.css('right', (340+(310*(i)))+'px');

            }

        },
        get_last_wrapper_code = function(chatbox){

            return (get_wrapper_list(chatbox).last().hasClass('wrapper_right')) ? codigos.GABINETE : codigos.ASSISTIDO;

        },
        scroll_down_element = function(element){

            element = $(element);
            element.scrollTop(element.prop("scrollHeight"));

        },
        chatbox_scroll_to_position = function(chatbox, position) {

            $(chatbox_get_body(chatbox)).scrollTop(position);

        },
        get_current_scroll_position = function(chatbox) {

            let chatbox_body = $(chatbox_get_body(chatbox));
            return chatbox_body.prop('scrollY');

        },
        scroll_down_to_element = function(element){

            let options = {
                behavior: 'smooth', // One of "auto" or "smooth". Defaults to "auto".
                block: 'start', // Defines vertical alignment; One of "start", "center", "end", or "nearest". Defaults to "start".
                // inline: 'end' // Defines horizontal alignment; One of "start", "center", "end", or "nearest". Defaults to "nearest".
            }

            element = $(element)[0];
            element.scrollIntoView(options);

        },
        scroll_down_to_unread = function(chatbox){

            scroll_down_to_element(chatbox.data('unread-message'));

        },
        scroll_down_body = function(chatbox){

            scroll_down_element(chatbox_get_body(chatbox));

        },
        verifica_rolagem = function(chatbox){

            chatbox_body = chatbox_get_body(chatbox);

            if(chatbox.hasClass('has_new_messages')){

                let unread_message = chatbox.data('unread-message');

                let unread_off_top = unread_message[0].offsetTop;

                // Se não tem barra de rolagem ou alcancou o fim das mensagens
                // if((chatbox_body[0].scrollHeight <= chatbox_body[0].clientHeight) || chatbox_body.scrollTop() + chatbox_body.innerHeight() >= chatbox_body[0].scrollHeight) {
                if((chatbox_body[0].scrollHeight <= chatbox_body[0].clientHeight) || chatbox_body.scrollTop() + chatbox_body.innerHeight() >= unread_off_top) {

                    // Remove a classe 'has_new_messages'
                    chatbox.removeClass('has_new_messages');

                    // Desassocia a mensagem a ser lida
                    chatbox.removeData('unread-message');

                }
            }

        },
        /**
         *
         * Resposta:
         *
         *  {
         *      type: "bearer",
         *      token: "eyJhbGciOiJI...",
         *      refreshToken: "9769ffe85c1a79cf96b29ae3484be610DAX...",
         *      message: "Login realizado com sucesso"
         *  }
         *
         */
        gera_token = function(callback){

            csrf = getCsrfToken();

            url = SOLAR_GERA_TOKEN_PATHNAME;

            data = {},
            headers = {
                'X-CSRFToken': csrf,
                'appSystem': 'solar'
            },

            $.ajax({
                url: url,
                type: 'post',
                data: data,
                headers: headers,
                success: callback
            });

        },
        renova_token = function(adonisApp, callback){

            csrf = getCsrfToken();

            url = SOLAR_RENOVA_TOKEN_PATHNAME ;

            data = {
                "refreshToken": adonisApp.refresh_token
            },
            headers = {
                'X-CSRFToken': csrf,
                'appSystem': 'solar'
            },

            $.ajax({
                url: url,
                type: 'post',
                data: data,
                headers: headers,
                success: callback
            });

        },
        /*

        Conversas agrupadas pelo ID do assistido (no Adonis)


        */
        busca_conversas_adonis = function(adonisApp, defensor_id, callback){

            csrf = getCsrfToken();

            url = ADONIS_BUSCA_CONVERSAS.replace('{defensor_id}', defensor_id);

            data = {},
            headers = {
                'X-CSRFToken': csrf,
                'appSystem': 'solar',
                'authorization': '{TOKEN_TYPE} {TOKEN}'.replace('{TOKEN_TYPE}', adonisApp.token_type).replace('{TOKEN}', adonisApp.authentication_token)
            },

            $.ajax({
                url: url,
                type: 'get',
                data: data,
                headers: headers,
                crossDomain: true,
                dataType: 'json',
                success: callback
            });

        },
        busca_informacoes_conversas_adonis = function(adonisApp, defensor_id, assistido_solar_id, callback){

            csrf = getCsrfToken();

            url = ADONIS_BUSCA_INFO_CONVERSAS.replace('{defensor_id}', defensor_id).replace('{assistido_id}', assistido_solar_id);

            data = {},
            headers = {
                'X-CSRFToken': csrf,
                'appSystem': 'solar',
                'authorization': '{TOKEN_TYPE} {TOKEN}'.replace('{TOKEN_TYPE}', adonisApp.token_type).replace('{TOKEN}', adonisApp.authentication_token)
            },

            $.ajax({
                url: url,
                type: 'get',
                data: data,
                headers: headers,
                crossDomain: true,
                dataType: 'json',
                success: callback
            });

        },
        get_channel_string = function(defensor_id, assistido_solar_id){

            if(typeof defensor_id == 'undefined') return false;

            if(typeof assistido_solar_id == 'undefined') return false;

            let channel_string = 'chat:a'+assistido_solar_id+'d'+defensor_id;

            return channel_string;

        },
        get_channel_string_by_usuario = function(usuario_da_lista){

            let defensor_id = usuario_da_lista.data('defensor');
            let assistido_solar_id = usuario_da_lista.data('assistido_solar_id');

            return get_channel_string(defensor_id, assistido_solar_id);

        },
        get_object_from_channel_string = function(channel_string){

            let split = channel_string.split('chat:')[1].split('a')[1].split('d');
            let assistido_solar_id = split[0];
            let defensor_id = split[1];

            return {
                assistido_solar_id: assistido_solar_id,
                defensor_id: defensor_id
            }

        },
        get_or_create_channel_adonis = function(adonisApp, channel_string){

            let channel = adonisApp.active_chats[channel_string];

            // Se o canal não existia ou se a conexão do canal já foi encerrada
            if(typeof channel == 'undefined' || !adonisApp.ws.getSubscription(channel_string)){
                // Instancia um novo canal
                channel = instancia_canal_adonis(adonisApp, channel_string);
            }

            return channel;

        },
        get_channel_by_chatbox = function(chatbox){
            let chat_list = chatbox.data('chat_list');
            let adonisApp = chat_list_get_adonis(chat_list);
            let defensor_id = chatbox.data('defensor');
            let assistido_solar_id = chatbox.data('assistido_solar_id');
            return get_or_create_channel_adonis(adonisApp, get_channel_string(defensor_id, assistido_solar_id));
        },
        get_conversa_by_id = function(channel, conversa_id){
            let retorno;
            channel.conversas.forEach(function(el, idx){
                if(el.id == conversa_id){
                    retorno = el;
                    return;
                }
            });
            return retorno;
        }
        instancia_canal_adonis = function(adonisApp, channel_string){

            let ws = adonisApp.ws;
            let chat_list = adonisApp.chat_list;
            let usuario_da_lista = pega_usuario_da_lista_por_channel_string(chat_list, channel_string);

            if(typeof ws == 'undefined'){
                return false;
            }

            let channel, subscription;

            subscription = ws.getSubscription(channel_string) || ws.subscribe(channel_string)

            if(typeof adonisApp.active_chats[channel_string] == 'undefined'){
                adonisApp.active_chats[channel_string] = {
                    channel_string: channel_string
                };
            }

            channel = adonisApp.active_chats[channel_string];

            channel.subscription = subscription;

            subscription.on('ready', () => {

                channel.is_connected = true;
                channel.is_with_error = false;

            });

            subscription.on('close', () => {

                channel.is_connected = false;
                channel.is_with_error = false;

            });

            subscription.on('message', (data) => {

                let objeto_mensagem = get_objeto_mensagem(data);

                let encontrou_a_conversa = false;

                // Coloca a mensagem na sua respectiva conversa
                let conversa = get_conversa_by_id(channel, data.conversation_id);
                if(typeof(conversa) != 'undefined'){
                    conversa.messages.push(data);
                    encontrou_a_conversa = true;
                }
                let continua_configuracao_de_mensagem = function(new_conversation){

                    let chatbox = chatbox_get_opened_chat(channel_string);

                    // Se o chat está fechado
                    if (typeof(chatbox) == 'undefined' || chatbox.hasClass('chatbox--closed')) {

                        // Marca a mensagem como não lida
                        data.received = false;

                        if(typeof(channel.unread_adonis_messages) == 'undefined'){
                            return false;
                        }

                        // Aumenta a quantidade de mensagens não lidas do usuario da lista
                        channel.unread_adonis_messages += 1;

                        set_element_badge(usuario_da_lista, channel.unread_adonis_messages);

                        // Atualiza logo todos os badges
                        atualiza_todos_badges_adonis(adonisApp);

                        // Se não tocou som recentemente
                        if(!tocou_som_recentemente){

                            // Toca o som
                            som_notificacao_edefensor[0].play();

                            // Diz que tocou recetemente durante os próximos segundos
                            tocou_som_recentemente = true;
                            setTimeout(function(){tocou_som_recentemente=false},TEMPO_ENTRE_NOTIFICACOES_SONORAS_EDEFENSOR);

                        } // Fim da condição "pode tocar o som"

                    }else{ // Se o chat está aberto

                        // Se tem uma nova coversa
                        if(typeof(new_conversation) != 'undefined'){
                            // Cria informação do protocolo
                            cria_informacao_adonis(chatbox, START_CONVERSATION_INFO.replace("{protocolo}", new_conversation.protocol), false);
                        }

                        // Se a mensagem foi enviada pelo assistido
                        if(data.sended_by === 'assistido'){

                            // Marca a mensagem como lida
                            data.received = true;

                            // Informa ao servidor que o Solar recebeu
                            subscription.emit('messageReceived', {
                                message_id: data.id
                            })

                        }

                        mensagem = cria_mensagem_adonis(chatbox, objeto_mensagem, false);

                        mensagem.on('click', function(e){

                            shine_message(mensagem);

                        });

                        // Rola até a mensagem enviada
                        scroll_down_to_element(mensagem);

                    }

                    // Posiciona os usuários da lista na posição correta
                    posiciona_pelo_timestamp_e_unread_adonis(chat_list);

                }

                // Se não encontrou a conversa
                if(!encontrou_a_conversa){

                    let assistido_solar_id = usuario_da_lista.data('assistido_solar_id');
                    let assistido = adonis_get_assistido_by_solar_id(adonisApp, assistido_solar_id);
                    let assistido_id = assistido.user.id;
                    let defensor_id = usuario_da_lista.data('defensor');

                    // Busca todas as conversas do Adonis
                    // Bem, eu poderia usar busca_informacoes_conversas_adonis
                    // mas esta função não traz as mensagens,
                    // então é mais seguro utilizar o busca_conversas_adonis.
                    busca_conversas_adonis(adonisApp, defensor_id, function (conversas_adonis_data, textStatus) {

                        conversas_adonis_data[assistido_id].forEach(function(conversation, conversation_idx){
                            // Se a id da conversa é igual ao id trazido na nova mensagem
                            if(conversation.id == data.conversation_id){

                                // Se o índice correspondente realmente está vazio
                                if(typeof(channel.conversas[conversation_idx] == 'undefined')){
                                    // Coloca na sua posição correspondente
                                    channel.conversas[conversation_idx] = conversation;
                                }else{
                                    // Se o índice estranhamente já está preenchido, só coloca no final
                                    channel.conversas.append(conversation);
                                }

                                continua_configuracao_de_mensagem(conversation);

                                return; // Sai do laço de repetição

                            }
                        });

                    });
                }else{
                    continua_configuracao_de_mensagem();
                }

            });

            subscription.on('endconversation', (ending_conversation) => {

                // Pega os IDs do defensor e do assistido
                let objeto_channel = get_object_from_channel_string(channel_string);
                let assistido_id = adonis_get_assistido_by_solar_id(adonisApp, objeto_channel.assistido_solar_id).user.id;
                let defensor_id = objeto_channel.defensor_id;

                // Pega as informações das conversas deste defensor com este assistido
                busca_informacoes_conversas_adonis(adonisApp, defensor_id, assistido_id, function(info_conversas, textStatus){

                    // Itera sobre as informações das conversas deste defensor com este assistido
                    info_conversas.forEach(function(conversa_info, conversa_idx){

                        // Se a conversa da iteração é a mesma conversa que está sendo finalizada
                        if(conversa_info.id == ending_conversation.id){

                            // Pega a conversa correspondente no canal
                            let conversa_do_adonis = get_conversa_by_id(channel, ending_conversation.id);

                            // Atualiza dados da conversa
                            conversa_do_adonis.finished_at = ending_conversation.finished_at;
                            conversa_do_adonis.upated_at = ending_conversation.upated_at;

                        }

                    });

                    // Pega um possível chatbox aberto
                    let opened_chatbox = chatbox_get_opened_chat(channel_string);

                    // Se o chatbox está aberto
                    if (typeof(opened_chatbox) != 'undefined' && !opened_chatbox.hasClass('chatbox--closed')) {

                        cria_informacao_adonis(opened_chatbox, END_CONVERSATION_INFO.replace("{protocolo}", ending_conversation.protocol), true);

                    }

                });

            });



            return channel;

        },
        adonis_get_assistido_by_solar_id = function(adonisApp, assistido_solar_id) {

            let retorno;

            adonisApp.assistidos.forEach(function(assistido, idx_assistido){
                if(assistido.user.solar_id == assistido_solar_id){
                    retorno = assistido;
                }
            });

            return retorno;

        },
        /**
         * URL de exemplo: chat/37/notreceived
         *
         *
         *
         *
         */
        busca_numero_de_mensagens_nao_lidas = function(adonisApp, defensor_id, callback){

            csrf = getCsrfToken();

            url = ADONIS_BUSCA_NUMERO_DE_MENSAGENS_NAO_LIDAS.replace('{defensor_id}', defensor_id);

            data = {},
            headers = {
                'X-CSRFToken': csrf,
                'appSystem': 'solar',
                'authorization': '{TOKEN_TYPE} {TOKEN}'.replace('{TOKEN_TYPE}', adonisApp.token_type).replace('{TOKEN}', adonisApp.authentication_token)
            };

            $.ajax({
                url: url,
                type: 'get',
                data: data,
                headers: headers,
                crossDomain: true,
                dataType: 'json',
                success: callback
            });

        },
        marca_mensagens_como_lidas = function(adonisApp, channel_string, callback){

            // TODO: Ajustar função de marcar mensagens como não lidas
            let objeto_channel = get_object_from_channel_string(channel_string);
            let assistido = adonis_get_assistido_by_solar_id(adonisApp, objeto_channel.assistido_solar_id);
            let assistido_id = assistido.user.id;
            let defensor_id = objeto_channel.defensor_id;
            let url = ADONIS_MARCA_TODAS_COMO_LIDAS.replace('{defensor_id}', defensor_id).replace('{assistido_id}', assistido_id);
            let csrf = getCsrfToken();
            let data = {};
            let headers = {
                'X-CSRFToken': csrf,
                'appSystem': 'solar',
                'authorization': '{TOKEN_TYPE} {TOKEN}'.replace('{TOKEN_TYPE}', adonisApp.token_type).replace('{TOKEN}', adonisApp.authentication_token)
            };

            $.ajax({
                url: url,
                type: 'post',
                data: data,
                headers: headers,
                success: callback,
                error: function(jqXHR, textStatus, errorThrown){
                    if(jqXHR.status == 401){
                        console.warn('Term que dar refresh no token');
                    }
                }
            });

        }
        adonis_encerrar_conversa = function(adonisApp, channel_string, callback) {

            let objeto_channel = get_object_from_channel_string(channel_string);
            let assistido = adonis_get_assistido_by_solar_id(adonisApp, objeto_channel.assistido_solar_id);
            let assistido_id = assistido.user.id;
            let defensor_id = objeto_channel.defensor_id;
            let url = ADONIS_ENCERRA_ATENDIMENTO.replace('{defensor_id}', defensor_id).replace('{assistido_id}', assistido_id);
            let csrf = getCsrfToken();
            let data = {};
            let headers = {
                'X-CSRFToken': csrf,
                'appSystem': 'solar',
                'authorization': '{TOKEN_TYPE} {TOKEN}'.replace('{TOKEN_TYPE}', adonisApp.token_type).replace('{TOKEN}', adonisApp.authentication_token)
            };

            $.ajax({
                url: url,
                type: 'post',
                data: data,
                headers: headers,
                success: callback,
                error: function(jqXHR, textStatus, errorThrown){

                    if(jqXHR.status == 404){
                        let mensagem = $.parseJSON(jqXHR.responseText).message;
                        alert(mensagem);
                    }else if(jqXHR.status == 401){
                        console.warn('Term que dar refresh no token');
                    }

                }
            });


        },
        sended_by_stoa = function(value) {

            if(typeof(value) == 'undefined'){
                return false;
            }

            if(typeof(value) == 'string'){
                value = parseInt(value);
            }

            switch (value) {
                case 0:
                    return "defensor";
                case 1:
                    return "assistido";
                default:
                    return false;
            }
        },
        sended_by_atos = function(value){

            if(typeof(value) !== 'string'){
                return false;
            }

            switch (value) {
                case "defensor":
                    return 0;
                case "assistido":
                    return 1;
                default:
                    return false;
            }

        },
        defensor_stoa = function(defensor_id) {
            return defensor_id;
        },
        assistido_stoa = function(chat_list, assistido_cpf) {

            let retorno = false;

            let adonis = chat_list_get_adonis(chat_list);

            adonis.assistidos.forEach(function(assistido, idx_assistido){

                if(assistido.dados.cpf == assistido_cpf){
                    if(typeof assistido.user.id != 'undefined'){
                        retorno = assistido.user.id;
                    }
                }

            });

            return retorno;
        },
        get_solar_user = function(){
            solar_user_id_element = $('#solar_user_id');
            solar_user_name_element = $('#solar_user_name');
            let user_object = {};
            if(solar_user_id_element.length > 0){
                user_object.id = solar_user_id_element.val();
            }
            if(solar_user_name_element.length > 0){
                user_object.name = solar_user_name_element.val();
            }
            return user_object;
        },
        envia_mensagem_adonis = function(chatbox,  defensor_id, assistido_solar_id, sended_by) {

            let chatbox_input = chatbox_get_input(chatbox);
            let message_text = chatbox_input.val();
            chatbox_input.val(''); // Já limpa o campo de texto
            if(message_text == ''){
                return false;
            }

            message_text = message_text.trim(); // Remove espaços antes e depois
            message_text = removeNewlinewBeginEnd(message_text); // Remove quebra de linhas antes e depois
            message_text = message_text.trim(); // Remove espaços antes e depois, só pra garantir

            let chat_list = chatbox_get_list(chatbox);

            let adonisApp = chat_list_get_adonis(chat_list);

            let channel_string = get_channel_string(defensor_id, assistido_solar_id);
            let channel = get_or_create_channel_adonis(adonisApp, channel_string);

            sended_by = sended_by_stoa(sended_by);

            if(sended_by === false){
                return false;
            }

            let data = {
                message: message_text,
                defensor: defensor_id,
                sended_by: sended_by,
            };

            data.assistido = assistido_solar_id;
            data.sended_by_solar_user = get_solar_user().id;

            channel.subscription.emit('newMessage', data);

        },
        /**
         * Cria uma mensagem no HTML
         * @param {string} text O texto a ser enviado
         * @param {integer} sended_by Quem irá enviar (sended_by: "0 gabinete / 1 assistido")
         */
        create_message_element = function(text, document_solar_id, atendimento_numero, sender_name, sended_date, classe_lado){

            var nova_div = $(document.createElement("div"));

            sended_date_date = sended_date.split(' ')[0].split('-');
            sended_date_time = sended_date.split(' ')[1];

            year = sended_date_date[0];
            month = sended_date_date[1];
            day = sended_date_date[2];

            hour = sended_date_time[0];
            minute = sended_date_time[1];
            second = sended_date_time[2];

            let message_content = "";

            if(typeof(document_solar_id) != 'undefined' && (document_solar_id!=null)){

                message_content = `
                <div class='document-path-element' onclick='baixaDocumentoSolar("${atendimento_numero}", "${document_solar_id}");'>
                    <i class='fa fa-file'></i>
                    <span>${text}</span>
                </div>
                `
            }else{

                message_content = `
                    <li class='message_text'>${text}</li>
                `

            }

            var message_element = nova_div.attr({
                "class": "chatbox__body__message "+classe_lado
            }).html([
                `<div class='clearfix'></div>
                <div class='ul_section_full'>
                    <ul class='ul_msg'>
                        <li><strong>${sender_name}</strong></li>
                        ${message_content}
                    </ul>
                    <div class='clearfix'></div>
                    <ul class='ul_msg2'>
                    </ul>
                </div>
                <div class='chatbox_timing'>
                    <ul>
                        <li><span href='#'>${day}/${month}/${year}</span></li>
                        <li><span href='#'>${sended_date_time}</span></li>
                    </ul>
                </div>`
            ].join(""));

            return message_element;

        },
        create_information_element = function(text){

            var nova_div = $(document.createElement("div"));

            var information_element = nova_div.attr({
                "class": "chatbox__body__information chatbox__body__message--center"
            }).html(
                `
                <div class='ul_section_full'>
                    <span class='ul_info'>${text}</span>
                </div>
                `
            );

            return information_element;

        },
        sended_by_to_wrapper_class = function(sended_by){

            switch (sended_by) {
                case codigos.GABINETE:
                    return 'wrapper_right'
                    break;
                case codigos.ASSISTIDO:
                    return 'wrapper_left'
                    break;
                case codigos.INFORMACAO:
                    return 'wrapper_center'
                    break;
                default:
                    break;
            }
        }
        create_new_wrapper = function(sended_by){

            wrapper_class = sended_by_to_wrapper_class(sended_by);

            var wrapper_element = $(document.createElement("div")).attr({
                "class": "chat_message_wrapper"
            }).addClass(
                wrapper_class
            );

            return wrapper_element;

        },
        get_objeto_mensagem = function(oldObject){

            return {
                content: oldObject.content,
                sended_by: oldObject.sended_by,
                sended_date: oldObject.sended_date,
                created_at: oldObject.created_at,
                document_path: oldObject.document_path,
                document_solar_id: oldObject.document_solar_id,
                document_solar_atendimento: oldObject.document_solar_atendimento
            };

        }
        cria_mensagem_adonis = function(chatbox, message, unread_message){

            // Verifica se os parâmetros obrigatórios foram passados
            if(typeof message.sended_by == 'undefined'){
                return false;
            }else if(typeof message.content == 'undefined'){
                return false;
            }else if(typeof message.created_at == 'undefined'){
                return false;
            }

            // Normaliza o sended_by
            let quem_enviou = sended_by_atos(message.sended_by);
            if(quem_enviou !== false){
                message.sended_by = quem_enviou;
            }else{
                return false;
            }

            // Normaliza a data
            let data_formatada = formata_data(new Date(message.created_at));
            if(data_formatada){
                message.created_at = data_formatada;
            }else{
                return false;
            }

            let sended_by = message.sended_by;

            // Normaliza os wrappers
            normalize_wrappers(chatbox);

            // Pega a lista de wrappers
            let wrapper_list = get_wrapper_list(chatbox);

            // Pega o último grupo de mensagens
            let last_wrapper = wrapper_list.last();

            // Pega a classe da mensagem que tem que enviar e o nome do remetente
            let info = chatbox_get_sended_by_info(chatbox, sended_by);
            let [classe_lado, sender_name] = [info.classe, info.descricao];

            // Armazena o HTML da nova mensagem em uma variável
            let new_message = create_message_element(message.content, message.document_solar_id, message.document_solar_atendimento, sender_name, message.created_at, classe_lado);

            // Se o código do remetente é diferente do código do último grupo
            if(wrapper_list.length == 0 || sended_by != get_last_wrapper_code(chatbox)){
                // Cria grupo de mensagens e adiciona nele, colocando ele no final da lista
                new_wrapper = create_new_wrapper(sended_by);
                new_wrapper.append(new_message);
                chatbox_get_body(chatbox).append(new_wrapper);
            // Se o grupo de mensagens é o mesmo
            }else{
                // Apenas adiciona a mensagem ao grupo
                last_wrapper.append(new_message);
            }

            // Se o gabinete enviou a mensagem
            if(sended_by == codigos.GABINETE){

                // rola conversa pra baixo
                scroll_down_body(chatbox);
                normalize_input_height(chatbox);

            // Se o assistido enviou a mensagem
            }else{

                // Se a mensagem é não lida e ainda não tem elemento de nova mensagem
                if(unread_message && (typeof chatbox.data('unread-message') == 'undefined')){

                    // Diz que tem nova mensagem
                    chatbox.addClass('has_new_messages');

                    // Associa o elemento a ser lido a esta mensagem
                    chatbox.data('unread-message', new_message);

                }

                // Se o chat estiver aberto
                if(!chatbox.hasClass('chatbox--tray')){
                    // Remove o ícone de novas mensagens se estiver no final
                    verifica_rolagem(chatbox);
                }

            }

            return new_message;

        },
        cria_informacao_adonis = function(chatbox, informacao, unread_info){

            // Verifica se os parâmetros obrigatórios foram passados
            if(typeof informacao == 'undefined'){
                return false;
            }

            // Normaliza os wrappers
            normalize_wrappers(chatbox);

            let new_info = create_information_element(informacao);

            // Cria grupo de mensagens e adiciona nele, colocando ele no final da lista
            new_wrapper = create_new_wrapper(codigos.INFORMACAO);
            new_wrapper.append(new_info);
            chatbox_get_body(chatbox).append(new_wrapper);

            // Se a mensagem é não lida e ainda não tem elemento de nova mensagem
            if(unread_info && (typeof chatbox.data('unread-message') == 'undefined')){

                // Diz que tem nova mensagem
                chatbox.addClass('has_new_messages');

                // Associa o elemento a ser lido a esta mensagem
                chatbox.data('unread-message', new_info);

            }

            return new_info;

        },
        instanciar_chat = function(chat_list, assistido_solar_id, defensor_id, instanciar_aberto){

            if(typeof instanciar_aberto == 'undefined'){
                instanciar_aberto = false;
            }

            let adonisApp = chat_list_get_adonis(chat_list);

            let assistido = chat_list_get_assistido(chat_list, assistido_solar_id);
            let titular = adonisApp.titulares[defensor_id];

            // TODO: Ajustar nome que aparece no título
            let chat_title = assistido.dados.nome+"("+titular.dados.id+")";
            let chat_long_title = "Defensor ("+titular.dados.servidor.nome+")";

            let tray_class = '';
            if(instanciar_aberto){
                tray_class = ' chatbox--tray';
            }

            let chatbox = $(document.createElement("div")).attr({
                "class": "chatbox chatbox22"+tray_class
            }).data(
                'assistido_solar_id', assistido_solar_id
            ).data(
                'defensor', defensor_id
            ).data(
                'chat_list', chat_list
            ).data(
                'fn_get_chat_item', function(){

                    let chatlist = chatbox.data('chat_list');

                    let assistido_solar_id = chatbox.data('assistido_solar_id'),
                        defensor_id = chatbox.data('defensor'),
                        chat_item = pega_usuario_da_lista(chatlist, defensor_id, assistido_solar_id);

                    return chat_item;
                }
            ).data(
                'fn_carrega_mensagens', function(){

                    let somente_novas = this.valueOf();
                    let old_scroll_y = get_current_scroll_position(chatbox);
                    let channel = get_channel_by_chatbox(chatbox);

                    // Para cada mensagem do canal
                    channel.conversas.forEach(function(conversa){

                        cria_informacao_adonis(chatbox, START_CONVERSATION_INFO.replace("{protocolo}", conversa.protocol), false);

                        conversa.messages.forEach(function(mensagem){

                            // Marca a mensagem como recebida
                            mensagem.received = true;

                            // Se só deve adicionar mensagens novas e a mensagem não é nova
                            if(somente_novas && !mensagem.new_message){

                                // Não faz nada
                                return;

                            }

                            let objeto_mensagem = get_objeto_mensagem(mensagem);

                            // Cria sua respectiva mensagem
                            let message_element = cria_mensagem_adonis(chatbox, objeto_mensagem, mensagem.new_message);

                            // Marca a mensagem como "não nova"
                            mensagem.new_message = false;

                            // Captura a última mensagem adicionada
                            ultima_mensagem = message_element;

                        });

                        // Se o campo "finished_at" não é indefinido e nem nulo, cria a informação de conversa finalizada
                        if(typeof(conversa.finished_at) != "undefined" && (conversa.finished_at)){
                            cria_informacao_adonis(chatbox, END_CONVERSATION_INFO.replace("{protocolo}", conversa.protocol), false);
                        }

                    });

                    // Marca todas as mensagens desta conversa como lida
                    marca_mensagens_como_lidas(adonisApp, get_channel_string(defensor_id, assistido_solar_id), function(data, textStatus){

                    });

                    if(somente_novas){ // Se deve carregar somente as mensagens novas

                        // Rola o chat para a posição que estava antes
                        chatbox_scroll_to_position(chatbox, old_scroll_y);

                    }else{ // Se deve carregar todas as mensagens,

                        setTimeout(function(){
                            scroll_down_body(chatbox);
                        }, 10);

                    }

                }
            ).html(
                `
                <div class='chatbox__title'>
                    <h5><a href='javascript:void(0);' title='"${chat_long_title}"'>"${chat_title}"</a></h5>
                    <button class='chatbox__title__close'>
                        <span>
                            <svg viewBox='0 0 12 12' width='12px' height='12px'>
                                <line stroke='#FFFFFF' x1='11.75' y1='0.25' x2='0.25' y2='11.75'></line>
                                <line stroke='#FFFFFF' x1='11.75' y1='11.75' x2='0.25' y2='0.25'></line>
                            </svg>
                        </span>
                    </button>
                </div>
                <div class='chatbox__body'>
                </div>
                <div class='panel-footer'>
                    <div class='input-group'>
                        <div class='footer-content'>
                            <div class='input-chat'>
                                <span id='new_messages_container'>
                                    <div class='new_messages_icon'>⇣</div>
                                </span>
                                <textarea rows='1' class='form-control chat_set_height'
                                placeholder='Digite aqui...' dir='ltr' spellcheck='false'
                                autocomplete='off' autocorrect='off' autocapitalize='off' contenteditable='true'></textarea>
                            </div>
                            <div class='btn-chat-group'>
                                <span class='input-group-btn'>
                                    <button class='btn bt_bg btn-sm btn-chat btn-file'>
                                        <i class='fa fa-paperclip img_attach'></i>
                                        <img class='btn-file-loading' src='/static/img/loader_16.gif' style='display:none;'>
                                    </button>
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class='chatbox__atendimento__modal' style='display: none;'>
                    <div class='chatbox__atendimento__modal_close'>
                        <span>X</span>
                    </div>
                    <div class='chatbox__atendimento__modal_title'>Selecione o atendimento que deseja solicitar o documento e clique no botão "Enviar solicitação de documento":</div>
                    <div class="chatbox__atendimento__modal_content">
                        <select class="chatbox__atendimento__modal_select form-control form-control-sm" style="margin-top: 20px" >
                        </select>
                        <div class="btn-group" style="margin-top: 20px;">
                            <button class="btn btn-danger chatbox__atendimento__modal_close_button">X</button>
                            <button class="btn btn-success chatbox__atendimento__modal_send_button">Enviar solicitação de documento</button>
                        </div>
                        <div class="chatbox__atendimento__modal_infobox">
                            <span class='chatbox__atendimento__modal_info'></span>
                        </div>

                    </div>
                    <span class='chatbox__atendimento__modal_footer'>Para fechar, clique no "X"</span>
                </div>
                `
            );

            chatbox.data('fn_carrega_mensagens').call(false);

            let chatbox_body = chatbox_get_body(chatbox),
                chatbox_title = chatbox_get_title(chatbox),
                chatbox_title_close = chatbox_get_title_close(chatbox),
                chatbox_new_messagens_icon = chatbox_get_new_messagens_icon(chatbox),
                chatbox_input = chatbox_get_input(chatbox),
                chatbox_file_button = chatbox_get_file_button(chatbox);

            chatbox_body.on('scroll', function(e){

                verifica_rolagem(chatbox);

            });

            // Quando clica no título, esconde/mostra chatbox
            chatbox_title.on('click', function() {


                // Se o Chatbox está fechado
                if(chatbox.hasClass('chatbox--tray')){

                    // Posicoina o cursor no campo de digitação
                    chatbox_posiciona_cursor(chatbox);

                }

                // Alterna entre fechado e aberto
                chatbox.toggleClass('chatbox--tray');

            });

            // Quando clica no fechar, fecha chatbox
            chatbox_title_close.on('click', function(e) {

                e.stopPropagation();
                chatbox.addClass('chatbox--closed');

            });

            // Quando clica no botão "novas mensagens", rola até o final
            chatbox_new_messagens_icon.on('click', function(e) {

                let new_message = chatbox.data('unread-message');

                scroll_down_to_unread(chatbox);

                // .children('.chatbox__body__message').first()
                shine_message(new_message);

            });

            // Quando aperta Enter no campo de envio, envia
            chatbox_input.on('keyup', function(e){

                let chatitem = chatbox.data('fn_get_chat_item').call();

                if(e.keyCode == 13){

                    dados = chatitem.data('fn_get_dados').call();

                    envia_mensagem_adonis(chatbox, dados.defensor_id, dados.assistido_solar_id, codigos.GABINETE);

                }

                // Quando pressionar Esc
                if(e.keyCode == 27){

                    // Fecha o chat
                    chatbox.addClass('chatbox--closed');

                }

            });

            chatbox_file_button.on('click', function() {

                let chatbox_file_button = chatbox_get_file_button(chatbox);
                let atendimento_modal = chatbox_get_atendimento_modal(chatbox);
                let atendimento_modal_select = chatbox_get_atendimento_modal_select(chatbox);
                let atendimento_modal_close = chatbox_get_atendimento_modal_close(chatbox);
                let atendimento_modal_close_button = chatbox_get_atendimento_modal_close_button(chatbox);
                let atendimento_modal_info = chatbox_get_atendimento_modal_info(chatbox);
                let atendimento_modal_footer = chatbox_get_atendimento_modal_footer(chatbox);

                let defensor_id = chatbox.data('defensor');
                let assistido_solar_id = chatbox.data('assistido_solar_id');

                if(chatbox_file_button.is(':disabled')){
                    return false;
                }

                modal_atendimento_mostra_icone_carregando(chatbox);

                // TODO: colocar os parâmetros nessa função
                busca_atendimentos_com_pendencias(defensor_id, assistido_solar_id, function(data, textStatus){

                    // O que acontece em caso de sucesso

                    if(typeof(data) != 'object'){
                        throw new Error('O valor trazido da requisição não é um objeto!');
                    }

                    if(!(data.length > 0)){
                        alert('Nenhum atendimento foi encontrado com documento pendente.');
                        throw new Error('O array veio vazio!');
                    }

                    // Esvazia o select
                    atendimento_modal_select.empty();

                    // Desabilita o botão enviar
                    desabilita_enviar_da_modal_atendimento(chatbox);

                    // Adiciona a opção neutra
                    let option_element = $(`<option value="---">Selecione um atendimento</option>`);
                    atendimento_modal_select.append(option_element);

                    // Preenche o select com os dados trazidos
                    data.forEach(function(at, idx_at){
                        let option_element = $(`<option value="${at.numero}">${at.numero} - ${at.tit_doc}</option>`);
                        atendimento_modal_select.append(option_element);
                    });

                    atendimento_modal_select.off('change').on('change', function() {

                        let value = this.value;
                        let channel = get_channel_by_chatbox(chatbox);

                        if(value == '---'){
                            desabilita_enviar_da_modal_atendimento(chatbox);
                            atendimento_modal_footer.html(`Selecione um atendimento`);
                            atendimento_modal_info.html('');

                            let botao_enviar_da_modal_atendimento = chatbox_get_botao_enviar_da_modal_atendimento(chatbox);
                            associa_evento_solicitar_documento(channel);

                        }else{ // Se selecionou um atendimento
                            // Habilita o botão enviar
                            desabilita_enviar_da_modal_atendimento(chatbox, true);
                            data.forEach(function(at, idx_at){
                                if(at.numero == value){
                                    atendimento_modal_info.html(`O documento a ser solicitado é: ${at.tit_doc}`);

                                    let botao_enviar_da_modal_atendimento = chatbox_get_botao_enviar_da_modal_atendimento(chatbox);
                                    associa_evento_solicitar_documento(channel, at.tit_doc, at.id_doc, at.numero);
                                }
                            });
                        }

                    });

                    // Associa o evento de fechar ao clicar no X
                    atendimento_modal_close.off('click').on('click', function(event){

                        atendimento_modal.css('display', 'none');

                    });

                    atendimento_modal_close_button.off('click').on('click', function(event){

                        atendimento_modal.css('display', 'none');

                    });

                    // Mostra a modal
                    atendimento_modal.css('display', 'inline');

                }, function(data){

                    // O que acontece em erro

                    modal_atendimento_mostra_icone_carregando(chatbox, true, 'Não foi possível carregar os atendimentos com documento pendente, tente novamente mais tarde.');

                }, function(data, textStatus){

                    // O que acontece em todo caso

                    modal_atendimento_mostra_icone_carregando(chatbox, true);

                });

            });

            // Quando acabar um movimento no chatbox
            chatbox.on('transitionend', function() {

                // Se tem a classe "closed", exclui o elemento
                if (chatbox.hasClass('chatbox--closed')) {
                    chatbox.remove();
                    normaliza_posicoes_chats();
                }

                // Se o chat estiver aberto
                if (!chatbox.hasClass('chatbox--tray')) {

                    // Some o ícone de novas mensagens se estiver no final
                    verifica_rolagem(chatbox);

                }

            });

            // Adiciona o elemento do chat no container de chats
            get_chats_container().append(chatbox);

            // Verifica a quantidade de chats instanciados e determina a posição deste
            normaliza_posicoes_chats();

            // Posicoina o cursor no campo de digitação
            chatbox_posiciona_cursor(chatbox);

            return chatbox;
        };

        /**
         * Funções do chat_list
         */

        let chat_list_get_bodycontent = function(chat_list) {
                return chat_list.find(".chat-user-list__bodycontent").first();
            },
            chat_list_get_body = function(chat_list) {
                return chat_list.find(".chat-user-list__body").first();
            },
            chat_list_get_title = function(chat_list) {
                return chat_list.find(".chat-user-list__title").first();
            },
            chat_list_get_rollerbody = function(chat_list) {
                return chat_list.find(".chat-user-list__rollerbody").first();
            },
            chat_list_get_roller = function(chat_list) {
                return chat_list.find(".chat-user-list__roller").first();
            },
            chat_list_get_users = function(chat_list) {
                return chat_list.find('a.chat-item-anchor');
            },
            chat_list_get_assistido = function(chat_list, assistido_solar_id) {

                /* let assistidos = chat_list.data('assistidos'); */
                let adonis = chat_list_get_adonis(chat_list);
                let retorno = false;

                adonis.assistidos.forEach(function(el, idx){
                    if(el.user.solar_id == assistido_solar_id){
                        retorno = el;
                    }
                });

                return retorno;

            },
            chat_list_get_adonis = function(chat_list) {
                return chat_list.data('adonis');
            },
            pega_usuario_da_lista_por_channel_string = function(chat_list, channel_string){

                let objeto_channel = get_object_from_channel_string(channel_string);

                return pega_usuario_da_lista(chat_list, objeto_channel.defensor_id, objeto_channel.assistido_solar_id);

            },
            pega_usuario_da_lista = function(chat_list, defensor, assistido_solar_id){

                let return_element;

                chat_list_get_users(chat_list).each(function(idx, chat_item){

                    chat_item = $(chat_item);

                    let chat_defensor = chat_item.data('defensor');
                    let chat_user_solar_id = chat_item.data('assistido_solar_id');

                    if(chat_defensor==defensor && chat_user_solar_id==assistido_solar_id){

                        return_element = chat_item;

                    }

                });

                return return_element;

            },
            get_or_create_usuario_da_lista = function(chat_list, conversa) {

                let usuario_da_lista = pega_usuario_da_lista(chat_list, conversa.defensor, conversa.assistido);

                // Se o usuario da lista não existia, instancia com base nos dados da conversa
                if(typeof usuario_da_lista == 'undefined'){
                    usuario_da_lista = instanciar_usuario_na_lista(chat_list, conversa.defensor, conversa.assistido);
                }

                return usuario_da_lista;

            },
            pega_usuarios_por_solar_id = function(chat_list, solar_id){

                let return_element = [];

                chat_list_get_users(chat_list).each(function(idx, el){
                    el = $(el);
                    if(el.data('assistido_solar_id')==solar_id){
                        return_element.push(el);
                    }
                });

                return return_element;

            },
            user_get_unread_badge = function(usuario_da_lista){

                return usuario_da_lista.find(".chat-item-unread .chat-item-unread-badge").first();

            },
            set_element_badge = function(usuario_da_lista, unread){
                user_get_unread_badge(usuario_da_lista).html(unread);
                let display_value;
                if(parseInt(unread)==0){
                    display_value = 'none';
                }else{
                    display_value = 'inline-block';
                }
                user_get_unread_badge(usuario_da_lista).css('display', display_value );
            }
            set_unread_adonis_messages = function(usuario_da_lista, count){

                let channel = usuario_da_lista.data('channel');

                if(typeof(count) != 'number'){
                    count = parseInt(count);
                }

                channel.unread_adonis_messages = count;

            },
            update_unread_badge_adonis = function(usuario_da_lista){

                let channel = usuario_da_lista.data('channel');

                if(typeof(channel) == 'undefined'){
                    throw new Error('O channel não foi encontrado em "data" neste usuario da lista.');
                }

                if(typeof(channel.unread_adonis_messages) == 'undefined') channel.unread_adonis_messages = 0;
                if(typeof(channel.unread_adonis_messages) != 'number') channel.unread_adonis_messages = parseInt(unread_adonis.length);

                let count = channel.unread_adonis_messages;

                set_element_badge(usuario_da_lista, count);

            },
            atualiza_todos_badges_adonis = function(adonisApp){

                // TODO: Criar uma lista com todos os usuarios da lista
                let usuarios_da_lista = chat_list_get_users(adonisApp.chat_list);

                usuarios_da_lista.each(function(idx_usuario_da_lista, usuario_da_lista){

                    usuario_da_lista = $(usuario_da_lista);

                    let channel_string = usuario_da_lista.data('channel').channel_string;
                    let opened_chatbox = chatbox_get_opened_chat(channel_string);
                    let channel = usuario_da_lista.data('channel');
                    let conversas = channel.conversas;
                    let numero_de_mensagens_nao_lidas = 0;

                    // Itera sobre as onversas e sobre as mensagens
                    conversas.forEach(function(conversa, idx_conversa){
                        conversa.messages.forEach(function(mensagem, idx_mensagem){
                            // Se a mensagem não foi recebida, aumenta o número de mensagens não lidas
                            if(mensagem.received == false){
                                // Se o chatbox está aberto
                                if(typeof(opened_chatbox) != 'undefined'){
                                    // Informa ao servidor que o Solar recebeu
                                    channel.subscription.emit('messageReceived', {
                                        message_id: mensagem.id
                                    })
                                }
                                numero_de_mensagens_nao_lidas += 1;
                            }
                        });
                    });

                    // TODO: Mudar a bagde deste usuario da lista
                    set_element_badge(usuario_da_lista, numero_de_mensagens_nao_lidas)

                });

            },
            lista_defensorias = function(callback) {

                $.get("/defensoria/listar/", {}, callback);

            },
            lista_assistidos_por_ids = function(lista_ids_assistidos, callback) {

                $.get("/api/v1/pessoasassistidas/por-ids", {ids_assistidos : JSON.stringify(lista_ids_assistidos)}, callback);

            },
            busca_atendimentos_com_pendencias = function(defensor_id, assistido_solar_id, success, error, complete) {

                // Lista os documentos pendentes de um atendimento:
                // curl -X GET --header 'Accept: application/json' --header 'Authorization: Token {token}' 'http://127.0.0.1:8000/api/v1/atendimentos/{numero_atendimento}/documentos/?pendentes=false'
                // http://127.0.0.1:8000/api/v1/atendimentos/{numero_atendimento}/documentos/?pendentes=false
                // http://127.0.0.1:8000/api/v1/atendimentos/com-documento-pendente/{defensor_id}/?assistido_id={assistido_solar_id}

                let url = SOLAR_ATENDIMENTOS_COM_DOC_PENDENTE.replace('{defensor_id}', defensor_id).replace('{assistido_solar_id}', assistido_solar_id);

                $.ajax({
                    /* async: false, */
                    success: success,
                    error: error,
                    complete: complete,
                    // crossDomain: true,
                    data: {},
                    method: 'GET',
                    url: url,
                  });

            },
            busca_informacoes_de_documento = function(atendimento_numero, documento_id, success) {

                // Lista os documentos pendentes de um atendimento:
                // curl -X GET --header 'Accept: application/json' --header 'Authorization: Token {token}' 'http://127.0.0.1:8000/api/v1/atendimentos/{numero_atendimento}/documentos/?pendentes=false'
                // http://127.0.0.1:8000/api/v1/atendimentos/{numero_atendimento}/documentos/?pendentes=false
                // http://127.0.0.1:8000/api/v1/atendimentos/com-documento-pendente/{defensor_id}/?assistido_id={assistido_solar_id}

                let url = SOLAR_INFORMACOES_DE_DOCUMENTO.replace('{atendimento_numero}', atendimento_numero).replace('{documento_id}', documento_id);

                $.ajax({
                    method: 'GET',
                    url: url,
                    data: {},
                    success: success,
                  });

            },
            baixaDocumentoSolar = function(atendimento_numero, documento_id) {

                console.log(typeof(atendimento_numero));
                console.log(typeof(documento_id));

                if(!(atendimento_numero) || !(documento_id) || atendimento_numero=='null' || documento_id=='null'){
                    alert('Número do atendimento ou identificação do documento não encontrado.');
                    return;
                }

                busca_informacoes_de_documento(atendimento_numero, documento_id, function(data, textStatus){

                    if(typeof(data.arquivo) == 'string'){
                        niceDownloadFile(data.arquivo);
                    }

                });

            },
            lista_possiveis_conversas = function(callback) {

                $.get(SOLAR_POSSIVEIS_CONVERSAS_PATHNAME, {}, callback);
            },
            lista_conversas = function(defensor_id, callback) {

                // http://10.103.17.160:3333/api/v1/messages/31/rooms

                // result = [
                //     {
                //         defensor_id: 31,
                //         defensoria_id: 2,
                //         assistido_cpf: "01183452225"
                //     }
                // ];

                $.get(KENNEDY_API_BASE+"/"+defensor_id+"/rooms", {}, callback);
            },
            lista_unread = function(assistido_cpf, callback) {

                // http://10.103.17.160:3333/api/v1/messages/01183452225/1/total

                // a = [
                //     { defensor_id: 31, defensoria_id: 2, total: "0" },
                //     { defensor_id: 37, defensoria_id: 44, total: "1" }
                // ];

                let url = KENNEDY_API_BASE+"/"+assistido_cpf+"/"+codigos.GABINETE+"/total";

                $.ajax({
                    async: false,
                    success: callback,
                    // crossDomain: true,
                    data: {},
                    method: 'GET',
                    url: url,
                  });

            },
            lista_mensagens = function(defensor_id, defensoria_id, assistido_cpf, callback) {

                // http://10.103.17.160:3333/api/v1/messages/31/2/01183452225/all

                // retult = [
                //     {
                //         id: 60,
                //         defensor_id: 31,
                //         defensoria_id: 2,
                //         assistido_cpf: "01183452225",
                //         message: "Teste de mensagem\n",
                //         sended_by: 0,
                //         sended_date: "2019-11-19T10:46:00.000Z",
                //         delivered_defensor: true,
                //         delivered_assistido: true,
                //         created_at: "2019-11-21 04:47:17",
                //         updated_at: "2019-11-21 04:47:39"
                //     },
                //     {
                //         id: 59,
                //         defensor_id: 31,
                //         defensoria_id: 2,
                //         assistido_cpf: "01183452225",
                //         message:
                //             "Estou com dúvidas no que esta acontecendo no meu processo",
                //         sended_by: 1,
                //         sended_date: "2019-11-19T10:52:33.000Z",
                //         delivered_defensor: false,
                //         delivered_assistido: true,
                //         created_at: "2019-11-19 06:55:08",
                //         updated_at: "2019-11-19 06:55:08"
                //     },
                // ];

                $.get(KENNEDY_API_BASE+"/"+defensor_id+"/"+defensoria_id+"/"+assistido_cpf+"/all", {}, callback);
            },
            lista_novas_mensagens = function(defensor_id, defensoria_id, assistido_cpf, callback) {

                // http://10.103.17.160:3333/api/v1/messages/31/2/01183452225/0

                // retult = [
                //     {
                //         id: 60,
                //         defensor_id: 31,
                //         defensoria_id: 2,
                //         assistido_cpf: "01183452225",
                //         message: "Teste de mensagem\n",
                //         sended_by: 0,
                //         sended_date: "2019-11-19T10:46:00.000Z",
                //         delivered_defensor: true,
                //         delivered_assistido: true,
                //         created_at: "2019-11-21 04:47:17",
                //         updated_at: "2019-11-21 04:47:39"
                //     },
                //     {
                //         id: 59,
                //         defensor_id: 31,
                //         defensoria_id: 2,
                //         assistido_cpf: "01183452225",
                //         message:
                //             "Estou com dúvidas no que esta acontecendo no meu processo",
                //         sended_by: 1,
                //         sended_date: "2019-11-19T10:52:33.000Z",
                //         delivered_defensor: false,
                //         delivered_assistido: true,
                //         created_at: "2019-11-19 06:55:08",
                //         updated_at: "2019-11-19 06:55:08"
                //     },
                // ];

                $.get(KENNEDY_API_BASE+"/"+defensor_id+"/"+defensoria_id+"/"+assistido_cpf+"/"+codigos.GABINETE, {}, callback);
            },
            possiveis_conversas_2_titulares = function(possiveis_conversas) {

                let titulares = [];

                // Para cada possível conversa
                possiveis_conversas.forEach(function(possivel_conversa, idx){

                    // Se não tinha ainda o objeto do titular
                    if(typeof titulares[possivel_conversa.titular] == 'undefined'){

                        // Cria o objeto do titular
                        titulares[possivel_conversa.titular] = {
                            buscou_assistidos: false,
                            salas: [],
                            dados: possivel_conversa.titular_dados
                        }
                    }

                    // Adiciona a sala no objeto do titular
                    titulares[possivel_conversa.titular].salas[possivel_conversa.defensoria] = {
                        assistidos: []
                    }

                });

                return titulares;
            },
            unread_from_conversa = function(conversa, unreads){

                let selected_unread = undefined;

                // Para cada unread encontrado
                unreads.forEach(function(unread, unread_idx){

                    // Pega o que faz referêcia à conversa que está tratando
                    if(unread.defensor_id == conversa.defensor_id){
                        selected_unread = unread;
                        return;
                    }

                });

                return selected_unread;

            },
            atualiza_sala_com_conversa = function(titulares, titular_idx, conversa, lista_cpf_assistidos) {

                let cpf = conversa.assistido_cpf;

                // Se não a sala não existe na lista de salas do titular, não continua
                if(typeof titulares[titular_idx].salas[defensoria_id] == 'undefined'){

                    // Isto significa que o usuário logado não tem permissão pra acessar a conversa
                    return;

                }

                // Se o array de assistidos não existia na sala, cria
                if(!titulares[titular_idx].salas[defensoria_id].assistidos instanceof Array){
                    titulares[titular_idx].salas[defensoria_id].assistidos = [];
                }

                // Coloca o CPF da conversa no array da sala se ele não for encontrado
                if(titulares[titular_idx].salas[defensoria_id].assistidos.indexOf(cpf) === -1) titulares[titular_idx].salas[defensoria_id].assistidos.push(cpf);

                // Salva o cpf dos assistidos em um array
                if(lista_cpf_assistidos.indexOf(cpf) === -1) lista_cpf_assistidos.push(cpf);

            },
            verifica_se_ja_buscou_assistido_em_todas_as_salas = function(titulares) {

                // Verifica se já buscou o assistido em todas as salas
                let buscou_assistido_em_todas_as_salas = true;

                // Para cada titular
                titulares.forEach(function(titular){

                    if(!titular.buscou_assistidos){

                        buscou_assistido_em_todas_as_salas = false;
                        return;
                    }

                    // Se já descobriu que não buscou o assistido em todas as salas, para de tentar descobrir
                    if(!buscou_assistido_em_todas_as_salas){

                        return;
                    }

                });

                return buscou_assistido_em_todas_as_salas;

            },
            atualiza_chat_items_com_assistidos = function(chat_list, assistidos) {

                assistidos.forEach(function(assistido, idx){

                    // Procura os usuarios pelo id solar do assistido, para cada um
                    pega_usuarios_por_solar_id(chat_list, assistido.user.solar_id).forEach(function(chat_item, idx){

                        // Atualiza a propriedade 'assistido'
                        chat_item.data('assistido', assistido);

                        // Chama o método de atualizar
                        chat_item.data('fn_atualiza').call();

                    });

                });

            },
            ids_das_novas_mensagens = function(mensagens_novas) {

                let novas_mensagens_ids = [];

                mensagens_novas.forEach(function(nova_mensagem){

                    novas_mensagens_ids.push(nova_mensagem.id);

                });

                return novas_mensagens_ids;

            },
            marca_mensagens_como_novas_ou_nao = function(mensagens, mensagens_novas) {

                let novas_mensagens_ids = ids_das_novas_mensagens(mensagens_novas);

                // Para cada mensagem trazida de todas
                mensagens.forEach(function(mensagem){

                    // Presume que ela não é uma mensagem nova
                    mensagem.new_message = false;

                    // Se a mensagem existe na lista de mensagens novas
                    if(novas_mensagens_ids.indexOf(mensagem.id) != -1){

                        // Diz que ela é uma mensagem nova
                        mensagem.new_message = true;

                    }

                });

            },
            populate_adonisApp_with_jsonData = function(adonisApp, jsondata){

                adonisApp.token_type = jsondata.type;
                adonisApp.authentication_token = jsondata.token;
                adonisApp.refresh_token = jsondata.refreshToken;

            },
            instanciar_lista_usuarios = function(defensorias){

                let lista_usuarios_container = $("#chat-user-list-container"),
                    title = "Chat e-Defensor";

                let context_menu = instancia_context_menu('context-menu');

                let chat_user_list = $(document.createElement("div")).attr({
                    "class": "chat-user-list chat-user-list--tray"
                }).data(
                    'defensorias', defensorias
                ).data(
                    'context-menu', context_menu
                ).data(
                    'assistidos', []
                ).data(
                    'fn_adiciona_assistidos', function(){

                        let assistidos = this;

                        // Para cada assistido da lista passada por parâmetro
                        assistidos.forEach(function(assistido, idx){

                            // Se não tem CPF, pula ele
                            if(!assistido.dados.cpf instanceof String && typeof assistido.dados.cpf !== 'string'){
                                return;
                            }

                            // Se o assistido não tem foto ou se não aderiu ao e-Defensor, não inclui ele na lista
                            if((typeof assistido.dados.foto == 'undefined')||(assistido.dados.aderiu_edefensor.valueOf() == false)){
                                return;
                            }

                        });
                    }
                ).html([
                "<div class='chat-user-list__title'>",
                "   <h5><a href='javascript:void(0);'>"+title+"</a></h5>",
                "   <button class='chat-user-list__title__tray'>",
                "       <span>",
                "       </span>",
                "   </button>",
                "</div>",
                "<div class='chat-user-list__header'>",
                "    <span class='chat-user-list__top-title'>",
                "        Últimas mensagens",
                "    </span>",
                "</div>",
                "<div class='chat-user-list__rollerbody'>",
                "    <div class='chat-user-list__roller'>",
                "    </div>",
                "</div>",
                "<div class='chat-user-list__body'>",
                "    <div class='chat-user-list__bodycontent'>",
                "    </div>",
                "</div>",
                ].join(""));



                let chat_list_title = chat_list_get_title(chat_user_list),
                    chat_list_rollerbody = chat_list_get_rollerbody(chat_user_list);

                chat_list_rollerbody.on('scroll', function(e){
                    posiciona_todos_pelo_indice(chat_user_list);
                });

                // Quando clica no ícone de mostrar/esconder lista de chats
                chat_list_title.on('click', function() {
                    chat_user_list.toggleClass('chat-user-list--tray');
                });

                chat_user_list.on('click', function() {
                    context_menu.data('fn_hide').call();
                });

                // Adiciona o elemento do chat no container de chats
                lista_usuarios_container.append(chat_user_list);

                return chat_user_list;
            },
            get_or_create_lista_usuarios = function(defensorias) {

                let lista_usuarios_container = $("#chat-user-list-container");

                if(lista_usuarios_container.find('div.chat-user-list').length > 0){
                    return lista_usuarios_container.find('div.chat-user-list').first();
                }

                return instanciar_lista_usuarios(defensorias);

            }
            pega_elemento_anterior = function(chat_list, chat_element) {

                let before_element = '',
                    timestamp = chat_element.data('timestamp');

                let chat_list_items = chat_list_get_users(chat_list);

                chat_list_items.each(function(idx, el){

                    el = $(el);

                    if(timestamp > parseInt(el.data('timestamp'))){
                        before_element = el;
                    }

                });

                return before_element;

            },
            insere_pelo_timestamp = function(chat_list, chat_item) {

                let chat_list_bodycontent = chat_list_get_bodycontent(chat_list),
                    before_element = pega_elemento_anterior(chat_list, chat_item);

                if(before_element == ''){
                    chat_list_bodycontent.append(chat_item);
                }else{
                    before_element.before(chat_item);
                }

            },
            ordena_pelo_timestamp = function(lista_usuarios) {

                return lista_usuarios.sort(function(a, b){

                    let timestamp_a = parseInt($(a).data('timestamp')),
                        timestamp_b = parseInt($(b).data('timestamp'));

                    if (timestamp_a > timestamp_b){
                        return -1;
                    }else{
                        return 1;
                    }

                });

            },
            ordena_pelo_timestamp_adonis = function(lista_usuarios) {

                if(typeof(lista_usuarios) != 'object'){
                    throw new Error('A lista passada por parâmetro não é um objeto!')
                }

                if(lista_usuarios.length == 0){
                    return [];
                }

                let active_chats = $(lista_usuarios[0]).data('chat_list').data('adonis').active_chats;

                return lista_usuarios.sort(function(a, b){

                    let conversas_a = $(a).data('channel').conversas;
                    let conversas_b = $(b).data('channel').conversas;
                    let ultima_conversa_a = conversas_a[conversas_a.length-1];
                    let ultima_conversa_b = conversas_b[conversas_b.length-1];
                    let timestamp_a = Date.parse(ultima_conversa_a.messages[ultima_conversa_a.messages.length-1].created_at);
                    let timestamp_b = Date.parse(ultima_conversa_b.messages[ultima_conversa_b.messages.length-1].created_at);

                    if (timestamp_a > timestamp_b){
                        return -1;
                    }else{
                        return 1;
                    }

                });

            },
            posiciona_pelo_timestamp_e_unread = function(chat_list) {

                let lista_unread = [],
                    lista_read = [];

                let chat_list_items = chat_list_get_users(chat_list);


                if(chat_list_items.length >0){

                    chat_list_items.each(function(idx, el){
                        if(parseInt($(el).data('unread'))>0) {
                            lista_unread.push(el);
                        }else{
                            lista_read.push(el);
                        }
                    });

                    lista_unread = ordena_pelo_timestamp(lista_unread);

                    lista_read = ordena_pelo_timestamp(lista_read);

                    let chat_body = chat_list_get_body(chat_list);

                    let current_element;
                    if(lista_unread.length > 0){
                        current_element = lista_unread[0];
                    }else if(lista_read.length > 0){
                        current_element = lista_read[0];
                    }

                    lista_unread.forEach(function(el, idx){

                        if(current_element == el){
                            chat_body.prepend($(el));
                        }else{
                            $(current_element).after($(el));
                            current_element = el;
                        }
                    });

                    lista_read.forEach(function(el, idx){

                        if(current_element == el){
                            chat_body.prepend($(el));
                        }else{
                            $(current_element).after($(el));
                            current_element = el;
                        }

                    });

                    posiciona_todos_pelo_indice(chat_list);

                }

                atualiza_tamanho_do_roller(chat_list);

            }
            posiciona_pelo_timestamp_e_unread_adonis = function(chat_list) {

                let lista_unread = [],
                    lista_read = [];

                let chat_list_items = chat_list_get_users(chat_list);


                if(chat_list_items.length >0){

                    chat_list_items.each(function(idx, el){
                        if(parseInt($(el).data('unread'))>0) {
                            lista_unread.push(el);
                        }else{
                            lista_read.push(el);
                        }
                    });

                    lista_unread = ordena_pelo_timestamp_adonis(lista_unread);

                    lista_read = ordena_pelo_timestamp_adonis(lista_read);

                    let chat_body = chat_list_get_body(chat_list);

                    let current_element;
                    if(lista_unread.length > 0){
                        current_element = lista_unread[0];
                    }else if(lista_read.length > 0){
                        current_element = lista_read[0];
                    }

                    lista_unread.forEach(function(el, idx){

                        if(current_element == el){
                            chat_body.prepend($(el));
                        }else{
                            $(current_element).after($(el));
                            current_element = el;
                        }
                    });

                    lista_read.forEach(function(el, idx){

                        if(current_element == el){
                            chat_body.prepend($(el));
                        }else{
                            $(current_element).after($(el));
                            current_element = el;
                        }

                    });

                    posiciona_todos_pelo_indice(chat_list);

                }

                atualiza_tamanho_do_roller(chat_list);

            }
            posiciona_pelo_indice = function(chat_list, chat_item) {

                let index = chat_list_get_users(chat_list).index(chat_item),
                    rolagem = lista_pega_rolagem(chat_list),
                    top = 0 + index*UDL_HEIGHT - rolagem;

                chat_item.css('top', top+'px');

            },
            posiciona_todos_pelo_indice = function(chat_list) {

                normaliza_rolagem_de_usuarios(chat_list);

                chat_list_get_users(chat_list).each(function(idx, el) {
                    el = $(el);
                    posiciona_pelo_indice(chat_list, el);
                });

            },
            lista_pega_rolagem = function(chat_list) {

                let rollerbody = chat_list_get_rollerbody(chat_list);

                return rollerbody[0].scrollTop;

            },
            normaliza_rolagem_de_usuarios = function(chat_list) {

                // Normaliza posição do Rolerbody
                let body = chat_list_get_body(chat_list),
                    rollerbody = chat_list_get_rollerbody(chat_list),
                    roller = chat_list_get_roller(chat_list),
                    body_offset = get_container_offset(body),
                    user_list = chat_list_get_users(chat_list),
                    height = user_list.length*UDL_HEIGHT;

                rollerbody.css('top', body_offset.top);
                rollerbody.css('left', body_offset.left);

                // Normaliza o tamanho do rollerbody
                rollerbody.css('width', body[0].offsetWidth+12);
                rollerbody.css('height', body[0].offsetHeight-22);

                // Normaliza barra de rolagem
                roller.css('height', height+'px');

            },
            instanciar_usuario_na_lista = function(chat_list, defensor_id, assistido_solar_id, unread) {

                // Cria um usuário com os dados
                /* let assistido_aux = {
                    dados: {
                        cpf: cpf,
                        nome: 'Não definido'
                    }
                }; */

                let adonisApp = chat_list_get_adonis(chat_list);
                let assistido_adonis = adonis_get_assistido_by_solar_id(adonisApp, assistido_solar_id);

                // Se não foi passado o unread por parãmetro, é 0
                unread = (typeof unread == 'undefined') ? 0 : unread;

                var usuario_da_lista = $(document.createElement("a")).attr({
                    "href": "javascript:void(0);",
                    "class": "chat-item-anchor",
                }).data(
                    'assistido_solar_id', assistido_solar_id
                ).data(
                    'defensor', defensor_id
                ).data(
                    'timestamp', 0
                ).data(
                    'unread', unread
                ).data(
                    'fetched', false
                ).data(
                    'chat_list', chat_list
                ).data(
                    'fn_atualiza', function() {

                        real_usuario_da_lista = this.valueOf();

                        let adonisApp = chat_list.data('adonis');
                        let defensor_id = usuario_da_lista.data('defensor');
                        let assistido_solar_id = usuario_da_lista.data('assistido_solar_id');
                        let assistido = chat_list_get_assistido(chat_list, assistido_solar_id);

                        // Se o assistido não foi encontrado na lista global, lança erro
                        if(typeof assistido == 'undefined') {

                            throw new Error('O assistido não foi encontrado na lista global!');

                        }

                        // Se o assistido tem foto de perfil
                        if(assistido.dados.foto){

                            // Mostra a foto de perfil no usuário da lista
                            profile_url = assistido.dados.foto;

                            // Pega a foto do usuário da lista
                            let usuario_da_lista_foto = usuario_da_lista.find('.chat-item-photo').find('img').first();

                            // Se a foto de perfil está diferente
                            if(usuario_da_lista_foto.attr('src') != profile_url){

                                // Atualiza a foto do usuário da lista
                                usuario_da_lista_foto.attr('src', profile_url);

                            }

                        }

                        let titular = adonisApp.titulares[defensor_id];
                        let def_nome = titular.dados.servidor.nome;
                        let defensor_color = seedHexColor(parseInt(defensor_id+1));

                        usuario_da_lista.attr('title', "Com o defensor "+defensor_id+" ("+def_nome+")");
                        usuario_da_lista.find('.chat-item-name').first().css('color', defensor_color).html(assistido.dados.nome);
                        usuario_da_lista.find('.chat-item-cpf').first().css('color', defensor_color).html(" ("+assistido.dados.cpf+")");

                        atualiza_todos_badges_adonis(adonisApp);

                    }
                ).data(
                    'fn_get_dados', function() {

                        let assistido_solar_id = usuario_da_lista.data('assistido_solar_id');
                        let assistido = chat_list_get_assistido(chat_list, assistido_solar_id);
                        let assistido_cpf = assistido.dados.cpf;
                        let defensor_id = usuario_da_lista.data('defensor')
                        let unread = usuario_da_lista.data('unread');

                        return {
                            assistido_cpf: assistido_cpf,
                            assistido_solar_id: assistido_solar_id,
                            defensor_id: defensor_id,
                            unread: unread
                        };

                    }
                ).html([
                "        <div class='chat-item'>",
                "            <div class='chat-item-photo'>",
                "                <img src='/static/img/user.jpg' />",
                "            </div>",
                "            <div class='chat-item-text'>",
                "                <span class='chat-item-name'>",
                "                </span>",
                "                <span class='chat-item-cpf'>",
                "                </span>",
                "            </div>",
                "            <div class='chat-item-unread'>",
                "                <span class='badge badge-important chat-item-unread-badge'></span>",
                "            </div>",
                "        </div>"
                ].join(""));

                // Se o usuário ainda não existe na lista
                if(typeof assistido_adonis == 'undefined'){

                    return false;

                // Se o usuário existe na lista
                }else{

                    // Só atualiza as informações do usuário da lista
                    usuario_da_lista.data('fn_atualiza').call(usuario_da_lista);

                }

                // Quando clicar no usuário da lista
                usuario_da_lista.on('click', function(){

                    let assistido_solar_id = usuario_da_lista.data('assistido_solar_id');
                    let assistido = chat_list_get_assistido(chat_list, assistido_solar_id);
                    let defensor_id = usuario_da_lista.data('defensor');

                    // Tenta obter um possível chat já aberto
                    let chat_obtido = chatbox_get_opened_chat(get_channel_string(defensor_id, assistido.user.solar_id));

                    // Se foi encontrado algum chat aberto com estes dados
                    if(typeof chat_obtido != 'undefined') {

                        shine_chat(chat_obtido);

                    }else{

                        instanciar_chat(usuario_da_lista.data('chat_list'), assistido.user.solar_id, defensor_id);

                        set_element_badge(usuario_da_lista, 0);

                    }

                });

                // Quado clicar com o botão direito no usuário da lista
                usuario_da_lista.on('contextmenu', function(e) {

                    let context_menu = chat_list.data('context-menu');
                        opcao_arquivar = context_menu.find('a.context-menu-arquivar'),
                        opcao_testar = context_menu.find('a.context-menu-testar'),
                        opcao_cancelar = context_menu.find('a.context-menu-cancelar');

                    opcao_arquivar.off('click').on('click', function(){

                        channel_string = get_channel_string_by_usuario(usuario_da_lista);
                        adonis_encerrar_conversa(adonisApp, channel_string, function(data, textStatus){

                        });

                        context_menu.data('fn_hide').call();

                    });

                    opcao_testar.off('click').on('click', function(){

                        renova_token(adonisApp, function(data, textStatus){

                            if(textStatus == 'success'){

                                jsondata = $.parseJSON(data);
                                populate_adonisApp_with_jsonData(adonisApp, jsondata);

                            }

                        });

                        context_menu.data('fn_hide').call();

                    });

                    opcao_cancelar.off('click').on('click', function(){
                        context_menu.data('fn_hide').call();
                    });

                    var top = e.pageY - 10;
                    var left = e.pageX - 90;

                    context_menu.css({
                        display: "block",
                        top: top,
                        left: left
                    }).addClass("show");

                    e.preventDefault();

                });

                let chat_list_bodycontent = chat_list_get_bodycontent(chat_list);
                chat_list_bodycontent.append(usuario_da_lista);

                posiciona_pelo_timestamp_e_unread(chat_list);

                usuario_da_lista.hide(1);
                usuario_da_lista.show(600);

                return usuario_da_lista;

            },
            instancia_context_menu = function(custom_id){

                let context_menu_container = $("#context-menu-container");

                let context_menu = $(document.createElement("div")).attr({
                    "id": custom_id,
                    "class": "dropdown-menu",
                    "role": "menu",
                    "aria-labelledby": "dropdownMenu"
                }).data(
                    'fn_hide', function(){
                        context_menu.removeClass("show").hide(300);
                    }
                ).html([
                    "    <li><a tabindex='-1' href='javascript:void(0);' class='context-menu-arquivar'>Finalizar conversa</a></li>",
                    "    <li><a tabindex='-1' href='javascript:void(0);' class='context-menu-testar' style='display:none;'>Testar (Refresh Token)</a></li>",
                    "    <li class='divider'></li>",
                    "    <li><a tabindex='-1' href='javascript:void(0);' class='context-menu-cancelar'>Cancelar</a></li>",
                ].join(""));

                context_menu_container.append(context_menu);

                return context_menu;
            },
            atualiza_tamanho_do_roller = function(chat_list) {
                let roller = chat_list.find('div.chat-user-list__roller'),
                    chat_list_items = chat_list_get_users(chat_list),
                    items_count = chat_list_items.length;

                roller.css('height', items_count*UDL_HEIGHT+'px')
            },
            fecha_usuario_da_lista = function(usuario_pra_fechar) {
                usuario_pra_fechar.hide(600, function(){
                    usuario_pra_fechar.remove();
                    posiciona_pelo_timestamp_e_unread(chat_list);
                })
            },
            atualiza_timestamp = function(chat_list, chat_item, timestamp) {

                chat_item.data('timestamp', timestamp);

                insere_pelo_timestamp(chat_list, chat_item);

                posiciona_pelo_timestamp_e_unread(chat_list);

            };

        context_menu = undefined;
        chat_list = undefined;
        tocou_som_recentemente = false;
        som_notificacao_edefensor = $('#notificacao_edefensor_001');


        adonisApp = {
            is_connected: true,
            active_chats: [],
            assistidos: [], // Obtidos das conversas do adonis
            titulares: [],
            numero_mensagens_nao_lidas: [],
            ws: undefined,
            chat_list: undefined,
            authentication_token: undefined,
            refresh_token: undefined,

        };


        // Busca as Defensorias e depois continua
        lista_defensorias(function(defensorias, textStatus){

            // Lista as possíveis conversas (titular/defensoria que o usuário logado tem acesso)
            lista_possiveis_conversas(function(possiveis_conversas, textStatus){

                // Se trouxe ao menos uma possível conversa
                if(textStatus == 'success' && possiveis_conversas.length > 0) {

                    // Preenche a lista de titulares com base nas possíveis conversas
                    adonisApp.titulares = possiveis_conversas_2_titulares(possiveis_conversas);

                    gera_token(function (data, textStatus) {

                        jsondata = $.parseJSON(data);
                        populate_adonisApp_with_jsonData(adonisApp, jsondata);

                        let chat_list = get_or_create_lista_usuarios(defensorias);

                        adonisApp.chat_list = chat_list;

                        // Associa a variável adonis no chat_list
                        chat_list.data('adonis', adonisApp);

                        // Itera sobre os titulares pra buscar as conversas no Adonis e o numero de mensagens não lidas
                        adonisApp.titulares.forEach(function(el, titular_idx){

                            adonisApp.titulares[titular_idx].buscou_assistidos = false;

                            busca_numero_de_mensagens_nao_lidas(adonisApp, titular_idx, function (data, textStatus) {

                                // Salva o valor obtido na variável adonis
                                adonisApp.numero_mensagens_nao_lidas[titular_idx] = data;

                                busca_conversas_adonis(adonisApp, titular_idx, function (conversas_adonis_data, textStatus) {

                                    let lista_ids_assistidos_a_procurar =  [];

                                    // Itera sobre os dados que foram trazidos
                                    Object.entries(conversas_adonis_data).forEach(([idx_assistido, assistido]) => {

                                        if(typeof assistido[0] == 'undefined'){
                                            return false;
                                        }

                                        if(typeof assistido[0].user == 'undefined' || assistido[0].user == null){
                                            return false;
                                        }

                                        // Pega o usuario solar com base na primeira conversa
                                        usuario_solar = assistido[0].user;

                                        //Se o assistido ainda não existe na variavel adonisApp, cria
                                        if(typeof adonisApp.assistidos[idx_assistido] == 'undefined'){
                                            adonisApp.assistidos[idx_assistido] = {};
                                        }

                                        // Associa o usuario solar ao assistido
                                        adonisApp.assistidos[idx_assistido].user = usuario_solar;

                                        // Verifica se a ID do usuario solar ainda não existe no array e insere
                                        if(lista_ids_assistidos_a_procurar.indexOf(usuario_solar.solar_id) == -1){
                                            lista_ids_assistidos_a_procurar.push(usuario_solar.solar_id);
                                        }

                                    });

                                    // Marca no titular que já buscou o assistido (já colocou a id no array)
                                    adonisApp.titulares[titular_idx].buscou_assistidos = true;

                                    // Verifica se já buscou assistido em todas as salas
                                    buscou_assistido_em_todas_as_salas = verifica_se_ja_buscou_assistido_em_todas_as_salas(adonisApp.titulares)

                                    // Se já buscou os assistidos em todas as salas
                                    if(buscou_assistido_em_todas_as_salas){

                                        if(lista_ids_assistidos_a_procurar.length > 0){

                                            // Consulta cada assistido pra atualizar os usuários do chat
                                            lista_assistidos_por_ids(lista_ids_assistidos_a_procurar, function(assistidos_data, textStatus){

                                                let assistidos = assistidos_data.results;

                                                // Para cada um dos assistidos que trouxe da consulta
                                                assistidos.forEach(function(assistido, idx_assistido){

                                                    // Itera sobre os assistidos da variável adonisApp
                                                    adonisApp.assistidos.forEach(function(assistido_adonis, idx_el){

                                                        // Se a ID Solar do assistido adonis é igual à id trazida na consulta
                                                        if(adonisApp.assistidos[idx_el].user.solar_id == assistido.id){

                                                            // Cria um atributo "dados" no assistido adonis com os dados trazidos
                                                            adonisApp.assistidos[idx_el].dados = assistido;

                                                        }

                                                    });

                                                });

                                                // Web Socket Adonis
                                                let ws = adonis.Ws(ADONIS_CONNECTION_URI);

                                                adonisApp.ws = ws;

                                                ws.withApiToken(adonisApp.authentication_token);
                                                try {
                                                    ws.connect();
                                                } catch (err) {
                                                    throw new Error('Houve um erro ao tentar conectar com o web socket.');
                                                }

                                                ws.on('open', () => {

                                                    adonis.is_connected = true;
                                                    adonis.is_with_error = false;

                                                });

                                                ws.on('error', (error) => {

                                                    // Se o token expirou
                                                    if(error.code == 'E_INVALID_JWT_REFRESH_TOKEN'){

                                                        renova_token(adonisApp, function(data, textStatus){

                                                            if(textStatus == 'success'){

                                                                jsondata = $.parseJSON(data);
                                                                populate_adonisApp_with_jsonData(adonisApp, jsondata);

                                                            }

                                                        });
                                                    }

                                                    adonis.is_connected = false;
                                                    adonis.is_with_error = true;

                                                });

                                                ws.on('close', () => {

                                                    adonis.is_connected = false;
                                                    adonis.is_with_error = false;

                                                });

                                                chat_list.data('fn_adiciona_assistidos').call(adonisApp.assistidos);

                                                atualiza_chat_items_com_assistidos(chat_list, adonisApp.assistidos);

                                                // Itera sobre os dados que foram trazidos das conversas para criar os usuarios da lista
                                                Object.entries(conversas_adonis_data).forEach(([idx_assistido, conversas_do_assistido]) => {

                                                    let assistido_do_adonis = adonisApp.assistidos[idx_assistido];

                                                    conversa_chat = {
                                                        defensor: titular_idx,
                                                        assistido:  assistido_do_adonis.user.solar_id
                                                    }

                                                    // Pega o usuario da lista se ele existe
                                                    let usuario_da_lista = get_or_create_usuario_da_lista(chat_list, conversa_chat);

                                                    let channel_string = get_channel_string(titular_idx, assistido_do_adonis.user.solar_id);
                                                    let channel = get_or_create_channel_adonis(adonisApp, channel_string);
                                                    channel.conversas = conversas_do_assistido;

                                                    // Inverte as mensagens de cada conversa
                                                    conversas_do_assistido.forEach(function(conversa, idx_conversa){
                                                        conversa.messages = conversa.messages.reverse();
                                                    });

                                                    usuario_da_lista.data('channel', channel);
                                                    channel.usuario_da_lista = usuario_da_lista;

                                                    // Procura pelo unread deste assistido
                                                    adonisApp.numero_mensagens_nao_lidas[titular_idx].forEach(function(unread_adonis, idx_unread_adonis){

                                                        if(unread_adonis.assistido = assistido_do_adonis.user.id){

                                                            channel.unread_adonis = unread_adonis;

                                                            set_unread_adonis_messages(usuario_da_lista, unread_adonis.__meta__.total_messages);
                                                            atualiza_todos_badges_adonis(adonisApp);

                                                        }
                                                    });

                                                });

                                                posiciona_pelo_timestamp_e_unread_adonis(chat_list);

                                                $(window).unload(function(event){
                                                    adonisApp.active_chats.forEach(function(idx, active_chat){
                                                        active_chat.close();
                                                    });
                                                    // Na verdade, só este comando era suficiente, pois ele "Removes all subscriptions and does not trigger a reconnection."
                                                    adonisApp.ws.close();
                                                });

                                            });

                                        } // Fim da condição "lista de assistidos com base nas conversas está vazia"

                                    } // Fim da condição "já buscou assistido em todas as salas"


                                }); // Fim da requisição que busca as conversas no Adonis

                            }); // Fim da requisiççao que busca o número de mensagens não lidas

                        }); // Fim da iteração sobre os titulares pra buscar as conversas no Adnois

                    }); // Fim da requisição Gera Token

                } // Fim da condição "trouxe ao menos uma possível conversa"

            }); // Fim da requisição "Lista as possíveis conversas"

        }); // Fim da requisição "Busca as Defensorias"

    }); // Fim do "$(document).ready"

})(jQuery);
