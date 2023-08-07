var atenderApp = angular.module('atenderApp', ['SisatApp','ngRoute','ui.utils','ui.bootstrap','$strap.directives','ngSanitize','maskMoney']);

atenderApp.config(['$httpProvider',
	function($httpProvider){
		$httpProvider.interceptors.push('HttpRequestInterceptor');
	}]);

atenderApp.config(['$routeProvider',
	function($routeProvider){
		$routeProvider.
			when('/atividades', {
				name: 'atividades',
				templateUrl: 'atender/tab/atividades/',
				controller: 'AtividadeCtrl'
			}).
			when('/documentos', {
				name: 'documentos',
                templateUrl: 'atender/tab/documentos/'
            }).
			when('/documento/:documentoId', {
				name: 'documentos',
                templateUrl: 'atender/tab/documentos/'
            }).
			when('/documento/:documentoId/:modal', {
				name: 'documentos',
                templateUrl: 'atender/tab/documentos/'
			}).
			when('/eproc', {
				name: 'eproc',
				templateUrl: 'atender/tab/processos/eproc/'
            }).
			when('/eproc/:processoId/grau/:processoGrau', {
				name: 'eproc',
				templateUrl: 'atender/tab/processos/eproc/'
			}).
			when('/historico', {
				name: 'historico',
				templateUrl: 'atender/tab/historico/'
			}).
			when('/oficios', {
				name: 'oficios',
				templateUrl: 'atender/tab/oficios/'
			}).
			when('/outros', {
				name: 'outros',
				templateUrl: 'atender/tab/outros/'
			}).
			when('/processos', {
				name: 'processos',
				templateUrl: 'atender/tab/processos/'
			}).
			when('/processo/:processoId/grau/:processoGrau', {
				name: 'processos',
				templateUrl: 'atender/tab/processos/'
			}).
			when('/processo/:processoId/:pendente', {
				name: 'processos',
				templateUrl: 'atender/tab/processos/'
			}).
			when('/propac', {
				name: 'propac',
				templateUrl: 'atender/tab/propacs/',
				controller: 'PropacsBuscarCtrl'
            }).
			when('/tarefas', {
				name: 'tarefas',
				templateUrl: 'atender/tab/tarefas/'
			}).
			when('/tarefa/:tarefaId', {
				name: 'tarefas',
				templateUrl: 'atender/tab/tarefas/'
			}).
			otherwise({
				redirectTo: '/historico'
			});
	}]);

atenderApp.controller('AtendimentoFormCtrl', ['$scope', 'fileUpload', 'Shared', function ($scope, fileUpload, Shared) {

	$scope.shared = Shared;
    $scope.status = {};
    $scope.iniciado = false;
    $scope.forma_presencial_existe = false;

	$scope.$watch('status.success', function() {
		if(typeof($scope.status.success)=='boolean')
		{
			if($scope.status.success)
			{
				show_stack_success('Registro salvo com sucesso!');
				$scope.get_permissao_botoes();
			}
			else
			{
				show_stack_error('Erro ao salvar registro!');
				if ($scope.status.data.errors.message !== undefined) {
				    show_stack_error($scope.status.data.errors.message);
                }
			}

			if ($scope.status.data.recarregar_pagina !== undefined && $scope.status.data.recarregar_pagina === true) {
				    location.reload();
            }
            else {
                $('#modal-confirmar-acesso').modal('hide');
            }
		}
 	});

	$scope.$watch('indeferimento_por_negacao_hipo', function() {
		if($scope.atendimento) {
            $scope.atendimento.indeferimento_classe = $scope.indeferimento_por_negacao_hipo;
            sessionStorage.setItem('indeferimento_por_negacao_hipo', $scope.indeferimento_por_negacao_hipo);
        }
	});

	$scope.$watch('indeferimento_por_negacao', function() {
		if($scope.atendimento) {
            $scope.atendimento.indeferimento_classe = $scope.indeferimento_por_negacao;
        }
	});

	$scope.$watch('atendimento.historico', function() {
        if($scope.iniciado)
        {
            localStorage.setItem('historico', $scope.atendimento.historico);
            $scope.recuperar_historico = false;
        }
        else
        {
            $scope.iniciado = true;
        }
 	});

	$scope.init = function(params)
	{
        $scope.atendimento = params;
        $scope.atendimento.historico = $scope.shared.historico;
        $('#id_historico').val($scope.atendimento.historico); // força atualização do redactor


        // se não preencheu a forma_atendimento irá selecionar o Presencial como default
        if ($scope.atendimento.forma_atendimento === undefined) {
            if ($scope.atendimento.nome_forma_atendimento_padrao !== undefined && $scope.atendimento.nome_forma_atendimento_padrao.trim() !== '') {
                for (var i = 0; i < $scope.formasAtendimento.length; i++) {
                    if ($scope.formasAtendimento[i].nome === $scope.atendimento.nome_forma_atendimento_padrao) {
                        $scope.formaAtendimento_select = $scope.formasAtendimento[i];
                        $scope.forma_presencial_existe = true;
                        break;
                    }
                }
            }
        }
        else {
            // se preencheu a forma_atendimento
            // faz tratamento para inicializar a FormaAtendimento conforme o dado salvo
            for (var i = 0; i < $scope.formasAtendimento.length; i++){
                if ($scope.formasAtendimento[i].id === $scope.atendimento.forma_atendimento) {
                    $scope.formaAtendimento_select = $scope.formasAtendimento[i];
                    break;
                }
            }
        }

        // se preencheu o tipo de coletividade
        // faz tratamento para inicializar o TipoColetividade conforme o dado salvo
        if ($scope.atendimento.tipo_coletividade !== undefined) {
            for (var i = 0; i < $scope.tiposColetividade.length; i++) {
                if ($scope.tiposColetividade[i].id === $scope.atendimento.tipo_coletividade) {
                    $scope.tipoColetividade_select = $scope.tiposColetividade[i];
                    break;
                }
            }
        }

	};

	$scope.upload = function () {
        function success()
        {
            // após salvar o atendimento, atualiza botão de acesso público/privado
            $scope.$emit('on_listar_acesso_atendimento');
            // após salvar, remover histórico do localStorage
            localStorage.removeItem('historico');
            $scope.recuperar_historico = false;
        }
        $scope.status = {};

        // faz tratamento para salvar dado de formasAtendimento
        if ($scope.formaAtendimento_select !== null && $scope.formaAtendimento_select.id > 0) {
            $scope.atendimento.forma_atendimento = $scope.formaAtendimento_select.id;
        } else {
            $scope.atendimento.forma_atendimento = null;
        }

        // faz tratamento para salvar dado de tipo_coletividade
        if ($scope.tipoColetividade_select !== null && $scope.tipoColetividade_select.id > 0) {
            $scope.atendimento.tipo_coletividade = $scope.tipoColetividade_select.id;
        } else {
            $scope.atendimento.tipo_coletividade = null;
        }

        fileUpload.upload('salvar/', $scope.atendimento, $scope.status, success);

        if ($scope.exibir_vulnerabilidade && $scope.is_vulneravel === '1'){
            $scope.salvar_vulnerabilidades($scope.vulnerabilidades, atendimento_id.value);
        }
    };

    $scope.recuperar_historico_sessao = function(){
        $scope.atendimento.historico = localStorage.getItem('historico');
        $('#id_historico').val($scope.atendimento.historico); // força atualização do redactor
        $('#id_historico').setCode($scope.atendimento.historico); // força atualização do redactor
        $scope.recuperar_historico = false;
    };

    $scope.descartar_historico_sessao = function(){
        localStorage.setItem('historico', $scope.atendimento.historico);
        $scope.recuperar_historico = false;
    }

}]);

atenderApp.directive('datepicker', function () {
	return {
		restrict: "C",
		link: function (scope, elem, attrs) {
			$(elem).datepicker();
		}
	}
});

atenderApp.factory('Assunto', function(){
	return {arvore:[], lista:{}};
});

