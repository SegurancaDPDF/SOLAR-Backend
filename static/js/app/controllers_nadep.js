var siapApp = angular.module('siapApp', ['ngRoute','ngSanitize','ngResource','ui.utils','ui.bootstrap','$strap.directives','siapControllers']);

angular.module("siapApp").factory('DefensoriaAPI', function($resource) {
    return $resource('/api/v1/defensorias/:id.json', {id:'@id'}, {
	});
});

angular.module("siapApp").factory('DefensorAPI', function($resource) {
    return $resource('/api/v1/defensores/:id.json', {id:'@id'}, {
	});
});

siapApp.factory('Config', function(){
	return {
        is_superuser: false,
        URL_PROCESSO_TJ: '',
        NOME_PROCESSO_TJ: ''
	}
});

siapApp.factory('Preso', function(){
	return {
        id: null
    }
});

siapApp.config(function($httpProvider){
    $httpProvider.defaults.headers.post['X-CSRFToken'] = $('input[name=csrfmiddlewaretoken]').val();
	$httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
});

siapApp.config(function($interpolateProvider){
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

siapApp.run(function($rootScope){
	$rootScope.get_amd = function(obj){
		if(obj==undefined || obj.anos==undefined || obj.meses==undefined || obj.dias==undefined) {
            return '0a0m0d';
        }
		else {
            return '(_a)a(_m)m(_d)d'.replace('(_a)', obj.anos).replace('(_m)', obj.meses).replace('(_d)', obj.dias);
        }
	}
});

siapApp.run(function ($rootScope) {
    $rootScope.get_url_processo_tj = function (url, numero, grau, chave) {
        grau = (grau==undefined ? '' : grau);
        chave = (chave==undefined ? '' : chave);
        return url.replace(/{numero}/g, numero).replace(/{grau}/g, grau).replace(/{chave}/g, chave);
    };
});

siapApp.run(function($rootScope){
	$rootScope.Utils = {
		keys: Object.keys
	}
});

siapApp.filter('utc', function(){
    return function(d) {
        if(d==undefined) {
            return 'Não informado(a)';
        }
        date = new Date(d); //converte string em data
        date = new Date(date.getTime()+date.getTimezoneOffset()*60000); //soma diferenca de timezone
        if(d.length==10) {
            date = new Date(date.getTime() + date.getTimezoneOffset() * 60000); //soma diferenca de timezone
        }
        return date;
    }
});

siapApp.filter('startsWith', function() {
    return function(input, value) {
    	return input.sort(propComparator(value.toUpperCase()));
    };
});

siapApp.config(['$routeProvider',
	function($routeProvider){
		$routeProvider.
			when('/prisoes', {
				name: 'prisoes',
				templateUrl: '/static/template/siap/tab_prisoes.html',
				controller: 'PrisaoTabCtrl'
			}).
			when('/guias/:data_base', {
				name: 'guias',
				templateUrl: '/static/template/siap/tab_guias.html',
				controller: 'GuiaTabCtrl'
			}).
			when('/faltas', {
				name: 'faltas',
				templateUrl: '/static/template/siap/tab_faltas.html',
				controller: 'FaltaTabCtrl'
			}).
			when('/remissoes', {
				name: 'remissoes',
				templateUrl: '/static/template/siap/tab_remissoes.html',
				controller: 'RemissaoTabCtrl'
			}).
			when('/processos', {
				name: 'processos',
				templateUrl: '/static/template/siap/tab_processos.html',
				controller: 'ProcessoTabCtrl'
			}).
			when('/aprisionamentos', {
				name: 'aprisionamentos',
				templateUrl: '/static/template/siap/tab_aprisionamentos.html',
				controller: 'AprisionamentoTabCtrl'
			}).
			when('/interrupcoes', {
				name: 'interrupcoes',
				templateUrl: '/static/template/siap/tab_interrupcoes.html',
				controller: 'InterrupcaoTabCtrl'
			}).
			when('/historico', {
				name: 'historico',
				templateUrl: '/static/template/siap/tab_historico.html',
				controller: 'HistoricoTabCtrl'
			}).
			otherwise({
				redirectTo: '/prisoes'
			});
	}]);

var siapControllers = angular.module('siapControllers', []);

siapControllers.controller('VerPessoaCtrl', ['$scope', 'Preso', 'Config',
	function($scope, Preso, Config){

        $scope.config = Config;
		$scope.preso = Preso;

		$scope.$on('selectTab', function(event, args){
			$scope.tab = args.tab;
		});

		$scope.$on('VerPessoaCtrl:showModalAlterarRegime', function(event, args){
			$scope.showModalAlterarRegime();
			$scope.modalAlterarRegimeUrl = '/static/template/siap/modal_alterar_regime.html';
		});

		$scope.init = function(params, configs)
		{
			for(var key in configs) {
                $scope.config[key] = configs[key];
            }
            for(var key in params) {
                $scope.preso[key] = params[key];
            }
		};

		$scope.showModalAlterarRegime = function()
		{
			$('#modal-alterar-regime').modal();
			$scope.$broadcast('AlterarRegimeCtrl:novo', {tipo:1, prisao:$scope.preso.prisao, 'regime_atual': $scope.preso.regime_atual});
		};

		$scope.btnTransferir_click = function()
		{
			$scope.modalTransferirUrl = '/static/template/siap/modal_registrar_transferencia.html';
		};

		$scope.showModalTransferir = function()
		{
			$('#modal-registrar-transferencia').modal();
		};

		$scope.btnSoltar_click = function()
		{
			$scope.modalSoltarUrl = '/static/template/siap/modal_registrar_soltura.html';
		};

		$scope.showModalSoltar = function()
		{
			$('#modal-registrar-soltura').modal();
        };

	}
]);

siapControllers.controller('PrisaoTabCtrl', ['$scope', '$http', 'Preso', 'Config',
	function($scope, $http, Preso, Config){

        $scope.config = Config;
		$scope.prisoes = {};
		$scope.prisoes_inativas = {};
		$scope.permissao_delete_prisao = false;

		$scope.$emit('selectTab', {tab:1});

		$scope.carregar = function()
		{
			$http.get('/nucleo/nadep/preso/($0)/prisao/get/'.replace('($0)', Preso.id)).success(function(data){
				$scope.prisoes = data.prisoes;
				$scope.prisoes_inativas = data.prisoes_inativas;
				$scope.LISTA = data.LISTA;
				$scope.permissao_delete_prisao = data.permissao_delete_prisao;
			});
		};

		$scope.sel = function(obj)
		{
			if(obj!=undefined) {
                obj.sel = true;
            }
		};

		$scope.unsel = function(obj)
		{
			if(obj!=undefined) {
                obj.sel = false;
            }
		};

		$scope.converter = function()
		{
			$http.post('/nucleo/nadep/prisao/converter/($0)/'.replace('($0)', $scope.prisao.id), $scope.prisao).success(function(data){
				if(data.success)
				{
					$('#modal-converter-pena').modal('hide');
					$scope.carregar();
				}
			});
		};

		$scope.btnConverter_click = function(obj)
		{
			$scope.prisao = obj;
			var horas = $scope.prisao.duracao_pena.anos * 365 + $scope.prisao.duracao_pena.meses * 30 + $scope.prisao.duracao_pena.dias;
			$scope.prisao.duracao_pena.horas = '(_0):00'.replace('(_0)', horas);
		};

		$scope.carregar();

		$scope.showModalExcluirPrisao = function()
		{
			$('#modal-excluir-prisao').modal();
		};

		$scope.btnExcluir_click = function(obj)
		{
			$scope.prisao = obj;
			$scope.modalExcluirPrisaoUrl = '/static/template/siap/modal_excluir_prisao.html';
		};

        $scope.excluir = function() {
            $http.post('/nucleo/nadep/prisao/excluir/($0)/'.replace('($0)', $scope.prisao.id), $scope.prisao).success(function (data) {
                if (data.success) {
                    $('#modal-excluir-prisao').modal('hide');
                    $scope.carregar();
                }
            });
        }
	}
]);

siapControllers.controller('GuiaTabCtrl', ['$scope', '$routeParams', '$http', '$location', 'Preso', 'Config',
	function($scope, $routeParams, $http, $location, Preso, Config){

		$scope.params = Preso;
		$scope.meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];

		$scope.$emit('selectTab', {tab:2});

		$http.get('/nucleo/nadep/preso/($0)/guia/get/?db=($1)'.replace('($0)', Preso.id).replace('($1)', $routeParams.data_base)).success(function(data){
            $scope.preso = data.preso;
			$scope.LISTA = data.LISTA;
		});

		$http.get('/nucleo/nadep/preso/($0)/calculo/get/?db=($1)'.replace('($0)', Preso.id).replace('($1)', $routeParams.data_base)).success(function(data){
            $scope.calculo = data;
		});

		$scope.carregar = function()
		{
			if($scope.params.dia)
			{
				$scope.params.data_base = $scope.params.dia.toISOString().slice(0,10).replace(/-/g,'');
				$location.path('/guias/($0)'.replace('($0)', $scope.params.data_base));
			}
		};

		$scope.carregar_hora = function(hora)
		{
			$scope.hora = hora;
		};

		$scope.carregar_horas = function(prisao)
		{
			$http.get('/nucleo/nadep/prisao/($0)/horas/get/'.replace('($0)', prisao)).success(function(data){
				$scope.horas = data;
				$scope.relatorio = null;
				$scope.ano_atual = data.data_consulta.substring(0, 4);
			});
		};

		$scope.salvar_horas = function(obj)
		{
			$http.post('/nucleo/nadep/prisao/($0)/horas/salvar/'.replace('($0)', obj.prisao), obj).success(function(data){
				if(data.success)
				{
					$('#modal-cadastrar-horas').modal('hide');
					$scope.carregar_horas(obj.prisao);
				}
			});
		};

		$scope.excluir_horas = function(obj)
		{
			$http.post('/nucleo/nadep/prisao/($0)/horas/excluir/'.replace('($0)', obj.prisao), obj).success(function(data){
				if(data.success)
				{
					$('#modal-excluir-horas').modal('hide');
					$scope.carregar_horas(obj.prisao);
				}
			});
		};

		$scope.btnLiquidar_click = function()
		{
			$scope.$broadcast('LiquidarPenaCtrl:novo', {prisao:$scope.calculo.execucao});
		};

		$scope.btnProgressao_click = function()
		{
			$scope.$broadcast('AlterarRegimeCtrl:novo', {tipo:0, prisao:$scope.calculo.execucao, 'regime_atual': $scope.calculo.regime_atual});
		};

		$scope.btnRegressao_click = function()
		{
			$scope.$broadcast('AlterarRegimeCtrl:novo', {tipo:1, prisao:$scope.calculo.execucao, 'regime_atual': $scope.calculo.regime_atual});
		};

		$scope.showModalAlterarRegime = function()
		{
			$('#modal-alterar-regime').modal();
		}

	}
]);

siapControllers.controller('FaltaTabCtrl', ['$scope', '$http', 'Preso',
	function($scope, $http, Preso){

		$scope.$emit('selectTab', {tab:3});

		$scope.$on('FaltaTabCtrl:carregar', function(event, args){
			$scope.carregar();
		});

		$scope.carregar = function()
		{
			delete $scope.falta;
			$http.get('/nucleo/nadep/preso/($0)/falta/get/'.replace('($0)', Preso.id)).success(function(data){
				$scope.faltas = data.faltas;
				$scope.LISTA = data.LISTA;
			});
		};

		$scope.$on('FaltaTabCtrl:carregar_falta', function(event, args){
			$scope.carregar_falta(args);
		});

		$scope.carregar_falta = function(falta)
		{

			$scope.falta = falta;
			delete $scope.falta.movimentos;

			if(falta.processo_numero){
				$http.get(`/processo/${falta.processo_numero}/fase/listar/?grau=${falta.processo_grau}`).success(function(data){
					$scope.falta.movimentos = data;
				});
			}

		};

		$scope.carregar();

		$scope.excluir = function()
		{
			$http.post('/nucleo/nadep/preso/($0)/falta/excluir/'.replace('($0)', Preso.id), $scope.falta).success(function(data){
				if(data.success)
				{
					$('#modal-excluir-falta').modal('hide');
					$scope.carregar();
				}
			});
		};

		$scope.excluir_movimento = function()
		{
			$http.post('/processo/fase/($0)/excluir/'.replace('($0)', $scope.movimento.id)).success(function(data){
				if(data.success)
				{
					$('#modal-excluir-fase-processo').modal('hide');
					$scope.carregar_falta($scope.falta);
				}
			});
		};

		$scope.btnExcluir_click = function(obj)
		{
			$scope.falta = obj;
			$scope.modalExcluirFaltaUrl = '/static/template/siap/modal_excluir_falta.html';
		};

		$scope.btnAlterar_click = function(obj)
		{
			$scope.$broadcast('CadastroFaltaCtrl:carregar', {falta:obj});
		};

		$scope.btnNovo_click = function()
		{
			$scope.$broadcast('CadastroFaltaCtrl:novo');
		};

		$scope.btnNovoMovimento_click = function()
		{
			$scope.$broadcast('CadastroMovimentoPADCtrl:novo', $scope.falta);
		};

		$scope.btnAlterarMovimento_click = function(obj)
		{
			$scope.$broadcast('CadastroMovimentoPADCtrl:carregar', obj);
		};

		$scope.btnExcluirMovimento_click = function(obj)
		{
			$scope.movimento = obj;
			$scope.modalExcluirMovimentoUrl = '/static/template/siap/modal_excluir_movimento_pad.html';
		};

		$scope.showModalExcluirFalta = function()
		{
			$('#modal-excluir-falta').modal();
		};

		$scope.showModalExcluirMovimento = function()
		{
			$('#modal-excluir-movimento-pad').modal();
		}

	}
]);

siapControllers.controller('RemissaoTabCtrl', ['$scope', '$http', 'Preso',
	function($scope, $http, Preso){

		$scope.$emit('selectTab', {tab:4});

		$scope.$on('RemissaoTabCtrl:carregar', function(event, args){
			$scope.carregar();
		});

		$scope.carregar = function()
		{
			$http.get('/nucleo/nadep/preso/($0)/remissao/get/'.replace('($0)', Preso.id)).success(function(data){
				$scope.remissoes = data.remissoes;
				$scope.total = data.total;
				$scope.LISTA = data.LISTA;
			});
		};

		$scope.carregar();

		$scope.excluir = function()
		{
			$http.post('/nucleo/nadep/preso/($0)/remissao/excluir/'.replace('($0)', Preso.id), $scope.remissao).success(function(data){
				if(data.success)
				{
					$('#modal-excluir-remissao').modal('hide');
					$scope.carregar();
				}
			});
		};

		$scope.calcular = function(remissao)
		{

			var str = $scope.LISTA.TIPO[remissao.tipo]; // texto para verificacao, formato: "texto (fracao)"
			var exp = /\(([^)]+)\)/; // expressao regular para extrair a fracao
			var mat = exp.exec(str);

			if(mat) {
                remissao.dias_remissao = Math.floor(remissao.dias_registro * eval(mat[1]) * 100) / 100;
            }
			else {
                remissao.dias_remissao = 0;
            }

		};

		$scope.btnExcluir_click = function(obj)
		{
			$scope.remissao = obj;
			$scope.modalExcluirRemissaoUrl = '/static/template/siap/modal_excluir_remissao.html';
		};

		$scope.btnAlterar_click = function(obj)
		{
			$scope.$broadcast('CadastroRemissaoCtrl:carregar', {remissao:obj});
		};

		$scope.btnNovo_click = function()
		{
			$scope.$broadcast('CadastroRemissaoCtrl:novo');
		};

		$scope.showModalExcluirRemissao = function()
		{
			$('#modal-excluir-remissao').modal();
		}

	}
]);

