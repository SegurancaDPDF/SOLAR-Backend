angular.module("SisatApp").factory('CategoriaDeAgendaAPI', function($resource) {
    return $resource('/api/v1/categorias-de-agendas.json');
});
