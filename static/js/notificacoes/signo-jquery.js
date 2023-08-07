function isNull(object) {
    return object === null;
}

function isUndef(object) {
    return object === undefined;
}

function isNumber(object) {
    return typeof object === 'number';
}

// https://gist.github.com/dannvix/214bc31ae46d8c447333
function formatter(literals, ...substitutions) {
    return {
        format: function () {
            let out = [], i = 0, k = 0;
            for (i, k; i < literals.length; i++) {
                out[k++] = literals[i];
                out[k++] = Number.isInteger(substitutions[i]) ?
                    arguments[substitutions[i]] :
                    arguments[0][substitutions[i]];
            }
            out[k] = literals[i];
            return out.join("");
        },
    };
}


var item_template = formatter`
                                <li class="new">
                                    <a href="${"link"}" target="_blank">
                                        <span class="pull-right text-info">${"created_at_human"}</span>
                                        <div class="media">
                                            <img class="media-object img-polaroid pull-left" src="/servidor/solar/foto/">
                                            <div class="media-body">
                                                <h4 class="media-heading">${"title"}</h4>
                                                <p>${"content"}</p>
                                            </div>
                                        </div>
                                        <div class="notification muted">
                                            ${"sender_name"}
                                        </div>
                                    </a>
                                </li>
`;


