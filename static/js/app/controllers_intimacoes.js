class IntimacaoDOM{
    //obrigado!!! https://stackoverflow.com/questions/494143/creating-a-new-dom-element-from-an-html-string-using-built-in-dom-methods-or-pro
    static createElementFromHTML(htmlString) {
        var div = document.createElement('div');
        div.innerHTML = htmlString.trim();
        return div.firstChild; 
      }

    static ocultarElementos(container){
        document.querySelector(container).childNodes.forEach((element => {
            if(element.style) element.style.display = "none";
        }));
    }

    static inserirElemento(container, elemento){
        document.querySelector(container).appendChild(IntimacaoDOM.createElementFromHTML(elemento));
    }
}

class Intimacoes{

    constructor(data){
        this.form_abrir_prazos = document.querySelector('#AbrirPrazosForm');
        this.preencherModalComDefensores(data.servidor.lista_defensores);
        this.onSubmit(data);
    }

    onSubmit(data) {
        this.form_abrir_prazos.onsubmit = function(event){

            event.preventDefault();

            //lista de checkbox avisos
            let checkbox_selecionados = [...document.querySelectorAll('input[name="avisos"]:checked')];
            let array_avisos_selecionados = checkbox_selecionados.length > 0 ?  [...document.querySelectorAll('input[name="avisos"]:checked')] : [event.submitter.parentElement.parentElement.parentElement.children[0].children[0]];
            /* existem 2 cenários: 
                1 - seleção de multiplos (checkbox) avisos para abertura em lote ou
                2 - abertura de apenas 1 aviso
                Se  array_avisos_selecionados > 0 significa que foram selecionados 1 ou vários checkbox, então faz abertura em lote (de todos) caso
                contrario está sendo aberto apenas 1 aviso através do botão amarelho "Abrir Prazo"
            */
            // Se é defensor abre prazo direto
            if(data.servidor.eh_defensor == true){
                
                Intimacoes.exibirModal();

                IntimacaoDOM.ocultarElementos("#modal-selecionar-defenfensor .modal-body");
                IntimacaoDOM.inserirElemento("#modal-selecionar-defenfensor .modal-body", '<div class="containerassinador"><div class="lds-ripple"><div></div><div></div></div></div>');
                
                document.querySelector("#btnabrirprazo").disabled = true;
                document.querySelector("#modal-selecionar-defenfensor .modal-header h3").innerHTML="<i class='fa fa-file-signature'></i> Abrindo Prazos";

                Intimacoes.abrirPrazoNoSolar(array_avisos_selecionados, data.servidor.cpf_usuario).then(
                    (resposta_do_solar_em_json) => {
                        Intimacoes.atualizarHTML(resposta_do_solar_em_json, array_avisos_selecionados);
                        IntimacaoDOM.ocultarElementos("#modal-selecionar-defenfensor .modal-body");
                        IntimacaoDOM.inserirElemento("#modal-selecionar-defenfensor .modal-body", '<div class="swal2-icon swal2-success swal2-animate-success-icon" style="display: flex;"><div class="swal2-success-circular-line-left" style="background-color: rgb(255, 255, 255);"></div><span class="swal2-success-line-tip"></span><span class="swal2-success-line-long"></span><div class="swal2-success-ring"></div><div class="swal2-success-fix" style="background-color: rgb(255, 255, 255);"></div><div class="swal2-success-circular-line-right" style="background-color: rgb(255, 255, 255);"></div></div>');
                        setTimeout(function() {Intimacoes.fecharModal();}, 2000);
                        
                    }
                );

            }else{
                // pergunta ao assessor qual defensor ele está representando para obter o cpf do defensor responsavel
                // só irá disparar request ao SOLAR quando selecionado Defensor no Modal

                Intimacoes.exibirModal();               

                document.querySelector("#btnabrirprazo").addEventListener('click', function() {

                    IntimacaoDOM.ocultarElementos("#modal-selecionar-defenfensor .modal-body");     

                    IntimacaoDOM.inserirElemento("#modal-selecionar-defenfensor .modal-body", '<div class="containerassinador"><div class="lds-ripple"><div></div><div></div></div></div>');
                    
                    document.querySelector("#btnabrirprazo").disabled = true;

                    document.querySelector("#modal-selecionar-defenfensor .modal-header h3").innerHTML="<i class='fa fa-file-signature'></i> Abrindo Prazos";

                    let cpf_do_defensor_selecionado_no_modal = document.querySelector("[name=defensor_usuario_id]").value;

                    Intimacoes.abrirPrazoNoSolar(array_avisos_selecionados, cpf_do_defensor_selecionado_no_modal).then(
                        (resposta_do_solar_em_json) => {
                            Intimacoes.atualizarHTML(resposta_do_solar_em_json, array_avisos_selecionados);
                            IntimacaoDOM.ocultarElementos("#modal-selecionar-defenfensor .modal-body");
                            IntimacaoDOM.inserirElemento("#modal-selecionar-defenfensor .modal-body", '<div class="swal2-icon swal2-success swal2-animate-success-icon" style="display: flex;"><div class="swal2-success-circular-line-left" style="background-color: rgb(255, 255, 255);"></div><span class="swal2-success-line-tip"></span><span class="swal2-success-line-long"></span><div class="swal2-success-ring"></div><div class="swal2-success-fix" style="background-color: rgb(255, 255, 255);"></div><div class="swal2-success-circular-line-right" style="background-color: rgb(255, 255, 255);"></div></div>');
                        }
                    );

                });

            }
        }
    }

