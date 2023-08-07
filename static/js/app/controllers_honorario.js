function HonorariosCtrl($scope, $http, $filter, AtuacaoAPI, DefensorAPI)
{

    $scope.atuacoes = [];
    $scope.defensores = [];
    $scope.vincular_ao_titular_do_setor = false;

    $scope.carregar = function(honorario_id)
    {

        $scope.audiencia = {honorario:{valor_estimado:0, defensor:null}};

        if($scope.vincular_ao_titular_do_setor && $scope.atuacoes.length > 0){
            $scope.audiencia.honorario.defensor = $scope.atuacoes[0].defensor;
        }
        else{
            $http.get('/processo/fase/'+honorario_id+'/get/json/').success(function(data){
                if(!data.error)
                {
                    for (var i = 0; i < $scope.defensores.length; i++) {
                        if ($scope.defensores[i].id == data.fase.defensor_cadastro) {
                            $scope.audiencia.honorario.defensor = $scope.defensores[i];
                        }
                    }
                }
            });
        }

    };

    $scope.init = function(defensoria_id, vincular_ao_titular_do_setor)
    {

        $scope.vincular_ao_titular_do_setor = vincular_ao_titular_do_setor;

        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        AtuacaoAPI.get({defensoria_id:defensoria_id, apenas_defensor:true, ativo:true, apenas_vigentes:true, limit:1000}, function(data){
            $scope.atuacoes = data.results;
        });

        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        DefensorAPI.get({ativo:true, limit:1000}, function(data){
            $scope.defensores = data.results;
        });

    }

}
