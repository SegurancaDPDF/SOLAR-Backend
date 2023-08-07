angular.module("SisatApp").factory('patrimonioAPI', function($http) {
    let _get_patrimonio_tipo = () => {
        return $http.get('/api/v1/pessoasassistidas/patrimonios-tipos.json');
    }
    let _get_patrimonio_assistido = ($assistido_id) => {
        return $http.get(`/api/v1/pessoasassistidas/${$assistido_id}/patrimonios.json`);
    }
    let _delete_patrimonio_assistido = (patrimonio_id) => {
        return $http.delete(`/assistido/patrimonio/${patrimonio_id}`);
    }
    return {
        get_patrimonios_tipo: _get_patrimonio_tipo,
        get_patrimonio_assistido: _get_patrimonio_assistido,
        delete_patrimonio_assistido: _delete_patrimonio_assistido
    }
});
