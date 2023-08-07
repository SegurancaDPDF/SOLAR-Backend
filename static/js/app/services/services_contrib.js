angular.module("SisatApp").factory('AreaAPI', function($resource) {
    return $resource('/api/v1/areas/:id.json', {id:'@id'}, {
	});
});

angular.module("SisatApp").factory('CartorioAPI', function($resource) {
    return $resource('/api/v1/cartorios/:id.json', {id:'@id'}, {
	});
});

angular.module("SisatApp").factory('ComarcaAPI', function($resource) {
    return $resource('/api/v1/comarcas/:id.json', {id:'@id'}, {
	});
});

angular.module("SisatApp").factory('ContribDocumentoServiceAPI', function($resource) {
    return $resource('/api/v1/tipos-documento/:id.json');
});

angular.module("SisatApp").factory('DefensoriaAPI', function($resource) {
    return $resource('/api/v1/defensorias/:id.json', {id:'@id'}, {
	});
});

angular.module("SisatApp").factory('DefensoriaAPIv2', function($resource) {
    return $resource('/api/v2/defensorias/:id', {id:'@id'}, {
	});
});

angular.module("SisatApp").factory('DefensoriaEtiquetaAPI', function($resource) {
    return $resource('/api/v1/defensorias-etiquetas/:id.json', {id:'@id'}, {
        update: {method: 'PATCH'}
	});
});

angular.module("SisatApp").factory('EstadoAPI', function($resource) {
    return $resource('/api/v1/estados/:id.json', {id:'@id'}, {
	});
});

angular.module("SisatApp").factory('EtiquetaAPI', function($resource) {
    return $resource('/api/v1/etiquetas/:id.json', {id:'@id'}, {
        update: {method: 'PATCH'}
	});
});

angular.module("SisatApp").factory('MunicipioAPI', function($resource) {
    return $resource('/api/v1/municipios/:id.json', {id:'@id'}, {
	});
});

angular.module("SisatApp").factory('SituacaoServiceAPI', function($resource) {
    return $resource('/api/v1/situacoes/:id.json');
    });

angular.module("SisatApp").factory('TipoRendaServiceAPI', function($resource) {
    return $resource('/api/v1/tipos-renda/:id.json');
    });