(function () {
    'use strict';

    function Signo() {
    }

    var self = this;
    var primeira_atualizacao = true;
    var startmessage;
    var signo_socket_url;
    var socket;
    var theuser;
    var app;
    var signodata;
    var all_messages_url;
    var mark_all_as_read_url;
    var solar_messages;
    var solar_messages_count;
    var solar_ultima_mensagem = null;
    var other_messages;
    var other_messages_count;

    // elementos no html (solar)
    var signo_notifications;
    var notification_dropdown;
    var notificacoes_contador;
    var ulNotificacoes;

    // elementos no html (outros)
    var signo_notifications_outros;
    var notification_dropdown_outros;
    var notificacoes_contador_outros;
    var ulNotificacoes_outros;

    var startsigno = function () {
        socket = new WebSocket(signo_socket_url);
        var id = {
            channel: 'NotificationChannel',
            user: '' + theuser + ''
            ,
            app: 'SOLAR'
            ,
            group_by: 'app' // ou 'module'
            // only_app: 'solar',
        };

        var sub_cmd = {
            command: 'subscribe',
            identifier: JSON.stringify(id)
        };
        startmessage = JSON.stringify(sub_cmd);
        socket.onerror = function (error) {
            //console.log('erros do WebSocket: ' + error + error[0] + error[1]);
        };

        socket.onopen = function (event) {
            socket.send(startmessage);
            //console.log("onopen. Conectado " + signo_socket_url);
        };
        socket.onclose = function (event) {
        };

        socket.onmessage = function (event) {

            var data = JSON.parse(event.data);

            if (isUndef(data.message) || isNumber(data.message)) {
                //console.log('onmessage: isUndef(data.message) || isNumber(data.message)');
            } else if (isNull(data.message)) {
                // Signo.notificationRemoveAll();
                //console.log('onmessage:  else if (isNull(data.message))');
            } else {
                parse_messages(data);
            }
        };

    };

    var atualizarInterface = function () {
        ulNotificacoes.html("");
        $(notificacoes_contador).text(solar_messages_count);
        $(notificacoes_contador).attr('title', solar_messages_count + ' notificações');
        var balancar = false;
        for (var appname in solar_messages) {
            if (solar_messages.hasOwnProperty(appname)) {
                var messages = solar_messages[appname];
                for (var index in messages) {
                    if (messages.hasOwnProperty(index)) {
                        var msg = messages[index];
                        if(msg.sender)
                        {
                            msg.sender_name = msg.sender.username;
                            msg.sender_username = msg.sender.username;
                        }
                        else
                        {
                            msg.sender_name = '(sistema)';
                            msg.sender_username = 'solar';
                        }
                        msg.created_at_human = jQuery.timeago(msg.created_at);
                        var x = {
                            'content': msg.content,
                            'title': msg.title,
                            'link': msg.link,
                            'mark_as_read': msg.mark_as_read

                        };
                        var item = item_template.format(msg);
                        $(ulNotificacoes).append($(item));
                        if (index == 0 && msg.id > solar_ultima_mensagem.id) {
                            solar_ultima_mensagem = msg;
                            balancar = true;
                        }
                    }
                }
            }
        }
        if(balancar)
        {
            $('#signo-notifications').animateCss('shake', function () {});
        }
    };

    var atualizarInterfaceOutros = function () {
        ulNotificacoes_outros.html("");
        $(notificacoes_contador_outros).text(other_messages_count);
        $(notificacoes_contador_outros).attr('title', other_messages_count + ' notificações');
        for (var appname in other_messages) {

            if (other_messages.hasOwnProperty(appname)) {
                $(ulNotificacoes_outros).append($('<li class="notification text-center"><b>'+appname+'</b></li>'));
                var messages = other_messages[appname];
                for (var index in messages) {
                    if (messages.hasOwnProperty(index)) {
                        var msg = messages[index];
                        if(msg.sender)
                        {
                            msg.sender_username = msg.sender.username;
                        }
                        else
                        {
                            msg.sender_username = '(sistema)';
                        }
                        msg.created_at_human = jQuery.timeago(msg.created_at);
                        var x = {
                            'content': msg.content,
                            'title': msg.title,
                            'link': msg.link,
                            'mark_as_read': msg.mark_as_read

                        };
                        var item = item_template.format(msg);
                        $(ulNotificacoes_outros).append($(item));
                    }
                }
            }
        }
        window.solar_messages = solar_messages;
        window.solar_ultima_mensagem = solar_ultima_mensagem;
    };

    var parse_messages = function (data_json) {
        var _other_messages = Object.assign({}, data_json.message.notifications.message[0]);
        delete _other_messages['SOLAR_DEV'];
        delete _other_messages['SOLAR'];
        var _counter_other_messages = 0;
        for (var key in _other_messages) {
            if (_other_messages.hasOwnProperty(key)) {
                _counter_other_messages += _other_messages[key].length;
            }
        }
        signodata = data_json;
        all_messages_url = data_json.message.notifications.all_message.link;
        mark_all_as_read_url = data_json.message.notifications.mark_all_read.link;
        solar_messages = {'SOLAR': Object.assign([], data_json.message.notifications.message[0]['SOLAR'])};
        if(solar_ultima_mensagem==null)
        {
            solar_ultima_mensagem = solar_messages.SOLAR[0];
        }
        solar_messages_count = solar_messages['SOLAR'].length;
        other_messages = _other_messages;
        other_messages_count = _counter_other_messages;
            atualizarInterface();
            atualizarInterfaceOutros();
    };
    Signo.connection = function (signosocket_url, user, app) {
        signo_socket_url = signosocket_url;
        theuser = window.atob(user);
        app = app;

        $(document).ready(function () {

            // SOLAR
            signo_notifications = $("#signo-notifications");
            notification_dropdown = $(".dropdown", signo_notifications);
            notificacoes_contador = $(".notificacoes-contador", signo_notifications);
            ulNotificacoes = $(".notificacoes-ul", signo_notifications);

            // OUTROS
            signo_notifications_outros = $("#signo-notifications-outros");
            notification_dropdown_outros = $(".dropdown", signo_notifications_outros);
            notificacoes_contador_outros = $(".notificacoes-contador", signo_notifications_outros);
            ulNotificacoes_outros = $(".notificacoes-ul", signo_notifications_outros);

            startsigno();

            // https://codepen.io/bsngr/pen/frDqh
            $('.signo-notifications div.btn-group').hover(function() {
                $(this).find('.dropdown-menu').stop(true, true).delay(100).fadeIn(200);
              }, function() {
                $(this).find('.dropdown-menu').stop(true, true).delay(100).fadeOut(200);
            });

        });

    };
    window.Signo = Signo;

})();