    static async abrirPrazoNoSolar(array_avisos_selecionados, cpf_responsavel) {
            // pega todos os avisos selecionados e manda via POST para o SOLAR
                const response = await fetch('/processo/intimacao/abrir-prazo/', 
                {
                    method: 'POST',
                    headers: new Headers({ 
                        'Content-type': 'application/json; charset=UTF-8', 
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value 
                        }),
                    body: JSON.stringify({'cpf_responsavel': cpf_responsavel, 'avisos': array_avisos_selecionados.map(function(aviso){return aviso.value;})})
                });
                const resposta_do_solar_em_json = await response.json();

                return resposta_do_solar_em_json;
    }

    preencherModalComDefensores(lista_defensores){

        let select_defensor_form = document.querySelector("[name=defensor_usuario_id]");

        lista_defensores.forEach(function(defensor){
            let option = document.createElement('option');
            option.value = defensor.cpf;
            option.text = defensor.nome;
            select_defensor_form.appendChild(option);
        });

    }

    static atualizarHTML(resposta_do_solar_em_json, array_avisos_selecionados){
        // Após obter resposta do SOLAR em JSON atualiza as TR's do HTML
        resposta_do_solar_em_json.comunicacoes.forEach((comunicacao) => {

            // Primeiro verifica situações de erro de conexão ou aviso fechado
            if (comunicacao.error){
                for(let i=0; i<array_avisos_selecionados.length; i++){
                    if(array_avisos_selecionados[i].value==`${comunicacao.processo},${comunicacao.numero}`){
                        // insere mensagem genérica
                        array_avisos_selecionados[i].parentElement.parentElement.children[8].innerText = 'Sistema Offline ou Aviso Já Fechado';
                        // remove ao checkbox para não ser aberto novamente
                        array_avisos_selecionados[i].checked=false   
                        // coloca class css para sinalizar mudança visual
                        array_avisos_selecionados[i].parentElement.parentElement.className="error";
                    }
                }
                show_stack_error(comunicacao.error)
                return;
            }

            for(let i=0; i<array_avisos_selecionados.length; i++){
                if(array_avisos_selecionados[i].value==`${comunicacao.processo},${comunicacao.numero}`){
                    let data_referencia = new Date(comunicacao.data_referencia);
                    // remove ao checkbox para não ser aberto novamente
                    array_avisos_selecionados[i].checked=false   
                    // desabilita checkbox
                    array_avisos_selecionados[i].disabled=true
                    // coloca class css para sinalizar mudança visual
                    array_avisos_selecionados[i].parentElement.parentElement.className="warning";
                    // insere data final
                    array_avisos_selecionados[i].parentElement.parentElement.children[7].innerHTML = `${Intimacoes.adicionaZero(data_referencia.getDate().toString())}/${Intimacoes.adicionaZero(data_referencia.getMonth()+1).toString()}/${data_referencia.getFullYear()}<br/>${Intimacoes.adicionaZero(data_referencia.getHours()).toString()}:${Intimacoes.adicionaZero(data_referencia.getMinutes()).toString()}`;
                    // insere texto aberto
                    array_avisos_selecionados[i].parentElement.parentElement.children[8].innerText = 'Aberto';
                    // desabilita botão peticionar
                    array_avisos_selecionados[i].parentElement.parentElement.children[9].children[0].children[3].disabled = true;
                    if(comunicacao.documentos.length){
                        // habilita botão documento intimação
                        array_avisos_selecionados[i].parentElement.parentElement.children[9].children[0].children[1].classList.remove('disabled');
                        // insere link do documento intimação
                        array_avisos_selecionados[i].parentElement.parentElement.children[9].children[0].children[1].href = `/procapi/processo/${comunicacao.processo}/documento/${comunicacao.documentos[0].documento}/`;
                        // adiciona propriedade target no link do documento intimação
                        array_avisos_selecionados[i].parentElement.parentElement.children[9].children[0].children[1].setAttribute("target", "_blank");
                    }
                }
            }
        });
    }