siapControllers.controller('ProcessoTabCtrl', ['$scope', '$http', 'Preso', 'Config',
	function($scope, $http, Preso, Config){

		$scope.$emit('selectTab', {tab:5});
        $scope.preso = null;
        $scope.config = Config;

		$http.get('/nucleo/nadep/preso/($0)/processo/get/'.replace('($0)', Preso.id)).success(function(data){
            $scope.preso = data.preso;
			$scope.LISTA = data.LISTA;
		});

	}
]);

siapControllers.controller('AprisionamentoTabCtrl', ['$scope', '$http', 'Preso',
	function($scope, $http, Preso){

		$scope.$emit('selectTab', {tab:6});

		$scope.$on('AprisionamentoTabCtrl:carregar', function(event, args){
			$scope.carregar();
		});

		$scope.carregar = function()
		{
			$http.get('/nucleo/nadep/preso/($0)/aprisionamento/get/'.replace('($0)', Preso.id)).success(function(data){
				$scope.aprisionamentos = data.aprisionamentos;
				$scope.total = data.total;
				$scope.total_detracao = data.total_detracao;
				$scope.LISTA = data.LISTA;
			});
		};

		$scope.carregar();

		$scope.excluir = function()
		{
			$http.post('/nucleo/nadep/preso/($0)/aprisionamento/excluir/'.replace('($0)', Preso.id), $scope.aprisionamento).success(function(data){
				if(data.success)
				{
					$('#modal-excluir-aprisionamento').modal('hide');
					$scope.carregar();
				}
			});
		};

		$scope.btnAlterar_click = function(obj)
		{
			$scope.$broadcast('CadastroTransferenciaCtrl:carregar', {pessoa:Preso.id, aprisionamento:obj});
		};


		$scope.btnExcluir_click = function(obj)
		{
			$scope.aprisionamento = obj;
			$scope.modalExcluirAprisionamentoUrl = '/static/template/siap/modal_excluir_aprisionamento.html';
		};

		$scope.showModalExcluirAprisionamento = function()
		{
			$('#modal-excluir-aprisionamento').modal();
		};

	}
]);

