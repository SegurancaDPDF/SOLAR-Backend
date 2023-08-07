angular.module("SisatApp").factory('FormaAtendimentoAPI', function($resource) {
    return $resource('/api/v1/formas-atendimento/:id.json', {id:'@id'}, {
	});
});

angular.module("SisatApp").factory('QualificacaoServiceAPI', function($resource) {
    return $resource('/api/v1/qualificacoes/:id.json');
});

angular.module("SisatApp").factory('TipoColetividadeServiceAPI', function($resource) {
    return $resource('/api/v1/atendimentos/tipos-coletividade.json');
});