function RelatorioIndexCtrl($scope, $http, CategoriaDeAgendaAPI, DefensorAPI, DefensoriaAPI) {

	$scope.meses = [
		{id:1, nome:'Janeiro'},
		{id:2, nome:'Fevereiro'},
		{id:3, nome:'Março'},
		{id:4, nome:'Abril'},
		{id:5, nome:'Maio'},
		{id:6, nome:'Junho'},
		{id:7, nome:'Julho'},
		{id:8, nome:'Agosto'},
		{id:9, nome:'Setembro'},
		{id:10, nome:'Outubro'},
		{id:11, nome:'Novembro'},
		{id:12, nome:'Dezembro'}];

	$scope.set_report = function(report)
	{

		$scope.relatorio.titulo = report.titulo;
		$scope.relatorio.status = null;
		$scope.relatorio.resource = report.resource;
		$scope.relatorio.name = report.name;
		$scope.relatorio.agrupadores = report.agrupadores;
		$scope.relatorio.format = report.format;
		$scope.relatorio.fields = report.fields;
        $scope.relatorio.extra = report.extra;
        $scope.relatorio.params['aliases'] = report.aliases;

		if(report.extra)
		{
			for(var i = 0; i < report.extra.length; i++)
			{
				$scope.listar_extra(report.extra[i])
            }
        }

        // parâmetros reservados e que seus valores não podem ser removidos
        var reservados = ['ano', 'mes', 'data_inicial', 'data_final', 'aliases'];

        // remove valores previamente preenchidos para parâmetros não usados no relatório
        for(var key in $scope.relatorio.params){
            if(!$scope.relatorio.fields[key] && !reservados.includes(key))
            {
                delete $scope.relatorio.params[key];
            }
        }

        // se parâmetro 'comarca_id' não possui valor, força remoção do valor de parâmetro dependente 'defensoria_id'
        if($scope.relatorio.fields['comarca_id'] && !$scope.relatorio.params['comarca_id'])
        {
            delete $scope.relatorio.params['defensoria_id'];
        }

        // remove select2 antes de reaplicar
        $("#modal-imprimir select").select2('destroy');

        // aplica select2 após 1 segundo (necessário devido ao processamento do AngularJS)
        window.setTimeout(function()
        {
            $("#modal-imprimir select").select2({
                width: '100%'
            });
        }
        , 1000);

    };

	$scope.listar_extra = function(extra)
	{
		if(!extra.choices && extra.choices_url)
		{
			$http.get(extra.choices_url).success(function(data){
				if('results' in data){
					data = data['results'];
				}
				for(var i=0; i<data.length; i++){
					data[i].nome = $scope.get_nome_by_keys(data[i]);
				}
				extra.choices = data;
			});
		}
	};

	$scope.get_nome_by_keys = function(obj)
	{
		let keys = ['nome', 'titulo'];
		for(var i=0; i<keys.length; i++)
		{
			if(keys[i] in obj){
				return obj[keys[i]];
			}
		}
	}

	$scope.gerar_data = function()
	{

        var hoje = new Date();

        if($scope.relatorio.params.ano==undefined){
            $scope.relatorio.params.ano = hoje.getFullYear();
        }

        if($scope.relatorio.params.mes==undefined)
        {
            $scope.relatorio.params.mes = hoje.getMonth() + 1;
        }

		var ano = $scope.relatorio.params.ano;
		var mes = $scope.relatorio.params.mes;

			if(mes==0)
			{
                $scope.relatorio.params.data_inicial = new Date(Date.UTC(ano, 0, 1));
                $scope.relatorio.params.data_final = new Date(Date.UTC(ano, 11, 31, 23, 59, 59));
			}
			else
			{
				$scope.relatorio.params.data_inicial = new Date(Date.UTC(ano, mes-1, 1));
				$scope.relatorio.params.data_final = new Date(Date.UTC(ano, mes, 0, 23, 59, 59));
			}

        $scope.fields.data_final = $scope.relatorio.params.data_final;

	};

    $scope.gerar = function()
    {
		if($scope.relatorio.fields.ano || $scope.relatorio.fields.mes) {
            $scope.gerar_data();
        }

		if($scope.relatorio.extra)
		{
			for(var i = 0; i < $scope.relatorio.extra.length; i++) {
			    if ($scope.relatorio.extra[i].type === 'text' && $scope.relatorio.extra[i].value != null) {
			        $scope.relatorio.params[$scope.relatorio.extra[i].name] = $scope.relatorio.extra[i].value.replace(',,', '').replace(/,+$/, '').trim();
                }
                else {
                    $scope.relatorio.params[$scope.relatorio.extra[i].name] = $scope.relatorio.extra[i].value;
                }
            }
		}

        Chronus.generate($scope,
            $scope.relatorio.user,
            $scope.relatorio.name,
            $scope.relatorio.resource,
            $scope.relatorio.params,
            $scope.relatorio.format
        );

    };

	$scope.alterar_diretoria = function(obj)
	{
		var report = $scope.relatorio;
		report.status = null;

		delete report.params['comarca_id'];
		if(report.params['diretoria_id'] == null) {
            delete report.params['diretoria_id'];
        }

	};

	$scope.listar_diretorias = function()
	{

		$scope.relatorio.status=null;
		$scope.diretorias = null;

		$http.get('/diretoria/listar/').success(function(data){
			$scope.diretorias = data;
		});

	};

	$scope.listar_comarcas = function()
	{

		$scope.relatorio.status=null;
		$scope.comarcas = null;

		$http.get('/comarca/listar/').success(function(data){
			data.forEach(function(e){
				e.coordenadoria = e.coordenadoria || e.id;
			});
			$scope.comarcas = data;
		});

	};

	$scope.listar_indicadores_meritocracia = function()
	{
		$scope.indicadores = null;
		$http.get('/indicador_meritocracia/listar/').success(function(data){
			$scope.indicadores = data;
		});
	};

	$scope.listar_defensores = function()
	{

		$scope.relatorio.status=null;
		$scope.defensores = null;

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensorAPI.get({incluir_atuacoes:false, ativo:true, limit:1000}, function(data){
			$scope.defensores = data.results;
		});

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensoriaAPI.get({limit:1000}, function(data){
			$scope.defensorias = data.results;
		});

	};

	$scope.listar_servidores = function()
	{
		$scope.servidores = null;
		$http.get('/servidor/listar/json/').success(function(data){
			$scope.servidores = data;
		});
	};

	$scope.listar_areas = function()
	{

		$scope.relatorio.status=null;
		$scope.areas = null;

		$http.get('/area/listar/').success(function(data){
			$scope.areas = data;
		});

	};

	$scope.listar_categorias_de_agenda = function()
	{
		$scope.relatorio.status=null;
		$scope.categorias_de_agenda = null;

		CategoriaDeAgendaAPI.get({}, function(data) {
			$scope.categorias_de_agenda = data.results;
		});

	};

	$scope.init = function(data)
	{
        var hoje = new Date();

        $scope.fields = {
            data_final: null, // campo de exibição de data final
        };

        $scope.relatorio = {
            params: {
				ano: hoje.getFullYear(),
				mes: hoje.getMonth() + 1
            },
            tipo: 0,
            resource: null,
            status: null};

        for(var key in data) {
            $scope.relatorio[key] = data[key];
        }

		$scope.gerar_data();
		$scope.listar_diretorias();
		$scope.listar_comarcas();
		$scope.listar_defensores();
		$scope.listar_servidores();
		$scope.listar_areas();
		$scope.listar_categorias_de_agenda();
		$scope.listar_indicadores_meritocracia();


	};

	$http.get('/relatorios/listar/').success(function(data){
		$scope.relatorios = data;
    });

    // ao alterar campo 'data_final', aplicar data/hora final do dia selecionado no parametro dos relatórios
	$scope.$watch('fields.data_final', function() {
        if($scope.fields.data_final)
        {
            $scope.relatorio.params.data_final = $scope.fields.data_final.getMaxUTCDateTime();
        }
    });

}