siapControllers.controller('InterrupcaoTabCtrl', ['$scope', '$http', 'Preso',
	function($scope, $http, Preso){

		$scope.$emit('selectTab', {tab:7});

		$scope.$on('InterrupcaoTabCtrl:carregar', function(event, args){
			$scope.carregar();
		});

		$scope.carregar = function()
		{
			$http.get('/nucleo/nadep/preso/($0)/interrupcao/get/'.replace('($0)', Preso.id)).success(function(data){
				$scope.interrupcoes = data.interrupcoes;
				$scope.total = data.total;
			});
		};

		$scope.carregar();

		$scope.excluir = function()
		{
			$http.post('/nucleo/nadep/preso/($0)/interrupcao/excluir/'.replace('($0)', Preso.id), $scope.interrupcao).success(function(data){
				if(data.success)
				{
					$('#modal-excluir-interrupcao').modal('hide');
					$scope.carregar();
				}
			});
		};

		$scope.btnAlterar_click = function(obj)
		{
			$scope.$broadcast('CadastroInterrupcaoCtrl:carregar', {interrupcao:obj});
		};

		$scope.btnExcluir_click = function(obj)
		{
			$scope.interrupcao = obj;
			$scope.modalExcluirInterrupcaoUrl = '/static/template/siap/modal_excluir_interrupcao.html';
		};

		$scope.btnNovo_click = function()
		{
			$scope.$broadcast('CadastroInterrupcaoCtrl:novo');
		};

		$scope.showModalExcluirInterrupcao = function()
		{
			$('#modal-excluir-interrupcao').modal();
		};

		$scope.getTotalDiasInterrupcao = function()
		{
			var total = 0;
			for(var i in $scope.interrupcoes) {
                total += $scope.interrupcoes[i].dias;
            }
			return total;
		}

	}
]);

siapControllers.controller('HistoricoTabCtrl', ['$scope', '$http', 'Preso',
	function($scope, $http, Preso){

		$scope.$emit('selectTab', {tab:8});

		$scope.carregar = function()
		{
			$http.get('/nucleo/nadep/preso/($0)/historico/'.replace('($0)', Preso.id)).success(function(data){
				for(var i = 0; i < data.historico.length; i++)
				{
					data.historico[i].class_color = $scope.get_color(data.historico[i]);
					data.historico[i].class_icon = $scope.get_icon(data.historico[i]);
				}
				$scope.historico = data.historico;
				$scope.LISTA = data.LISTA;
			});
		};

		$scope.get_color = function(evento)
		{
			switch(evento.evento)
			{
				case 1:
				case 5:
				case 6:
				case 7:
					return 'red';
				case 2:
				case 8:
					return 'green';
				case 11:
					return 'blue';
				default :
					return 'black';
			}
		};

		$scope.get_icon = function(evento)
		{
			return {
				1:'fas fa-lock',
				2:'fas fa-unlock',
				3:'fas fa-comments',
				4:'fas fa-comments',
				5:'fas fa-gavel',
				6:'fas fa-thumbs-down',
				7:'fas fa-undo',
				8:'fas fa-retweet',
				9:'fas fa-sync',
				10:'fas fa-truck',
                11:'fas fa-random',
                13:'fas fa-folder'
            }[evento.evento];
		};

		$scope.carregar();

	}
]);

