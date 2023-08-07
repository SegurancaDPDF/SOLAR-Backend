function NucleoDiligenciaAtividadeCtrl($scope, $http, $filter)
{

	$scope.atividade = {multiplicador: 1};
    $scope.documento = {};
    $scope.assistido = null;

    $scope.$watch('documento.arquivo', function () {

        if ($scope.documento && $scope.documento.arquivo) {
            var ext = $scope.documento.arquivo.name.split('.').pop();
            switch(ext)
            {
                case 'doc':
                case 'docx':
                    $("#ArquivoAnexarDocumentoForm").val('');
                    $scope.documento.arquivo = null;
                    $scope.documento_anexo_resultado = true;

                    break;
                default:
                    $scope.documento_anexo_resultado=null;
            }
        }
    });

    $scope.$watch('documento.documento_online', function () {

        if ($scope.documento && $scope.documento.documento_online) {
			$scope.documento.salvando=true;
            $('#AnexarDocumentoForm').submit();
        }
    });

	$scope.$watch('documento.link', function () {
		if ($scope.documento && $scope.documento.link) {
			$('#AnexarDocumentoForm').attr('action', $scope.documento.link);
		}
	});

	$scope.$watch('data_atendimento', function() {
		$scope.set_data_atendimento();
	});

	$scope.$watch('hora_atendimento', function() {
		$scope.set_data_atendimento();
	});

	$scope.set_data_atendimento = function () {
		$scope.atividade.data_atendimento = $filter('date')($filter('utc')($scope.data_atendimento), "dd/MM/yyyy") + ' ' + $scope.hora_atendimento;
	};

	$scope.set_atividade = function(obj){
		$scope.atividade = obj;
	};

	$scope.set_ultima_atividade = function(qualificacao_titulo, qualificacao_id, historico) {
	    $scope.atividade.qualificacao = {id:qualificacao_id, titulo:qualificacao_titulo};
	    $scope.atividade.historico = historico;
    };

    $scope.set_nova_atividade = function(reabrir) {
	    $scope.atividade.qualificacao = {id:null, titulo:""};
		$scope.atividade.historico = "";
		$scope.reabrir_atividade = reabrir;
    };

	$scope.init = function(nucleo)
	{

		var params = {nucleo: nucleo, tipo: 20};
		$http.post('/atendimento/qualificacao/listar/', params).success(function(data){
			$scope.qualificacoes = data.qualificacoes;
        });

        $scope.atividade = {multiplicador: 1, atendimentos: [], documentos: []};

	};

	$scope.get_pessoa = function(pessoa_id)
	{
		if($scope.assistido==null){
			$http.get('/assistido/'+pessoa_id+'/json/get/').success(function(data){
				$scope.assistido = data;
				$scope.assistidos[pessoa_id] = data;
			});
		}
	}

}
