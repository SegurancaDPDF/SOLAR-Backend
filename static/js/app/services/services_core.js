angular.module("SisatApp").factory('SettingServiceAPI', function($resource) {
    return $resource('/api/v1/settings/:action.json', {id:'@id'}, {
        recuperar: {method: 'GET', params: {action: 'recuperar'}}
    });
});

angular.module("SisatApp").factory('PeriodicTaskAPI', function($resource) {
    return $resource('/api/v1/periodic-tasks/:id.json', {id:'@id'}, {
        update: {method: 'PATCH'}
    });
});