siapControllers.controller('CadastroFaltaCtrl', ['$scope', '$http', '$filter', 'Preso',
	function($scope, $http, $filter, Preso)
	{

		$scope.lista_resultado = ['Aguardando Julgamento', 'Procedente', 'Improcedente'];
		$scope.falta = {pessoa:Preso.id, estabelecimento_penal:Preso.prisao.estabelecimento_penal};

		$http.get('/nucleo/nadep/estabelecimento/get/').success(function(data){
            $scope.lista_estabelecimentos = data;
		});

		$scope.$watch('data_fato', function() {
			set_data_fato();
		});

		$scope.$watch('hora_fato', function() {
			set_data_fato();
		});

		$scope.$on('CadastroFaltaCtrl:novo', function(event, args){
			$scope.novo();
		});

		$scope.$on('CadastroFaltaCtrl:carregar', function(event, args){
			$scope.falta = angular.copy(args.falta);
			$scope.falta.resultado = $scope.falta.resultado.toString();
			$scope.data_fato = $filter('date')($filter('utc')($scope.falta.data_fato), "ddMMyyyy");
			$scope.hora_fato = $filter('date')($filter('utc')($scope.falta.data_fato), "HHmm");
			set_data_fato();
		});

		$scope.recarregar_remissao = function()
		{
			$http.post('/nucleo/nadep/preso/($0)/remissao/total/get/'.replace('($0)', $scope.falta.pessoa), {'data_referencia': dataHoraFormatadaParaUTC($scope.falta.data_fato)}).success(function(data) {
				for(var item in data)
				{
					data[item].desconto = parseInt(data[item].total / 3);
					$scope.recalcular_remissao(data[item]);
				}
				$scope.falta.remissoes = data;
			});
		};

		$scope.recalcular_remissao = function(item)
		{
			item.restante = item.total - item.desconto;
		};

		$scope.novo = function()
		{
			$scope.falta = {pessoa:$scope.falta.pessoa, estabelecimento_penal:$scope.falta.estabelecimento_penal};
			$scope.data_fato = null;
			$scope.hora_fato = null;
		};

		$scope.salvar = function()
		{
			$http.post('/nucleo/nadep/preso/($0)/falta/salvar/'.replace('($0)', $scope.falta.pessoa), $scope.falta).success(function(data){
				if(data.success)
				{
					$('#modal-cadastrar-falta').modal('hide');
					$scope.$emit('FaltaTabCtrl:carregar');
				}
			});
		};

		function set_data_fato()
		{
			if($scope.data_fato && $scope.hora_fato)
			{
				$scope.falta.data_fato = getDataHoraFormatada($scope.data_fato + $scope.hora_fato);
				$scope.recarregar_remissao();
			}
		}

	}
]);

siapControllers.controller('CadastroRemissaoCtrl', ['$scope', '$http', '$filter', 'Preso',
	function($scope, $http, $filter, Preso)
	{

		$scope.remissao = {pessoa:Preso.id};

		$scope.$watch('data_inicial', function() {
			$scope.remissao.data_inicial = getDataFormatada($scope.data_inicial);
		});

		$scope.$watch('data_final', function() {
			$scope.remissao.data_final = getDataFormatada($scope.data_final);
		});

		$scope.$on('CadastroRemissaoCtrl:novo', function(event, args){
			$scope.novo();
		});

		$scope.$on('CadastroRemissaoCtrl:carregar', function(event, args){

			$scope.remissao = angular.copy(args.remissao);
			$scope.remissao.tipo = args.remissao.tipo.toString();
			$scope.remissao.para_progressao = args.remissao.para_progressao.toString();

			$scope.data_inicial = $filter('date')(args.remissao.data_inicial, "ddMMyyyy");
			$scope.data_final = $filter('date')(args.remissao.data_final, "ddMMyyyy");

		});

		$scope.novo = function()
		{
			$scope.remissao = {pessoa:$scope.remissao.pessoa};
			$scope.data_inicial = null;
			$scope.data_final = null;
		};

		$scope.salvar = function()
		{
			$http.post('/nucleo/nadep/preso/($0)/remissao/salvar/'.replace('($0)', $scope.remissao.pessoa), $scope.remissao).success(function(data){
				if(data.success)
				{
					$('#modal-cadastrar-remissao').modal('hide');
					$scope.$emit('RemissaoTabCtrl:carregar');
				}
			});
		}

	}
]);

siapControllers.controller('CadastroInterrupcaoCtrl', ['$scope', '$http', '$filter', 'Preso',
	function($scope, $http, $filter, Preso)
	{

		$scope.interrupcao = {pessoa:Preso.id};

		$scope.$watch('data_inicial', function() {
			$scope.interrupcao.data_inicial = getDataFormatada($scope.data_inicial);
		});

		$scope.$watch('data_final', function() {
			$scope.interrupcao.data_final = getDataFormatada($scope.data_final);
		});

		$scope.$on('CadastroInterrupcaoCtrl:novo', function(event, args){
			$scope.novo();
		});

		$scope.$on('CadastroInterrupcaoCtrl:carregar', function(event, args){
			$scope.interrupcao = jQuery.extend({}, args.interrupcao);
			if($scope.interrupcao.data_inicial) {
                $scope.data_inicial = $filter('date')($filter('utc')($scope.interrupcao.data_inicial), "ddMMyyyy");
            }
			if($scope.interrupcao.data_final) {
                $scope.data_final = $filter('date')($filter('utc')($scope.interrupcao.data_final), "ddMMyyyy");
            }
		});

		$scope.novo = function()
		{
			$scope.errors = null;
			$scope.interrupcao = {pessoa:$scope.interrupcao.pessoa};
		};

		$scope.salvar = function()
		{
			$http.post('/nucleo/nadep/preso/($0)/interrupcao/salvar/'.replace('($0)', $scope.interrupcao.pessoa), $scope.interrupcao).success(function(data){
				$scope.errors = data.errors;
				if(data.success)
				{
					$('#modal-cadastrar-interrupcao').modal('hide');
					$scope.$emit('InterrupcaoTabCtrl:carregar');
				}
			});
		}

	}
]);

siapControllers.controller('BuscarProcessoCtrl', ['$scope', '$http', '$filter', 'DefensorAPI',
	function($scope, $http, $filter, DefensorAPI)
	{

		$http.get('/area/listar/').success(function(data){
			$scope.areas = data;
		});

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensorAPI.get({incluir_atuacoes:false, ativo:true, limit:1000}, function(data){
			$scope.defensores = data.results;
		});

		$scope.carregar = function(numero, validar_inquerito)
		{
			if(!$scope.processo)
			{
				$scope.carregando = true;
				var url = '/procapi/processo/($0)/consultar/'.replace('($0)', numero.replace(/[^0-9]/g,''));
				$http.get(url).success(function(data){
					$scope.processo = data.processo;
                    $scope.carregando = false;
                    if(validar_inquerito)
                    {
                        $scope.validar_inquerito(data.processo);
                    }
				});
			}
		};

		$scope.carregar_defensorias = function(defensor_id)
		{

			$scope.defensorias = [];

			if(defensor_id!=undefined)
			{
				$http.get('/defensor/'+defensor_id+'/atuacoes/').success(function(data){
					for(var i = 0; i < data.length; i++) {
                        $scope.defensorias.push(data[i].defensoria);
                    }
				});
			}

		};

		$scope.carregar_vinculado = function(processo)
		{
			if(!processo.consultado)
			{
				processo.consultado = true;
				processo.carregando = true;
				var url = '/procapi/processo/($0)/consultar/'.replace('($0)', processo.numero.replace(/[^0-9]/g,''));
				$http.get(url).success(function(data){
					processo.resposta = {sucesso: data.sucesso, mensagem: data.mensagem};
					processo.processo = data.processo;
					processo.carregando = false;
					$scope.carregar_atendimentos(processo);
					$scope.processo.consultados = $filter('filter')($scope.processo.vinculados, {consultado:true}).length == $scope.processo.vinculados.length;
					if(processo.processo.classe.acao_penal)
					{
						$scope.processo.acao_penal = processo;
					}
				});
			}
		};

		$scope.carregar_atendimentos = function(processo)
		{
			$http.get(`/processo/${processo.numero}/get/json/?grau=${processo.grau||''}`).success(function(data){
				if(data.processo) {
                    processo.atendimentos = data.processo.partes;
                }
			});
		};

		$scope.salvar_processo = function(execucao)
		{

			var params = {};
			for(var key in execucao) {
                params[key] = execucao[key] != null && typeof execucao[key] === 'object' ? execucao[key].id : execucao[key];
            }

			$http.post('/processo/salvar/', params).success(function(data) {
				if($scope.processo.classe.inquerito)
				{
					window.location = '?processo={0}&parte={1}&inquerito={2}'.replace('{0}', params.numero).replace('{1}', data.parte).replace('{2}', $scope.processo.numero);
				}
				else
				{
					$scope.execucao.parte_id = data.parte;
					$scope.execucao.processo_id = data.processo;
				}
			});

		};

		$scope.selecionar_parte = function(parte)
		{
			if($scope.processo.classe.inquerito)
			{
				window.location = '?processo={0}&parte={1}&inquerito={2}'.replace('{0}', $scope.execucao.numero).replace('{1}', parte.id).replace('{2}', $scope.processo.numero);
			}
			else
			{
				$scope.execucao.parte_id = parte.id;
				$scope.execucao.processo_id = parte.processo;
			}
		};

		$scope.validar_inquerito = function(processo)
		{
			if(processo.classe.inquerito && processo.vinculados.length)
			{
				$('#modal-vincular-acao-penal').modal('show');
				for(var i = 0; i < processo.vinculados.length; i++)
				{
					$scope.carregar_vinculado(processo.vinculados[i]);
				}
            }
        }

	}
]);