function AtendimentoIndexCtrl($scope, $http, $filter, FormaAtendimentoAPI)
{

	$scope.motivos_exclusao = [];

	// utilizado para carregar o popover com dados do atendimento
	$scope.atendimento_popover = null;
	$scope.atendimentos_popover = {};

    $scope.carregar = function()
    {

        $scope.semanas = [];
        $scope.atendimentos = [];
        $scope.documentos = [];
        $scope.tarefas = [];
		$scope.atendimento_atual = null;

        $scope.carregando = true;
        $scope.carregando_resumo = true;
        $scope.carregando_documentos = true;
        $scope.carregando_tarefas = true;

		$http.post('/defensor/'+$scope.defensor+'/atuacoes/', {data_ini:$scope.dia, data_fim:$scope.dia}).success(function(data){
			$scope.atuacoes = data;
		});

		$http.post('index/resumo/get/', {data:$scope.dia}).success(function(data){

            dia = $filter('utc')($scope.dia);
            $scope.carregarMes(dia.getFullYear(), dia.getMonth(), data);
			$scope.carregando_resumo = false;

            $scope.ativar_acompanhamento_processo = data.ativar_acompanhamento_processo

            $http.post('index/get/', {data:$scope.dia}).success(function(data){
                $scope.atendimentos = [];
                if (Array.isArray(data)){
                    $scope.atendimentos = data;

					for (var i = 0; i < data.length; i++) {
						var atendimento = data[i];
						if (atendimento.em_atendimento && atendimento.em_atendimento.servidor_id == $scope.servidor) {
							$scope.atendimento_atual = atendimento;
						}
					}

                }
                else {
                    show_stack_error(data.mensagem);
                }
                $scope.carregando = false;

                $http.post('index/tarefas/get/', {data:$scope.dia}).success(function(data){

                    $scope.tarefas = data;

					var defensorias = [];
					for(var i = 0; i < data.length; i++) {
                        defensorias.push(data[i].defensoria);
                    }

					defensorias.sort();
					defensorias = defensorias.filter(function(elem, index, self){
						return index == self.indexOf(elem)
                    });


                    // CRIA PRATELEIRAS DE TAREFAS
                    var prateleiras = [];

                    // Tipos de tarefas (alertas, cooperações e tarefas)
                    var prateleiras_base = [
                        {
                            tipo: 'Alertas',
                            class: 'label-important',
                            filtro: {eh_alerta: true}
                        },
                        {
                            tipo: 'Cooperações',
                            class: 'label-warning',
                            filtro: {eh_cooperacao: true}
                        },
                        {
                            tipo: 'Tarefas',
                            class: 'label-info',
                            filtro: {eh_tarefa: true}
                        }
                    ];

                    for(var i = 0; i < prateleiras_base.length; i++)
                    {

                        // cria prateleira 'todos' para cada tipo de tarefa
                        prateleiras.push(Object.assign({nome: 'Todos', nome_class: 'bold'}, prateleiras_base[i]));

                        // criar prateleiras por defensoria para cada tipo de tarefa
                        for(var j = 0; j < defensorias.length; j++)
                        {
                            var prateleira = Object.assign({nome: defensorias[j]}, prateleiras_base[i]);
                            prateleira.filtro = Object.assign({}, prateleira.filtro, {defensoria: defensorias[j]});
                            prateleiras.push(prateleira);
                        }

                    }

                    $scope.prateleiras_tarefas = prateleiras;
                    $scope.carregando_tarefas = false;

                });

                $http.post('index/documentos/get/', {data:$scope.dia}).success(function(data){
                    $scope.documentos = data;
                    $scope.carregando_documentos = false;
                });

                if ($scope.ativar_acompanhamento_processo){
                    $http.post('/processo/partes/get').success(function(data){
                        $scope.partes = data;
                        $scope.carregando_parte = false;
                    });
                }

            });

		});

    };

    $scope.carregarMes = function(ano, mes, resumo)
    {

        $scope.ano = ano;
        $scope.mes = mes;

        var ini = new Date(ano, mes, 1);
        var fim = new Date(ano, mes + 1, 0);

        $scope.data_ini = ini;
        $scope.data_fim = fim;

        var last = new Date(ano, mes, 1);
        last.setHours(-24);

        var diasMes = fim.getDate();
        var diaSemana = ini.getDay();

        var semana = [];
        var semanas = [];

        semanas = [];
        semanas.push(semana);

        for(var i = 0; i < diaSemana; i++) {
            semana.push(last.getDate() - (diaSemana - i - 1));
        }

        for(var dia = 1; dia <= diasMes; dia++)
        {

            if(diaSemana==0)
            {
                semana = [];
                semanas.push(semana);
            }

            semana.push({data:new Date(ano, mes, dia), audiencias:resumo.audiencias[dia-1], agendamentos:resumo.agendamentos[dia-1]});

            diaSemana++;
            if(diaSemana==7) {
                diaSemana = 0;
            }

        }

        if(diaSemana!=0)
        {
            for(var i = diaSemana; i < 7; i++) {
                semana.push(i - diaSemana + 1);
            }
        }

        $scope.semanas = semanas;

    };

	$scope.carregar_visualizacoes = function(obj)
	{
		$http.get('/atendimento/tarefa/' + obj.id +'/get/').success(function(data){
			obj.visualizacoes = data.visualizacoes;
		});
	};

    $scope.marcar_tarefas = function(marcar, filtro)
    {

        var tarefas = $filter('filter')($scope.tarefas, filtro, true);
        tarefas = $filter('filter')(tarefas, $scope.filtro_tarefa, true);
        tarefas = $filter('filter')(tarefas, $scope.filtro_tarefas, true);

        for(var i = 0; i < tarefas.length; i++)
        {
            tarefas[i].marcada = marcar;
        }

    }

	$scope.chamar = function (atendimento) {
        $http.post('/atendimento/recepcao/chamar/', {'atendimento': atendimento, 'tipo': 1}).success(function (data) {

            if (data['success']) {
                show_stack_success("Notificado");
            } else {
                if (data['msg'] !== '')
                    show_stack_error(data['msg']);
                else
                    show_stack_error("Erro!");
            }
        });
    }

    $scope.init = function(servidor_id, defensor_id, comarca_id)
    {
        $scope.servidor = servidor_id;
        $scope.defensor = defensor_id;
        $scope.comarca = comarca_id;
        $scope.dia = new Date();
        $scope.carregar();
    }

	$scope.formas_atendimento = {};

	// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
	FormaAtendimentoAPI.get({limit:1000}, function(data){
		// Transforma array em object p/ facilitar consultas pelo id
		for(var i = 0; i < data.results.length; i++)
		{
			$scope.formas_atendimento[data.results[i].id] = data.results[i];
		}
	});

	$scope.get_atendimento = function(atendimento)
	{

        $scope.atendimento = null;
        $scope.atendimento_popover = null;

		if($scope.atendimentos_popover[atendimento]) {
            $scope.atendimento = $scope.atendimentos_popover[atendimento];
            $scope.atendimento_popover = $scope.atendimentos_popover[atendimento];
        }
		else
		{

			$scope.atendimentos_popover[atendimento] = {};
			$http.get('/atendimento/'+atendimento+'/json/get/').success(function(data){
                $scope.atendimento = data;
                $scope.atendimento_popover = data;
				$scope.atendimentos_popover[atendimento] = data;
				$scope.motivos_exclusao = data.motivos_exclusao;
			});

        }

	};

}

function AtividadeCtrl($scope, $http, $filter)
{

	$scope.atividade = {multiplicador: 1};
	$scope.documento = {};

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

	$scope.set_reabrir_atividade = function(){
	    $scope.reabrir_atividade = true;
    };

	$scope.init = function(nucleo)
	{
	    $scope.reabrir_atividade = false;

		var params = {nucleo: nucleo, tipo: 20};
		$http.post('/atendimento/qualificacao/listar/', params).success(function(data){
			$scope.qualificacoes = data.qualificacoes;
		});

	}

}

function AssuntoCtrl($scope, $http, Assunto)
{

	$scope.assunto = Assunto;
	$scope.carregou_assuntos = false;

	$scope.carregar_assuntos = function(pai)
	{
	    if (!$scope.carregou_assuntos) {
            $http.get('/atendimento/assuntos/get/').success(function (data) {
                $scope.carregou_assuntos = true;

                $scope.assunto.lista = data;
                $scope.assunto.arvore = [];

                for (item in data) {
                    for (filho in data[item].filhos) {
                        data[item].filhos[filho] = data[data[item].filhos[filho]];
                    }
                    if (data[item].pai == null) {
                        $scope.assunto.arvore.push(data[item]);
                    }
                }

                if (pai != undefined) {
                    $scope.abrir_arvore_assuntos(pai);
                }
            });
        }
	};

	$scope.abrir_arvore_assuntos = function(pai)
	{
		if(pai==undefined)
		{
			for(var i in $scope.assunto.lista)
			{
				if($scope.assunto.lista[i].filhos.length)
				{
					$scope.assunto.lista[i].sel = ($scope.filtro_assuntos != undefined);
				}
			}
		}
		else
		{
			if($scope.assunto.lista[pai].pai) {
                $scope.abrir_arvore_assuntos($scope.assunto.lista[pai].pai);
            }
			$scope.assunto.lista[pai].sel = true;
		}
	};

	$scope.adicionar = function(assunto)
	{
		$scope.novo = {pai: assunto, codigo:null, titulo:null};
	};

	$scope.mover_item = function(item, pos)
	{
		$http.post('/atendimento/assuntos/mover/', {id:item.id, posicao:pos}).success(function(data) {
			if(data.success) {
                $scope.carregar_assuntos(item.pai);
            }
			else {
                alert(data.erro);
            }
		});
	};

	$scope.salvar = function()
	{
		$http.post('/atendimento/assuntos/salvar/', $scope.novo).success(function(data) {
			$scope.carregar_assuntos($scope.novo.pai.id);
		});
	};

	$scope.excluir = function(assunto)
	{
		$scope.selecionado = assunto;
		$('#modal-excluir-assunto').modal();
	};

	$scope.excluir_confirmar = function()
	{
		$http.post('/atendimento/assuntos/excluir/', {id:$scope.selecionado.id}).success(function(data) {
			if(data.success) {
                $scope.carregar_assuntos($scope.selecionado.pai);
            }
			else {
                alert(data.erro);
            }
		});

	};

	$scope.btnSalvarAssuntosAtendimentoClick = function()
	{
		$scope.$emit('on_salvar_assuntos_atendimento');
	};

	$scope.init = function()
	{
		$scope.carregar_assuntos();
		console.log("carregando assuntos sem precisar de novo");
	}

}

