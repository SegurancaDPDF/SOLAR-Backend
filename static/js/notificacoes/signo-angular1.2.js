'use strict';
window.signosocketurl = 'wss://signo.defensoria.to.def.br/cable';
window.signoCurrentAppName = 'SOLAR';
window.signoNotificationRootElementSelector = "#notification";
window.signoShowAllElementSelector = "#notification > ul > li.col-md-6.media.mostra-todas > a > span";

window.notificacoesMainDivSelector = '#notificacoes-div';
window.notificacaoBotaoContadorSelector = 'a.notificacoes-contador';
window.notificacaoUlSelector = 'ul.notificacoes-ul';
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


function NotificacoesSignoCtrl($scope, $http, $timeout) {
    var theuser;
    var socket_url;
    var socket = {};
    var id;
    var sub_cmd;
    $scope.socket = {};
    $scope.solar_messages = {};
    $scope.other_messages = {};
    $scope.solar_messages_count = 0;
    $scope.other_messages_count = 0;
    $scope.all_messages_url = "";
    $scope.signodata = {};
    $scope.init = function (user, app) {
        window.signo_angular_scope = $scope;

        console.log('app: ' + app);
        theuser = window.atob(user);
        console.log('usuario: ' + theuser);

        socket_url = window.signosocketurl;

        startsigno();

    };
    $scope.notificacoes = {
        'mensagens': {}
    };
    // setInterval(function () {
    //     // console.log($scope.testValue++);
    //     console.log('asdasd');
    //     $scope.$apply()
    // }, 1000);

    function startsigno() {
        $scope.socket = new WebSocket(socket_url);

        id = {
            channel: 'NotificationChannel',
            user: '' + theuser + ''
            ,
            app: 'solar'
            ,
            group_by: 'app' // ou 'module'
            // only_app: 'solar',
        };

        sub_cmd = {
            command: 'subscribe',
            identifier: JSON.stringify(id)
        };

        $scope.socket.onerror = function (error) {
            console.log('erros do WebSocket: ' + error + error[0] + error[1]);
        };

        $scope.socket.onopen = function (event) {
            $scope.socket.send(JSON.stringify(sub_cmd));
            console.log("onopen. Conectado " + socket_url);
        };
        $scope.socket.onclose = function (event) {
        };

        $scope.socket.onmessage = function (event) {
            console.log('onmessage');
            var data = JSON.parse(event.data);

            if (isUndef(data.message) || isNumber(data.message)) {
            } else if (isNull(data.message)) {
                // Signo.notificationRemoveAll();
                console.log('passou aqui');
            } else {
                // Signo.notificationRemoveAll();
                var other_messages = Object.assign({}, data.message.notifications.message[0]);
                delete other_messages['solar_dev'];
                delete other_messages['solar'];
                var counter_other_messages = 0;
                for (var key in other_messages) {
                    if (other_messages.hasOwnProperty(key)) {
                        counter_other_messages += other_messages[key].length;
                    }
                }
                window.$timeout=$timeout;
                var scope = angular.element($("#signo-notifications")).scope();

                // scope.$apply(function () {
                scope.signodata = data;
                scope.all_messages_url = data.message.notifications.all_message.link;
                scope.mark_all_as_read_url = data.message.notifications.mark_all_read.link;
                scope.solar_messages = {'SOLAR': Object.assign([], data.message.notifications.message[0].solar_dev)};
                scope.solar_messages_count = $scope.solar_messages['SOLAR'].length;
                scope.other_messages = other_messages;
                scope.other_messages_count = counter_other_messages;
                window.solar_messages = $scope.solar_messages;
                scope.notificacoes.mensagens = {
                    'all_messages_url': scope.all_messages_url,
                    'mark_all_as_read_url': scope.mark_all_as_read_url,
                    'solar_messages': scope.solar_messages,
                    'solar_messages_count': scope.solar_messages_count,
                    'other_messages': scope.other_messages,
                    'other_messages_count': scope.other_messages_count
                };
                console.log('onmessage $apply');

                // });
            }
        };

    }

}