siapControllers.controller('ConverterPenaCtrl', ['$scope', '$http', '$filter', 'Preso',
	function($scope, $http, $filter, Preso)
	{

	}
]);

siapControllers.controller('AlterarRegimeCtrl', ['$scope', '$http', '$filter', '$location', 'Preso',
	function($scope, $http, $filter, $location, Preso)
	{

		$scope.LISTA = {REGIME:{0:'Fechado', 1:'Semiaberto', 2:'Aberto'}};

		$scope.$watch('data_registro', function() {
			if($scope.data_registro) {
                $scope.regime.data_registro = getDataFormatada($scope.data_registro);
            }
		});

		$scope.$watch('data_base', function() {
			if($scope.data_base) {
                $scope.regime.data_base = getDataFormatada($scope.data_base);
            }
		});

		$scope.$on('AlterarRegimeCtrl:novo', function(event, args){

			$scope.regime = args;
			$scope.regime.regime = ($scope.regime.regime_atual + ($scope.regime.tipo ? -1: 1)).toString();
			$scope.set_estabelecimento_penal();

		});

		$scope.set_estabelecimento_penal = function()
		{
			if($scope.estabelecimentos && $scope.regime)
			{
				for(var i = 0; i < $scope.estabelecimentos.length; i++)
				{
					if($scope.estabelecimentos[i].id==$scope.regime.prisao.estabelecimento_penal)
					{
						$scope.regime.estabelecimento_penal = $scope.estabelecimentos[i];
					}
				}
			}
		};

		$scope.salvar = function()
		{
			$scope.errors = null;
			$scope.salvando = true;

			$http.post('/nucleo/nadep/prisao/($0)/regime/alterar/'.replace('($0)', $scope.regime.prisao.id), $scope.regime).success(function(data){
				if(data.success)
				{
					$('#modal-alterar-regime').modal('hide');
					$location.path('/guias/($0)'.replace('($0)', explode($scope.data_base, [[4,4],[2,2],[0,2]]).join('')));
					location.reload();
				}else{
					$scope.errors = data.errors;
				}
				$scope.salvando = false;
			});
		};

		$http.get('/nucleo/nadep/estabelecimento/get/').success(function(data){
            $scope.estabelecimentos = data;
			$scope.set_estabelecimento_penal();
		});

	}
]);

siapControllers.controller('LiquidarPenaCtrl', ['$scope', '$http', '$filter', '$location', 'Preso',
	function($scope, $http, $filter, $location, Preso)
	{

		$scope.$watch('data_liquidacao', function() {
			if($scope.data_liquidacao) {
                $scope.regime.data_liquidacao = getDataFormatada($scope.data_liquidacao);
            }
		});

		$scope.$on('LiquidarPenaCtrl:novo', function(event, args){
			$scope.regime = args;
		});

		$scope.salvar = function()
		{
			$scope.errors = null;
			$scope.salvando = true;

			$http.post('/nucleo/nadep/prisao/($0)/regime/liquidar/'.replace('($0)', $scope.regime.prisao.id), $scope.regime).success(function(data){
				if(data.success)
				{
					$('#modal-liquidar-pena').modal('hide');
					$location.path('/prisoes');
					location.reload();
				}else{
					$scope.errors = data.errors;
				}
				$scope.salvando = false;
			});
		};

	}
]);

siapControllers.controller('CadastroTransferenciaCtrl', ['$scope', '$http', '$filter', 'Preso', 'DefensoriaAPI',
	function($scope, $http, $filter, Preso, DefensoriaAPI) {

		$scope.$watch('data_inicial', function() {
			$scope.aprisionamento.data_inicial = getDataFormatada($scope.data_inicial);
		});

		$scope.$watch('data_final', function() {
			$scope.aprisionamento.data_final = getDataFormatada($scope.data_final);
		});

		$scope.$watch('prisao', function() {
            $scope.aprisionamento.prisao = null;
            if(typeof($scope.prisao)==="object")
            {
                $scope.aprisionamento.prisao = $scope.prisao.id;
            }
		});

		$scope.$watch('estabelecimento_penal', function() {
            $scope.aprisionamento.estabelecimento_penal = null;
            if(typeof($scope.estabelecimento_penal)==="object")
            {
                $scope.aprisionamento.estabelecimento_penal = $scope.estabelecimento_penal.id;
            }
        });

		$scope.$watch('defensoria', function() {
            $scope.defensores = null;
            $scope.aprisionamento.defensoria = null;
            if(typeof($scope.defensoria)==="object")
            {
                $scope.aprisionamento.defensoria = $scope.defensoria.id;
                $http.get('/defensoria/' + $scope.aprisionamento.defensoria + '/get/').success(function (data) {
                    $scope.defensores = data.defensores;
                });
            }
        });

		$scope.$on('CadastroTransferenciaCtrl:carregar', function(event, args){

			$scope.aprisionamento = {
				id: args.aprisionamento.id,
				pessoa: args.pessoa,
				historico: args.aprisionamento.historico,
				municipio: args.aprisionamento.estabelecimento_penal.municipio,
				estabelecimento_penal: args.aprisionamento.estabelecimento_penal.id
            };

			$scope.data_inicial = $filter('date')($filter('utc')(args.aprisionamento.data_inicial), "ddMMyyyy");
			$scope.data_final = $filter('date')($filter('utc')(args.aprisionamento.data_final), "ddMMyyyy");

			$scope.carregar_estabelecimentos();

			for(var i = 0; i < $scope.prisoes.length; i++)
			{
				if($scope.prisoes[i].id==args.aprisionamento.prisao.id) {
                    $scope.prisao = $scope.prisoes[i];
                }
            }
        });

		$scope.carregar_prisoes = function () {
			$scope.prisoes = null;
			$http.get('/nucleo/nadep/pessoa/' + $scope.aprisionamento.pessoa + '/prisao/get/').success(function (data) {
				$scope.prisoes = data;
			});
		};

		$scope.carregar_estabelecimentos = function () {
			$http.get('/nucleo/nadep/estabelecimento/get/').success(function (data) {
				$scope.estabelecimentos = data;
			});
        };

        $scope.carregar_defensorias = function () {
			// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
			DefensoriaAPI.get({limit:1000}, function(data){
				$scope.defensorias = data.results;
			});
        };

		$scope.salvar = function() {
			$http.post('/nucleo/nadep/preso/($0)/aprisionamento/salvar/'.replace('($0)', $scope.aprisionamento.pessoa), $scope.aprisionamento).success(function(data){
				if(data.success)
				{
					$('#modal-cadastrar-aprisionamento').modal('hide');
					$scope.$emit('AprisionamentoTabCtrl:carregar');
				}
				$scope.errors = data.errors;
			});
		};

		$scope.transferir = function() {
			$http.post('/nucleo/nadep/preso/($0)/transferir/'.replace('($0)', $scope.aprisionamento.pessoa), $scope.aprisionamento).success(function(data){
				if(data.success)
				{
					location.reload();
				}
				else
				{
					$scope.errors = data.errors;
				}
			});
		};

		$scope.init = function (pessoa_id) {
			$scope.aprisionamento = {pessoa: pessoa_id};
			$scope.carregar_prisoes();
            $scope.carregar_estabelecimentos();
            $scope.carregar_defensorias();
		};

		$scope.init(Preso.id);

	}
]);

