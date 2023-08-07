function ItineranteCtrl($scope, $http, $filter, DefensoriaAPI)
{

    $scope.itinerantes = [];

    $scope.estado = null;
    $scope.municipios = [];

    $http.get('/servidor/listar/json/').success(function(data){
        $scope.defensores = data;
    });

    $scope.init = function(estado, diretoria)
    {
        $scope.estado = estado;
        $scope.diretoria = diretoria;
        $scope.listar({encerrado:false,autorizado:false,ativo:true});

        DefensoriaAPI.get({eh_itinerante:'true', limit:1000}, function(data){
			$scope.defensorias = data.results;
			
		});
        
    };

    $scope.novo = function()
    {
        $scope.itinerante = {participantes:[]};
        $scope.listar_municipios();
        
    };

    $scope.editar = function(e)
    {
        $scope.itinerante = e;
        $scope.listar_municipios();
    };

    $scope.listar = function(filtro)
    {
        if(filtro!=undefined) {
            $scope.filtro = filtro;
        }

        $scope.itinerantes = null;

        $http.post('listar/', $scope.filtro).success(function(data){
            $scope.itinerantes = data;
            $scope.vincular_municipios();
            $scope.verificar_conflitos();
        });
    };

    $scope.listar_municipios = function()
    {
        if(!$scope.municipios.length && $scope.estado)
        {
            $http.get('/estado/'+$scope.estado+'/municipios/').success(function(data){
                $scope.municipios = data;
                $scope.vincular_municipios();
            });
        }
    };

    $scope.popover = function(obj)
    {

        var content = '<ul>';
        for(var i = 0; i < obj.conflitos.length; i++) {
            content += '<li>' + obj.conflitos[i].titulo + '</li>';
        }
        content += '</ul>';

        return {'content': content};
    };

    $scope.verificar_conflitos = function()
    {

        if($scope.itinerantes==null) {
            return;
        }

        for(var i=0; i<$scope.itinerantes.length; i++) {
            $scope.itinerantes[i].conflitos = [];
        }

        for(var i=0; i<$scope.itinerantes.length; i++)
        {
            for(var j=i+1; j<$scope.itinerantes.length; j++)
            {
                var iniA = new Date($scope.itinerantes[i].data_inicial);
                var iniB = new Date($scope.itinerantes[j].data_inicial);
                var fimA = new Date($scope.itinerantes[i].data_final);
                var fimB = new Date($scope.itinerantes[j].data_final);
                if(!(iniA > fimB || fimA < iniB) && $scope.itinerantes[i].ativo && $scope.itinerantes[j].ativo)
                {
                    $scope.itinerantes[i].conflitos.push($scope.itinerantes[j]);
                    $scope.itinerantes[j].conflitos.push($scope.itinerantes[i]);
                }
            }
        }

    };

    $scope.vincular_municipios = function()
    {

        if($scope.itinerantes==null) {
            return;
        }

        for(var i = 0; i < $scope.itinerantes.length; i++)
        {
            for(var j = 0; j < $scope.municipios.length; j++)
            {
                if($scope.itinerantes[i].municipio.id == $scope.municipios[j].id)
                {
                    $scope.itinerantes[i].municipio = $scope.municipios[j];
                    break;
                }
            }
        }

    };

	$scope.salvar = function(e)
	{
        e.conflitos = null;
        $http.post('salvar/', e).success(function(data){
            if(data.success)
            {
                $scope.listar();
                $('#modal-cadastrar-itinerante').modal('hide');
                show_stack('Evento registrado com sucesso!', false, 'success');
            }
            else
            {
                var msg = '';
                for(var e = 0; e < data.errors.length; e++) {
                    msg += '<li>' + data.errors[e] + '</li>';
                }
                show_stack('<b>Erro ao registrar evento!</b><ul>' + msg + '</ul>', false, 'error');
            }
        });
	};

    $scope.excluir = function(obj)
    {
        if(obj==undefined)
        {
            $scope.selecionado.conflitos = null;
            $http.post('excluir/', $scope.selecionado).success(function(data){
                if(data.success)
                {
                    $scope.listar();
                    $('#modal-excluir-itinerante').modal('hide');
                    show_stack_success('Registro excluído com sucesso!');
                }
                else {
                    show_stack_error('Ocorreu um erro ao excluir o registro!');
                }
            });
        }
        else {
            $scope.selecionado = obj;
        }
    };

    $scope.autorizar = function(obj)
    {
        if(obj==undefined)
        {
            $scope.selecionado.conflitos = null;
            $http.post('autorizar/', $scope.selecionado).success(function(data){
                if(data.success)
                {
                    $scope.listar();
                    $('#modal-autorizar-itinerante').modal('hide');
                    show_stack_success('Registro autorizado com sucesso!');
                }
                else {
                    show_stack_error('Ocorreu um erro ao autorizar o registro!');
                }
            });
        }
        else {
            $scope.selecionado = obj;
        }
    };

    $scope.visualizar = function(obj)
    {
        $scope.selecionado = obj;
        $scope.relatorio = {};
    };

    $scope.adicionar_participante = function(participante)
    {
        if(participante) {
            $scope.itinerante.participantes.push(participante);
            $scope.itinerante.participante = null;
        }
    };

    $scope.remover_participante = function(participante)
    {
        $scope.itinerante.participantes.remove(participante);
    };

}

function DistribuicaoCtrl($scope, $http)
{

	$scope.buscar = function(filtro)
	{

		if(filtro!=undefined) {
            $scope.filtro = filtro;
        }

		$http.post('', $scope.filtro).success(function(data){
			$scope.atuacoes = data.atuacoes;
			$scope.defensores = data.defensores;
			$scope.atendimentos = data.atendimentos;
		});

	};

	$scope.salvar = function()
	{
		if($scope.atendimentos){
			$http.post('salvar/',$scope.atendimentos).success(function(data){
                show_stack('Atendimentos atualizados com sucesso!', false, 'success');
                for(var a in $scope.atendimentos) {
                    delete $scope.atendimentos[a].modificado;
                }
			});
		}
	};

    $scope.set_atendimento = function(atendimento) {
        $scope.atendimento = atendimento;
    }


}
