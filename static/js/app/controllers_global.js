function ProcessoPendenteCtrl($scope, $http, $interval)
{

    var chamada;

    $scope.init = function(defensor_id, processo_numero)
    {

        if(angular.isDefined(chamada)) {
            return;
        }
        $scope.listar(defensor_id, processo_numero);

        chamada = $interval(function(){
            if($scope.hora_expiracao==0) {
                $scope.listar(defensor_id, processo_numero);
            }
            $scope.hora_expiracao--;
        }, 1000);

    };

    $scope.listar = function (defensor_id, processo_numero) {
        $http.get('/processo/pendente/defensor/' + defensor_id + '/get/').success(function(data){

            $scope.varas = data.varas;
            $scope.meses = data.meses;
            $scope.processos = data.processos;
            $scope.processos_len = Object.keys(data.processos).length;
            $scope.hora_expiracao = data.hora_expiracao ? data.hora_expiracao : 300;
            global_fechar_box_processos(data.hora_expiracao!=0 || !$scope.processos_len);
            global_fechar_seta_processos(!$scope.processos_len);

            if(processo_numero)
            {
                for(processo in data.processos)
                {
                    if(data.processos[processo].numero==processo_numero) {
                        $scope.selecionado = data.processos[processo];
                    }
                }
            }

        });
    };

    $scope.popover = function(titulo, conteudo, pos)
    {
        return {"title": titulo, "content": conteudo, "placement": pos};

    };

    $scope.selecionar =function(processo)
    {
        $scope.selecionado = processo;
    }
}

function TermoAceiteCtrl($scope, $http, $interval)
{
    $scope.termos = [];
    $scope.currentTermo = null;
    $scope.salvando = false;

    $scope.init = function(servidor_id)
    {
        $http.get('/aceite/' + servidor_id + '/termo/json/get/').success(function(termos){
            if (!!termos) {
                $scope.termos = termos;
                $scope.nextTermo();
            }
        });
    };

    $scope.nextTermo = function () {
        if ($scope.termos.length > 0) {
            var termo = $scope.termos.shift();
            $scope.currentTermo = termo;
            $('#modal-termo-aceite').modal({
                show: true,
                keyboard: false,
                backdrop: 'static'
            });
        } else {
            $scope.currentTermo = null;
            $('#modal-termo-aceite').modal('hide');
        }
    }

    $scope.aceitar = function (termo, servidor_id, csrf_token, aceito) {

        $scope.salvando = true;
        termo.servidor_id = servidor_id;
        termo.aceito = aceito;

        var config = {
            method: 'POST',
            url: '/aceite/termo/json/post/',
            data: termo,
            headers:{
                'X-CSRFToken': csrf_token
            }
        }

        $http(config).success(function(resp){
            if (resp) {
                $scope.nextTermo();
                $scope.salvando = false;
            }
        });

    }
}

//guichê
function abrirModalAlterarGuiche(){
    const usuarioId = document.getElementById('usuario_id').value
    const csrf_token = document.getElementById('csrf_token').value
    $.ajax({
        type: "POST",
        url: "/comarca/predio/guiche/get/",
        data: {usuario: usuarioId, csrfmiddlewaretoken: csrf_token},
        success: (data) => {
            exibirDadosNaModalAlterarGuiche(data)
        }
    })
    $("#modal-alterar-guiche").modal();
}

function exibirDadosNaModalAlterarGuiche(data){

    // limpa o formulário
    initAlterarGuiche();

    if (data.guiche_atual){
        //numero atual
        labelGuicheSala.innerText = data.guiche_atual.tipo.nome
        numeroGuicheAtual.innerText = data.guiche_atual.numero;

        //andar atual
        andarAtual.innerText =  data.guiche_atual.andar === 0 ? 'Térreo' : `${data.guiche_atual.andar}º andar`

        //predio atual
        predioAtual.innerText = `${data.guiche_atual.predio_atual.nome} - ${data.guiche_atual.defensoria.nome}`
    }

    data.defensorias_disponiveis.forEach((defensoria) => {
        //select defensoria
        const predioItem = document.createElement("option");
        predioItem.innerText = `${defensoria.defensoria.predio.nome} - ${defensoria.defensoria.nome}`;
        predioItem.value = defensoria.defensoria.predio.id;
        predioItem.dataset.qtdAndares = defensoria.defensoria.predio.qtd_andares;
        predioItem.dataset.defensoriaID = defensoria.defensoria.id;
        selectPredio.add(predioItem);
    })
}

//limpa os campos da modal de alterar guichê
function initAlterarGuiche(){
    // reseta o select de predio
    const qtdPredios = selectPredio.length
    for (let i=0; i < qtdPredios; i++){
        selectPredio.remove(1);
    }

    // reseta o select de andar
    const qtdAndares = selectAndar.length
    for (let i=0; i < qtdAndares; i++){
        selectAndar.remove(1);
    }
    selectAndar.value = ""

    // reseta o select de tipo
    selectTipoGuiche.value = "";

    //reseta o input de número do guichê
    inputGuicheNumero.value = null;

    numeroGuicheAtual.innerText = ""
    andarAtual.innerText = ""
    predioAtual.innerText = ""
}

function selecionarPredio(predio){
    const indexPredioSelecionado = predio.options.selectedIndex;
    const qtdAndares = predio.options[indexPredioSelecionado].dataset.qtdAndares;

    const selectAndar = document.getElementById('selectAndar');

    const a = selectAndar.length
    for (let i=0; i < a; i++){
        selectAndar.remove(1);
    }

    for(let i = 0; i <= qtdAndares; i++){
        const descricaoAndar = i===0 ? 'Térreo' : `${i}º andar`
        const opcao_andar = document.createElement("option");
        opcao_andar.innerText = descricaoAndar;
        opcao_andar.value = i;
        selectAndar.add(opcao_andar);
    }
}

//salvar guichê
function salvarGuiche(forcarTrocaDeGuiche) {
    const csrf_token = document.getElementById('csrf_token').value
    const selectPredio = document.getElementById('selectPredio')
    const indexPredioSelecionado = selectPredio.options.selectedIndex;
    const defensoriaID = selectPredio.options[indexPredioSelecionado].dataset.defensoriaID

    $.ajax({
        type: "POST",
        url: "/comarca/guiches/salvar/",
        data: {
            csrfmiddlewaretoken: csrf_token,
            predio_id: document.getElementById('selectPredio').value,
            tipo_id: document.getElementById('selectTipoGuiche').value,
            andar: document.getElementById('selectAndar').value,
            numero: document.getElementById('inputGuicheNumero').value,
            defensoria_id: defensoriaID,
            forcarTrocaDeGuiche: forcarTrocaDeGuiche,
        },
        success: (data) => {
            if (data['success']){
                $('#modal-alterar-guiche').modal('hide');
                $('#modal-guiche-conflito').modal('hide');
                show_stack_success("Guichê alterado com sucesso!");
            }
            else{
                show_stack_error(data['dados']['mensagem']);
                $('#modal-alterar-guiche').modal('hide');
                document.getElementById('servidorConflito').innerText = data['dados']['nome_antigo_usuario']
                $('#modal-guiche-conflito').modal('show');
            }
        }
    })
}