siapControllers.controller('CadastroSolturaCtrl', ['$scope', '$http', 'Preso',
	function($scope, $http, Preso) {

		$scope.LISTA = {
			TIPO:{
				1:'Dec. Juíz do Ato Conversão em Flagrante',
				2:'Habeas Corpus',
				3:'Liberdade Provisória',
				4:'Pagamento de Fiança',
				5:'Revogação de Prisão Preventiva',
				6:'Sentença Absolutória',
				7:'Relaxamento de Prisão'
			}
		};

		$scope.$watch('data_inicial', function() {
			$scope.aprisionamento.data_inicial = getDataFormatada($scope.data_inicial);
		});

		$scope.$watch('data_final', function() {
			$scope.aprisionamento.data_final = getDataFormatada($scope.data_final);
		});

		$scope.$watch('prisao', function() {
			if($scope.prisao) {
                $scope.aprisionamento.prisao = $scope.prisao.id;
            }
		});

		$scope.carregar_prisoes = function () {
			$scope.prisoes = null;
			$http.get('/nucleo/nadep/pessoa/' + $scope.aprisionamento.pessoa + '/prisao/get/').success(function (data) {
				$scope.prisoes = data;
			});
		};

		$scope.registrar = function() {
			$http.post('/nucleo/nadep/preso/($0)/soltar/'.replace('($0)', $scope.aprisionamento.pessoa), $scope.aprisionamento).success(function(data){
				if(data.success)
				{

					$('#modal-registrar-soltura').modal('hide');

					if($scope.regressao) {
                        $scope.$emit('VerPessoaCtrl:showModalAlterarRegime');
                    }
					else {
                        location.reload();
                    }

				}
				else
				{
					$scope.errors = data.errors;
				}
			});
		};

		$scope.$emit('FaltaTabCtrl:carregar');

		$scope.init = function (pessoa_id) {
			$scope.aprisionamento = {pessoa: pessoa_id};
			$scope.carregar_prisoes();
		};

		$scope.init(Preso.id);

	}
]);

siapControllers.controller('CadastroMovimentoPADCtrl', ['$scope', '$http', '$filter', 'DefensorAPI',
	function($scope, $http, $filter, DefensorAPI)
	{

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensorAPI.get({incluir_atuacoes:false, ativo:true, limit:1000}, function(data){
			$scope.defensores = data.results;
		});

        $http.get('/processo/fase/tipo/listar/').success(function(data){
            $scope.tipos = data;
        });

		$scope.$watch('defensor', function() {
			if($scope.movimento && $scope.defensor) {
                $scope.movimento.defensor_cadastro = $scope.defensor.id;
            }
		});

		$scope.$watch('tipo', function() {
			if($scope.movimento && $scope.tipo) {
                $scope.movimento.tipo = $scope.tipo.id;
            }
		});

		$scope.$watch('data_protocolo', function() {
			set_data_protocolo();
		});

		$scope.$watch('hora_protocolo', function() {
			set_data_protocolo();
		});

		$scope.$on('CadastroMovimentoPADCtrl:novo', function(event, args){
			$scope.falta = args;
			$scope.novo($scope.falta.processo_id);
		});

		$scope.novo = function(processo)
		{
			$scope.defensor = null;
			$scope.tipo = null;
			$scope.data_protocolo = null;
			$scope.hora_protocolo = null;
			$scope.movimento = {processo:processo};
		};

		$scope.$on('CadastroMovimentoPADCtrl:carregar', function(event, args){
			$scope.movimento = angular.copy(args);
			$scope.movimento.defensor_cadastro = $scope.movimento.defensor_cadastro.id;
			$scope.movimento.tipo = $scope.movimento.tipo.id;
			$scope.defensor = get_object_by_id($scope.defensores, $scope.movimento.defensor_cadastro);
			$scope.tipo = get_object_by_id($scope.tipos, $scope.movimento.tipo);
			$scope.data_protocolo = $filter('date')($filter('utc')($scope.movimento.data_protocolo), "ddMMyyyy");
			$scope.hora_protocolo = $filter('date')($filter('utc')($scope.movimento.data_protocolo), "HHmm");
			set_data_protocolo();
		});

		$scope.salvar = function()
		{
            $scope.errors = null;
			$http.post('/processo/fase/salvar/', $scope.movimento).success(function(data){
				if(data.success)
				{
					$('#modal-cadastrar-movimento-pad').modal('hide');
					$scope.$emit('FaltaTabCtrl:carregar_falta', $scope.falta);
				}
				else
                {
                    $scope.errors = data.errors;

                }
			});
		};

		function set_data_protocolo()
		{
			if($scope.data_protocolo && $scope.hora_protocolo) {
                $scope.movimento.data_protocolo = getDataHoraFormatada($scope.data_protocolo + $scope.hora_protocolo);
            }
		}

	}
]);

function NadepCtrl($scope, $http, $filter)
{

}

