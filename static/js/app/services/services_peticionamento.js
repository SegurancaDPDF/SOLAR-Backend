angular.module("SisatApp").factory('ManifestacaoDocumentoServiceAPI', function($resource) {
    return $resource('/api/v1/manifestacao_processual/:numero/documentos/:id.json');
});

angular.module("SisatApp").factory('ProcapiAvisoServiceAPI', function($resource) {
    return $resource('/api/v1/procapi/avisos.json');
});
