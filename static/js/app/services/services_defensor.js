app.factory('AtuacaoAPI', function($resource) {
    return $resource('/api/v1/atuacoes/:id.json', {id:'@id'}, {
		update: {method: 'PATCH'}
	});
});

angular.module("SisatApp").factory('DefensorAPI', function($resource) {
    return $resource('/api/v1/defensores/:id.json', {id:'@id'}, {
	});
});

angular.module("SisatApp").factory('TarefaServiceAPI', function($resource) {
    return $resource('/api/v1/atendimentos/:numero/tarefas/:id.json');
});

angular.module("SisatApp").service('PropacTarefaService', function($http){
    const api_verion_prefix = "/api/v1";
    const base_url = api_verion_prefix + '/propac-tarefas';

    this.listarTarefasMovimento = function(movimentoId){
        const url = base_url + '/?movimento=' + movimentoId;
        return $http.get(url);
    };

    this.detalharTarefaMovimento = function(tarefaId) {
        const url = base_url + "/" + tarefaId;
        return $http.get(url);
    };

    this.salvarTarefaMovimento = function(tarefa) {
        const url = base_url + "/"
        return $http.post(url, tarefa);
    };

    this.finalizarTarefa = function(tarefa) {
        const url = base_url + "/" + tarefa + "/finalizar_tarefa/";
        return $http.post(url, null);
    };

    this.excluirTarefa = function(tarefa) {
        const url = base_url + "/" + tarefa + "/";
        return $http.delete(url, null);
    };

    this.listarDefensorias = function(tarefa) {
        const url = base_url + "/defensorias";
        console.log("lista defensorias: ", url);
        return $http.get(url);
    };

    this.salvarDocumentosTarefasPropac = function(listaDocumentos) {
        const url = api_verion_prefix + "/propac-tarefa-documento/";
        return $http.post(url, listaDocumentos);
    };

    this.carregarSetorResponsavel = function(setorResponsavel) {
        const url = '/defensoria/' + setorResponsavel + '/get/';
        return $http.get(url);
    };
});

angular.module("SisatApp").service('DocumentoAtendimentoService', function($http){
    const api_verion_prefix = "/api/v1";
    const base_url = api_verion_prefix + '/pastas-documentos';

    this.listarPastasAtendimento = function(numeroAtendimento) {
        const url = base_url + `/?atendimento=${numeroAtendimento}`;
        return $http.get(url)
    };
});