    static exibirModal(){
        document.querySelector(".background-modal").classList.add('modal-backdrop');
        document.querySelector(".background-modal").style.opacity = "0.6";
        document.querySelector(".background-modal").style.display = "block";
        document.querySelector("#modal-selecionar-defenfensor").style.top = "30%";
        document.querySelector("#modal-selecionar-defenfensor").style.visibility = "visible";
        document.querySelector("#modal-selecionar-defenfensor").style.display = "block";
        document.querySelector("#modal-selecionar-defenfensor").style.opacity = "1";
    }

    static fecharModal(){
        document.querySelector(".background-modal").classList.remove('modal-backdrop');
        document.querySelector(".background-modal").style.opacity = "0";
        document.querySelector("#modal-selecionar-defenfensor").style.top = "0";
        document.querySelector("#modal-selecionar-defenfensor").style.visibility = "hidden";
        document.querySelector("#modal-selecionar-defenfensor").style.display = "none";
        document.querySelector("#modal-selecionar-defenfensor").style.opacity = "0";
    }

    static adicionaZero(numero){
        if (numero <= 9) 
            return "0" + numero;
        else
            return numero; 
    }
}

function BuscarIntimacoesCtrl($scope, $http, AtuacaoAPI, DefensoriaAPI, EtiquetaAPI) {


    $scope.aviso = null;
    $scope.defensoria = null;
    $scope.etiquetas = [];
    $scope.pode_alterar_defensoria = true;

    $scope.etiquetar = function(aviso_numero, defensoria_id, servidor_id)
    {

        $scope.aviso = aviso_numero;
        $scope.defensoria = null;
        $scope.etiquetas = [];
        $scope.pode_alterar_defensoria = true;

        if(defensoria_id){
            $scope.defensoria = parseInt(defensoria_id);
            $scope.pode_alterar_defensoria = false;
        }

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        AtuacaoAPI.get({servidor_id:servidor_id, apenas_vigentes:true, limit:1000}, function(data){
            $scope.atuacoes = data.results;
            if($scope.defensoria){
                $scope.carregar_etiquetas();
            }
        });

    }

    $scope.carregar_etiquetas = function(){
        if($scope.defensoria)
        {
            // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
            EtiquetaAPI.get({defensorias:$scope.defensoria, limit:1000}, function(data){
                $scope.etiquetas = data.results;
            });
        }
    }

    $scope.btnCadastrarEtiqueta_click = function(servidor_id)
    {
        $scope.$broadcast('GerenciarEtiquetasCtrl:init', {
            servidor_id:servidor_id,
            solicitar_defensoria: false
        });
    };

    $scope.btnCadastrarEtiquetaSimplificado_click = function(servidor_id)
    {
        $scope.$broadcast('GerenciarEtiquetasCtrl:init', {
            servidor_id:servidor_id,
            solicitar_defensoria: true
        });
    };

    $scope.btnVincularDefensoriaEtiqueta_click = function(servidor_id)
    {
        $scope.$broadcast('VincularEtiquetasDefensoriasCtrl:init', {
            servidor_id:servidor_id
        });
    };

    $scope.btnVincularEtiquetaServidor_click = function(servidor_id)
    {
        $scope.$broadcast('VincularEtiquetasServidoresCtrl:init', {
            servidor_id:servidor_id
        });
    };

}

