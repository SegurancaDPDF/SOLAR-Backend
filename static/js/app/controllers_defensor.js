app.filter('comarcas_da_diretoria', function(){
	return function(itens, diretoria) {
        var filtered = [];
		angular.forEach(itens, function(value,key){
			if(value.id==diretoria || value.coordenadoria==diretoria){
				this.push(value);
			}
		}, filtered);
		return filtered;
    }
});

function AtuacaoCtrl($scope, $http, $filter, AtuacaoAPI, DefensorAPI, DefensoriaAPI)
{

	$scope.defensor = {};
	$scope.defensores = [];
	$scope.defensorias = [];
    $scope.atuacoes = [{id: 0, nome: 'Substituição'}, {id: 1, nome: 'Acumulação'}, {id: 2, nome: 'Titular'}];
    $scope.documentos = [{id: 0, nome: 'Portaria'}, {id: 1, nome: 'Ato'}, {id: 2, nome: 'Edital'}, {id: 3, nome: 'Resolução'}];
	
	$scope.tipo = null;
	$scope.atuacoes_lst = {};
	$scope.atuacoes_por_defensoria = [];

	$scope.listar_defensorias = function()
	{
		if($scope.defensorias===null)
		{			
			// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
			DefensoriaAPI.get({limit:1000}, function(data){
				$scope.defensorias = data.results;
			});
		}
	}

	$scope.show_atuacao = function(defensor, tipo)
	{

		$scope.defensor = { ...defensor };

		$scope.errors = null;
		$scope.atuacao = $scope.atuacoes[tipo];

		var hoje = new Date();

        $scope.defensor.atuacao = {
		    tipo: tipo,
            data_inicial: hoje,
            data_final: (tipo==2 ? null : hoje),
            defensor:(tipo==0 ? null : defensor.id),
            titular:(tipo==0 ? defensor.id : null),
            agendamentos:[]
		};

		$scope.listar_defensorias();

		$http.get('../'+$scope.defensor.id+'/atuacoes/').success(function(data){
			$scope.defensor.atuacoes = data;
		});

		$('#modal-atuacao').modal();

	};

	$scope.show_detalhes = function(defensor)
	{

		$scope.defensor = { ...defensor };

		$http.get('../'+$scope.defensor.id+'/atuacoes/').success(function(data){
			$scope.defensor.atuacoes = data;
			$('#modal-detalhes').modal();
		});

	};

	$scope.show_alterar = function(atuacao)
	{
		$scope.atuacao = angular.copy(atuacao);
		$('#modal-alterar').modal();
	};

	$scope.show_excluir = function(atuacao)
	{
		$scope.atuacao = atuacao;
		$scope.data_fim = new Date();
        $http.get('/defensor/'+$scope.atuacao.defensor.id+'/defensoria/'+$scope.atuacao.defensoria.id+'/substitutos/').success(function(data) {
            $scope.atuacao.substituicoes = data;
            $http.get('/evento/atuacao/'+$scope.atuacao.id+'/listar/').success(function(data) {
                $scope.atuacao.agendas = data;
                $('#modal-excluir').modal();
            });
        });
	};

	$scope.excluir = function()
	{
		$scope.atuacao.data_fim = $scope.data_fim;
		$http.post('excluir/', $scope.atuacao).success(function(data){
			if(data.success)
			{
				$scope.recarregar($scope.ativos);
				$('#modal-excluir').modal('hide');
			}
		});
	};

	$scope.salvar = function()
	{

		$scope.salvando = true;
		$scope.errors = null;
		$scope.defensor.atuacao.agendamentos = [];

		$http.post('salvar/', $scope.defensor.atuacao).success(function(data){

			if(data.success)
			{
				$scope.defensor.atuacao.id = data.atuacao;

				if($scope.defensor.atuacao==2) {
                    $scope.defensor.titular = data.titular;
                }

				$scope.init();

				if(!data.agendamentos.length) {
                    $('#modal-atuacao').modal('hide');
                }

			}
			else
			{
				$scope.errors = data.errors;
			}

			$scope.defensor.atuacao.agendamentos = data.agendamentos;
			$scope.salvando = false;

		});
	};

	$scope.salvar_documento = function()
	{

		$scope.salvando = true;
		
		var atuacao = {id: $scope.atuacao.id, documento: $scope.atuacao.documento};
		AtuacaoAPI.update(atuacao, function(data){
			$scope.atuacao = data;
			$scope.recarregar($scope.ativos);
			$scope.salvando = false;
			$('#modal-alterar').modal('hide');
		});

	}

	$scope.remanejar_agendamentos = function()
	{
		var agendamentos = $filter('filter')($scope.defensor.atuacao.agendamentos, {sel:true}, true);
		$http.post('remanejar-agendamentos/' + $scope.defensor.atuacao.id + '/', $scope.defensor.atuacao.agendamentos).success(function(data){
			$('#modal-atuacao').modal('hide');
			$scope.salvando = false;
		});
	};

	$scope.listar_atuacoes_por_defensoria = function()
	{
		$scope.carregando = true;
		$http.get('/defensoria/listar/').success(function(data){
			$scope.atuacoes_por_defensoria = data;
			$scope.carregando = false;
		});
	};

	$scope.carregar_atuacoes = function(tipo)
	{
		
		$scope.tipo = tipo;

		if($scope.atuacoes_lst[$scope.tipo]!==undefined) {
            return;
		}
		
		$scope.carregando = true;

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		AtuacaoAPI.get({ativo:$scope.ativos, tipo: $scope.tipo, limit:1000}, function(data){
			$scope.atuacoes_lst[tipo] = data.results;
			$scope.carregando = false;
		});

	};

    $scope.recarregar = function(ativos)
    {
		$scope.init();
		$scope.ativos = ativos;
		$scope.carregar_atuacoes($scope.tipo);
    };

	$scope.init = function()
	{

        $scope.defensores = null;
		$scope.defensorias = null;
		$scope.atuacoes_lst = {};

		$http.get('/comarca/listar/').success(function(data){
			$scope.comarcas = data;
		});

        $scope.carregando = true;

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensorAPI.get({incluir_atuacoes:true, ativo:true, limit:1000}, function(data){
			$scope.defensores = data.results;
			$scope.carregando = false;
		});

	}

}

