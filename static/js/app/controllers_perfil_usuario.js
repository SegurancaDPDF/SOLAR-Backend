function PerfilComarcasCtrl($scope, $http)
{

    $scope.listar_diretorias = function() {

        $http.get('/diretoria/listar/').success(function(data){

            var grupos = [];
            var grupo = [];
            var item = 0;

            for(var i in data)
            {
                grupo.push(data[i]);

                if(grupo.length==4)
                {
                    grupos.push(grupo);
                    grupo = [];
                }

            }

            grupos.push(grupo);
            $scope.grupos = grupos;

        });

    }

	$scope.init = function()
	{
        $scope.listar_diretorias();
    }
}

function PerfilUsuarioCtrl($scope, $http, $filter)
{

    $scope.perfil = {};
    $scope.visualizar_atuacao = [];
    $scope.initial_visualizar_atuacao = [];
    $scope.salvando = false;

    // Quando os valores iniciais forem detectados
    $scope.$watch('initial_visualizar_atuacao', function(newVal, oldVal) {
        // Passa os valores iniciais para a model
        newVal.forEach(function(valor, indice){
            $scope.visualizar_atuacao[indice] = valor;
        });
    });

    $scope.alterar_senha_user = function()
    {
        $scope.dados_resposta = null;
        $http.post('/perfil/editar/senha/',{
            'senha_antiga':$scope.perfil.senha_antiga,
            'senha_nova':$scope.perfil.senha_nova,
            'senha_confirma':$scope.perfil.senha_confirma}).success(function(data){

            $scope.dados_resposta = data;
            $scope.perfil.senha_antiga = null;
            $scope.perfil.senha_nova = null;
            $scope.perfil.senha_confirma = null;
            if ($scope.dados_resposta.erro == false){
                window.setTimeout(function() {
                    $scope.$apply(function() {
                        $('#modal-alterar-senha').modal('hide');
                    });
                }, 4000);
            }
             window.setTimeout(function() {
                $scope.$apply(function() {
                        $scope.dados_resposta = null;
                    });
                }, 3500);
        });

    };

    $scope.alterar_email_user = function()
    {
        $scope.dados_resposta = null;
        $http.post('/perfil/editar/email/',{'email':$scope.perfil.email}).success(function(data){

            $scope.dados_resposta = data;
            if ($scope.dados_resposta.erro == false){
                window.setTimeout(function() {
                    $scope.$apply(function() {
                        $('#modal-alterar-email').modal('hide');
                    });
                }, 4000);
            }
             window.setTimeout(function() {
                $scope.$apply(function() {
                        $scope.dados_resposta = null;
                    });
                }, 3500);
        });

    };

    $scope.configurar_visualizacao_chat_por_atuacao = function()
    {
        $scope.dados_resposta = null;

        // Obtém o json das ids a serem ativadas
        let atuacoes_a_ativar_id_list = [];
        $scope.visualizar_atuacao.forEach(function(el, idx){
            if(el){
                atuacoes_a_ativar_id_list.push(idx);
            }
        });
        atuacoes_a_ativar_id_list = JSON.stringify(atuacoes_a_ativar_id_list);

        $http.post('/perfil/editar/configurar-visualizacao-chat-por-atuacao/',{'atuacoes_a_ativar_id_list':atuacoes_a_ativar_id_list}).success(function(data){

            $scope.dados_resposta = data;
            if ($scope.dados_resposta.erro == false){
                window.setTimeout(function() {
                    $scope.$apply(function() {
                        $('#modal-visualizar-chat-por-atuacao').modal('hide');
                    });
                }, 4000);
            }
             window.setTimeout(function() {
                $scope.$apply(function() {
                        $scope.dados_resposta = null;
                    });
                }, 3500);
        });

    };

    $scope.set_credencial = function(credencial)
    {
        $scope.perfil = angular.copy(credencial);
    }

    $scope.alterar_senha_eproc = function()
    {

        $scope.dados_resposta = null;
        $scope.salvando = true;

        $http.post('/perfil/editar/senha-eproc/', $scope.perfil).success(function(data){

            $scope.dados_resposta = data;
            $scope.perfil.senha_eproc = null;
            $scope.perfil.senha_eproc_confirma = null;
            $scope.salvando = false;

            if ($scope.dados_resposta.sucesso == true)
            {
                window.setTimeout(function() {
                    $scope.$apply(function() {
                        $('#modal-alterar-dados-eproc').modal('hide');
                        location.reload();
                    });
                }, 4000);
            }

            window.setTimeout(function() {
                $scope.$apply(function() {
                    $scope.dados_resposta = null;
                });
            }, 3500);

        });

    }

    $scope.alterar_senha_projudi = function()
    {
        $scope.dados_resposta = null;
        console.log("Senha projudi")

        $http.post('/perfil/editar/usuario-projudi/', $scope.perfil).success(function(data){
            $scope.dados_resposta = data;
            $scope.perfil.usuario_projudi = null;
            console.log($scope.dados_resposta.sucesso)

            if ($scope.dados_resposta.sucesso == true)
            {
                window.setTimeout(function() {
                    $scope.$apply(function() {
                        $('#modal-alterar-dados-projudi').modal('hide');
                        location.reload();
                    });
                }, 1000);
            }

            window.setTimeout(function() {
                $scope.$apply(function() {
                    $scope.dados_resposta = null;
                });
            }, 3500);


        });
    }

}

function DefensorServidorCtrl($scope, $http)
{
    $scope.defensor = {};

    $scope.limpar_dados = function()
    {
        $scope.defensor.login_eproc = null;
        $scope.defensor.senha_eproc = null;
        $scope.defensor.confirma_senha_eproc = null;
    }

}
