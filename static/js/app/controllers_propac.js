function PropacsDefaultCtrl($scope, $http, $filter)
{

    $scope.defensores = [];

    $scope.listar_defensores = function(defensoria_id)
    {
        $http.get('/defensoria/'+defensoria_id+'/get/').success(function(data){
            $scope.defensores = data.defensores;
        });
    }

}

function PropacsCtrl($scope, $http, $filter)
{
     $scope.$watch('procedimento.acesso', function(novo, velho) {
         if(novo == 20 && !$scope.defensorias){
             $scope.listar_defensorias();
         }
     });

     $scope.listar_defensorias = function() {
         if (!$scope.defensorias) {
             $scope.carregando_defensorias_acesso = true;

             $http.get('/defensoria/listar/').success(function (data) {
                $scope.defensorias = data;

                $scope.preencher_defensorias_acesso();
                $scope.carregando_defensorias_acesso = false;
             });
         }
     };

     $scope.preencher_defensorias_acesso = function(){
         for (var i = 0; i < $scope.defensorias.length; i++) {
            for (var j = 0; j < $scope.defensorias_acesso_ids.length; j++) {
                if ($scope.defensorias[i].id == $scope.defensorias_acesso_ids[j]) {
                    $scope.defensorias_acesso.push($scope.defensorias[i]);
                }
            }
        }
     };

    $scope.defensores = {};
    $scope.defensoria_responsavel = null;
    $scope.defensor_responsavel = null;
    $scope.defensorias_acesso_ids = [];

    $scope.participantes = [];
    $scope.participante = null;

    $scope.listar_defensores = function(defensoria_id)
    {
        $http.get('/defensoria/'+defensoria_id+'/get/').success(function(data){
            $scope.defensores = {};
            var d = data.defensores;
            for (var i=0; i< d.length; i++) {
                if (d[i].eh_defensor === true){
                    $scope.defensores[d[i].id] = {'id': d[i].id, 'nome': d[i].nome};
                }
            }
        });
    };

    $scope.adicionar_participante = function(participante)
    {
        if(participante) {
            $scope.defensorias_acesso.push(participante);
            $scope.participante = null;
        }
    };

    $scope.remover_participante = function(participante)
    {
        $scope.defensorias_acesso.remove(participante);
    };

    $scope.init = function(params)
    {
        $scope.carregando_defensorias_acesso = true;
        $scope.procedimento = params;
        $scope.defensorias = null;

        $scope.defensorias_acesso = [];
        $scope.defensorias_acesso_ids = params['defensorias_acesso_ids'];
        $scope.defensoria_responsavel = params['defensoria_responsavel'];
        $scope.listar_defensores($scope.defensoria_responsavel);
        $scope.defensor_responsavel = params['defensor_responsavel'];
        $scope.carregando_defensorias_acesso = false;
    }

}

