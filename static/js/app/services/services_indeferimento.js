angular.module("SisatApp").factory('IndeferimentoServiceAPI', function($resource) {
    return $resource('/api/v1/indeferimentos.json');
});

angular.module("SisatApp").factory('IndeferimentoPrateleiraServiceAPI', function($resource) {
    return $resource('/api/v1/indeferimentos/prateleiras.json');
});