function AtendimentoCtrl($scope, $route, $routeParams, $location, $http, $filter, Assunto, Shared, fileUpload, DefensorAPI, DefensoriaAPIv2, TipoColetividadeServiceAPI, AtuacaoAPI, QualificacaoServiceAPI)
{

	$scope.$route = $route;
	$scope.$location = $location;
	$scope.$routeParams = $routeParams;

    $scope.assunto = Assunto;
    $scope.assistidos = {};
    $scope.shared = Shared;
    $scope.iniciado = false;
    $scope.formaAtendimento_select = '';
    $scope.tipoColetividade_select = '';
    $scope.motivos_exclusao = [];
	let removeListenerLocationChangeStart;

	$scope.btnAlterarVisita_click = function(visita, prisao_id)
	{
		visita.prisao = prisao_id;
		$scope.$broadcast('VisitaCtrl:carregar', visita);
	};

	$scope.btnNovaVisita_click = function(atendimento, atendimento_inicial, hoje, pre_cadastro)
	{
		$scope.$broadcast('VisitaCtrl:init', {
			atendimento:atendimento,
			atendimento_inicial:atendimento_inicial,
			hoje:hoje,
			pre_cadastro:pre_cadastro
		});
	};

	$scope.btnExcluir_click = function(atendimento)
	{
		if(!$scope.atendimento || $scope.atendimento.numero!=atendimento)
		{
			$scope.atendimento = null;
			$http.get('/atendimento/'+atendimento+'/json/get/').success(function(data){
				$scope.atendimento = data;
				$scope.motivos_exclusao = data.motivos_exclusao;
			});
		}
	};

	$scope.set_formulario = function(formulario)
	{
		$scope.formulario = formulario;
	};

	$scope.salvar_formulario = function()
	{
		$scope.salvando = true;
		$http.post('formulario/salvar/', $scope.formulario).success(function(data){
			$scope.salvando = false;
			show_stack('Formulário salvo com sucesso!', false, 'success');
		});
	};

	$scope.listar = function()
	{

        $scope.carregando = true;
        $scope.atendimentos = null;
        $scope.atendimento = null;

		$http.get('atender/get/').success(function(data){

			for(var i = 0; i < data.length; i++)
			{
				if(data[i].numero == $scope.numero)
				{
					$scope.atendimento = data[i];
                    $scope.shared.historico = data[i].historico;
				}
				else
				{
					for(var j = 0; j < data[i].filhos.length; j++)
					{
						if(data[i].filhos[j].numero == $scope.numero)
						{
                            $scope.shared.historico = data[i].filhos[j].historico;
						}
					}
				}
				data[i].editavel = (new Date(data[i].data_atendimento) > $scope.dia_um);
			}

			$scope.atendimentos = data;
            $scope.carregando = false;

            var historico_sessao = localStorage.getItem('historico');

            if(historico_sessao && historico_sessao != 'undefined' && $scope.shared.historico != historico_sessao)
            {
                $scope.recuperar_historico = true;
            }

		});

        //config EXIBIR_VULNERABILIDADE_DIGITAL
		if (typeof exibir_vulnerabilidade_digital !== 'undefined') {
			$scope.exibir_vulnerabilidade = exibir_vulnerabilidade_digital.value.toLowerCase() === 'true';
			if ($scope.exibir_vulnerabilidade){
				$scope.listar_vulnerabilidade();
			}
		}
	};

    $scope.listar_vulnerabilidade = function(){
        $http.post('vulnerabilidades/get/', document.getElementById('atendimento_id').value)
        .success((data) => {
            $scope.vulnerabilidades = data['json']['vulnerabilidade']
            $scope.mensagem_vulnerabilidade_digital = data['mensagem']
            $scope.is_vulneravel = data['json']['possui_vulnerabilidade'] ? '1' : ''  // caso já exista vulnerabilidade, recebe 1 que é sim
        });
    }

    $scope.salvar_vulnerabilidades = function(vulnerabilidades, atendimentoId){
        $http.post('vulnerabilidades/salvar/', {
            'vulnerabilidades': vulnerabilidades,
            'atendimento_id': atendimentoId,
        }).success((data) => $scope.exibirCheckboxesVulnerabilidade(false));
	}

    $scope.exibirCheckboxesVulnerabilidade = (exibir=true) => {
        checkboxes.style.display = exibir ? 'block' : 'none';
    }

    $scope.toggleExibirCheckboxesVulnerabilidade = function(){
        let exibir = checkboxes.style.display === 'block' ? false : true;
        $scope.exibirCheckboxesVulnerabilidade(exibir);
    }

	$scope.listar_outros = function()
	{
		$scope.outros = null;
		$http.get('atender/outros/get/').success(function(data){
			$scope.outros = data;
			$scope.carregando_documentos = false;
		});
	};

	$scope.set_outro = function(atendimento) {
		$scope.outro = atendimento;
	};

	$scope.$on('on_listar_acesso_atendimento', function(event, args){
		$scope.listar_acesso();
	});

	$scope.listar_acesso = function()
	{
		$scope.acessos = null;
		$http.get('acesso/').success(function(data){
			$scope.acessos = data;
		});
	};

	$scope.conceder_acesso = function(defensor_id, publico)
	{
		$scope.acessos = null;
		$http.post('acesso/conceder/', {defensor:defensor_id, publico:publico}).success(function(data){
			$scope.listar_acesso();
		});
	};

	$scope.revogar_acesso = function(defensor_id, publico)
	{
		$scope.acessos = null;
		$http.post('acesso/revogar/', {defensor:defensor_id, publico:publico}).success(function(data){
			$scope.listar_acesso();
		});
	};

	$scope.solicitar_acesso = function(defensor_id)
	{
		$scope.acessos = null;
		$http.post('acesso/solicitar/', {defensor:defensor_id}).success(function(data){
			location.reload();
		});

	};

	$scope.$on('on_salvar_assuntos_atendimento', function(event, args){
		$scope.salvar_assuntos();
	});

	$scope.salvar_assuntos = function()
	{

		var assuntos = [];

		for(var i in $scope.assunto.lista)
		{
			if($scope.assunto.lista[i].pai && !$scope.assunto.lista[i].filhos.length && $scope.assunto.lista[i].sel)
			{
				assuntos.push(i);
			}
		}
		$http.post('assunto/salvar/', assuntos).success(function(data){
			// monta array e salva os assuntos selecionados
			if(data.assuntos.length)
			{
				$scope.atendimento.assuntos = {};
				for(var i in data.assuntos)
				{
					$scope.atendimento.assuntos[data.assuntos[i]] = $scope.assunto.lista[data.assuntos[i]];
				}
			}
			else
			{
				$scope.atendimento.assuntos = null;
			}
			// fecha modal
			$('#modal-arvore-assuntos').modal('hide');
		});
	};

	$scope.vincular_assuntos = function()
	{
		for(var key in $scope.atendimento.assuntos){
			$scope.assunto.lista[key].sel = true;
		}
	};

	$scope.get_resumo_apoio = function(apoio)
	{
		$scope.apoio = apoio;
		$scope.apoio.resumo = null;
		$http.get('/atendimento/' + $scope.apoio.numero + '/atividade/resumo/get/').success(function(data){
			$scope.apoio.resumo = data.resumo;
		});
	};

	$scope.get_pessoa = function(pessoa_id)
	{

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

    $scope.showModal = function(name)
    {
        $(name).modal();
    };

    $scope.get_permissao_botoes = function(){
        // carrega as permissões dos botões da Ficha de Atendimento

        $http.get('json/get/permissao/').success(function(data){
            if (data.sucesso) {
                $scope.permissao_botoes = data.permissao_botoes;
                if (data.permissao_botoes && data.permissao_botoes.pode_agendar) {
                    window.removeEventListener("beforeunload", confirmaAtendimentoEncerrado, false);
                }
            }
            else {
                $scope.permissao_botoes = {};
            }
		});
    };

    $scope.init_tab_historico = function()
	{
	    $scope.listar();
        $scope.get_permissao_botoes();

		DefensoriaAPIv2.get({limit:1000, ativo:true, serializer: 'basico'}, function(data){
			result = data.results;
			for (var i = 0; i < result.length; i++) {
				if (result[i].atuacao == null) {
					result[i].atuacao = '';
				} else {
					result[i].atuacao = ' - ' + result[i].atuacao;
				}
			}
			$scope.defensorias_encaminhamento = result;
		});
    };

	$scope.encaminhamento_atendimento = function(){
		$('#modal-encaminhamento-atendimento').modal('show');
		$scope.carrega_qualificacoes_encaminhamento();
		aplicar_select2('modal-encaminhamento-atendimento');
	}

	$scope.remeter = function(defensoria_destino_id, atuacao, motivo, observacao) {
		atendimento_id = null
		if ($scope.atendimento.tipo[1] == 'Inicial') {
			atendimento_id = $scope.atendimento.id;
		}
		else {
			atendimento_id = $scope.atendimento['inicial_id'];
		}

		$http.post('remeter_atendimento/', {
				atendimento_id: atendimento_id,
				defensoria_destino_id: defensoria_destino_id,
				defensor_destino_id: atuacao['defensor']['id'],
				qualificacao_id: motivo.id,
				historico: observacao
			}).success(function(data){
			if(data.success) {
				location.reload();
				show_stack_success('Atendimento remetido com sucesso!');
			}
			else {
				show_stack_error('Ocorreu um erro ao remeter o atendimento!');
			}
		});
	}

	$scope.carregar_defensores_encaminhamento = function(defensoria_id) {
		AtuacaoAPI.get({defensoria_id: defensoria_id, ativo:true, apenas_vigentes:true, apenas_defensor:true}, function(data) {
			$scope.atuacoes_defensores_encaminhamento = data.results;
		});
	}

	$scope.carrega_qualificacoes_encaminhamento = function() {
		$scope.qualificacoes_encaminhamento = null;
		QualificacaoServiceAPI.get({tipo:50}, function(data) {
			$scope.qualificacoes_encaminhamento = data.results;
		});
	}

    $scope.listar_formas_atendimento = function()
	{
		$scope.formasAtendimento = null;
		$http.get('/atendimento/formas/listar/defensor/').success(function(data){
			$scope.formasAtendimento = data;
		});
	};

    // lista os tipos de coletividade utilizados
    $scope.listar_tipos_coletividade = function()
	{
		$scope.tiposColetividade = null;
		TipoColetividadeServiceAPI.get({}, function(data) {
			$scope.tiposColetividade = data.results;
		});
	};

	$scope.init = function(numero, dia_um, realizado, agendamentoFuturo, permissaoEditar)
	{
		// TODO: Verificar se histórico foi alterado em vez da situação do atendimento
		console.log(numero, dia_um, realizado, agendamentoFuturo, permissaoEditar, (permissaoEditar && !realizado && !agendamentoFuturo));
        if (!realizado && !agendamentoFuturo && permissaoEditar) {
            removeListenerLocationChangeStart = $scope.$on("$locationChangeStart", function(event, next, current) {
                const naoPodeAgendar = !($scope.permissao_botoes ? $scope.permissao_botoes.pode_agendar : true);
                const origemDestinoIguais = (next == current);
                if (!origemDestinoIguais && naoPodeAgendar) {
                    const confirmouMudancaAba = confirm('Este atendimento não está encerrado, deseja realmente sair?');
                    if(confirmouMudancaAba) {
                        removeListenerLocationChangeStart();
                    } else {
                        event.preventDefault();
                    }
                }
            });
            window.addEventListener("beforeunload", confirmaAtendimentoEncerrado);
        }

		dia_um = dia_um.split('/');
		$scope.dia_um = new Date(dia_um[2], dia_um[1]-1, dia_um[0]);
		$scope.numero = numero;

		$scope.carregando = true;
		$scope.listar_acesso();

		$http.get('formulario/listar/').success(function(data){
			$scope.formularios = data.formularios;
		});

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensorAPI.get({incluir_atuacoes:false, ativo:true, limit:1000}, function(data){
			$scope.defensores = data.results;
		});

		$scope.listar_formas_atendimento();
		$scope.listar_tipos_coletividade();
	}

    function confirmaAtendimentoEncerrado (event) {
        event.returnValue = "Atendimento não encerrado!";
    }
}

function BuscarCtrl($scope, $http, ComarcaAPI, DefensorAPI, DefensoriaAPI)
{

    $scope.sucesso = true;
	$scope.filtro = {ultima:true, total:0};
	$scope.assistidos ={};
	$scope.motivos_exclusao = [];
	$scope.comarcas = [];

	// utilizado para carregar o popover com dados do atendimento
	$scope.atendimento_popover = null;
	$scope.atendimentos_popover = {};

	$scope.$watch('defensor', function() {
		if($scope.defensor) {
            $scope.filtro.defensor = $scope.defensor.id;
        }
		else {
            $scope.filtro.defensor = '';
        }
		$scope.validar();
	});

	$scope.$watch('defensoria', function() {
		if($scope.defensoria) {
            $scope.filtro.defensoria = $scope.defensoria.id;
        }
		else {
            $scope.filtro.defensoria = '';
        }
		$scope.validar();
	});

	$scope.init = function(filtro)
	{

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensoriaAPI.get({limit:1000}, function(data){
			$scope.defensorias = data.results;
			$scope.defensoria = get_object_by_id($scope.defensorias, filtro.defensoria);
			aplicar_select2('BuscarAtendimentoForm', true);
		});

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensorAPI.get({incluir_atuacoes:false, ativo:true, limit:1000}, function(data){
			$scope.defensores = data.results;
			$scope.defensor = get_object_by_id($scope.defensores, filtro.defensor);
			aplicar_select2('BuscarAtendimentoForm', true);
		});

		for(var key in filtro) {
            $scope.filtro[key] = filtro[key];
		}

        $scope.filtro.data_ini = DataConversao(filtro['data_ini']);
        $scope.filtro.data_fim = DataConversao(filtro['data_fim']);

		$scope.validar();
		$scope.buscar(0);

	};

	$scope.validar = function () {
		var filtro = $scope.filtro;
		var data_ini = (filtro.data_ini != undefined && filtro.data_ini);
		var data_fim = (filtro.data_fim != undefined && filtro.data_fim);
		var datas = (data_ini && data_fim && data_ini <= data_fim) || (!data_ini && !data_fim);
		$scope.valido = datas && (data_ini || data_fim || filtro.defensor || filtro.defensoria || filtro.filtro) && (!$scope.defensor || $scope.defensor.id) && (!$scope.defensoria || $scope.defensoria.id);
	};

	$scope.get_atendimento = function(atendimento)
	{

        $scope.atendimento = null;
        $scope.atendimento_popover = null;

		if($scope.atendimentos_popover[atendimento]) {
            $scope.atendimento = $scope.atendimentos_popover[atendimento];
            $scope.atendimento_popover = $scope.atendimentos_popover[atendimento];
        }
		else
		{

			$scope.atendimentos_popover[atendimento] = {};
			$http.get('/atendimento/'+atendimento+'/json/get/').success(function(data){
                $scope.atendimento = data;
                $scope.atendimento_popover = data;
				$scope.atendimentos_popover[atendimento] = data;
				$scope.motivos_exclusao = data.motivos_exclusao;
			});

        }

	};

	$scope.buscar = function(pagina, recarregar) {

		$scope.filtro.pagina = (pagina==undefined ? 0 : pagina);
		$scope.carregando = true;

        if(pagina==0 && recarregar)
        {
            var url = gerar_url($scope.filtro, ['data_ini', 'data_fim', 'defensor', 'defensoria', 'filtro', 'situacao']);
            window.location.assign(url);
            return;
        }

		var filtro = {...$scope.filtro}; // copia valor para alterar formato das datas
		filtro['data_ini'] = date_to_string_ddmmyyyy(filtro['data_ini']);
		filtro['data_fim'] = date_to_string_ddmmyyyy(filtro['data_fim']);

		$http.post('/atendimento/buscar/', filtro).success(function (data) {

            $scope.sucesso = data.sucesso;

            if(data.sucesso)
            {

                $scope.LISTA = data.LISTA;
                $scope.filtro.ultima = data.ultima;
                $scope.filtro.paginas = data.paginas;

                if(data.atendimentos.length && !data.ultima) {
                    data.atendimentos[data.atendimentos.length - 1].ultimo = true;
                }

                if(data.pagina===0)
                {
                    for(var i = 0; i < data.atendimentos.length; i++) {
                        // for (var j =0; data.atendimentos[i].pessoas.length; j++){
                        for (var j = 0; j < data.atendimentos[i].pessoas.length; j++) {
                            if (data.atendimentos[i].pessoas[j].pessoa__nome_social !== null &&
                                data.atendimentos[i].pessoas[j].pessoa__nome_social.trim() === '') {
                                data.atendimentos[i].pessoas[j].pessoa__nome_social = null;
                            }
                            if (data.atendimentos[i].pessoas[j].pessoa__apelido !== null &&
                                data.atendimentos[i].pessoas[j].pessoa__apelido.trim() === '') {
                                data.atendimentos[i].pessoas[j].pessoa__apelido = null;
                            }
                        }
                    }
                    $scope.atendimentos = data.atendimentos;
                    $scope.filtro.total = data.total;
                }
                else
                {
                    for(var i = 0; i < data.atendimentos.length; i++) {
                        for (var j = 0; j < data.atendimentos[i].pessoas.length; j++) {
                            if (data.atendimentos[i].pessoas[j].pessoa__nome_social === ''){
                                data.atendimentos[i].pessoas[j].pessoa__nome_social = null;
                            }
                            if (data.atendimentos[i].pessoas[j].pessoa__apelido === ''){
                                data.atendimentos[i].pessoas[j].pessoa__apelido = null;
                            }
                        }

                        $scope.atendimentos.push(data.atendimentos[i]);
                    }
                }

            }
            else
            {
                $scope.mensagem = data.mensagem;
                $('#id_filtro').addClass('tooltip-error').attr('data-trigger', 'manual').attr('title', data.mensagem).tooltip('show');
            }

			$scope.carregando = false;

		});
	};

	$scope.get_pessoa = function(pessoa_id)
	{

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

	$scope.carregar_comarcas = function()
	{

		if($scope.comarcas.length==0)
		{
			// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
			ComarcaAPI.get({ativo:true, limit:1000}, function(data){
				$scope.comarcas = data.results;
			});
		}
	}

	$scope.validar();

}

function TarefaCtrl($scope, $http, TarefaServiceAPI, QualificacaoServiceAPI)
{

    $scope.defensorias = [];
    $scope.responsaveis = [];
    $scope.documentos = null;
	$scope.tipos_tarefas = []

	$scope.prioridades = [
        {id:0, nome:'Urgente', class:'label-important'},
        {id:1, nome:'Alta', class:'label-warning'},
        {id:2, nome:'Normal', class:'label-info'},
        {id:3, nome:'Baixa', class:'label-info'},
        {id:4, nome:'Alerta', class:'label-warning'},
        {id:5, nome:'Cooperação', class:'label-warning'}
    ];
	$scope.tarefas = [];
    $scope.resposta_para = [];
    $scope.tarefa_id = null;

    $scope.prateleiras = [
        {
            alertas: true,
            nome: 'ALERTAS',
            filtro: {eh_alerta: true}
        },
        {
            cooperacoes: true,
            nome: 'COOPERAÇÕES',
            filtro: {eh_cooperacao: true}
        },
        {
            tarefas: true,
            nome: 'TAREFAS',
            filtro: {eh_tarefa: true}
        },
    ];

	$scope.carregar_setor_responsavel = function() {

        $scope.responsaveis = [];
        $scope.qualificacoes = [];
        $scope.setor_responsavel = null;

		if($scope.nova_tarefa.setor_responsavel)
		{
            $http.get('/defensoria/' + $scope.nova_tarefa.setor_responsavel + '/get/').success(function (data) {
                $scope.setor_responsavel = data;
                $scope.responsaveis = data.defensores;
                $scope.qualificacoes = data.qualificacoes;
            });
        }

 	};

	$scope.carregar_tipos_tarefas = function()
	{
		QualificacaoServiceAPI.get({tipo:40}, function(data) {
			$scope.tipos_tarefas = data.results;
		});
	}

	$scope.carregar_dados = function()
	{

        $scope.setor_responsavel = null;
        $scope.listar_processos();

		$http.get('defensorias/').success(function(data){
			result = data.defensorias;
			for (var i = 0; i < result.length; i++) {
				if (result[i].atuacao != null) {
					result[i].nome = result[i].nome + ' - ' + result[i].atuacao;
				}
			}
			$scope.defensorias = result;
			$scope.resposta_para = data.resposta_para;
        }).then(function() {
			aplicar_select2('modal-cadastrar-tarefa');
		});
	}

	$scope.nova = function(prioridade)
	{
        $scope.nova_tarefa = {prioridade:prioridade};
		$scope.carregar_dados();
	};

	$scope.editar = function(tarefa)
	{
		$scope.nova_tarefa = {
			'id': tarefa.id,
			'setor_responsavel': tarefa.setor_responsavel.id,
			'tipo': tarefa.tipo,
			'responsavel': tarefa.responsavel ? tarefa.responsavel.id: null,
			'processo': tarefa.processo,
			'resposta_para': tarefa.resposta_para ? tarefa.resposta_para.id : null,
			'prioridade': tarefa.prioridade,
			'titulo': tarefa.titulo,
			'descricao': tarefa.descricao,
			'data_inicial': tarefa.data_inicial,
			'data_final': tarefa.data_final
		}
		$scope.carregar_dados();
		$scope.carregar_setor_responsavel();
	}

	$scope.excluir = function(obj)
	{
		if(obj==undefined)
		{

		    if($scope.excluindo)  {
		        return;
		    }
		    $scope.excluindo = true;

			$http.post('tarefa/excluir/', $scope.tarefa).success(function(data){
				if(data.success)
				{
					$('#modal-excluir-tarefa').modal('hide');
                    show_stack_success('Registro excluído com sucesso!');
                    window.location.assign('#/tarefas');
				}
				else
				{
					show_stack_error('Ocorreu um erro ao excluir o registro!');
				}
				$scope.excluindo = false;
			});

		}
		else {
            $scope.tarefa = obj;
        }
	};

    $scope.abrir = function(obj, recarregar)
    {
        if(recarregar)
        {
            var url = '#/tarefa/' + obj.id;
            window.location.assign(url);
        }
        else
        {

            TarefaServiceAPI.get({numero: $scope.atendimento_numero, id:obj.id}, function(data) {
                $scope.tarefa = data;
                $scope.tarefa.novo_status = ($scope.tarefa.status ? 0 : 2);
                $http.get('/atendimento/tarefa/' + $scope.tarefa.id +'/visualizar/').success(function(data){});
            });

            $scope.listar_documentos();

        }
    }

	$scope.finalizar = function(obj)
	{
        $http.post('tarefa/finalizar/', $scope.tarefa).success(function(data){
            if(data.success)
            {
                show_stack_success('Registro atualizado com sucesso!');
                location.reload();
            }
            else
            {
                show_stack_error('Ocorreu um erro ao atualizar o registro!');
            }
        });
	};

	$scope.salvar = function()
	{

	    if($scope.salvando)  {
	        return;
        }
	    $scope.salvando = true;

		$http.post('tarefa/salvar/', $scope.nova_tarefa).success(function(data){
			if(data.success)
			{
                show_stack_success('Registro salvo com sucesso!');
				$('#modal-cadastrar-tarefa').modal('hide');
                $('#modal-cadastrar-alerta').modal('hide');
				if($scope.nova_tarefa.id)
				{
					window.location.reload();
				}
				else
				{
					var url = '#/tarefa/' + data.id;
					window.location.assign(url);
				}
			}
			$scope.salvando = false;
		});
	};

	$scope.listar = function()
	{

	    $scope.tarefas = [];
	    $scope.carregando_tarefas = true;

        TarefaServiceAPI.get({numero: $scope.atendimento_numero}, function(data) {

            $scope.tarefas = data.results;

			for(var i = 0; i < $scope.tarefas.length; i++)
			{
				if($scope.tarefa_id==$scope.tarefas[i].id)
				{
					$scope.tarefa_id = null;
					$scope.abrir($scope.tarefas[i], false);
				}
			}

            $scope.carregando_tarefas = false;

        });

    };

    $scope.listar_processos = function() {
        $http.get('atender/processos/get/').success(function(data){
            $scope.processos = data;
        });
    };

    $scope.listar_documentos = function() {
        $http.get('json/get/documentos/').success(function(data){
            $scope.documentos = data.documentos;
        });
    }

	$scope.popover = function (obj, url) {
		var title = obj.titulo;
		var content = '<p>Criado em: [[documento.criado_em|date:\'dd/MM/yyyy\']]</p>';
		content += '<p>Criado por: [[ documento.nome_servidor ]]</p>';
		content += '<p>Assinado? [[ documento.esta_assinado ? \'Sim\' : \'Não\' ]]</p>';
		return {"title": title, "content": content};
	};

	$scope.init = function (args)
	{

		for(var key in args) {
            $scope[key] = args[key];
        }

        $scope.listar();
		$scope.carregar_tipos_tarefas();

	}

}

function OficioCtrl($scope, $http) {

    $scope.responsaveis = [];
    $scope.prioridades = [{id: 0, nome: 'Urgente'}, {id: 1, nome: 'Alta'}, {id: 2, nome: 'Normal'}, {
        id: 3,
        nome: 'Baixa'
    }];
    $scope.prioridades_class = ['label-important', 'label-warning', 'label-info', ''];
    $scope.tarefas = [];
    $scope.resposta_para = [];

    $scope.nova = function () {
        $scope.tarefa = {prioridade: -1};
    }

    $scope.salvar = function () {
        if ($scope.salvando) return;
        $scope.salvando = true;

        $http.post('tarefa/salvar/', $scope.tarefa).success(function (data) {
            if (data.success) {
                $http.post('oficio/salvar/', $scope.tarefa).success(function (data) {
					if (data.success) {
						show_stack_success('Ofício salvo com sucesso!');
						$('#modal-encaminhar-oficio').modal('hide');
						window.location.reload(true);
					} else {
						show_stack_error('Ocorreu um erro ao salvar o registro!');
						$scope.salvando = false;
					}
                });
            } else {
                show_stack_error('Ocorreu um erro ao salvar o registro!');
				$scope.salvando = false;
            }
        });
    }

    $scope.$watch('responsavel', function () {
        if ($scope.responsavel)
            $scope.tarefa.responsavel = $scope.responsavel.id;
        else
            $scope.tarefa.responsavel = null;
    });

    $scope.popover = function (obj, url) {
        var title = obj.titulo;
        var content = '<p>Criado em: [[documento.criado_em|date:\'dd/MM/yyyy\']]</p>';
        content += '<p>Criado por: [[ documento.nome_servidor ]]</p>';
        content += '<p>Assinado? [[ documento.esta_assinado ? \'Sim\' : \'Não\' ]]</p>';
        return {"title": title, "content": content};
    };

    $scope.init = function (args) {

        for (var key in args){
			$scope[key] = args[key];
		}

		$http.get('/defensoria/' + $scope.tarefa.setor_responsavel + '/get/').success(function (data) {
			$scope.responsaveis = data.defensores;
		});
    }

}

app.filter('distribuir_mudou_responsavel', function(){
	return function(itens) {
        var filtered = [];
		angular.forEach(itens, function(value, key){
			if(value.pre_responsavel != value.responsavel){
				this.push(value);
			}
		}, filtered);
		return filtered;
    }
});

function DistribuicaoCtrl($scope, $http)
{

	$scope.buscar = function(filtro)
	{

		if(filtro!=undefined) {
            $scope.filtro = filtro;
        }

		$scope.atuacoes = [];
		$scope.assessores = [];
		$scope.atendimentos = [];
		$scope.carregando = true;

		$http.post('',$scope.filtro).success(function(data){
			$scope.atuacoes = data.atuacoes;
			$scope.assessores = data.assessores;
			$scope.atendimentos = data.atendimentos;
			$scope.carregando = false;
		});

	};

	$scope.salvar = function()
	{
		$scope.salvando = true;
		if($scope.atendimentos){
			$http.post('salvar/', $scope.atendimentos).success(function(data){
				$scope.buscar()
				$scope.salvando = false;
				show_stack('Atendimentos atualizados com sucesso!', false, 'success');
			});
		}
	}

}


function ArquivarAtendimentoCtrl($scope, $http) {
	$scope.atendimentoNumero = null;
	$scope.documentoUpload = null;
	$scope.documentoUploadNome = null;
	$scope.qualificacoes = null;
	$scope.qualificacoesPorTipo = [];
	$scope.justificativa = "";
	$scope.qualificacaoSelecionada = null;

	$scope.getQualificacoes = function() {
		const url = "/api/v1/qualificacoes?tipo=60,61";
		$http.get(url).success(function (data) {
			const tiposSet = new Set();
			const tipos = data.results.filter(el => {
				const duplicado = tiposSet.has(el.tipo);
				tiposSet.add(el.tipo);
				return !duplicado;
			});
			const tiposQualificoes = tipos.map(function(tipo) {
				const tipoQualificacao = {
					tipoId: tipo.tipo,
					nome: tipo.tipo_nome,
					qualificacoes: data.results.filter(function(qualificacao) {
						return qualificacao.tipo == tipo.tipo;
					}).map(function(qualificacao) {
						return {
							id: qualificacao.id,
							nome: qualificacao.titulo
						}
					}),
				  };
				return tipoQualificacao;
			});
			$scope.qualificacoes = tiposQualificoes;
		}).error(function (data) {
			console.error("Ocorreu um erro ao arquivar o atendimento.");
		});
	}

	$scope.filtraQualificacoes = function(tipoQualificacaoArquivamento) {
		for (qualificacao of $scope.qualificacoes) {
			if (qualificacao.tipoId == tipoQualificacaoArquivamento.tipoId) {
				$scope.qualificacoesPorTipo = qualificacao.qualificacoes;
				break;
			}
		}
	}

	$scope.removerDocumento = function() {
		$scope.documento_upload = null;
	}

	$scope.limpaTela = function () {
		$scope.documentoUpload = null;
		$scope.qualificacoes = [];
		$scope.qualificacoesPorTipo = [];
	}

	$scope.arquivarAtendimento = function () {
		const url = `/api/v1/atendimentos/${$scope.atendimentoNumero}/arquivar/`;
		const formData = new FormData();
		formData.append("historico", $scope.justificativa);
		formData.append("qualificacao", $scope.qualificacaoSelecionada.id);
		formData.append("origem", $scope.atendimentoNumero);
		if ($scope.documentoUpload) {
			formData.append("documento_arquivo", $scope.documentoUpload);
			formData.append("documento_nome", $scope.documentoUploadNome || $scope.documentoUpload.name);
		}
		$http.post(url, formData, {
			transformRequest: angular.identity,
			headers: {'Content-Type': undefined}
		}).success(function (data) {
			show_stack_success('O atendimento foi arquivado com sucesso!', false);
			window.location.reload(true);
		}).error(function(data, status) {
			if (status == 403) {
				if (data.erro) {show_stack_error(data.erro)};
			}
		});
	}
}


function DesarquivarAtendimentoCtrl($scope, $http) {
	$scope.atendimentoNumero = null;
	$scope.documentoUpload = null;
	$scope.documentoUploadNome = null;
	$scope.justificativa = "";

	$scope.getQualificacoes = function() {
		const url = "/api/v1/qualificacoes?tipo=62";
		$http.get(url).success(function (data) {
			const qualificacoes = data.results.map(function(qualificacao) {
				return {
					id: qualificacao.id,
					nome: qualificacao.titulo
				}
			});
			$scope.qualificacoes = qualificacoes;
			$scope.qualificacaoSelecionada = qualificacoes.length ? qualificacoes[0] : null;
		});
	}

	$scope.removerDocumento = function() {
		$scope.documento_upload = null;
	}

	$scope.limpaTela = function () {
		$scope.documentoUpload = null;
	}

	$scope.desarquivarAtendimento = function () {
		const url = `/api/v1/atendimentos/${$scope.atendimentoNumero}/desarquivar/`;
		const formData = new FormData();
		formData.append("historico", $scope.justificativa);
		formData.append("qualificacao", $scope.qualificacaoSelecionada.id);
		if ($scope.documentoUpload) {
			formData.append("documento_arquivo", $scope.documentoUpload);
			formData.append("documento_nome", $scope.documentoUploadNome || $scope.documentoUpload.name);
		}
		$http.post(url, formData, {
			transformRequest: angular.identity,
			headers: {'Content-Type': undefined}
		}).success(function (data) {
			show_stack_success('O atendimento foi desarquivado com sucesso!', false);
			window.location.reload(true);
		}).error(function(data, status) {
			if (status == 403) {
				if (data.erro) {show_stack_error(data.erro)};
			}
		});
	}
}


function DocumentoCtrl($scope, $http, $location, $window, $log, fileUpload, ContribDocumentoServiceAPI, DefensoriaAPI, DefensoriaAPIv2)
{
	const ATENDIMENTO = 1;
	const ASSISTIDO = -1;
	const prefixosArquivos = {
		[ATENDIMENTO]: "documentos_atendimento",
		[ASSISTIDO]: "documentos_assistido"
	};

	$scope.documentosSelecionados = {
		[ATENDIMENTO]: [],
		[ASSISTIDO]: []
	};

	$scope.ATENDIMENTO = ATENDIMENTO;
	$scope.ASSISTIDO = ASSISTIDO;

	$scope.documento = {};
	$scope.documentos = {};
	$scope.defensorias = [];

	$scope.listaDocumentosEscolhidos = [];
	$scope.listaDocumentosEnviando = [];
	$scope.pastasDocumentos = [];

	$scope.criaDocumentoPendencia = function () {
		$scope.listaDocumentosEscolhidos.push({
			id: null,
			nome: "",
			documento: null,
			arquivo: null
		});
	}

	$scope.limparDocumentosSelecionadosUpload = function () {
		// Reseta apenas a lista de documentos para upload e não a lista de documentos sendo enviados.
		$scope.listaDocumentosEscolhidos = [];
	}

	$scope.validaDocumentoTemNome = function (documento) {
		return documento.nome? true : false;
	}

	$scope.removerDocumento = function (index) {
		$scope.listaDocumentosEscolhidos.splice(index, 1);
	}

    $scope.selecionaArquivosUpload = function (e) {
		$scope.$apply(function () {
			for (var i = 0; i < e.files.length; i++) {

				let nome = e.files[i].name;
				nome = nome.substring(0, nome.lastIndexOf('.')).replaceAll('_', ' ');

				$scope.listaDocumentosEscolhidos.push({
					id: null,
					nome: nome,
					documento: null,
					arquivo: e.files[i]
				});

			}
		});
		aplicar_select2('modal-upload-documentos');
	};

	// adicionar múltiplos documentos por upload
	$scope.adicionarMultiplosDocumentos = function(atendimento_numero) {
		const url = '/atendimento/'+ atendimento_numero + '/documento/salvar/';
		$scope.documentos_com_erro = false;

		for(const [index, documento] of $scope.listaDocumentosEscolhidos.entries()) {
			const tipoDocumento = documento.documento ? documento.documento.id : null;
			documento.documento = tipoDocumento;
			documento.pasta = documento.pasta ? documento.pasta.id : null;
			const nomeArquivo = documento.arquivo? documento.arquivo.name : "documento de pendência";

			const identificadorArquivo = index + nomeArquivo;
			$scope.listaDocumentosEnviando.push(identificadorArquivo);
			fileUpload.uploadPromise(
				url,
				documento
			).success(function(data) {
				$scope.listaDocumentosEnviando.pop();
				const nomeArquivo = documento.arquivo? documento.arquivo.name : "documento de pendência";
                if(data.success)
                {
					show_stack_success('Documento ' + nomeArquivo + ' salvo com sucesso!', false);
                }
                else{
                    $scope.documentos_com_erro = true;
                    show_stack_error('Erro ao salvar o documento ' + nomeArquivo + ': ' + data.errors[0][1], false);
                }
			}).error(function(data) {
				$scope.listaDocumentosEnviando.pop();
				show_stack_error('Erro ao salvar o documento! ');
			});
		}
	};

	$scope.$watch('estaEnviando', function(newValue, oldValue) {
		const estavaEnviando = !newValue && oldValue;

		if (estavaEnviando) {
			$('#modal-upload-documentos').modal('hide');
			$scope.limparDocumentosSelecionadosUpload();
			if(!$scope.documentos_com_erro)
				show_stack_success('Todos os documentos foram enviados com sucesso!', false);
			$scope.listar();
		}
	});

	Object.defineProperty($scope, 'estaEnviando', {
		/*
			Simula uma computed property para indicar o status do upload
			Compatível com os browsers:
			Chrome >= 5
			Edge >= 12
			Firefox >= 4
			Internet Explorer >= 9
			Opera >= 11.6
			Safari >= 5.1
		*/
		get: function() {
			if (!$scope.listaDocumentosEnviando) {return false};
			return $scope.listaDocumentosEnviando.length > 0 ? true : false;
		}
	});

	$scope.selecionarDocumentoDownload = function (documento, tipoListaID) {
		const index = $scope.documentosSelecionados[tipoListaID].indexOf(documento);
		if (index == -1) {
			$scope.documentosSelecionados[tipoListaID].push(documento);
		} else {
			$scope.documentosSelecionados[tipoListaID].splice(index, 1);
		}
	};

	$scope.listaDocumentosPasta = function (pasta_nome, incluirNaoSelecionados=true) {
		return $scope.documentos.uploads.filter(function(doc) {
			return doc.pasta_nome == pasta_nome && (doc.sel || incluirNaoSelecionados)
		});
	};

	$scope.selecionarTodosDocumentos = function (listaDocumentos, tipoListaID) {
		const documentosParaSelecionar = listaDocumentos.filter(function (documento) {
			return !$scope.documentosSelecionados[tipoListaID].includes(documento)
		});
		for (documento of documentosParaSelecionar) {
			$scope.enumerar(documento, tipoListaID);
			documento.sel = true;
			$scope.documentosSelecionados[tipoListaID].push(documento);
		}
	};

	$scope.desselecionarTodosDocumentos = function (documentosSelecionados, tipoListaID) {
		const documentosDesselecionarDownload = [];
		for (documento of documentosSelecionados) {
			$scope.enumerar(documento, tipoListaID);
			documento.sel = false
			documentosDesselecionarDownload.push(documento)
		}
		for (doc of documentosDesselecionarDownload) {
			$scope.selecionarDocumentoDownload(doc, tipoListaID);
		}
	};

	$scope.downloadDocumentos = function (listaDocumentos, tipoListaID) {
		if (!listaDocumentos.length > 0)
			return

		// const url = '/atendimento/documentos/documentos_download/'
		const arquivos = listaDocumentos.filter(function(documento) {
			// Valida autorização de documentos GED
			const naoPodeBaixarGED = !documento.documento_online_pode_baixar;
			if (documento.documento_online_pk_uuid && naoPodeBaixarGED) {
				return false;
			}
			return true;
		}).map(function(documento) {
			return documento["pk"]
		});

		const numero_atendimento = $scope.documentos.atendimento_numero;
		const prefixo_nome_arquivo = prefixosArquivos[tipoListaID] + "_" + numero_atendimento;
		const url = '/atendimento/' + numero_atendimento + '/atender/tab/documentos/documentos_download/';

		$http.post(url, {
			prefixo_arquivo: prefixo_nome_arquivo,
			arquivos_solicitados: arquivos, tipo_documentos: tipoListaID},
			{responseType:'arraybuffer'})
		.success(function (data, status, headers) {
			const contentType = headers()['content-type'];
			const linkElement = document.createElement('a');
			let filename = "documentos.zip"

			try {
				filename = headers()["content-disposition"].split('filename=')[1].split(';')[0].replace("\"", "").replace("\"", "");
			} catch (exception) {
				$log.warn("Ocorreu um erro ao tentar recuperar o nome original/final do arquivo retornado pela requisição.");
			}

			try {
				const blob = new Blob([data], {type: contentType});
				const url = $window.URL.createObjectURL(blob);
				linkElement.setAttribute('href', url);
				const clickEvent = new MouseEvent("click", {
					"view": $window,
					"bubbles": true,
					"cancelable": false
				});
				linkElement.setAttribute("download", filename);
				linkElement.dispatchEvent(clickEvent);
			} catch (ex) {
				$log.error("Ocorreu um erro ao tentar processar a resposta da requisição com o arquivo para download.");
			}
		})
		.error(function(error) {
			$log.error("Ocorreu um erro ao tentar solicitar download dos arquivos.")
		});
	}

	$scope.impressao = {};
	$scope.relatorios = [
		{name: 'pendentes', label: 'Documentos do Atendimento', assistido:false},
		{name: 'recibo_documentacao', label: 'Recibo de Documentação', assistido:true}
	];

	$scope.excluir = function(obj)
	{
		if(obj==undefined)
		{
			$http.post('documento/excluir/', $scope.documento).success(function(data){
				if(data.success)
				{
					$scope.listar();
					$('#modal-excluir-documento').modal('hide');
					show_stack_success('Documento excluído com sucesso!');
					location.reload();
				}
				else
				{
					show_stack_error('Ocorreu um erro ao excluir o documento!');
				}
			});
		}
		else
		{
			$scope.documento = obj;
		}
	};

	$scope.cancelar_update_documento = function() {
        // TODO: verifiar necessidade desta função

		$scope.documento_status = {};
        $scope.documento_upload = {
            'id': null,
            'nome': ''
        };
    };

	// adicionar Documento por upload
    $scope.adicionar_documento = function(atendimento_numero) {
        /*
        CUIDADO! Cerifique-se se o 'atendimento_numero' é elegível para receber documentos. Na página 'Atender' esse
        número pode ser alterado, visto que o atendimento aberto pode ser um pedido de apoio, devendo o documento ser
        vinculado a um atendimento diferente. Ao adicionar documento em pedido de apoio, este não aparecerá na lista
        de documentos da página 'Atender', mas aparecerá no painel do núcleo em que foi solicitado o pedido de apoio
        */

        function on_success(posted, returned) {
			// Se informado, vincula documento a uma manifestação processual
			if(returned.success && $scope.manifestacao_id){
				var params = {
					"manifestacao": $scope.manifestacao_id,
					"origem": 10,
					"origem_id": returned.documento.id,
					"posicao": 0,
					"tipo_mni": null,
					"nivel_sigilo": 0
				}
				$http.post('/api/v1/manifestacao_processual/'+$scope.manifestacao_id+'/documentos/', params).success(function(data){
					window.location.reload(true);
				});
			}
        }
        fileUpload.upload(
            '/atendimento/'+ atendimento_numero + '/documento/salvar/',
            $scope.documento_upload,
            $scope.documento_status,
			on_success
        );

    };

    // Status do upload de documento
    $scope.documento_status = {};

    /* Utilizado para monitorar o retorno do upload de documento */
	$scope.$watch('documento_status.success', function() {
		if(typeof($scope.documento_status.success) === 'boolean')
		{
			if($scope.documento_status.success)
			{
                $('#modal-documentos-atendimento').modal('hide');
				show_stack_success('Documento salvo com sucesso!');
				$scope.listar();
			}
			else
			{
				show_stack_error('Erro ao salvar documento!');
			}

			$scope.documento_status = {};
		}
 	});

	$scope.listar = function()
	{

		if($scope.manifestacao_id) return;

	    $scope.documentos = [];
	    $scope.carregando_documentos = true;

        // carrega documentos vinculados ao atendimento
		$http.get('documento/').success(function(data){

			$scope.documentos = data;
            $scope.carregando_documentos = false;

            if($scope.documento_id)
            {

                for(var i=0; i<data.uploads.length; i++)
                {
                    if(data.uploads[i].id==$scope.documento_id)
                    {
                        $scope.carregar(data.uploads[i], false);
                    }
                }

                if($scope.documento && $scope.modal)
                {
                    $('#' + $scope.modal).modal('show');
                }

            }

		});

	};

	$scope.carregar = function(documento, agendar)
	{

		$scope.fecharModalEditar()
        documento = angular.copy(documento);

        $scope.pessoa_id = documento.pessoa_id;
        $scope.tem_pessoa = ($scope.pessoa_id!=null);

        documento.modo = 1;

        if(agendar && documento.status_resposta==null) {
            documento.status_resposta = 0;
        }

        // Aplica objeto tipo documento selecionado
        if(documento.documento_id!=null)
        {
            for(var i = 0; i < $scope.tipos.length; i ++)
            {
                if($scope.tipos[i].id==documento.documento_id) {
					documento.documento = documento.documento_id;
					$scope.tipo_documento_selecionado = $scope.tipos[i];
                }
            }
        }

        $scope.documento = documento;
        $scope.documento_upload = documento;

	};

    $scope.enumerados = [];
	$scope.quantidade_documentos_anexos = 0;
    $scope.enumerar = function(documento, lista){
        // lista -> 1 = atendimento, -1 = assistido
        var pk = documento.pk * lista;
        var index = $scope.enumerados.indexOf(pk);

		// Se já existe na lista, remove item e reordena demais itens
        if(index >= 0)
        {
            // Remove da lista e remove posição
            $scope.enumerados.splice(index, 1);
            documento.posicao = null;

            // Reordena outros itens da lista
            for(var i = index; i < $scope.enumerados.length; i++)
            {
                // Documentos do Atendimento
                if($scope.enumerados[i] > 0)
                {
                    for(var j = 0; j < $scope.documentos.uploads.length; j++)
                    {
                        if($scope.documentos.uploads[j].pk == $scope.enumerados[i]){
                            $scope.documentos.uploads[j].posicao--;
                        }
                    }
                }
                // Documentos da Pessoa
                else
                {
                    for(var j = 0; j < $scope.documentos.assistidos_documentos.length; j++)
                    {
                        if($scope.documentos.assistidos_documentos[j].pk == $scope.enumerados[i] * -1){
                            $scope.documentos.assistidos_documentos[j].posicao--;
                        }
                    }
                }
            }

        }
        // Senão, adiciona no final da lista
        else
        {
            $scope.enumerados.push(pk);
            documento.posicao = $scope.enumerados.length - $scope.quantidade_documentos_anexos;

			if(documento.documento_resposta_id){
				$scope.enumerados.push(documento.documento_resposta_id);
				$scope.quantidade_documentos_anexos += 1;
			}
        }


    }

	$scope.init = function(args)
	{

		DefensoriaAPIv2.get({limit:1000, serializer: 'basico'}, function(data){
			$scope.defensorias = data.results;
		});

        for(var key in args)
        {
            $scope[key] = args[key];
        }

		$scope.cancelar_update_documento();
		$scope.listar();

		// carrega tipos de documentos
		ContribDocumentoServiceAPI.get({exibir_em_documento_atendimento:true, ativo:true}, function(data) {
			$scope.tipos = data.results;
		});

    }

	$scope.$on('DocumentoCtrl:carregar', function(event, args){
		$scope.carregar(args, false);
	});

	$scope.$on('DocumentoCtrl:atualizarPastas', function(event, pastas) {
		$scope.pastasDocumentos = pastas;
	});

	$scope.fecharModalEditar = ()=>{

		$('#modal-geral-editar').modal('hide');
	}
	$scope.editar_ged = (documento)=>{
		doc= angular.copy(documento);
		idDoc =documento.pk


		if(idDoc != undefined || doc != undefined){
			lookup_atendimento = null
			$http.get('/api/v1/atendimentos/'+lookup_atendimento+'/documento-online/'+idDoc).success(function(data){


				resultadoDoc = data

				resultadoDoc.nome = doc.nome

				resultadoDoc.pasta = doc.pasta ? doc.pasta.id : null
				resultadoDoc.defensoria = doc.defensoria
				if(resultadoDoc.defensoria == undefined){
					resultadoDoc.defensoria = doc.defensoria_id
				}

				$http({ method: 'PATCH',
							url: '/api/v1/atendimentos/'+lookup_atendimento+'/documento-online/'+idDoc+'/',
							data: resultadoDoc
					  }).success( (deuCerto)=>{

							$scope.listar()
							location.reload()


						  }

						)
				}, (error)=>{
					show_stack_error('Erro ao editar! Verifique se todos os campos foram preenchidos corretamente.');
				})

		}





	}



}

function NucleoCtrl($scope, $http)
{

    $scope.defensorias = [];
    $scope.defensoria = null;

    $scope.atuacoes = [];
    $scope.atuacao = null;

	$scope.$watch('defensoria', function() {
		$scope.qualificacoes = [];
		if($scope.defensoria)
		{
			var params = {nucleo: $scope.defensoria.nucleo__id, tipo: 10};
			$http.post('/atendimento/qualificacao/listar/', params).success(function(data){
                $scope.qualificacoes = data.qualificacoes;
                if (data.qualificacoes.length) {
                    $scope.qualificacao = data.qualificacoes[0];
                }
			});
		}
 	});

     $scope.init = function(defensor_id){
        $http.get('/nucleo/defensoria/listar/').success(function(data){
            $scope.defensorias = data.defensorias;
        });
        if(defensor_id > 0)
        {
            $http.get('/defensor/{0}/supervisores/atuacoes/'.replace('{0}', defensor_id)).success(function(data){
                $scope.atuacoes = data;
            });
        }
    }

}

function NucleoDPGCtrl($scope, $http, $filter)
{

    $scope.tipo_indeferimento = null;
	$scope.defensoria = null;

	$scope.$watch('defensoria', function() {
		$scope.classes = [];
		if($scope.defensoria)
		{
			var params = {tipo: $scope.tipo_indeferimento};
			$http.post('/core/classe/listar/', params).success(function(data){
                $scope.classes = data;
                $scope.classe = data[0];
			});
		}
     });

     $scope.init = function(tipo_indeferimento){

        $scope.tipo_indeferimento = tipo_indeferimento;

        $http.post('/nucleo/defensoria/listar/', {indeferimento:true}).success(function(data){

            var filtro = {};

            switch($scope.tipo_indeferimento)
            {
                case 6030:
                    filtro = {nucleo__indeferimento_pode_receber_impedimento:true};
                    break;
                case 6040:
                    filtro = {nucleo__indeferimento_pode_receber_suspeicao:true};
                    break;
            }

            $scope.defensorias = $filter('filter')(data.defensorias, filtro, true);
            $scope.defensoria = $scope.defensorias[0];

        });

     }

}

function OrganizacaoCtrl($scope, $http)
{

	$scope.pessoa = {};
	$scope.pessoas = [];

	$scope.listar_municipios = function(estado)
	{
		$http.get('/estado/'+$scope.pessoa.estado+'/municipios/').success(function(data){
			$scope.municipios = data;
		});
	};

	$scope.pesquisar = function(filtro)
	{
		$http.get('/assistido/comunidade/listar/',{params:{'q':filtro}}).success(function(data){
			$scope.pessoas = data;
		});
	};

	$scope.carregar = function(obj)
	{
		$scope.tab = 1;
		$scope.pessoa = obj;
		$scope.listar_municipios($scope.pessoa.estado);
	};

	$scope.salvar = function(ultimo)
	{

		$scope.salvando = true;

		$http.post($('#ComunidadeForm').attr('action'), $scope.pessoa).success(function(data){

			if(data.success)
			{
				$scope.salvando = false;
				$scope.pessoa = data.pessoa;
				$('#modal-comunidade').modal('hide');
				show_stack_success('Registro gravado com sucesso!');
			}
			else
			{
				show_stack_error('Erro ao salvar! Verifique se todos os campos foram preenchidos corretamente.');
			}

			$scope.salvando = false;

		}).error(function(){

			show_stack_error('Erro ao salvar! Verifique se todos os campos foram preenchidos corretamente.');
			$scope.salvando = false;

		});

	};

	$scope.limpar = function(tab)
	{
		$scope.tab = (tab == undefined ? 0 : tab);
		$scope.pessoa = {};
		$scope.estado = null;
	};

	function init()
	{

		$scope.limpar();

		$http.get('comunidade/listar/').success(function(data){
			$scope.tab = (data.success ? 1 : 0);
			$scope.pessoa = data.comunidade;
			if($scope.pessoa) {
                $scope.listar_municipios($scope.pessoa.estado);
            }
		});

		$http.get('/estado/listar/').success(function(data){
			$scope.estados = data;
		});

	}

	init();

}

function VisitaCtrl($scope, $http, $filter, DefensorAPI, AtuacaoAPI, FormaAtendimentoAPI, QualificacaoServiceAPI) {

	$scope.estabelecimentos = [];
	$scope.defensores = [];
	$scope.qualificacoes = [];
	$scope.formas_atendimento = [];

	$scope.$on('VisitaCtrl:init', function(event, args) {
		$scope.emit = args.emit;
		$scope.init(args.atendimento, args.atendimento_inicial, args.hoje, args.pre_cadastro);
	});

	$scope.init = function (atendimento, atendimento_inicial, hoje, pre_cadastro) {

		if(hoje != null)
		{
			hoje = hoje.split('/');
			hoje = new Date(hoje[2], hoje[1]-1, hoje[0]);
			$scope.data_atendimento = hoje;
		}

		$scope.visita = {'inicial': atendimento_inicial, 'origem': atendimento};

		for(var key in pre_cadastro) {
            $scope.visita[key] = pre_cadastro[key];
        }

		$scope.init_dados();

	};

	$scope.init_dados = function()
	{
		if($scope.estabelecimentos.length==0)
		{
			$http.get('/api/v1/estabelecimentos-penais/').success(function (data) {
				$scope.estabelecimentos = data.results;
				$scope.estabelecimento_penal = get_object_by_id($scope.estabelecimentos, $scope.visita.estabelecimento_penal);
				aplicar_select2('modal-visita');
			});
		}

		if($scope.defensores.length==0)
		{
			DefensorAPI.get({incluir_atuacoes:false, ativo:true, limit:1000}, function(data){
				$scope.defensores = data.results;
				$scope.defensor = get_object_by_id($scope.defensores, $scope.visita.defensor);
				aplicar_select2('modal-visita');
			});
		}

		if($scope.qualificacoes.length==0)
		{
			QualificacaoServiceAPI.get({tipo:10, penal:true, ativo:true, limit:1000}, function(data){
				$scope.qualificacoes = data.results;
				$scope.qualificacao = get_object_by_id($scope.qualificacoes, $scope.visita.qualificacao);
				aplicar_select2('modal-visita');
			});
		}

		if($scope.formas_atendimento.length==0)
		{
			FormaAtendimentoAPI.get({limit:1000}, function(data){
				$scope.formas_atendimento = data.results;
				$scope.forma_atendimento = get_object_by_id($scope.formas_atendimento, $scope.visita.forma_atendimento);
				aplicar_select2('modal-visita');
        	});
		}
	}

	$scope.listar_defensorias = function () {
		if($scope.defensor!==undefined && $scope.data_atendimento!==undefined && $scope.hora_atendimento!==undefined)
		{
			let data_atendimento = $filter('date')($scope.data_atendimento, 'yyyy-MM-dd') + ' ' + $scope.hora_atendimento;
			AtuacaoAPI.get({servidor_id:$scope.defensor.id, apenas_defensor:true, data_inicial:data_atendimento, data_final:data_atendimento, limit:1000}, function(data){
				$scope.atuacoes = data.results;
				$scope.set_defensoria($scope.visita.defensoria);
				aplicar_select2('modal-visita');
			});
		}
	};

	$scope.salvar = function (redirecionar) {
		$scope.salvando = true;
		$http.post('/nucleo/nadep/prisao/' + $scope.visita.prisao + '/visita/salvar/', $scope.visita).success(function (data) {
			$scope.salvando = false;
			if (data.success)
			{
				if(redirecionar) {
                    location.reload();
                }
				if($scope.emit) {
					$scope.visita.numero = data.numero;
                    $scope.$emit($scope.emit, $scope.visita);
                }
				$('#modal-visita').modal('hide');
			}
			else
			{
                show_stack_error(data.message || 'Erro ao salvar! Verifique se todos os campos foram preenchidos corretamente.');
				$scope.errors = data.errors;
			}
		});
	};

	$scope.set_data_atendimento = function () {
		if($scope.data_atendimento!=undefined)
		{
			$scope.visita.data_atendimento = $filter('date')($filter('utc')($scope.data_atendimento), "dd/MM/yyyy") + ' ' + $scope.hora_atendimento;
			$scope.listar_defensorias();
		}
	};

	$scope.set_defensoria = function(defensoria_id)
	{
		for(var i = 0; i < $scope.atuacoes.length; i++)
		{
			if($scope.atuacoes[i].defensoria.id==defensoria_id) {
                $scope.defensoria = $scope.atuacoes[i];
            }
		}
	};

	$scope.$on('VisitaCtrl:carregar', function(event, args){
		$scope.visita = {
			id: args.id,
			data_atendimento: args.data_atendimento,
			estabelecimento_penal: (args.preso ? args.preso.estabelecimento_penal_id : null),
			defensor: args.defensor_id,
			defensoria: args.defensoria_id,
			qualificacao: args.qualificacao_id,
			forma_atendimento: args.forma_atendimento_id,
			historico: args.historico,
			prisao: args.prisao
		};
		$scope.data_atendimento = $scope.visita.data_atendimento;
		$scope.hora_atendimento = $filter('date')($filter('utc')($scope.visita.data_atendimento), "HH:mm");
		$scope.init_dados();
	});

	$scope.$watch('data_atendimento', function() {
		$scope.set_data_atendimento();
	});

	$scope.$watch('hora_atendimento', function() {
		$scope.set_data_atendimento();
	});

	$scope.$watch('estabelecimento_penal', function() {
		if($scope.estabelecimento_penal)
			$scope.visita.estabelecimento_penal = $scope.estabelecimento_penal.id;
	});

	$scope.$watch('defensor', function() {
		if($scope.defensor)
		{
			$scope.visita.defensor = $scope.defensor.id;
			$scope.listar_defensorias();
		}
	});

	$scope.$watch('defensoria', function() {
		if($scope.defensoria && $scope.defensoria.defensoria)
		{
			$scope.visita.atuacao = $scope.defensoria.id;
			$scope.visita.defensoria = $scope.defensoria.defensoria.id;
		}
	});

	$scope.$watch('qualificacao', function() {
		if($scope.qualificacao) {
            $scope.visita.qualificacao = $scope.qualificacao.id;
        }
	});

	$scope.$watch('forma_atendimento', function() {
		if($scope.forma_atendimento) {
            $scope.visita.forma_atendimento = $scope.forma_atendimento.id;
        }
	});

}

function AcessoCtrl($scope, $http)
{

	$scope.informacoes = function(atendimento)
	{
		$http.get('/atendimento/'+atendimento+'/json/get/').success(function(data){
			$scope.atendimento = data;
			$('#modal-informacoes').modal();
		});
	}

}

angular.module('SisatApp').controller('AtendimentoSemAgendaCtrl',['$scope','$http', function($scope, $http){

	// Variaveis acessiveis por todas funções do controller
	let select_defensorias;
	let select_defensor;
	let select_qualificacoes;
	let array_qualificacoes = [];

	$scope.criar_atendimento_inicial_sem_agenda = function(dados_para_criar_atendimento){
			// Primeiro obtem as atuações do usuário que será utilizado para popular os selects de defensoria e defensor
            $http.get(`/api/v1/atuacoes?servidor_id=${dados_para_criar_atendimento.servidor_defensor_id}&ativo=true&apenas_vigentes=true`)
            .then(function(atuacoes){
                $('#modal-inicial-sem-agenda').modal('show');
				// Limpa o HTML para inserir os novos elementos
				document.querySelector("#modal-inicial-sem-agenda .modal-body").innerHTML = '';
				// Cria um option falso para forçar o usuário a selecionar uma das opções da tela
                select_defensorias = document.createElement("select");
                select_defensorias.classList.add("span12");
                let option_fake = document.createElement("option");
                option_fake.value = "";
                option_fake.text = "---------------------";
                select_defensorias.appendChild(option_fake);

				// Cria outros selects com o option falso já criado
                select_defensor = select_defensorias.cloneNode();
                select_qualificacoes =  select_defensorias.cloneNode();
				select_qualificacoes.id = 'id_qualificacoes';
				select_qualificacoes.style.margin = '0';

				// Preenche o select de defensorias baseado nas informações de lotações
                atuacoes.data.results.forEach(function(lotacaoes){
                    let option = document.createElement("option");
                    option.value = lotacaoes.defensoria.id;
                    option.text = lotacaoes.defensoria.nome;
                    select_defensorias.appendChild(option);
                });

				// Preenche o select de qualificações
				_obter_qualificacoes('/api/v1/qualificacoes/?tipo=10&exibir_em_atendimentos=true&limit=1000&possui_orgao_encaminhamento=false').then(function(qualificacoes){
					qualificacoes.forEach(function(qualificacao){
                        let option = document.createElement("option");
                        option.value = qualificacao.id;
                        option.text = `${qualificacao.titulo} (${qualificacao.area.nome})`;
                        select_qualificacoes.appendChild(option);

                    });
				});

				// Preenche o select de defensores lotados na defensoria selecionada pelo usuário
                select_defensorias.addEventListener("change", function(){
                    select_defensor.innerHTML = "";
					option_fake.setAttribute("disabled", true);
                    $http.get(`/api/v1/atuacoes?defensoria_id=${select_defensorias.value}&apenas_defensor=true&apenas_vigentes=true`).then(function(lotacoes){
                        lotacoes.data.results.forEach(function(defensor){
                            let option = document.createElement("option");
                            option.value = defensor.defensor.id;
                            option.text = defensor.defensor.nome;
                            select_defensor.appendChild(option);
                        });
                    });
                });

				// injeta todos os elementos na modal já existente
				let label_container_defensoria = document.createElement("label");
				label_container_defensoria.className = "control-label";
				let label_container_defensor = label_container_defensoria.cloneNode();
				let label_container_qualificacoes = label_container_defensoria.cloneNode();

				let label_defensoria = document.createElement("label");
				label_defensoria.textContent="Defensoria:";
				label_container_defensoria.appendChild(label_defensoria);
				document.querySelector("#modal-inicial-sem-agenda .modal-body").appendChild(label_container_defensoria);
                document.querySelector("#modal-inicial-sem-agenda .modal-body").appendChild(select_defensorias);


				let label_defensor = document.createElement("label");
				label_defensor.textContent="Defensor(a):";
				label_container_defensor.appendChild(label_defensor);
				document.querySelector("#modal-inicial-sem-agenda .modal-body").appendChild(label_container_defensor);
                document.querySelector("#modal-inicial-sem-agenda .modal-body").appendChild(select_defensor);


				let label_qualificacoes = document.createElement("label");
				label_qualificacoes.textContent="Qualificação do Atendimento:";
				label_container_qualificacoes.appendChild(label_qualificacoes);
				document.querySelector("#modal-inicial-sem-agenda .modal-body").appendChild(label_container_qualificacoes);
                document.querySelector("#modal-inicial-sem-agenda .modal-body").appendChild(select_qualificacoes);


				$("#id_qualificacoes").select2({
					width: '100%',
					margin: '0'
				});

				let btn_atender_agora = document.querySelector("#modal-inicial-sem-agenda-btn-atender-agora");
                btn_atender_agora.addEventListener("click", function(){
					btn_atender_agora.setAttribute("disabled", true);
                    // Chama API para criar o agendamento inicial com base nas informações selecionadas pelo usuário
					$http.post(`/api/v1/agendamentos/marcarinicial/`, {
                        pessoas_assistidas_ids: [dados_para_criar_atendimento.requerente_id],
                        defensoria_id: select_defensorias.value,
                        comarca_id: dados_para_criar_atendimento.comarca_servidor_id,
                        defensor_titular_id: select_defensor.value,
                        qualificacao_id: select_qualificacoes.value,
						atendimento_tipo_ligacao: false
                    })
					//Após criado atendimento, libera o atendimento na recepção (via API) e já rediciona para atendimento liberado
					.then(function(response){
                        let numero_atendimento_inicial = response.data.numero;
                        $http.post(`/api/v1/agendamentos/${numero_atendimento_inicial}/salvareliberaratendimento/`).then(
                            function(response){
                                if(response.data.sucesso == true){
                                    window.location.href = `/atendimento/${numero_atendimento_inicial}/#historico`;
                                }
                            }
                        );
                    });
                });

            });
	}

	$scope.retorno_sem_agenda = function(dados_do_atendimento){
		if (dados_do_atendimento.eh_defensor == false){
			// Obtem os defensores atuando na defensoria caso for assessor
			$http.get(`/api/v1/atuacoes?defensoria_id=${dados_do_atendimento.defensoria_atendimento_id}&apenas_defensor=true&apenas_vigentes=true`)
			.then(function(result){
				if (result.data.results.length == 0){
					show_stack_error('Não é possível prosseguir, a sua defensoria não possui defensores lotados');
					 return;
				}
				// Se tem mais de um defensor atuando na defensoria, exibe modal perguntando para qual defensor deverá ir o atendimento
				if(result.data.results.length > 1){
					$('#modal-defensores').modal('show');
					let select = document.createElement("select");
					select.classList.add("span12");
					result.data.results.forEach(function(defensor){
						let option = document.createElement("option");
						option.value = defensor.defensor.id;
						option.text = defensor.defensor.nome;
						select.appendChild(option);
					});
					document.querySelector("#modal-defensores .modal-body").appendChild(select);
					document.querySelector("#modal-defensores-btn-selecionar").addEventListener('click', function(event){

						document.querySelector("#modal-defensores-btn-selecionar").disabled = true;

						dados_do_atendimento.defensor_id = select.value;

						_prosseguir_com_retorno_agora(dados_do_atendimento);

					});
				}else{
					dados_do_atendimento.defensor_id = result.data.results[0].defensor.id;
					_prosseguir_com_retorno_agora(dados_do_atendimento);
				}
			});
		}else if (dados_do_atendimento.eh_defensor){
			dados_do_atendimento.defensor_id = dados_do_atendimento.servidor_defensor_id;
			_prosseguir_com_retorno_agora(dados_do_atendimento);
		}
	}

	_prosseguir_com_retorno_agora = function(dados_do_agendamento){

		document.querySelector("#atender-agora").disabled = true;

		$http.post(`/api/v1/agendamentos/${dados_do_agendamento.numero_atendimento}/marcarretorno/`, {
			pessoa_assistida_id: dados_do_agendamento.requerente_id,
			defensor_titular_id: dados_do_agendamento.defensor_id,
			comarca_id: dados_do_agendamento.comarca_servidor_id,
			defensoria_id: dados_do_agendamento.defensoria_atendimento_id
		}).then(function(response){

			retorno = response.data;

			$http.post(`/api/v1/agendamentos/${retorno.numero}/salvareliberaratendimento/`).then(
				function(response){
					if(response.data.sucesso == true){
						window.location.href = `/atendimento/${retorno.numero}/#historico`;
					}
				}
			);
		});
	}

	_obter_qualificacoes = function(url){

		return $http.get(url).then(function(response){

			response.data.results.forEach((result) => {
				array_qualificacoes.push(result);
			});

			if (response.data.next){
				return _obter_qualificacoes(response.data.next);
			}else{
				return array_qualificacoes;
			}
        });
	}

}]);


function PastaAtendimentoCtrl($scope, $http, DocumentoAtendimentoService) {

	$scope.pastas = [];
	$scope.pasta = {};
	$scope.numeroAtendimento = null;

	$scope.criarEditarPasta = function(pasta) {
		if (pasta.id)
			$scope.editarPasta(pasta)
		else
			$scope.criarPasta(pasta);
	}

	function exibirMsgPastaDuplicada (data, response) {
		// TODO: Melhorar / padronizar tratamento de erros (Frontend e API)
		return (response === 400 && data.non_field_errors && data.non_field_errors[0] === "Os campos atendimento, nome devem criar um set único.");
	}

	$scope.criarPasta = function (pasta) {
		const data = {
			atendimento: $scope.numeroAtendimento,
			nome: pasta.nome,
			descricao: pasta.descricao
		}
		const url = '/api/v1/pastas-documentos/';
		$http.post(url, data).success(function (data) {
			$scope.pastas.push(data);
			$scope.limpaSelecao();
			show_stack_success('Pasta criada com sucesso!');
		}).error(function(data, response) {
			if (exibirMsgPastaDuplicada(data, response)) {
				show_stack_error(`Já existe uma pasta chamada "${pasta.nome}".`);
			} else {
				show_stack_error("Ocorreu um erro ao criar a pasta.");
			}
		});
	}

	$scope.editarPasta = function (pasta) {
		const pastaId = pasta.id;
		const data = {
			id: pastaId,
			atendimento: $scope.numeroAtendimento,
			nome: pasta.nome,
			descricao: pasta.descricao
		}
		const url = `/api/v1/pastas-documentos/${pastaId}/`;
		$http.put(url, data).success(function (data) {
			for(const pastaIndex in $scope.pastas) {
				if ($scope.pastas[pastaIndex].id == data.id) {
					$scope.pastas[pastaIndex] = data;
					break;
				}
			}
			show_stack_success('Pasta editada com sucesso!');
		}).error(function(data, response) {
			if (exibirMsgPastaDuplicada(data, response)) {
				show_stack_error(`Já existe uma pasta chamada "${pasta.nome}".`);
			} else {
				show_stack_error("Ocorreu um erro ao atualizar a pasta.");
			}
		});
	}

	$scope.carregarPastas = function() {
		DocumentoAtendimentoService.listarPastasAtendimento($scope.numeroAtendimento)
		.success(function (data) {
			$scope.pastas = data.results;
			$scope.$emit("DocumentoCtrl:atualizarPastas", data.results);
		}).error(function() {
			console.error("Ocorreu um erro ao recuperar lista de pastas do atendimento.");
		});
	}

	$scope.selecionaPasta = function(pastaSelecionada) {
		$scope.pasta = angular.copy(pastaSelecionada);
	}

	$scope.limpaSelecao = function() {
		$scope.pasta = null;
	}

	$scope.init = function (numeroAtendimento) {
		$scope.numeroAtendimento = numeroAtendimento;
		$scope.pasta = null;
		$scope.carregarPastas();
	}
}
