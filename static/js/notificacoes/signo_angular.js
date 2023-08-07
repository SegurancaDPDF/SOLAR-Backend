window.signosocketurl = 'wss://signo.defensoria.to.def.br/cable';

(function () {
    'use strict';

    app.factory('SignoWebsocket', function ($websocket) {
        // Open a WebSocket connection
        var ws = $websocket(window.signosocketurl);

        var collection = [];

        ws.onMessage(function (event) {
            console.log('message: ', event);
            var res;
            try {
                res = JSON.parse(event.data);
            } catch (e) {
                res = {'username': 'anonymous', 'message': event.data};
            }

            collection.push({
                username: res.username,
                content: res,
                timeStamp: event.timeStamp
            });
        });
        ws.onError(function (event) {
            console.log('connection Error', event);
        });

        ws.onClose(function (event) {
            console.log('connection closed', event);
        });
        ws.onOpen(function () {
            console.log('connection open');
            // ws.send('Hello World');
            // ws.send('again');
            // ws.send('and again');
        });
        return {
            ws: ws,
            collection: collection,
            status: function () {
                return ws.readyState;
            },
            send: function (message) {
                if (angular.isString(message)) {
                    ws.send(message);
                }
                else if (angular.isObject(message)) {
                    ws.send(JSON.stringify(message));
                }
            }

        };

    });

    function NotificacoesSignoCtrl($scope, SignoWebsocket) {
        var theuser;
        var socket_url;
        var socket = {};
        var id;
        var sub_cmd;
        var startmessage;
        $scope.SignoWebsocket = SignoWebsocket;
        $scope.collection = {};
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
            startmessage = JSON.stringify(sub_cmd);
            setTimeout(function () {
                console.log('startmessage');
                SignoWebsocket.send(startmessage);

                setInterval(function () {
                    // console.log('setInterval');
                    $scope.collection = SignoWebsocket.collection;
                    window.collection = $scope.collection;
                }, 1000);

            }, 500);

        };
        $scope.$watch('collection', function () {
            console.log('collection mudou');
            console.log($scope.collection);

        });
        window.SignoWebsocket = SignoWebsocket;
    }

    window.NotificacoesSignoCtrl = NotificacoesSignoCtrl;
})();

