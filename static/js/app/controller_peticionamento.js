function PeticionamentoCtrl($scope, $http, ManifestacaoDocumentoServiceAPI, AtuacaoAPI, DefensorAPI) {

    $scope.manifestacao_id = null;
    $scope.documentos = [];
    $scope.pessoas_atendimento = [];
    $scope.documentos_atendimento = [];
    $scope.carregando_documentos = false;
    $scope.importando_documentos = false;

    $scope.init = function(manifestacao_id, defensoria_id, defensor_id, eh_defensor)
    {
        $scope.manifestacao_id = manifestacao_id;

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		AtuacaoAPI.get({defensoria_id: defensoria_id, ativo:true, apenas_vigentes:true, apenas_defensor:true}, function(data){

            if(eh_defensor){
                $scope.atuacoes_para_protocolo = data.results.filter(function(el){ return el.defensor.id == defensor_id});
            }
            else{
                $scope.atuacoes_para_protocolo = data.results;
            }

            if($scope.atuacoes_para_protocolo.length > 0 && ($scope.atuacoes_para_protocolo.length == 1 || eh_defensor))
            {
                $scope.atuacao_para_protocolo = $scope.atuacoes_para_protocolo[0];
                $scope.carregar_defensor_para_protocolo();
            }

		});

    }

    $scope.carregar_defensor_para_protocolo = function()
    {
        $scope.defensor_para_protocolo = null;

        if($scope.atuacao_para_protocolo){
            DefensorAPI.get({id: $scope.atuacao_para_protocolo.defensor.id}, function(data){
                $scope.defensor_para_protocolo = data;
            });
        }

    }

	$scope.carregar_pessoa = function(pessoa_id)
	{
	    $scope.$broadcast('BuscarPessoaModel:carregar_pessoa', pessoa_id);
	};

	$scope.carregar_documento = function(origem_id, origem_tipo)
	{

        var documento = {};
        for(var i = 0; i < $scope.documentos_atendimento.length; i++)
        {
            if($scope.documentos_atendimento[i].id == origem_id && $scope.documentos_atendimento[i].origem == origem_tipo){
                documento = $scope.documentos_atendimento[i];
            }
        }

		$scope.$broadcast('DocumentoCtrl:carregar', documento);

	};

    $scope.listar_documentos_atendimento = function(atendimento_numero)
    {

        $scope.carregando_documentos = true;

        ManifestacaoDocumentoServiceAPI.get({numero: $scope.manifestacao_id}, function(data) {

            $scope.documentos = data.results;

            $http.get('/atendimento/'+atendimento_numero+'/documento/').success(function(data){

                var documentos_atendimento = [];

                // normaliza documentos do atendimento
                for(var i = 0; i < data.uploads.length; i++)
                {
                    documentos_atendimento.push({
                        id: data.uploads[i].id,
                        nome: data.uploads[i].nome,
                        pendente: data.uploads[i].pendente,
                        pessoa_id: null,
                        origem: 10
                    });
                }

                // normaliza documentos das pessoas
                for(var i = 0; i < data.assistidos_documentos.length; i++)
                {
                    documentos_atendimento.push({
                        id: data.assistidos_documentos[i].pk,
                        nome: data.assistidos_documentos[i].nome,
                        pendente: data.assistidos_documentos[i].pendente,
                        pessoa_id: data.assistidos_documentos[i].pessoa_id,
                        origem: 20
                    });
                }

                // verifica quais documentos já foram adicionados à manifestação
                for(var i = 0; i < documentos_atendimento.length; i++)
                {
                    for(var j = 0; j < $scope.documentos.length; j++)
                    {
                        if(documentos_atendimento[i].id == $scope.documentos[j].origem_id && documentos_atendimento[i].origem == $scope.documentos[j].origem){
                            documentos_atendimento[i].vinculado = true;
                            documentos_atendimento[i].selecionado = true;
                        }
                    }
                }

                $scope.pessoas_atendimento = data.assistidos;
                $scope.documentos_atendimento = documentos_atendimento;
                $scope.carregando_documentos = false;

            });
        });

    }

    $scope.importar_documentos = function()
    {

        $scope.importando_documentos = true;
        var documentos = [];

        for(var i = 0; i < $scope.documentos_atendimento.length; i++)
        {
            if($scope.documentos_atendimento[i].selecionado && !$scope.documentos_atendimento[i].vinculado){
                documentos.push($scope.documentos_atendimento[i]);
            }
        }

        if(documentos.length){
            $scope.importar_documento(documentos, 0);
        }

    }

    $scope.importar_documento = function(documentos, posicao)
    {

        var documento = documentos[posicao];
        var dados = {
            "manifestacao": $scope.manifestacao_id,
            "origem": documento.origem,
            "origem_id": documento.id,
            "posicao": 0,
            "tipo_mni": null,
            "nivel_sigilo": 0
        }

        $http.post('/api/v1/manifestacao_processual/'+$scope.manifestacao_id+'/documentos/', dados).success(function(data){
            posicao++;
            if(posicao < documentos.length)
                $scope.importar_documento(documentos, posicao);
            else
                window.location.reload(true);
        });

    }

}

