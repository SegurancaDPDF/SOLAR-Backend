window.signosocketurl = 'wss://signo.defensoria.to.def.br/cable';
window.signoCurrentAppName = 'ODIN';
window.signoNotificationRootElementSelector = "#notification";
window.signoShowAllElementSelector = "#notification > ul > li.col-md-6.media.mostra-todas > a > span";

window.notificacoesMainDivSelector = '#notificacoes-div';
window.notificacaoBotaoContadorSelector = 'a.notificacoes-contador';
window.notificacaoUlSelector = 'ul.notificacoes-ul';


(function () {
    var divNotificacoes = $(window.notificacoesMainDivSelector);
    var botaoContador= divNotificacoes.find(window.notificacaoBotaoContadorSelector);
    var ulNotificacao= divNotificacoes.find(window.notificacaoUlSelector);
    window.botaoContador= botaoContador;
    window.ulNotificacao= ulNotificacao;

    function Signo() {
    }

    Array.prototype.selectBy = function (attribute, value) {
        return this.reduce(function (groups, item) {
            var key = ((item[attribute] === value) ? value : 'others');
            groups[key] = groups[key] || [];
            groups[key].push(item);
            return groups;
        }, {});
    };

    Array.prototype.groupBy = function (attribute) {
        return this.reduce(function (groups, item) {
            var value = item[attribute];
            groups[value] = groups[value] || [];
            groups[value].push(item);
            return groups;
        }, {});
    };


    Signo.mark_as_read = function (notification) {
        var xhttp;
        if (window.XMLHttpRequest) {
            xhttp = new XMLHttpRequest();
        } else {
            xhttp = new ActiveXObject("Microsoft.XMLHTTP");
        }
        xhttp.open("GET", notification, true);
        xhttp.send();
    };

    // Signo.appNotification = function (app) {
    //     var title = '' +
    //         '<li class="notification text-center">' +
    //         '<b><i>' + app + '</i></b>' +
    //         '</li>';
    //     $(signoShowAllElementSelector).before(title);
    // };

    // Signo.notificacaoHtml = function (item) {
    //     var notificacao = '' +
    //         '<li class="media notification">' +
    //         '<div class="media-body">' +
    //         '<a href="' + item.link + '" target="_blank">' +
    //         '<span class="label label-default pull-right">' +
    //         jQuery.timeago(item.created_at) +
    //         '</span>' +
    //         '<h6 class="media-heading">' + item.app + '</h6>' +
    //         '<p class="margin-none">' +
    //         item.title +
    //         '</p>' +
    //         '</a>' +
    //         '<h4 onclick=Signo.mark_as_read(\'' + item.mark_as_read + '\'); >' +
    //         '<i class="fa fa-fw icon-visual-eye-fill pull-right  pre_notificacao"></i>' +
    //         '</h4>' +
    //         '</div>' +
    //         '</li>';
    //     $(signoShowAllElementSelector).before(notificacao);
    // };

    Signo.notification = function (user, maingroup, datam) {

        // console.log(datam);

        var keys = Object.keys(datam);
        // console.log('chaves:' + keys);

        // var data = datam[maingroup];
        var total_messages = 0;
        for (var k = 0; k < keys.length; k++){
            total_messages += datam[keys[k]].length;
        }

        // var length = total_messages < 9 ? total_messages : '+9';
        var length = total_messages;

        botaoContador.html(length);
        if(length >= 2){
            botaoContador.attr('title', '' + length + ' notificações');
        }else{
            botaoContador.attr('title', '' + length + ' notificação');
        }


        for (var j = 0; j < keys.length; j++) {
            var key = keys[j];
            // console.log('key: '+  key);
            ulNotificacao.append('<li class="notification text-center"><b><i>'+ key +'</i></b></li>');
            if (datam.hasOwnProperty(key)) {
                var data = datam[key];
                for (var i = 0; i < data.length; i++) {
                    var item = data[i];
                    var notification_date = jQuery.timeago(item.created_at);

                    // $('#notification-dropdown .dropdown-menu').append('' +
                    //     '<li class="media">' +
                    //     '    <div class="media-body">' +
                    //     '        <span class="label label-default pull-right">' + notification_date + '</span>' +
                    //     '        <h5 class="media-heading"><a href="' + item.link + '">' + item.title + '</a></h5>' +
                    //     '        <p class="margin-none">' + item.content + '</p>' +
                    //     '    </div>' +
                    //     '</li>'
                    // );

                    var myvar = '<li class="new">'+
                    '    <a href="' + item.link +'">'+
                    '        <div class="notificationx">' + item.title + ' <small class="helper-font-small"> - ' + notification_date + '</small></div>' +
                    '        <div class="notification-linha2">' + item.content + '</div>'+
                    // '        <div class="media">'+
                    // '            <img class="media-object pull-left" data-src="js/holder.js/64x64" alt="64x64"'+
                    // '                 style="width: 64px; height: 64px;"'+
                    // '                 src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAACYUlEQVR4Xu2Y26tpURTGP9sl8UBJHpBbIfGAB+W/R8k1Sh5IkQeS+/0WTmOU3TnnYa+zrX3aO8YsZRrLmGt84/JjaWaz2Q0vvDQigFSAtIDMgBeegZAhKBQQCggFhAJCgRdWQDAoGBQMCgYFgy8MAfkzJBgUDAoGBYOCQcHgCysgGFSLwfP5jHa7jclkgre3N/j9fjidzj9qqt/v8zWxWAwOh+PDevtqf0rFrboCarUa5vM5QqEQizAej5FOp2Eymfjs5XKJarWK6/X6TwJ8tb//KgBlK5PJcFYpu7Tf7/cwm83QarW8LxaLMBgMWK1W7wJQkNPpFIlEAnq9HuVyGRaLhe3ZbPbT/pSC/MiuqgIou3TzVqsVx+MRt9sNHo8Hbrebz6zX6zidTggEAqCg7y1An5VKJb7mLlQqlcLhcHjI37cLYDQaEY1GuQV6vR5nljLe7Xb5PQXWaDQQiUQ4uxQ0tQ21Bq14PA6bzcbtQoI+4u9REVRVAGU9l8u9l+xut0M+n0cwGMRoNOKA/l7hcBgulwvD4RDNZpPNNDjppcbftwhAh1YqFWw2Gw56sVhgMBggmUxCo9Hgcrnwfa3Xa3Q6Hfh8PiYEDURqAZoVOp0Os9mMv0Ot9Ig/qphHl6oKoEMpa61Wi4caDTSv18sZ/n2R7T4D7HY7B7ndbkF9T+gsFAosBO1JnM/4U8KqkjCqBVA64KfbRQC1vwR/eoaV7k8qQCpAHonJIzF5JKY0KZ/ZLhQQCggFhAJCgWee8kqxCQWEAkIBoYBQQGlSPrNdKCAUEAoIBYQCzzzllWJ7eQr8AnnzV5+f9jRJAAAAAElFTkSuQmCC">'+
                    // '            <div class="media-body">'+
                    // '                <h4 class="media-heading">Lorem ipsum'+
                    // '                    <small class="helper-font-small">' + notification_date + '</small>'+
                    // '                </h4>'+
                    // '                <p>Raw denim you probably haven\'t heard of them jean shorts Austin.</p>'+
                    // '            </div>'+
                    // '        </div>'+
                    '    </a>'+
                    '</li>';

                    ulNotificacao.append(myvar);






                    // //@TODO: aguardar implementação do Ricardo de limpar notificações por app.
                    // if (i === data.length - 1) {
                    //     $('#notification-dropdown .dropdown-menu').append('' +
                    //         '<li>' +
                    //         '    <a href="#" class="btn btn-primary">' +
                    //         '        <i class="fa fa-list"></i>' +
                    //         '        <span>Limpar notificações</span>' +
                    //         '    </a>' +
                    //         '</li>'
                    //     );
                    // }
                }

            }
        }

    };

    Signo.notificationRemoveAll = function () {
        botaoContador.html('0');
        botaoContador.attr('Nenhuma notificação');
        $('#notification-dropdown').html('');
        ulNotificacao.html('');
    };

    Signo.connection = function (user, this_app) {

        var theuser = window.atob(user);
        var socket_url = window.signosocketurl;

        var socket = new WebSocket(socket_url);

        var id = {
            channel: 'NotificationChannel',
            user: theuser
            ,
            app: 'solar'
            ,
            group_by: 'app' // ou 'module'
            // only_app: 'solar',


        };

        var sub_cmd = {
            command: 'subscribe',
            identifier: JSON.stringify(id)
        };

        function isNull(object) {
            return object === null;
        }

        function isUndef(object) {
            return object === undefined;
        }

        function isNumber(object) {
            return typeof object === 'number';
        }

        function isTrue(object) {
            return isNull(object) || object > 0;
        }

        function onlyThisApp(link, app) {
            return link + '?q[app_name_cont]=' + app
        }

        function length(messages1, messages2) {
            if (isUndef(messages1)) {
                return messages2.slice(0, 5).length;
            }
            if (isUndef(messages2)) {
                return messages1.slice(0, 5).length;
            }
            var messageLength = messages1.slice(0, 5).length;
            return messageLength + messages2.slice(0, 5 - messageLength).length;
        }

        socket.onerror = function (error) {
            console.log('erros do WebSocket: ' + error + error[0] + error[1]);
        };

        socket.onopen = function (event) {
            socket.send(JSON.stringify(sub_cmd));
            console.log("Conectado " + socket_url);
        };

        socket.onmessage = function (event) {
            var data = JSON.parse(event.data);

            if (isUndef(data.message) || isNumber(data.message)) {
            } else if (isNull(data.message)) {
                Signo.notificationRemoveAll();
            } else {
                Signo.notificationRemoveAll();

                var messages = data.message.notifications.message;
                console.log(data);
                var grouppedArray = messages.groupBy('app');

                Signo.notification(theuser, 'solar_dev', grouppedArray);

                var myvar = '<li class="fixed" style="bottom: 0">'+
                '    <div class="btn-group">'+
                ''+
                '        <a class="btn btn-small notificacoes-ver-todas" href="' + data.message.notifications.all_message.link +'">Mostrar todas</a>'+
                ''+
                ''+
                '        <a class="btn btn-small notificacoes-marcar-todas-como-lidas" href="' + data.message.notifications.mark_all_read.link + '">Marcar todas como lidas</a>'+
                ''+
                '    </div>'+
                '</li>';
                ulNotificacao.append(myvar);


            }
        };


        socket.onclose = function (event) {
        };
    };
    window.Signo = Signo;
})();
