window.signosocketurl = 'wss://signo.defensoria.to.def.br/cable';
(function () {
    'use strict';

    function isNull(object) {
        return object === null;
    }

    function isUndef(object) {
        return object === undefined;
    }

    function isNumber(object) {
        return typeof object === 'number';
    }

    app.factory('SignoWebsocket', function () {
        var service = {};

        service.connect = function (socketurl, initialmessage, onmessagecallback) {
            service.onmessagecallback = onmessagecallback;
            console.log('service.connect to: ' + socketurl);
            if (service.ws) {
                return;
            }

            var ws = new WebSocket(socketurl);

            ws.onopen = function () {
                console.log('service.ws.onopen');
                service.callback("Succeeded to open a connection");
            };

            ws.onerror = function () {
                console.log('service.ws.onerror');
                service.callback("Failed to open a connection");
            };

            ws.onmessage = function (event) {
                console.log('service.ws.onmessage');
                // service.callback(message.data);
                service.onmessagecallback(event)
            };

            service.ws = ws;
            setTimeout(function(){ service.send(initialmessage);}, 1000);

        };

        service.send = function (message) {
            service.ws.send(message);
        };

        service.subscribe = function (callback) {
            service.callback = callback;
        };

        return service;
    });


    function NotificacoesSignoCtrl($scope, SignoWebsocket) {
        var theuser;
        var socket_url;
        var socket = {};
        var id;
        var sub_cmd;
        var onmessage = function (event) {
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
                // $scope.$apply(function () {
                $scope.signodata = data;
                $scope.all_messages_url = data.message.notifications.all_message.link;
                $scope.mark_all_as_read_url = data.message.notifications.mark_all_read.link;
                $scope.solar_messages = {'SOLAR': Object.assign([], data.message.notifications.message[0].solar_dev)};
                $scope.solar_messages_count = $scope.solar_messages['SOLAR'].length;
                $scope.other_messages = other_messages;
                $scope.other_messages_count = counter_other_messages;
                window.solar_messages = $scope.solar_messages;
                console.log('SignoWebsocket.onmessage');

                // });
            }
            console.log('$scope.$apply()');
            $scope.$apply();
        };
        $scope.solar_messages = {};
        $scope.other_messages = {};
        $scope.solar_messages_count = 0;
        $scope.other_messages_count = 0;
        $scope.all_messages_url = "";
        $scope.signodata = {};
        $scope.messages = [];

        SignoWebsocket.subscribe(function (message) {
            // $scope.messages.push(message);
            $scope.$apply();
        });

        $scope.connect = function () {
            console.log('$scope.connect');
            SignoWebsocket.connect(socket_url, JSON.stringify(sub_cmd), onmessage);


        };

        $scope.send = function () {
            SignoWebsocket.send($scope.text);
            $scope.text = "";
        };
        $scope.init = function (user, app) {
            window.signo_angular_scope = $scope;

            console.log('app: ' + app);
            theuser = window.atob(user);
            console.log('usuario: ' + theuser);

            socket_url = window.signosocketurl;

            console.log('init');
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

            $scope.connect();


        };
        window.SignoWebsocket = SignoWebsocket;
    }

    window.NotificacoesSignoCtrl = NotificacoesSignoCtrl;
})();