class Peticionamento{

    constructor(dados_do_backend){
        this._pode_editar = dados_do_backend.pode_editar;
        this._pode_filtrar_classe_assunto_competencia = dados_do_backend.pode_filtrar_classe_assunto_competencia;
        this._possui_reu = dados_do_backend.possui_reu;
        this._sistema_webservice = dados_do_backend.sistema_webservice;
        this._competencia = dados_do_backend.competencia;
        this._assunto_principal = dados_do_backend.assunto_principal;
        this._assuntos_secundarios = dados_do_backend.assuntos_secundarios;
        this._classe = dados_do_backend.acao;
        this.headers = new Headers({
            'Content-type': 'application/json; charset=UTF-8',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        });
        this._load = document.createElement('img');
        this._load.src = '/static/img/load.gif';
        this._load.style = "top: 5px; left: 0; margin-left: auto; margin-right: auto; right: 0; border: 0;"

        this._input_competencia = document.querySelector("#id_competencia_mni");
        this._input_classe = document.querySelector("#id_acao_form");
        this._input_assunto_principal = document.querySelector("#id_assunto_principal_form");
        this._input_assuntos_secundarios = document.querySelector("#id_assuntos_secundarios_form");

        this.popularInputCompetencia(this._competencia);

        // Se tem competência
        //então preenche o input classes (classe depende de competencia)
        if(this._competencia){
            // caso _classe esteja null nada será pré-selecionado
            this.popularInputClasse(this._classe);
        }

        // Se tem competência
        // e tem classe
        // então carrega assuntos (assunto depende de classe e competencia)
        if (this._competencia && this._classe){
            // caso _assunto_principal e _assuntos_secundarios sejam null nada será pré-selecionado
            this.popularInputAssuntoPrincipal(this._assunto_principal, this._assuntos_secundarios)
        }

        // Se possui reu, esconde mensagem de alerta
        if(this._possui_reu)
        {
            if (document.querySelector(".alert-reu") !== null) {
                document.querySelector(".alert-reu").style = 'display: none';
            }
        }

        if (this._input_competencia !== null) {
            // atualiza input após interação do usuário
            this._input_competencia.onchange = function(event) {
                // Reseta os proxímos inputs do form
                this._input_classe.innerHTML = '';
                this._input_assunto_principal.innerHTML = '';
                this._input_classe.parentElement.querySelector('div a span').textContent = '';
                this._input_assunto_principal.parentElement.querySelector('div a span').textContent = '';

                // Define valor da variável local para o que foi selecionado no input pelo usuário
                this._competencia = this._input_competencia.value;
                // Realiza requisição ajax e atualiza input seguinte
                this.popularInputClasse();
            }.bind(this);
        }

        if (this._input_classe !== null) {
            // atualiza input após interação do usuário
            this._input_classe.onchange = function(event) {
                // Reseta os proxímos inputs do form
                this._input_assunto_principal.innerHTML = '';
                this._input_assunto_principal.parentElement.querySelector('div a span').textContent = '';

                // Define valor da variável local para o que foi selecionado no input pelo usuário
                this._competencia = this._input_competencia.value;
                this._classe = this._input_classe.value;
                // Realiza requisição ajax e atualiza input seguinte
                this.popularInputAssuntoPrincipal();
            }.bind(this);
        }

    }