function GerenciarEtiquetasCtrl($scope, $http, AtuacaoAPI, EtiquetaAPI, DefensoriaEtiquetaAPI) {

    $scope.etiqueta = {};
    $scope.etiquetas = [];
    $scope.salvando = false;

	$scope.$on('GerenciarEtiquetasCtrl:init', function(event, args) {
		$scope.init(args.servidor_id, args.solicitar_defensoria);
	});

    $scope.init = function(servidor_id, solicitar_defensoria)
    {
        $scope.limpar_etiqueta();
        if(solicitar_defensoria)
            $scope.carregar_atuacoes(servidor_id);
        else
            $scope.carregar_etiquetas();
    }

    $scope.limpar_etiqueta = function(){
        $scope.etiqueta.id = null;
        $scope.etiqueta.nome = '';
        $scope.etiqueta.cor = '#3a87ad'; // label-info
    }

    $scope.carregar_atuacoes = function(servidor_id){
        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        AtuacaoAPI.get({servidor_id:servidor_id, apenas_vigentes:true, limit:1000}, function(data){
            $scope.atuacoes = data.results;
            $scope.etiqueta.defensoria = $scope.atuacoes[0].defensoria.id;
            $scope.carregar_etiquetas();
        });

    }

    $scope.carregar_etiquetas = function(){

        let params = {limit:1000};

        if($scope.etiqueta.defensoria)
            params['defensorias'] = $scope.etiqueta.defensoria;

        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        EtiquetaAPI.get(params, function(data){
            $scope.etiquetas = data.results;
        });
    }

    $scope.selecionar_etiqueta = function(e)
    {
        let etiqueta = angular.copy(e);
        if($scope.etiqueta.defensoria)
            etiqueta.defensoria = $scope.etiqueta.defensoria;
        $scope.etiqueta = etiqueta;
    }

    $scope.salvar_etiqueta = function(){

        $scope.salvando = true;

        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        if($scope.etiqueta.id)
        {
            EtiquetaAPI.update($scope.etiqueta, function(data){
                $scope.salvando = false;
                $scope.carregar_etiquetas();
                $scope.limpar_etiqueta();
                show_stack_success('Registro salvo com sucesso!');
            });
        }
        else
        {
            EtiquetaAPI.save($scope.etiqueta, function(data){
                $scope.carregar_etiquetas();
                $scope.salvando = false;
                $scope.limpar_etiqueta();
                show_stack_success('Registro salvo com sucesso!');
            });
        }
    }

    $scope.remover_etiqueta = function(id){
        $scope.salvando = true;
        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        EtiquetaAPI.delete({id: id}, function(data){
            $scope.carregar_etiquetas();
            $scope.salvando = false;
        });
    }

}

function VincularEtiquetasDefensoriasCtrl($scope, $http, AtuacaoAPI, EtiquetaAPI, DefensoriaEtiquetaAPI) {

    $scope.etiqueta = {};
    $scope.etiquetas = [];
    $scope.etiquetas_defensorias = [];
    $scope.atuacoes = [];
    $scope.defensorias = [];
    $scope.defensorias_ids = [];
    $scope.salvando = false;

	$scope.$on('VincularEtiquetasDefensoriasCtrl:init', function(event, args) {
		$scope.init(args.servidor_id);
	});

    $scope.init = function(servidor_id)
    {
        $scope.etiqueta = {};
        $scope.carregar_etiquetas();
        $scope.carregar_atuacoes(servidor_id);
    }

    $scope.carregar_atuacoes = function(servidor_id){
        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        AtuacaoAPI.get({servidor_id:servidor_id, apenas_vigentes:true, limit:1000}, function(data){
            $scope.atuacoes = data.results;
        });
    }

    $scope.carregar_etiquetas = function(){
        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        EtiquetaAPI.get({limit:1000}, function(data){
            $scope.etiquetas = data.results;
        });
    }

    $scope.carregar_etiqueta = function()
    {

        var defensorias = [];
        $scope.etiqueta.lista_defensorias = [];

        for(var i = 0; i < $scope.atuacoes.length; i++){

            var defensoria = angular.copy($scope.atuacoes[i].defensoria);
            defensoria.sel = false;

            for(var j = 0; j < $scope.etiqueta.defensorias.length; j++)
            {
                if(defensoria.id == $scope.etiqueta.defensorias[j]){
                    defensoria.sel = true;
                }
            }

            defensorias.push(defensoria);

        }
        
        $scope.etiqueta.lista_defensorias = defensorias;

    }

    $scope.salvar_etiqueta = function(){
        $scope.salvando = true;
        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        if($scope.etiqueta.id)
        {
            EtiquetaAPI.update($scope.etiqueta, function(data){
                $scope.salvando = false;
                show_stack_success('Registro salvo com sucesso!');
            });
        }
    }

}

