function BuscarQualificacaoModel($scope, $http, AreaAPI)
{

	$scope.areas = [];
	$scope.item_qualificacao = {};
	$scope.filtro = {query:'', area:''};
	$scope.last_filtro = '';

	// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
	AreaAPI.get({limit:1000}, function(data){
		$scope.areas = data.results;
	});

	$scope.buscar_key = function(e)
    {
        // Busca automatico se enter (13)
        if(e.which==13)
        {
            $scope.buscar();
            // Cancela evento padrao do enter (limpar form)
            e.preventDefault();
        }
    };

	$scope.buscar_area = function(filtro)
	{
		$scope.buscar(filtro, false);
	}

	$scope.buscar = function(filtro, usar_cache = true)
	{

		if(filtro!=undefined) {
            $scope.filtro.query = filtro;
        }

		if(!usar_cache || ($scope.filtro.query.trim().length >= 3 && $scope.filtro.query.trim() != $scope.last_filtro)){

			$scope.carregando = true;
			$scope.last_filtro = $scope.filtro.query.trim();
			$scope.itens_qualificacao = null;

			$http.post('buscar/', $scope.filtro).success(function(data){
				$scope.itens_qualificacao = data;
				$scope.carregando = false;
			});
		}

	};

	$scope.qualificar = function()
	{
		$('#modal-vincular-processo').modal();
	};

	$scope.novo = function()
	{
		$('#modal-nova-qualificacao').modal();
	};

	$scope.visualizar = function(item_qualificacao)
	{
		$scope.item_qualificacao = item_qualificacao;
	}

}
