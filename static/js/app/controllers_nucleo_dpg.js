function NucleoDPGCtrl($scope, $http, $filter)
{

    $scope.medida_pretendida = '';
    $scope.justificativa = '';

    // limpa dados armazenados
    $scope.clear_storage_data = function()
    {
        localStorage.removeItem('medida_pretendida');
        localStorage.removeItem('justificativa');
    }

    // recupera dados armazenados
    $scope.load_storage_data = function()
    {
        $scope.medida_pretendida = localStorage.getItem('medida_pretendida');
        $scope.justificativa = localStorage.getItem('justificativa');
    }

    // salva dados
    $scope.save_storage_data = function(key)
    {
        localStorage.setItem(key, $scope[key]);
    }

	$scope.get_pessoa = function(pessoa_id)
	{

        if($scope.assistidos===undefined)
        {
            $scope.assistidos = {};
        }

		$scope.assistido = null;

		if($scope.assistidos[pessoa_id]) {
            $scope.assistido = $scope.assistidos[pessoa_id];
        }
		else
		{
			$scope.assistidos[pessoa_id] = {};
			$http.get('/assistido/'+pessoa_id+'/json/get/').success(function(data){
				$scope.assistido = data;
				$scope.assistidos[pessoa_id] = data;
			});
		}

	};

}

function IndeferimentoIndexCtrl($scope, $http, IndeferimentoServiceAPI, IndeferimentoPrateleiraServiceAPI)
{

    $scope.setor = null;
    $scope.nucleo = null;
    $scope.prateleira = null;
    $scope.prateleiras = null;

    $scope.init = function(setor_id, nucleo_id)
    {

        $scope.setor = setor_id;
        $scope.nucleo = nucleo_id;

        IndeferimentoPrateleiraServiceAPI.get({setor: $scope.setor}, function(data) {
            $scope.prateleiras = data.results;
            $scope.carregar_prateleira(data.results[0]);
        });

    };

    $scope.carregar_prateleira = function(prateleira)
    {

        $scope.prateleira = prateleira;

        if(prateleira && $scope.prateleira.classes==null)
        {
            IndeferimentoPrateleiraServiceAPI.get({setor: $scope.setor, prateleira: prateleira.prateleira}, function(data) {
                $scope.prateleira.classes = data.results;
            });
        }

    }

    $scope.carregar_prateleira_classe = function(classe)
    {

        $scope.classe = classe;

        if($scope.classe.indeferimentos==null)
        {
            IndeferimentoServiceAPI.get({setor: $scope.setor, prateleira: classe.prateleira, classe: classe.classe, limit: classe.total}, function(data) {
                $scope.classe.indeferimentos = data.results;
            });
        }

    };

    $scope.ver_solicitacao_url = function(obj)
    {
        if (obj.processo.setor_encaminhado)
            return Urls['indeferimento:ver_solicitacao'](obj.processo.uuid, $scope.nucleo, obj.processo.setor_encaminhado.id);

        return Urls['indeferimento:ver_solicitacao'](obj.processo.uuid, $scope.nucleo, obj.processo.setor_atual.id);
    }

}