function PropacsBuscarCtrl($scope, $http, $filter)
{

    $scope.procedimento = {};

    $scope.listar_propacs_procedimentos = function(defensorias_acesso)
	{
		if (defensorias_acesso!=undefined){
			$scope.procedimento.defensorias_acesso_ids = defensorias_acesso;
		}

		$scope.procedimento.exclusao_resultado = null;
		$scope.procedimentos = null;
		$http.post('atender/procedimentos/propacs/get/').success(function(data){
			$scope.procedimentos = data;
		});
	};

	$scope.buscar_procedimento = function(atendimento_numero) {
		$scope.procedimentos_busca = null;
		$scope.procedimento.selecionado = null;
		$scope.procedimento.resultado = null;
		$scope.procedimento.buscando = true;
		dados = {'filtro': $scope.procedimento.filtro, 'atendimento': atendimento_numero, 'acesso': $scope.procedimento.defensorias_acesso_ids};
		$http.post('/nucleo/procedimento/propacs/buscar/', dados ).success(function(data){
			window.setTimeout(function() {
			$scope.$apply(function() {
					$scope.procedimentos_busca = data['procedimentos'];
					$scope.procedimento.buscando = null
				});
			}, 500);
		});
	};

	$scope.buscar_procedimento_key = function(e , atendimento_numero)
    {
        if(!(typeof atendimento_numero !== typeof atendimento_numero && disabled !== false)){
                atendimento_numero=null;
          }
		$scope.procedimento.selecionado = null;
		$scope.procedimento.resultado = null;
        // Busca automatico se enter (13)
        if(e.which==13)
        {
            $scope.buscar_procedimento_filtro(atendimento_numero);
            // Cancela evento padrao do enter (limpar form)
            e.preventDefault();
        }
    };

	$scope.buscar_procedimento_filtro = function(atendimento_numero)
    {	$scope.procedimento.buscando = null;
        if($scope.procedimento.filtro.length>4)
        {
            $scope.buscar_procedimento(atendimento_numero);
        }
    };

	$scope.selecionar_procedimento = function(index){
		$scope.desselecionar_procedimento();
		$scope.procedimento.resultado = null;
		if ($scope.procedimentos_busca!=null){
			$scope.procedimento.selecionado = $scope.procedimentos_busca[index];
			$scope.procedimento.selecionado_index = index;
		}
	};

	$scope.desselecionar_procedimento = function(){
		$scope.procedimento.selecionado = null;
		$scope.procedimento.selecionado_index = null;
	};

	$scope.vincular_procedimento_atendimento = function(atendimento_vinculado){
		$scope.procedimento.resultado = null;
		$http.post('/nucleo/procedimento/propacs/vincular/',
				{uuid: $scope.procedimento.selecionado.uuid, atendimento: atendimento_vinculado}).success(function(data){
			$scope.procedimento.resultado = data;
			$scope.listar_propacs_procedimentos();
		});

		//Remove o item da lista
		$scope.procedimentos_busca.splice($scope.procedimento.selecionado_index , 1);

		//Apresenta mensagem de sucesso ou erro por 5 segundos
		window.setTimeout(function() {
			$scope.$apply(function() {
				$scope.procedimento.resultado=null;
			});
		}, 5000);

		// fecha modal
		$('#modal-buscar-procedimento').modal('hide');
		$scope.desselecionar_procedimento();
	};

	$scope.seleciona_para_exclusao = function(procedimento, atendimento_vinculado, index){

		$scope.procedimento.selecionado_para_exclusao = procedimento;
		$scope.procedimento.selecionado_para_exclusao_atendimento = atendimento_vinculado;
		$scope.procedimento.selecionado_para_exclusao_index = index;
	};

	$scope.excluir_procedimento = function(){
		dados = { uuid: $scope.procedimento.selecionado_para_exclusao.uuid,
				  atendimento : $scope.procedimento.selecionado_para_exclusao_atendimento,
				  acesso: $scope.procedimento.defensorias_acesso_ids
				};
		$http.post('/nucleo/procedimento/propacs/desvincular/', dados).success(function(data){
			$scope.procedimento.exclusao_resultado = data;
			if (data.sucesso){
				//Remove o item da tabela dos vinculados
				$scope.procedimentos.splice($scope.procedimento.selecionado_para_exclusao_index , 1);
			}
		});

		//Apresenta mensagem de sucesso ou erro por 5 segundos
		window.setTimeout(function() {
			$scope.$apply(function() {
				$scope.procedimento.exclusao_resultado=null;
			});
		}, 5000);

		// fecha modal
		$('#modal-excluir-procedimento-propac').modal('hide');
	}

}