    popularInputCompetencia(competencia_selecionada){

        let load = this._load.cloneNode(true);

        this.desativarInputsNoLoad(true);

        if (this._input_competencia !== null) {
            this._input_competencia.parentElement.appendChild(load);


            this.obterCompetenciasviaAPI().then((competencias_api) => {
                competencias_api.forEach((competencia) => {
                    let option = document.createElement('option');
                    option.value = competencia.codigo;
                    option.text = competencia.nome;
                    option.style.textTransform = 'captalize';
                    if(competencia.codigo == competencia_selecionada){
                        option.setAttribute('selected', 'selected');
                        this._input_competencia
                            .parentElement.querySelector('div a span')
                            .textContent = competencia.nome;
                    }
                    this._input_competencia.appendChild(option);
                });

                load.remove();
                this.desativarInputsNoLoad(!this._pode_editar);
            });
        }
    }


    popularInputClasse(classe_selecionada){

        let load = this._load.cloneNode(true);

        if (this._input_classe) {
            this._input_classe.parentElement.appendChild(load);

            this.desativarInputsNoLoad(true);

            // Insere um option fake
            let optionfake = document.createElement('option');
            optionfake.text = '---------';
            this._input_classe.innerHTML = '';
            this._input_classe.appendChild(optionfake);
            this._input_classe
                .parentElement.querySelector('div a span')
                .textContent = '---------';

            this.obterClassesviaAPI({'competencia': this._competencia}).then((classes_api) => {
                // remove o alerta de início
                document.querySelector(".alert-reu").style = 'display: none';

                classes_api.forEach((classe) => {
                    let option = document.createElement('option');
                    option.value = classe.codigo;
                    option.text = classe.nome;
                    option.style.textTransform = 'captalize';
                    // readiciona alerta caso exigir réu
                    if(classe.codigo == classe_selecionada){
                        if(!this._possui_reu){
                            // caso não tenha informação do webservice, presume-se que exige
                            if (classe.exige_polo_passivo_por_sistemas_webservice.length == 0){
                                document.querySelector(".alert-reu").style = 'display: block !important';
                                let btn_peticionar = document.querySelector(".btn-peticionar");
                                if(btn_peticionar){
                                    btn_peticionar.disabled = 'disabled';
                                }
                            }
                            // Caso tenha informação, compara com a exigência do webservice
                            for (let index = 0; index < classe.exige_polo_passivo_por_sistemas_webservice.length; index++) {
                                const classe_webservice = classe.exige_polo_passivo_por_sistemas_webservice[index];
                                if(classe_webservice.sistema_webservice == this._sistema_webservice){
                                    if(classe_webservice.exige_polo_passivo){
                                        document.querySelector(".alert-reu").style = 'display: block !important';
                                        let btn_peticionar = document.querySelector(".btn-peticionar");
                                        if(btn_peticionar){
                                            btn_peticionar.disabled = 'disabled';
                                        }
                                    }
                                }
                            }
                        }
                        option.setAttribute('selected', 'selected');
                        this._input_classe
                            .parentElement.querySelector('div a span')
                            .textContent = classe.nome;
                    }
                    this._input_classe.appendChild(option);
                });

                load.remove();
                this.desativarInputsNoLoad(!this._pode_editar);

            });
        }
    }