function PrisaoCtrl($scope, $http, $filter, DefensorAPI, DefensoriaAPI)
{

	$scope.fases = [];
	$scope.visitas = [];
	$scope.defensores = [];
	$scope.defensorias = [];

	/* ATENDIMENTOS */

	$scope.novo_atendimento = function()
	{
		$scope.atendimento = {pessoa:{telefones:[]}};
		$scope.init_telefone();
	};

	$scope.listar_atendimentos = function()
	{
		$scope.atendimentos = [];
		$http.post('atendimento/listar/').success(function(data){
            $scope.atendimentos = data;
		});
	};

	$scope.salvar_atendimento = function()
	{

		$scope.processar_telefone($scope.atendimento.pessoa.telefones); // telefone > ddd, numero

		$http.post('atendimento/salvar/',$scope.atendimento).success(function(data){
            if(data.success)
            {
                $('#modal-cadastrar-atendimento').modal('hide');
                $scope.listar_atendimentos();
            }
		});
	};

	$scope.ver_atendimento = function(atendimento)
	{
		$scope.atendimento = atendimento;
	};

	$scope.buscar_cpf = function()
	{
		if($scope.atendimento.pessoa.cpf)
		{
			$http.post('/assistido/cpf/'+$scope.atendimento.pessoa.cpf+'/json/get/').success(function(data){
				$scope.atendimento.pessoa = data;
				$scope.init_telefone();
				$scope.listar_municipios();
			});
		}
	};

	$scope.listar_municipios = function()
	{
		if($scope.atendimento.pessoa.estado==undefined) {
            $scope.atendimento.pessoa.estado = 17;
        }

		$http.get('/estado/' + $scope.atendimento.pessoa.estado + '/municipios/').success(function(data){
			$scope.municipios = data;
		});
	};

	// TELEFONE
	$scope.init_telefone = function()
	{

		if($scope.atendimento.pessoa.telefones == undefined) {
            $scope.atendimento.pessoa.telefones = [];
        }

		while($scope.atendimento.pessoa.telefones.length < 1) {
            $scope.adicionar_telefone();
        }

		$scope.processar_telefone($scope.atendimento.pessoa.telefones); // telefone < ddd, numero

	};

	$scope.adicionar_telefone = function()
	{
		$scope.atendimento.pessoa.telefones.push({id: null, ddd: null, numero: null, telefone: null, tipo: 0});
	};

	$scope.processar_telefone = function(telefones)
	{
		for(var i = 0; i < telefones.length; i++)
		{
			if(telefones[i].telefone)
			{
				var telefone = telefones[i].telefone.replace(/\D/g,'');
				telefones[i].ddd = telefone.substring(0,2);
				telefones[i].numero = telefone.substring(2);
			}
			else
			{
				telefones[i].telefone = telefones[i].ddd + telefones[i].numero;
			}
		}
	};

	/* VISITAS */

	$scope.nova_visita = function()
	{
		$scope.visita = {data_atendimento:new Date()};
	};

	$scope.ver_visita = function(visita)
	{
		$scope.visita = visita;
	};

	$scope.listar_visitas = function()
	{
		$scope.visitas = [];
		$http.post('visita/listar/').success(function(data){
            $scope.visitas = data;
		});
	};

	$scope.salvar_visita = function()
	{
		$http.post('visita/salvar/',$scope.visita).success(function(data){
            if(data.success)
            {
                $('#modal-cadastrar-visita').modal('hide');
                $scope.listar_visitas();
            }
		});
	};

	$scope.set_data_atendimento = function()
	{
		$scope.visita.data_atendimento = $filter('date')($filter('utc')($scope.visita.dia_atendimento), "dd/MM/yyyy") + ' ' + $scope.visita.hora_atendimento;
	};

	/* FASES PROCESSUAIS */

	$scope.nova_fase = function()
	{
		$scope.fase = {data_protocolo:new Date(), audiencia_realizada:0, audiencia_status: 0};
	};

	$scope.fase_carregar = function(fase_id)
	{
		$http.get('/processo/fase/'+fase_id+'/get/json/').success(function(data){

			$scope.fase = data.fase;
			$scope.fase.hora_protocolo = $filter('date')($filter('utc')($scope.fase.data_protocolo), "HH:mm");

			for(var i = 0; i < $scope.defensores.length; i++)
			{
				if($scope.defensores[i].id==$scope.fase.defensor_cadastro) {
                    $scope.fase.defensor = $scope.defensores[i];
                }
			}

			for(var i = 0; i < $scope.fases.length; i++)
			{
				if($scope.fases[i].id==$scope.fase.tipo) {
                    $scope.fase.tipo = $scope.fases[i];
                }
			}

		});
	};

	$scope.set_data_protocolo = function()
	{
		$scope.fase.data_hora_protocolo = $filter('date')($filter('utc')($scope.fase.data_protocolo), "dd/MM/yyyy") + ' ' + $scope.fase.hora_protocolo;
	};

	function init()
	{

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensorAPI.get({incluir_atuacoes:false, ativo:true, limit:1000}, function(data){
			$scope.defensores = data.results;
		});

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensoriaAPI.get({limit:1000}, function(data){
			$scope.defensorias = data.results;
		});

		$http.get('/processo/fase/tipo/listar/').success(function(data){
			$scope.fases = data;
		});

		$http.get('/estado/listar/').success(function(data){
			$scope.estados = data;
		});

		$scope.listar_visitas();
		$scope.listar_atendimentos();

	}

	init();

}

function FaltaCtrl($scope, $http)
{
	$scope.init = function(pessoa_id)
	{
		$scope.pessoa = pessoa_id;
		$scope.listar();
	};

	$scope.listar = function()
	{
		$http.get('/nucleo/nadep/preso/'+$scope.pessoa+'/falta/listar/').success(function(data){
            $scope.faltas = data;
		});
	}
}