function PropacTarefaCtrl($scope, $http, $location, PropacTarefaService,
                          QualificacaoServiceAPI, $log) {
    const STATUS_CADASTRO = 0
    const STATUS_CUMPRIDO = 2

    $scope.defensorias = [];
    $scope.responsaveis = [];
    $scope.documentos = null;
	$scope.tipos_tarefas = []
    $scope.movimento = null;
    $scope.propac = null;
    $scope.novaTarefa = null;

    $scope.prioridades_select = [
        'Urgente', 'Alta', 'Normal', 'Baixa'
    ]

	$scope.prioridades = [
        {id:0, nome:'Urgente', class:'label-important'},
        {id:1, nome:'Alta', class:'label-warning'},
        {id:2, nome:'Normal', class:'label-info'},
        {id:3, nome:'Baixa', class:'label-info'}
    ];
    $scope.tarefas = [];
    $scope.resposta_para = [];
    $scope.tarefa_id = null;

    $scope.prateleiras = [
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

		if($scope.novaTarefa.setor_responsavel) {
            PropacTarefaService.carregarSetorResponsavel($scope.novaTarefa.setor_responsavel).success(function(data) {
                $scope.setor_responsavel = data;
                $scope.responsaveis = data.defensores;
                $scope.qualificacoes = data.qualificacoes;
            });
        }
	};

	$scope.carregar_tipos_tarefas = function() {
        const TIPO_TAREFA = 40;
		QualificacaoServiceAPI.get({tipo:TIPO_TAREFA}, function(data) {
			$scope.tipos_tarefas = data.results;
		});
	}

    function limpaDatasNovaTarefa () {
        // Corrige bug do componente datepicker.
        const dtInicial = angular.element(document.getElementById('dtInicial'));
        const dtFinal = angular.element(document.getElementById('dtFinal'));
        dtInicial.context.value = null;
        dtFinal.context.value = null;
    }

	$scope.nova = function(prioridade) {
        $scope.novaTarefa = {prioridade:prioridade};
        limpaDatasNovaTarefa();
        $scope.setor_responsavel = null;
        $scope.responsaveis = null;

		PropacTarefaService.listarDefensorias().success(function(data, status) {
            $scope.defensorias = data.defensorias;
            $scope.resposta_para = data.resposta_para;
        }).error(function(data) {
            show_stack_error('Ocorreu um erro ao listar as defensorias!');
        });
	};

	$scope.excluir = function(tarefa) {
        if(tarefa==undefined) {
            if ($scope.excluindo) {
                return;
            }
            $scope.excluindo = true;
            PropacTarefaService.excluirTarefa($scope.tarefa.id).success(function(data, status) {
                if(status == 204) {
                    $('#modal-excluir-tarefa').modal('hide');
                    show_stack_success('Registro excluído com sucesso!');
                    window.location.assign('#/tarefas');
                    location.reload();
                }
            }).error(function(data, status) {
                show_stack_error('Ocorreu um erro ao excluir o registro!');
            });
            $scope.excluindo = false;
        } else {
            $scope.tarefa = tarefa;
        }
	};

    $scope.abrir = function(obj) {
        const url = '#/?tarefa=' + obj.id;
        window.location.assign(url);
        $scope.tarefa_id = obj.id;
        PropacTarefaService.detalharTarefaMovimento(obj.id).success(function(data) {
            $scope.tarefa = data;
            $scope.tarefa.novo_status = ($scope.tarefa.status ? STATUS_CADASTRO : STATUS_CUMPRIDO);
            $http.get('/atendimento/tarefa/' + $scope.tarefa.id +'/visualizar/').success(function(data){});
        }).error(function(data) {
            show_stack_error('Ocorreu um erro ao detalhar a tarefa!');
        });
    }

	$scope.finalizar = function(tarefa) {
        PropacTarefaService.finalizarTarefa(tarefa.id).success(function(data) {
            if(data.success) {
                show_stack_success('Registro atualizado com sucesso!');
                location.reload();
            // TODO verificar necessidade desse else, talvez seja possível utilizar apenas o callback de error
            } else {
                show_stack_error('Ocorreu um erro ao atualizar o registro!');
            }
        }).error(function(data) {
            show_stack_error('Ocorreu um erro ao atualizar o registro!');
        });

	};

    function formatDateToISOFormat(date) {
        if (!date) {return date}
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();

        return year + "-" + month + "-" + day
    }

	$scope.salvar = function(novaTarefa) {
        if($scope.salvando) {
            return;
        }
        $scope.salvando = true;

        if (novaTarefa.data_inicial || novaTarefa.data_final) {
            novaTarefa.data_inicial = formatDateToISOFormat(novaTarefa.data_inicial);
            novaTarefa.data_final = formatDateToISOFormat(novaTarefa.data_final);
        }


        novaTarefa.movimento = $scope.movimento;

        PropacTarefaService.salvarTarefaMovimento(novaTarefa).success(function(data, status) {
            if(status == 201) {
                show_stack_success('Registro salvo com sucesso!');
				$('#modal-cadastrar-tarefa').modal('hide');
                // $('#modal-cadastrar-alerta').modal('hide');
                const url = '#/?tarefa=' + data.id;
                window.location.assign(url);
			}
			$scope.salvando = false;
            location.reload();
        }).error(function(data) {
            show_stack_error('Ocorreu um erro ao tentar salvar a tarefa!');
        });
	};

	$scope.listar = function() {
        $scope.tarefas = [];
	    $scope.carregando_tarefas = true;

        PropacTarefaService.listarTarefasMovimento($scope.movimento).success(function(data) {
            $scope.tarefas = data.results;

            for(var i = 0; i < $scope.tarefas.length; i++) {
				if($scope.tarefa_id==$scope.tarefas[i].id) {
				    $scope.tarefa_id = null;
					$scope.abrir($scope.tarefas[i]);
                    break;
				}
			}
            $scope.carregando_tarefas = false;
        });

    };

	$scope.init = function (args) {

		for(var key in args) {
            $scope[key] = args[key];
        }

        const urlParams = $location.search();
        const tarefaIdUrl = urlParams["tarefa"];
        $scope.tarefa_id = tarefaIdUrl;
        $scope.listar();
		$scope.carregar_tipos_tarefas();

	}
}