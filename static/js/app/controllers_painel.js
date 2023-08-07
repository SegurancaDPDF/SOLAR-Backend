function PainelCtrl($scope, $http) {

    //DIA DA SEMANA
    const listaDiasDaSemana = ["DOMINGO", "SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA", "SEXTA-FEIRA", "SÁBADO"];
    const date = new Date();
    diaDaSemana.innerText = listaDiasDaSemana[date.getDay()];

    var predio = document.getElementById("predio_id").value;
    var carregando = false;
    var ultimoDados = [];

    $scope.carregar = function() {

        $http.get(`/painel/senhas/predio/${predio}/`).success(function(dados) {

            $scope.dados = dados;
			$scope.carregando = false;

            //verifica se há dados vindo na requisição ou em ultimoDados
            var dadosVazios = (dados.length == 0 || ultimoDados.length == 0);

			if (!dadosVazios) {
			    if (dados[0]['requerente_nome'] != ultimoDados[0]['requerente_nome']) {
                    atualizarPainel();
			    }
			    else if (dados[0]['hora'] != ultimoDados[0]['hora']) {
                    atualizarPainel();
			    }
			}

			if (ultimoDados !== dados && ultimoDados.length == 0) {
			    atualizarPainel();
			}

			ultimoDados = dados;
        });

        carregando = false;
    }

    $scope.init = function() {
        $scope.carregar();

        window.setInterval(function()
        {
            if(!carregando)
            {
                carregando = true;
                $scope.carregar();
            }
        }, 10000); //atualiza o painel de 10 em 10 segundos
     }

    $scope.alerta = function() {
        alertaSom();
        alertaPiscar();
    }

    // Relógio
    // https://codepen.io/afarrar/pen/JRaEjP

    function relogio() {

        const date = new Date();
        /**
         * padStart recebe dois argumentos. O primeiro é a qtd de caracteres
         * necessários e o segundo é o caracter que irá preencher o espaço vazio
         * no início da string.
         */

        const hora = String(date.getHours()).padStart(2, '0');
        const minuto = String(date.getMinutes()).padStart(2, '0');
        const segundo = String(date.getSeconds()).padStart(2, '0');

        const time = `${hora}:${minuto}:${segundo}`
        document.getElementById("hora").innerText = time;
        setTimeout(relogio, 1000);
    }

    relogio();

    function alertaPiscar(){
        let ladoEsquerdo = document.getElementById("left")
        for(let i = 0; i < 6; i++) {
            setTimeout(() => {
                if (ladoEsquerdo.style.visibility == 'hidden'){
                    ladoEsquerdo.style.visibility = 'visible'
                } else {
                    ladoEsquerdo.style.visibility = 'hidden'
                }
            }, (2*i + 1) * 250);
        }
    }

    function alertaSom(){
        somPainel.play();
    }

    function atualizarPainel() {

        if ($scope.dados.length > 0) {

            //STATUS ATENDIMENTO PRIORIDADE
            if ($scope.dados[0]['prioridade'] === 0) {
                prioridadeStatus.innerText = "NORMAL"
                prioridadeStatus.style.backgroundColor = "#66af62"
            } else {
                prioridadeStatus.innerText = "PRIORIDADE"
                prioridadeStatus.style.backgroundColor = "#b72a2a"
            }// FIM STATUS ATENDIMENTO PRIORIDADE

            // dados.lenght é igual a 4. Quantidade retornada pelo backend.
            for (i = 0; i < $scope.dados.length; i++){
                if (i >= 0 && i < 4){
                    document.getElementById(`nomeAssistido${i}`).innerText = $scope.dados[i]['requerente_nome'].toUpperCase();
                    document.getElementById(`tipoGuiche${i}`).innerText = $scope.dados[i]["guiche_tipo"] === 1 ? 'GUICHÊ' : 'SALA'
                    document.getElementById(`numeroGuiche${i}`).innerText = $scope.dados[i]['guiche_numero']
                    document.getElementById(`andar${i}`).innerText = $scope.dados[i]['andar'] === 0 ? "TÉRREO" : `${$scope.dados[i]['andar']}º ANDAR`
                }
            }

            nomeDefensoria.innerText = $scope.dados[0]['defensoria_nome'].toUpperCase()

            alertaSom();
            alertaPiscar();
        }

    }
}