function VincularEtiquetasServidoresCtrl($scope, $http, AtuacaoAPI, EtiquetaAPI, DefensoriaEtiquetaAPI) {

    $scope.etiqueta_defensoria = {};
    $scope.etiquetas_defensorias = [];
    $scope.atuacoes = [];
    $scope.defensorias = [];
    $scope.defensorias_ids = [];
    $scope.salvando = false;

	$scope.$on('VincularEtiquetasServidoresCtrl:init', function(event, args) {
		$scope.init(args.servidor_id);
	});

    $scope.init = function(servidor_id)
    {
        $scope.etiqueta_defensoria = {};
        $scope.usuarios_lotados = [];
        $scope.carregar_atuacoes(servidor_id);
    }

    $scope.carregar_atuacoes = function(servidor_id){
        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        AtuacaoAPI.get({servidor_id:servidor_id, apenas_vigentes:true, limit:1000}, function(data){

            let defensorias = [];
            let defensorias_ids = [];

            for(let i = 0; i < data.results.length; i++){
                defensorias.push(data.results[i].defensoria);
                defensorias_ids.push(data.results[i].defensoria.id);
            }

            $scope.atuacoes = data.results;
            $scope.defensorias = defensorias;
            $scope.defensorias_ids = defensorias_ids;
            $scope.carregar_etiquetas_defensorias();

        });
    }

    $scope.carregar_etiquetas_defensorias = function()
    {
        DefensoriaEtiquetaAPI.get({limit:1000, defensorias:$scope.defensorias_ids.toString()}, function(data){
            $scope.etiquetas_defensorias = data.results;
        });
    }

    $scope.carregar_etiqueta_defensoria = function()
    {
        $scope.usuarios_lotados = [];
        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        AtuacaoAPI.get({defensoria_id:$scope.etiqueta_defensoria.defensoria, apenas_vigentes:true, limit:1000}, function(data){
            let usuarios_lotados = data.results;
            let usuarios_autorizados = $scope.etiqueta_defensoria.usuarios_autorizados;
            for(let i = 0; i < usuarios_lotados.length; i++)
            {
                for(let j = 0; j < usuarios_autorizados.length; j++)
                {
                    if(usuarios_lotados[i].usuario == usuarios_autorizados[j]){
                        usuarios_lotados[i].sel = true;
                    }
                }
            }
            $scope.usuarios_lotados = usuarios_lotados;
        });
    }

    $scope.salvar_etiqueta_defensoria = function()
    {
        $scope.salvando = true;

        let usuarios_autorizados = [];
        for(let i = 0; i < $scope.usuarios_lotados.length; i++)
        {
            if($scope.usuarios_lotados[i].sel){
                usuarios_autorizados.push($scope.usuarios_lotados[i].usuario);
            }
        }

        DefensoriaEtiquetaAPI.update({id: $scope.etiqueta_defensoria.id, usuarios_autorizados: usuarios_autorizados}, function(data){
            $scope.etiqueta_defensoria.usuarios_autorizados = usuarios_autorizados;
            $scope.salvando = false;
            show_stack_success('Permissões atualizadas com sucesso!');
        });

    }

}