    popularInputAssuntoPrincipal(assunto_principal_selecionado, assuntos_secundarios_selecionados){

        let load_assunto_principal = this._load.cloneNode(true);
        let load_assunto_secundario = this._load.cloneNode(true);

        if (this._input_assunto_principal !== null && this._input_assuntos_secundarios !== null) {
            this._input_assunto_principal.parentElement.appendChild(load_assunto_principal);
            this._input_assuntos_secundarios.parentElement.appendChild(load_assunto_secundario);

            this.desativarInputsNoLoad(true);

            // Insere um option fake
            let optionfake = document.createElement('option');
            optionfake.text = '---------';
            this._input_assunto_principal.innerHTML = '';
            this._input_assunto_principal.appendChild(optionfake);
            this._input_assunto_principal
                .parentElement.querySelector('div a span')
                .textContent = '---------';

            this.obterAssuntosviaAPI({'competencia': this._competencia, 'classe': this._classe}).then((assuntos_api) => {
                assuntos_api.forEach((assunto) => {
                    let option = document.createElement('option');
                    option.value = assunto.codigo;
                    option.text = assunto.nome;
                    option.style.textTransform = 'captalize';
                    if(assunto.codigo == assunto_principal_selecionado){
                        let selected_option = option.cloneNode(true);
                        selected_option.setAttribute('selected', 'selected');
                        this._input_assunto_principal.appendChild(selected_option);
                        this._input_assuntos_secundarios.appendChild(option);
                    }
                    else if(assuntos_secundarios_selecionados && assuntos_secundarios_selecionados.includes(assunto.codigo.toString())){
                        let selected_option = option.cloneNode(true);
                        selected_option.setAttribute('selected', 'selected');
                        this._input_assunto_principal.appendChild(option);
                        this._input_assuntos_secundarios.appendChild(selected_option);
                    }
                    else {
                        this._input_assunto_principal.appendChild(option);
                        this._input_assuntos_secundarios.appendChild(option.cloneNode(true));
                    }
                });

                load_assunto_principal.remove();
                load_assunto_secundario.remove();

                // Recria componente select2 para selects de assuntos (obs: só funciona com jQuery)
                $('#id_assunto_principal_form').select2('destroy').select2({dropdownAutoWidth : true});
                $('#id_assuntos_secundarios_form').select2('destroy').select2({dropdownAutoWidth : true});

                this.desativarInputsNoLoad(!this._pode_editar);

            });
        }
    }

    desativarInputsNoLoad(status){
        if (status === null) {
            status = false;
        }

        if (this._input_competencia !== null) {
            this._input_competencia.disabled = status;
        }

        if (this._input_classe !== null) {
            this._input_classe.disabled = status;
        }

        if (this._input_assunto_principal !== null) {
            this._input_assunto_principal.disabled = status;
        }

        if (this._input_assuntos_secundarios !== null) {
            this._input_assuntos_secundarios.disabled = status;
        }
    }

    async obterCompetenciasviaAPI(){
        try {

            const response = await fetch(`/api/v1/procapi/competencias/?ativo=true&sistema_webservice=${this._sistema_webservice}`, new Request({
                method: 'GET',
                headers: this.header
            }));

            const resposta_do_solar_em_json = await response.json();
            return resposta_do_solar_em_json;

        } catch (error) {
            throw new Error(`Não foi possível obter as Competências da API do SOLAR: ${error.message}`);
        }
    }

    async obterClassesviaAPI(filtros){
        try {

            let comarca_selecionada = document.querySelector("#id_comarca").value;
            let url_classes = '/api/v1/procapi/classes/';

            if(this._pode_filtrar_classe_assunto_competencia)
            {
                url_classes += `?sistema_webservice=${this._sistema_webservice}&codigo_localidade=${comarca_selecionada}&codigo_competencia=${filtros.competencia}`
            }

            const response = await fetch(url_classes, new Request({
                method: 'GET',
                headers: this.header
            }));

            const resposta_do_solar_em_json = await response.json();
            return resposta_do_solar_em_json;

        } catch (error) {
            throw new Error(`Não foi possível obter as Classes da API do SOLAR: ${error.message}`);
        }
    }

    async obterAssuntosviaAPI(filtros){
        try {

            let comarca_selecionada = document.querySelector("#id_comarca").value;
            let url_assuntos = '/api/v1/procapi/assuntos/';

            if(this._pode_filtrar_classe_assunto_competencia)
            {
                url_assuntos += `?sistema_webservice=${this._sistema_webservice}&codigo_localidade=${comarca_selecionada}&codigo_competencia=${filtros.competencia}&codigo_classe=${filtros.classe}`
            }

            const response = await fetch(url_assuntos, new Request({
                method: 'GET',
                headers: this.header
            }));

            const resposta_do_solar_em_json = await response.json();
            return resposta_do_solar_em_json;

        } catch (error) {
            throw new Error(`Não foi possível obter os Assuntos da API do SOLAR: ${error.message}`);
        }
    }
}
