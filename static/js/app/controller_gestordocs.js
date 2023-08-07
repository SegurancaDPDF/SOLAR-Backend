function GestorDocs($scope, $http)
{
    $scope.hoje =new Date();
    $scope.titulo_documento = '';
    $scope.numero_documento = '';
    $scope.numero_atendimento = '';
    $scope.data_inicial = '';
    $scope.data_final = '';
    $scope.status_documento = 0;
	$scope.lst_status_documento = null;
	$scope.documentos = [];
	$scope.qtd_documentos = 0;
	$scope.carregando = false;
    $scope.search_url = document.getElementById('search_url').value;
    $scope.documento = null;

	$scope.init = function()
	{

		$http.post('').success(function (data) {
            $scope.lst_status_documento = data;
		});

	}
    $scope.clean = function(){
        $scope.titulo_documento ='';
        $scope.numero_documento ='';
        $scope.numero_atendimento ='';
        $scope.data_inicial ='';
        $scope.data_final ='';
        $scope.status_documento =0;
    };
	$scope.buscar = function() {

        $scope.documentos = [];
        $scope.documento = null;
		$scope.carregando = true;

        var conteudo = JSON.stringify({
            titulo_documento : $scope.titulo_documento ? $scope.titulo_documento : '',
            numero_documento : $scope.numero_documento ? $scope.numero_documento : '',
            numero_atendimento : $scope.numero_atendimento ? $scope.numero_atendimento : '',
            data_inicial : $scope.data_inicial ? $scope.data_inicial : '',
            data_final : $scope.data_final ? $scope.data_final : '',
            status_documento : $scope.status_documento ? $scope.status_documento : ''
        });

	    $http.post('/gestordocs/buscar/', conteudo).success(function (data) {
            $scope.qtd_documentos = data.documentos.length;
            if($scope.qtd_documentos > 0) {
                for(var i = 0; i < $scope.qtd_documentos; i ++) {
                    $scope.documentos.push(data.documentos[i]);
                }
                $('#tabela').attr('style', 'height:680px; overflow-y: scroll;');
            } else {
                $('#tabela').attr('style', '');
                $scope.clean();
                show_stack_error("A busca com os seguintes critérios não retornou dados");
            }
            $scope.carregando = false;
	    });

	}

	$scope.buscar_documento = function(pk_uuid) {
        if(pk_uuid !== undefined) {

            var conteudo = JSON.stringify({
                pk_uuid : pk_uuid ? pk_uuid[0][0] : '',
            });

            $http.post('/gestordocs/buscar_documento/', conteudo).success(function (data) {
                $scope.documento = data['documento'];
                data_url = '/docs/d/' + $scope.documento.pk_uuid + '/validar-detail/?no_nav=1&status=1'
                $('#pre-visualizacao').attr('data', data_url);

                console.log($scope.documento);
            });

        }
	}

	$scope.init();
}