function BuscarAtendimentoCtrl($scope, $http, DefensorAPI, DefensoriaAPI)
{

	$scope.filtro = {ultima:true, total:0};
	$scope.assistidos ={};

	$scope.$watch('defensor', function() {
		if($scope.defensor) {
            $scope.filtro.defensor = $scope.defensor.id;
        }
		else {
            $scope.filtro.defensor = null;
        }
		$scope.validar();
	});

	$scope.$watch('defensoria', function() {
		if($scope.defensoria) {
            $scope.filtro.defensoria = $scope.defensoria.id;
        }
		else {
            $scope.filtro.defensoria = null;
        }
		$scope.validar();
	});

	$scope.init = function(filtro)
	{

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensorAPI.get({incluir_atuacoes:false, ativo:true, limit:1000}, function(data){
			$scope.defensores = data.results;
			$scope.defensor = get_object_by_id($scope.defensores, filtro.defensor);
		});

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensoriaAPI.get({limit:1000}, function(data){
			$scope.defensorias = data.results;
			$scope.defensoria = get_object_by_id($scope.defensorias, filtro.defensoria);
		});

		for(var key in filtro) {
            $scope.filtro[key] = filtro[key];
        }

		$scope.validar();
		$scope.buscar(0);

	};

	$scope.validar = function () {
		var filtro = $scope.filtro;
		var data_ini = (filtro.data_ini != undefined && filtro.data_ini.length > 0);
		var data_fim = (filtro.data_fim != undefined && filtro.data_fim.length > 0);
		var datas = (data_ini && data_fim) || (!data_ini && !data_fim);
		$scope.valido = datas && (data_ini || data_fim || filtro.defensor || filtro.defensoria || filtro.filtro) && (!$scope.defensor || $scope.defensor.id) && (!$scope.defensoria || $scope.defensoria.id);
	};

	$scope.informacoes = function(atendimento)
	{
		if(!$scope.atendimento || $scope.atendimento.numero!=atendimento)
		{
			$scope.atendimento = null;
			$http.get('/atendimento/'+atendimento+'/json/get/').success(function(data){
				$scope.atendimento = data;
			});
		}
	};

	$scope.buscar = function(pagina, recarregar) {

		$scope.filtro.pagina = (pagina==undefined ? 0 : pagina);
		$scope.carregando = true;

		if(pagina==0 && recarregar)
        {
            var url = gerar_url($scope.filtro, ['comarca', 'defensoria', 'defensor', 'data_ini', 'data_fim', 'filtro']);
            window.location.assign(url);
        }

		$http.post('/nucleo/nadep/prisao/atendimento/buscar/', $scope.filtro).success(function (data) {

			$scope.LISTA = data.LISTA;
			$scope.filtro.ultima = data.ultima;
			$scope.filtro.paginas = data.paginas;

			for(var i = 0; i < data.atendimentos.length; i++) {
                $scope.perm_recepcao(data.atendimentos[i], data.usuario);
            }

			if(data.atendimentos.length && !data.ultima) {
                data.atendimentos[data.atendimentos.length - 1].ultimo = true;
            }

			if(data.pagina==0)
			{
				$scope.atendimentos = data.atendimentos;
				$scope.filtro.total = data.total;
			}
			else
			{
				for(var i = 0; i < data.atendimentos.length; i++) {
                    $scope.atendimentos.push(data.atendimentos[i]);
                }
			}

			$scope.carregando = false;

		});
	};

	$scope.perm_recepcao = function(atendimento, usuario)
	{
        atendimento.perm_recepcao = usuario.perms.atendimento_view_recepcao && usuario.comarca == atendimento.defensoria__comarca && !atendimento.data_atendimento;
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

	$scope.validar();

}

function BuscarPrisaoCtrl($scope, $http, DefensorAPI, DefensoriaAPI)
{

	$scope.filtro = {ultima:true, total:0};
	$scope.assistidos ={};

	$scope.$watch('comarca', function() {

		$scope.filtro.comarca = null;

		if($scope.comarca) {
            $scope.filtro.comarca = $scope.comarca.id;
        }

		$scope.validar();

	});

	$scope.$watch('defensoria', function() {

		$scope.filtro.defensoria = null;

		if($scope.comarca) {
            $scope.filtro.defensoria = $scope.defensoria.id;
        }

		$scope.validar();

	});

	$scope.$watch('defensor', function() {

		$scope.filtro.defensor = null;

		if($scope.defensor) {
            $scope.filtro.defensor = $scope.defensor.id;
        }

		$scope.validar();

	});

	$scope.init = function(filtro)
	{

		$http.get('/comarca/listar/').success(function (data) {
			$scope.comarcas = data;
			$scope.comarca = get_object_by_id($scope.comarcas, filtro.comarca)
		});

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensorAPI.get({incluir_atuacoes:false, ativo:true, limit:1000}, function(data){
			$scope.defensores = data.results;
			$scope.defensor = get_object_by_id($scope.defensores, filtro.defensor);
		});

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensoriaAPI.get({limit:1000}, function(data){
			$scope.defensorias = data.results;
			$scope.defensoria = get_object_by_id($scope.defensorias, filtro.defensoria);
		});

		for(var key in filtro) {
            $scope.filtro[key] = filtro[key];
        }

		$scope.validar();
		$scope.buscar(0);

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

	$scope.validar = function () {
		var filtro = $scope.filtro;
		$scope.valido = (filtro.data_ini || filtro.data_fim || filtro.comarca || filtro.defensoria || filtro.defensor || filtro.filtro);
	};

	$scope.buscar = function(pagina) {

		$scope.filtro.pagina = (pagina==undefined ? 0 : pagina);
		$scope.carregando = true;

		if(pagina==0) {
            $scope.registros = [];
        }

		$http.post('/nucleo/nadep/prisao/buscar/', $scope.filtro).success(function (data) {

			$scope.LISTA = data.LISTA;
			$scope.filtro.ultima = data.ultima;
			$scope.filtro.paginas = data.paginas;

			if(data.registros.length && !data.ultima) {
                data.registros[data.registros.length - 1].ultimo = true;
            }

			if(data.pagina==0)
			{
				$scope.registros = data.registros;
				$scope.filtro.total = data.total;
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

	$scope.validar();

}

function BuscarPresoCtrl($scope, $http, DefensorAPI, DefensoriaAPI)
{

	$scope.filtro = {ultima:true, total:0};
	$scope.assistidos ={};

	$scope.$on('BuscarPresoCtrl:salvar_visita', function(event, args){
		args.data_atendimento = dataHoraFormatadaParaUTC(args.data_atendimento);
		$scope.registro.visita = args;
	});

	$scope.$watch('comarca', function() {

		$scope.filtro.comarca = null;

		if($scope.comarca) {
            $scope.filtro.comarca = $scope.comarca.id;
        }

		$scope.validar();

	});

	$scope.$watch('defensoria', function() {

		$scope.filtro.defensoria = null;

		if($scope.defensoria) {
            $scope.filtro.defensoria = $scope.defensoria.id;
        }

		$scope.validar();

	});

	$scope.$watch('defensor', function() {

		$scope.filtro.defensor = null;

		if($scope.defensor) {
            $scope.filtro.defensor = $scope.defensor.id;
        }

		$scope.validar();

	});

	$scope.init = function(filtro)
	{

		$http.get('/api/v1/comarcas/?limit=1000&ativo=true').success(function (data) {
			$scope.comarcas = data.results;
			$scope.comarca = get_object_by_id($scope.comarcas, filtro.comarca);
		});

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensorAPI.get({incluir_atuacoes:false, ativo:true, limit:1000}, function(data){
			$scope.defensores = data.results;
			$scope.defensor = get_object_by_id($scope.defensores, filtro.defensor);
		});

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensoriaAPI.get({limit:1000}, function(data){
			$scope.defensorias = data.results;
			$scope.defensoria = get_object_by_id($scope.defensorias, filtro.defensoria);
		});

		for(var key in filtro) {
            $scope.filtro[key] = filtro[key];
        }

		$scope.validar();
		$scope.buscar(0);

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

	$scope.validar = function () {
		var filtro = $scope.filtro;
		$scope.valido = (filtro.data_ini || filtro.data_fim || filtro.comarca || filtro.defensoria || filtro.defensor || filtro.filtro);
	};

	$scope.buscar = function(pagina, recarregar) {

		$scope.filtro.pagina = (pagina==undefined ? 0 : pagina);
		$scope.carregando = true;

		if(pagina==0 && recarregar)
        {
            var url = gerar_url($scope.filtro, ['comarca', 'defensor', 'defensoria', 'data_ini', 'data_fim', 'filtro']);
            window.location.assign(url);
        }

		$http.post('/nucleo/nadep/preso/buscar/', $scope.filtro).success(function (data) {

			$scope.LISTA = data.LISTA;
			$scope.filtro.ultima = data.ultima;
			$scope.filtro.paginas = data.paginas;

			if(data.registros.length && !data.ultima) {
                data.registros[data.registros.length - 1].ultimo = true;
            }

			if(data.pagina==0)
			{
				$scope.registros = data.registros;
				$scope.filtro.total = data.total;
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

	$scope.salvar_anotacao = function()
	{

        $scope.anotacao.message = null;
        $scope.anotacao.salvando = true;

        var url = '/atendimento/($0)/anotacao/nova/'.replace('($0)', $scope.registro.parte__atendimento__numero);

		$http.post(
            url,
            getFormData($scope.anotacao),
            {
			    transformRequest: angular.identity,
                headers: {'Content-Type': undefined}
            }
        ).success(function (data) {
            $scope.anotacao.salvando = false;
            if(data.success){
                $scope.registro.anotacao = data.anotacao;
                $('#modal-anotacao').modal('hide');
                show_stack_success(data.message);
            }
            else{
                show_stack_error(data.message);
            }
		});
	};

	$scope.nova_anotacao = function(obj)
	{

		$scope.registro = obj;
        $scope.anotacao = {};
        $scope.listar_qualificacoes();

    };

	$scope.listar_qualificacoes = function()
	{
		$http.post('/atendimento/qualificacao/listar/', {tipo:30}).success(function(data) {
			$scope.qualificacoes = data.qualificacoes;
		});
	};

	$scope.nova_visita = function(obj)
	{
		$scope.registro = obj;
		$scope.$broadcast('VisitaCtrl:init', {
			emit:'BuscarPresoCtrl:salvar_visita',
			atendimento:obj.parte__atendimento__id,
			atendimento_inicial:obj.parte__atendimento__id,
			hoje:null,
			pre_cadastro:{
				prisao: obj.id,
				estabelecimento_penal:obj.estabelecimento_penal__id,
				defensor:$scope.filtro.defensor,
				defensoria:null,
				qualificacao:null
			}});
	};

	$scope.validar();

}