function EditalPlantaoCtrl($scope, $http, $filter)
{
	$scope.filtro = {ultima:true, total:0};
	$scope.assistidos ={};

	$scope.init = function(filtro)
	{

		for(var key in filtro) {
            $scope.filtro[key] = filtro[key];
        }
		
		$scope.filtro.data_inicial = DataConversao(filtro['data_inicial']);
        $scope.filtro.data_final = DataConversao(filtro['data_final']);

		$scope.validar();
		$scope.buscar(0);

	};

	$scope.validar = function () {
		var filtro = $scope.filtro;
		var data_inicial = (filtro.data_inicial != undefined && filtro.data_inicial.length > 0);
		var data_final = (filtro.data_final != undefined && filtro.data_final.length > 0);
		var datas = (data_inicial && data_final) || (!data_inicial && !data_final);
		$scope.valido = datas && (data_inicial || data_final);
	};

	$scope.buscar = function(pagina) {

		$scope.filtro.pagina = (pagina==undefined ? 0 : pagina);
		$scope.carregando = true;

		var filtro = {...$scope.filtro}; // copia valor para alterar formato das datas
		filtro['data_inicial'] = date_to_string_ddmmyyyy(filtro['data_inicial']);
		filtro['data_final'] = date_to_string_ddmmyyyy(filtro['data_final']);

		$http.post('/defensor/plantao/listar/', $scope.filtro).success(function (data) {

			$scope.filtro.ultima = data.ultima;
			$scope.filtro.paginas = data.paginas;
			$scope.defensor_id = data['defensor_id']

			if(data.pagina==0)
			{
				$scope.registros = data.registros;
				$scope.filtro.total = data.total;
				for(var i = 0; i < data.registros.length; i++) {
					if (data.registros[i].status == 0) {
						data.registros[i].status = 'Ativo'
					}
					if (data.registros[i].status == 1) {
						data.registros[i].status = 'Cancelado'
					}
					if (data.registros[i].status == 2) {
						data.registros[i].status = 'Exaurido'
					}
				}
			}
			else
			{
				for(var i = 0; i < data.registros.length; i++) {
                    $scope.registros.push(data.registros[i]);
                }
			}

			$scope.carregando = false;

		});
	};

	$scope.listar_inscritos = function(edital_id) {
		window.location.href = '../'+edital_id+'/inscricoes/';
	};


	$scope.inscrever = function(data)
    {
		$scope.inscrevendo = true;
        $scope.salvando = true;
        $scope.errors = [];
		dados = {
			'edital': $scope.edital_id,
			'data': data
		}
		
		$http.post('/defensor/plantao/inscrever/', dados).success(function (data) {
            if(data.success)
            {
                $('#modal-inscricao-edital-plantao').modal('hide');
                $scope.buscar(0);
            } 
            $scope.salvando = false;
            $scope.errors = data.errors;
        });
    };

	$scope.cancelar = function(data)
    {
        $scope.salvando = true;
        $scope.errors = [];
		dados = {
			'edital': $scope.edital_id,
			'data': data
		}
		
		$http.post('/defensor/plantao/cancelar/', dados).success(function (data) {
            if(data.success)
            {
                $('#modal-inscricao-edital-plantao').modal('hide');
                $scope.buscar(0);
            } 
            $scope.salvando = false;
            $scope.errors = data.errors;
        });
    };

	$scope.mostra_botao_inscrever= function(data)
    {
		if ($scope.acao == 'inscrever') {
			return true;
		}
		if ($scope.acao == 'cancelar') {
			return false;
		}
	};

    $scope.show_modal_data = function(id_edital, id_defensor, acao)
	{
		$http.post('/defensor/plantao/'+id_edital+'/vagas/').success(function (data) {
			$scope.vagas = data['vagas'];
		});
		if (acao == 0) { // Inscrever
			$scope.edital_id = id_edital;
			$scope.defensor_id = id_defensor;
			document.getElementById("myModalLabel").innerHTML = "Inscrever-se";
			document.getElementById("botao_inscrever").style.display = "inline"
			$scope.acao = 'inscrever';
		}
		if (acao == 1) { // Cancelar inscrição
			$scope.edital_id = id_edital;
			$scope.defensor_id = id_defensor;
			document.getElementById("myModalLabel").innerHTML = "Cancelar inscrição";
			document.getElementById("botao_inscrever").style.display = "none"
			$scope.acao = 'cancelar';
		}
		$('#modal-inscricao-edital-plantao').modal();
	};
	
}