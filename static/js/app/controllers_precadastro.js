function BuscarPessoaModel($scope, $http)
{

    $scope.salvo = false;
    $scope.salvando = false;
    $scope.tipo_filiacao = ['Mãe', 'Pai'];
    $scope.tipo_telefone = ['Celular', 'Residencial', 'Comercial', 'Recado', 'WhatsApp', 'SMS'];
    $scope.estado_id = 0;
    $scope.tipo_telefone_padrao = 0;

    $scope.limpar = function()
    {
        $scope.pessoa = {id:null, nome:null, data_nascimento:null, cpf:'', rg_numero:null, estado: $scope.estado_id, ganho_mensal:0, numero_membros:1, numero_membros_economicamente_ativos:0, ganho_mensal_membros:0, valor_imoveis:0, valor_moveis:0, valor_bens:0, valor_investimentos:0, valor_outros_bens:0, salario_funcionario: 0};
        $scope.filtro = {id:null, nome:null, data_nascimento:null, cpf:'', filiacao:[{id:null, nome:null, tipo:0}], deficiencias:{}, ganho_mensal:0, numero_membros:1, numero_membros_economicamente_ativos:0, ganho_mensal_membros:0, valor_imoveis:0, valor_moveis:0, valor_bens:0, valor_investimentos:0, valor_outros_bens:0, salario_funcionario:0};
        $scope.last_filtro = '';
        $scope.init_filiacao();
        $scope.init_telefone();
    };

    $scope.modificou = function()
    {
        $scope.salvo = false;
    };

    $scope.enviar_email = function (email, numero) {
        var csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
        $scope.carregandoEmail = true;
        $.ajaxSetup({
            headers: {
                "X-CSRFToken": csrf_token
            }
        });
        $.ajax({
            url: "/atendimento/129/enviar_lembrete_email/",
            data: {
                email: email,
            },
            type: 'POST',
            tryCount: 0,
            retryLimit: 3,
            success: function (data) {
                if (data['error']) {
                    this.tryCount++;
                    if (this.tryCount <= this.retryLimit) {
                        //try again
                        $.ajax(this);
                        return;
                    } else {
                        show_stack_error('Não foi possível reenviar o email. Problema de conexão.');
                        $scope.carregandoEmail = false;
                        return;
                    }
                }
                $scope.carregandoEmail = false;
                show_stack_success('Email reenviado com sucesso.');
            },
            error: function (xhr, textStatus, errorThrown) {
                if (textStatus === 'timeout') {
                    this.tryCount++;
                    if (this.tryCount <= this.retryLimit) {
                        //try again
                        $.ajax(this);
                        return;
                    }
                }
                if (xhr.status === 500) {
                    //handle error
                    this.tryCount++;
                    if (this.tryCount <= this.retryLimit) {
                        //try again
                        $.ajax(this);
                        return;
                    }
                } else {
                    //handle error
                    this.tryCount++;
                    if (this.tryCount <= this.retryLimit) {
                        //try again
                        $.ajax(this);
                        return;
                    }
                }
                show_stack_error('Não foi possível reenviar o email. Problema de conexão.');
                $scope.carregandoEmail = false;
            }
        });
    };
    
    $scope.buscar = function(visualizar)
    {

        $scope.buscou = true;

        //Continua se informar CPF OU nome OU filiacao maiores que 3 characteres
        if($scope.filtro.cpf ||
            ($scope.filtro.nome && $scope.filtro.nome.trim().length >= 3 && $scope.filtro.nome.trim() != $scope.last_filtro) ||
            ($scope.filtro.filiacao[0].nome && $scope.filtro.filiacao[0].nome.trim().length >= 3))
        {

            if($scope.filtro.nome) {
                $scope.last_filtro = $scope.filtro.nome.trim();
            }

            $scope.carregando = true;
            $scope.pessoas = [];

            $http.post('', $scope.filtro).success(function(data){

                $scope.sucesso = data.sucesso;

                if(data.sucesso) {

                    var data_pessoas = data.pessoas;

                    // transforma nome em array de nomes
                    if ($scope.filtro.nome) {
                        var filtro_nome = removeDiacritics($scope.filtro.nome).toUpperCase().split(' ');
                    }
                    else {
                        var filtro_nome = [];
                    }

                    // transforma nome da filiacao em array de nomes
                    if ($scope.filtro.filiacao[0].nome) {
                        var filtro_mae = removeDiacritics($scope.filtro.filiacao[0].nome).toUpperCase().split(' ');
                    }
                    else {
                        var filtro_mae = [];
                    }

                    // marca palavras do filtro que contenham no nome ou filiacao
                    for (var i = 0; i < data_pessoas.length; i++) {

                        data_pessoas[i].nome_mark = removeDiacritics(data_pessoas[i].nome);

                        for (var j = 0; j < filtro_nome.length; j++) {
                            data_pessoas[i].nome_mark = data_pessoas[i].nome_mark.replace(filtro_nome[j], '<mark>' + filtro_nome[j] + '</mark>');
                        }

                        for (var mae = 0; mae < data_pessoas[i].filiacao.length; mae++) {
                            data_pessoas[i].filiacao[mae].nome_mark = removeDiacritics(data_pessoas[i].filiacao[mae].nome);

                            for (var j = 0; j < filtro_mae.length; j++) {
                                data_pessoas[i].filiacao[mae].nome_mark = data_pessoas[i].filiacao[mae].nome_mark.replace(filtro_mae[j], '<mark>' + filtro_mae[j] + '</mark>');
                            }
                        }
                    }

                    var filtro = $scope.filtro.nome ? $scope.filtro.nome.toUpperCase() : '';
                    var result = [];

                    // Atribui nota aos resultados de acordo com a proximidade com o filtro
                    for (var i = 0; i < data_pessoas.length; i++) {

                        var nome = removeDiacritics(data_pessoas[i].nome).split(' ');
                        var total = 0;

                        data_pessoas[i].nota = 0;

                        for (var f = 0; f < filtro_nome.length; f++) {

                            var nota = Math.pow(0.1, (f - 1));

                            for (var n = 0; n < nome.length; n++) {
                                if (filtro_nome[f] == nome[n]) {
                                    nota = Math.pow(0.1, (f + 1)) * (n + 1);
                                    break;
                                }
                            }

                            data_pessoas[i].nota = data_pessoas[i].nota + nota;

                        }

                    }

                    // Ordena resultado de acordo com a nota
                    data_pessoas.sort(function (a, b) {
                        return a.nota - b.nota
                    });

                    // Ordena alfabeticamente resultados com a mesma nota
                    var i = 0;

                    while (data_pessoas.length > 0) {
                        if (data_pessoas.length == i || data_pessoas[i].nota != data_pessoas[0].nota) {
                            result = result.concat(splice_and_sort(data_pessoas, i));
                            i = 0;
                        }
                        i++;
                    }

                    // Atualiza dados do angular;
                    $scope.pessoas = result;

                    if (result.length) {

                        if (($scope.filtro.cpf && $scope.filtro.cpf != '') || visualizar) {

                            $scope.filtro = {
                                'id': result[0].id,
                                'nome': result[0].nome,
                                'data_nascimento': result[0].data_nascimento,
                                'filiacao': result[0].filiacao,
                                'cpf': result[0].cpf
                            };

                        }

                    }

                    // Faz tratamento do CSS de tooltip-error. Deixa o fundo preto padrão
                    $('#nome').removeClass('tooltip-error').attr('data-trigger', 'manual').attr('data-original-title', 'Pressione ENTER para buscar').tooltip('show');
                }
                else {
                    // Define mensagem de erro caso a consulta retorne erro ou alguma limitação
                    $scope.mensagem = data.mensagem;

                    // Faz tratamento do CSS de tooltip-error. Deixa o fundo vermelho com o arquivo sisat.css
                    $('#nome').addClass('tooltip-error').attr('data-trigger', 'manual').attr('data-original-title', data.mensagem).tooltip('show');
                }
                $scope.carregando = false;
            });
        }

    };

    $scope.cadastrar = function(estado_id, comarca_id)
    {

        if($scope.PesquisaForm.$valid)
        {

            $scope.pessoa = $scope.filtro;
            $scope.pessoa.estado = estado_id;
            $scope.pessoa.municipio = comarca_id;
            $scope.init_filiacao();
            $scope.init_telefone(true);

            $('#myTab a:last').tab('show');
            if($scope.pessoa.tipo == 1){
                $('#myTab2 a:last').tab('show'); 
            }

        }

    };

    $scope.confirmar = function(obj)
    {

        $scope.salvando = true;
        $scope.pessoa = obj;
        

        $scope.init_filiacao();
        $scope.init_telefone();

        $http.post('/atendimento/129/pessoa/set/'+$scope.pessoa.id+'/').success(function(data){

            $scope.pessoa = data.pessoa;
            $scope.pessoa.cpf_salvo = $scope.pessoa.cpf;
            $scope.pessoa.estado = ($scope.pessoa.estado ? $scope.pessoa.estado : $scope.estado_id);

            $scope.init_telefone();
            $scope.listar_municipios();

            $scope.salvando = false;

            $('#myTab a:last').tab('show');

            if($scope.pessoa.tipo == 1){
                $('#myTab2 a:last').tab('show'); 
            }else{
                $('#myTab2 a:first').tab('show'); 
            }

            if($scope.salvo) {
                $('#btn-modal-atendimento').click();
            }

        });

    };

    // FILIACAO
    $scope.init_filiacao = function()
    {

        if($scope.pessoa.filiacao == undefined) {
            $scope.pessoa.filiacao = [];
        }

        while($scope.pessoa.filiacao.length < 1) {
            $scope.adicionar_filiacao();
        }

    };

    $scope.get_filiacao = function(obj)
    {
        if(obj) {
            return $scope.tipo_filiacao[obj.tipo];
        }
        else {
            return $scope.tipo_filiacao[$scope.filtro.filiacao[0].tipo];
        }
    };

    $scope.set_filiacao = function(val, obj)
    {
        if(obj) {
            obj.tipo = val;
        }
        else {
            $scope.filtro.filiacao[0].tipo = val;
        }
    };

    $scope.adicionar_filiacao = function()
    {
        $scope.pessoa.filiacao.push({id:null, nome: null, tipo: 0});
    };

    $scope.remover_filiacao = function(index)
    {
        $http.post('/assistido/filiacao/excluir/', $scope.pessoa.filiacao[index]).success(function(data){
            $scope.pessoa.filiacao.splice(index, 1);
        });
    };

    // TELEFONE
    $scope.init_telefone = function(limpar)
    {

        if($scope.pessoa.telefones == undefined || limpar) {
            $scope.pessoa.telefones = [];
        }

        while($scope.pessoa.telefones.length < 1) {
            $scope.adicionar_telefone();
        }

        $scope.processar_telefone($scope.pessoa.telefones); // telefone < ddd, numero

    };

    $scope.get_tipo_telefone = function(obj)
    {
        return $scope.tipo_telefone[obj.tipo];
    };

    $scope.set_tipo_telefone = function(val, obj)
    {
        obj.tipo = val;
    };

    $scope.adicionar_telefone = function()
    {
        $scope.pessoa.telefones.push({id: null, ddd: null, numero: null, telefone: null, tipo: $scope.tipo_telefone_padrao});
    };

    $scope.remover_telefone = function(index)
    {
        $http.post(`/assistido/${$scope.pessoa.id}/telefone/excluir/`, $scope.pessoa.telefones[index]).success(function(data){
            $scope.pessoa.telefones.splice(index, 1);
        });
    };

    $scope.processar_telefone = function(telefones)
    {
        if(telefones)
        {
            for(var i = 0; i < telefones.length; i++)
            {
                if(telefones[i].telefone)
                {
                    telefones[i].ddd = telefones[i].telefone.substring(0,2);
                    telefones[i].numero = telefones[i].telefone.substring(2);
                }
                else
                {
                    telefones[i].telefone = telefones[i].ddd + telefones[i].numero;
                }
            }
        }
    };

    $scope.consultaCep = function() {
        if($scope.pessoa.cep) {
            $http.get(`/endereco/get_by_cep/${$scope.pessoa.cep}/`).then((data) => {
                let response = data.data;

                if('erro' in response) {
                    show_stack_error('O CEP informado é inválido.', true);
                } else {
                    $scope.pessoa.logradouro = (response['logradouro']).toUpperCase();
                    $scope.pessoa.bairro = (response['bairro']).toUpperCase();
                    $scope.pessoa.estado = response['estado_id'];
                    $scope.pessoa.municipio = response['municipio_id'];
                    $scope.listar_municipios();

                }
            });
        } else {
            $scope.pessoa.logradouro = '';
            $scope.pessoa.bairro = '';
            $scope.pessoa.municipio = '';
            $scope.pessoa.estado = '';
        }
    }

    $scope.salvar = function()
    {   

        var tab = document.getElementById("myTab2").getAttribute('value');

        if (tab == 0)
        {
            if($('#CadastroForm').valid())
            {

                $scope.salvando = true;
                $scope.pessoa.tipo_cadastro = 10; // cadastro simplificado
                $scope.init_telefone();

                show_stack('Salvando...', false);

                var dados = {
                    'pessoa': $scope.pessoa,
                    'enderecos': {}
                };

                $http.post($('#CadastroForm').attr('action'), dados).success(function(data){

                    $scope.salvo = data.success;

                    if(data.id)
                    {
                        $scope.pessoa.id = data.id;
                    }

                    if(data.success)
                    {

                        if($scope.salvar_e_confirmar)
                            $scope.confirmar(data.pessoa);
                        else if($scope.salvar_e_vincular)
                            $scope.vincular_pessoa();
                        else
                            window.location.reload(true);

                        show_stack_success('Registro gravado com sucesso!');
                    }
                    else
                    {
                        var msg = '';
                        for(var e = 0; e < data.errors.length; e++) {
                            msg += '<li><b>' + data.errors[e][0] + '</b>: ' + data.errors[e][1] + '</li>';
                        }
                        show_stack_error('<b>Erro ao salvar!</b><ul>' + msg + '</ul>', false, 'error');
                    }

                    $scope.salvando = false;

                }).error(function(){

                    show_stack_error('Erro ao salvar! Verifique se todos os campos foram preenchidos corretamente.');
                    $scope.salvando = false;

                });

            }
            else
            {
                $('.alert-error').removeClass('hidden'); //mostra mensagem de erro
            }

        } 
       
        else
        {
            if($('#CadastroFormPJ').valid())
            {

                $scope.salvando = true;
                $scope.pessoa.tipo_cadastro = 10; // cadastro simplificado
                $scope.pessoa.tipo = 1; // cadastro pessoa jurídica
                $scope.init_telefone(); // telefone > ddd, numero

                show_stack('Salvando...', false);

                var dados = {
                    'pessoa': $scope.pessoa,
                    'enderecos': {}
                };

                $http.post($('#CadastroFormPJ').attr('action'), dados).success(function(data){

                    $scope.salvo = data.success;

                    if(data.id)
                    {
                        $scope.pessoa.id = data.id;
                    }

                    if(data.success)
                    {
                        $scope.confirmar(data.pessoa);
                        show_stack_success('Registro gravado com sucesso!');
                    }
                    else
                    {
                        var msg = '';
                        for(var e = 0; e < data.errors.length; e++) {
                            msg += '<li><b>' + data.errors[e][0] + '</b>: ' + data.errors[e][1] + '</li>';
                        }
                        show_stack_error('<b>Erro ao salvar!</b><ul>' + msg + '</ul>', false, 'error');
                    }

                    $scope.salvando = false;

                }).error(function(){

                    show_stack_error('Erro ao salvar! Verifique se todos os campos foram preenchidos corretamente.');
                    $scope.salvando = false;

                });

            }
            else
            {
                $('.alert-error').removeClass('hidden'); //mostra mensagem de erro
            }
        }
    };

    $scope.vincular_pessoa = function()
    {

        var tipo_pessoa = document.getElementById("tipo_cadastro").getAttribute('value');

        var dados_vincular = {
            'pessoa_id': $scope.pessoa.id,
            'atendimento_id': $scope.atendimento.id,
            'responsavel': 0,
            'cadastrado': 0,
            'tipo_envolvido': tipo_pessoa
        };

        $http.post('/atendimento/recepcao/adicionar_pessoa/', dados_vincular).success(
            function(data){
                if (data.sucesso) {
                    $('#modal-pre-cadastro').modal('hide');
                    show_stack_success(data.pessoa.nome_tratado + ' vinculado(a)!');
                    window.location = '/atendimento/recepcao/marcados/' + $scope.atendimento.numero + '/?tab=' + String(parseInt(tipo_pessoa)+1);
                }
                else {
                    show_stack_error(data.mensagem);
                }
            }
        ).error(
            function(data){
                show_stack_error('Erro ao vincular pessoa!');
            }
        );

    };

    $scope.carregar = function()
    {
        $http.get('/atendimento/129/pessoa/get/').success(function(data){
            if(data.id)
            {

                $scope.pessoa = data;
                $scope.pessoa.cpf_salvo = $scope.pessoa.cpf;
                $scope.pessoa.estado = ($scope.pessoa.estado ? $scope.pessoa.estado : $scope.estado_id);

                $scope.init_filiacao();
                $scope.init_telefone();

                if(data.municipio) {
                    $scope.salvo = true;
                }

            }
        });
    };

    $scope.carregar_pessoa = function(pessoa_id){
        $http.get(`/assistido/${pessoa_id}/json/get/`).success(function(data){

            $scope.pessoa = data;

            $scope.init_filiacao();
            $scope.init_telefone();
            $scope.listar_municipios();

            if($scope.pessoa.tipo==0)
                $('#myTab2 a:first').tab('show');
            else
                $('#myTab2 a:last').tab('show');

        });
    }

    $scope.init_municipios = function()
    {
        dados = [];
        $('select[name="municipio"] option').each(function(i){
            if(!isNaN(parseInt($(this).val()))) {
                dados.push({'id': parseInt($(this).val()), 'nome': $(this).text()});
            }
        });
        $scope.municipios = dados;
    };

    $scope.listar_municipios = function()
    {
        $http.get('/estado/'+$scope.pessoa.estado+'/municipios/').success(function(data){
            $scope.municipios = data;
        });
    };

    $scope.buscar_key = function(e)
    {
        // Busca automatico se enter (13) ou espaco (32)
        if(e.which==13)
        {
            $scope.buscar();
            // Cancela evento padrao do enter (limpar form)
            e.preventDefault();
        }
    };

    function splice_and_sort(arr, qtd)
    {

        var arr_sort = arr.splice(0, qtd);

        arr_sort.sort(function(a,b){
            return (a.nome < b.nome) ? -1 : (a.nome > b.nome) ? 1 : 0;
        });

        return arr_sort;
    }

    $scope.init = function(estado_id, salvar_e_confirmar, salvar_e_vincular, atendimento, tipo_telefone_padrao)
    {

        $scope.estado_id = estado_id;
        $scope.tipo_telefone_padrao = tipo_telefone_padrao;
        $scope.limpar();
        $scope.init_municipios();
        $scope.salvar_e_confirmar = salvar_e_confirmar;
        $scope.salvar_e_vincular = salvar_e_vincular;
        $scope.atendimento = atendimento;

        if(salvar_e_confirmar)
            $scope.carregar();

    }
    
    $scope.init_clean = function(estado_id)
    {
        $scope.estado_id = estado_id;
        $scope.limpar();
        $scope.init_municipios();
    }

	$scope.$on('BuscarPessoaModel:carregar_pessoa', function(event, args){
		$scope.carregar_pessoa(args);
	});

}

function AtendimentosPessoaCtrl($scope, $http)
{

    $scope.atendimento = {};

    $scope.carregar = function(numero)
    {
        if($scope.atendimento[numero] == undefined)
        {
            $scope.atendimento[numero] = {carregando: true};
            $http.get('/atendimento/($0)/arvore/json/get/'.replace('($0)', numero)).success(function(data){
                $scope.atendimento[numero] = data;
            });
        }
    }
    
    //config.LEMBRETE_EMAIL_AGENDAMENTO_ONLINE é a mensagem que é enviada, pois não tem procedimentos
    $scope.reenviar_email = function (email, numero) {
        var csrf_token = document.getElementById("csrf_token").value;
        $scope.carregandoEmail = true;
        $.ajaxSetup({
            headers: {
                "X-CSRFToken": csrf_token
            }
        });

        $.ajax({
            url: "/atendimento/129/enviar_lembrete_email/",
            data: {
                email: email,
                numero: numero,
            },
            type: 'POST',
            tryCount: 0,
            retryLimit: 3,
            success: function (data) {
                if (data['error']) {
                    this.tryCount++;
                    if (this.tryCount <= this.retryLimit) {
                        //try again
                        $.ajax(this);
                        return;
                    } else {
                        show_stack_error('Não foi possível reenviar o email. Problema de conexão.');
                        $scope.carregandoEmail = false;
                        return;
                    }
                }
                else{
                    $scope.carregandoEmail = false;
                    show_stack_success('Email reenviado com sucesso.');
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                if (textStatus === 'timeout') {
                    this.tryCount++;
                    if (this.tryCount <= this.retryLimit) {
                        //try again
                        $.ajax(this);
                        return;
                    }
                }
                else if (xhr.status === 500) {
                    //handle error
                    this.tryCount++;
                    if (this.tryCount <= this.retryLimit) {
                        //try again
                        $.ajax(this);
                        return;
                    }
                } else {
                    //handle error
                    this.tryCount++;
                    if (this.tryCount <= this.retryLimit) {
                        //try again
                        $.ajax(this);
                        return;
                    }
                }
                show_stack_error('Não foi possível reenviar o email. Problema de conexão.');
                $scope.carregandoEmail = false;
            }
        });
    };

}

function ReclamacaoCtrl($scope, $http) {

    $scope.requisicaoAcontecendo = false;

    $scope.mudarEstadoDaRequisicao = function() {
        $scope.requisicaoAcontecendo = !$scope.requisicaoAcontecendo;
    }

    $scope.enviarReclamacao = function() {
        $scope.mudarEstadoDaRequisicao();

        let content = {
            reclamacaoDetalhes: $scope.detalhesDenuncia,
            nomeDoEstabelecimento: $scope.nomeDoEstabelecimento,
            tipoDoEstabelecimento: $scope.tipoDoEstabelecimento,
            logradouroDenuncia: $scope.logradouroDenuncia,
            bairroId: $scope.bairroId,
            numeroDenuncia: $scope.numeroDenuncia,
            cepDenuncia: $scope.cepDenuncia,
            complementoDenuncia: $scope.complementoDenuncia,
            municipioId: $scope.municipioId
        };

        $http.post('/atendimento/129/enviar_reclamacao_email/', content).then((data) => {
            window.location.reload(true);
        }, () => {
            show_stack_error('Houve um problema ao efetuar a solicitação, favor entrar em contato com o suporte.', true);
        });
    }

    $scope.detalhesToUpperCase = function() {
        if($scope.detalhesDenuncia) {
            $scope.detalhesDenuncia = ($scope.detalhesDenuncia).toUpperCase();
        }
    }

    $scope.consultarCep = function() {
        if($scope.cepDenuncia) {
            $http.get(`/endereco/get_by_cep/${$scope.cepDenuncia}/`).then((data) => {
                let response = data.data;

                if('erro' in response) {
                    show_stack_error('O CEP informado é inválido.', true);
                } else {
                    $scope.logradouroDenuncia = (response['logradouro']).toUpperCase();
                    $scope.bairroDenuncia = (response['bairro']).toUpperCase();
                    $scope.bairroId = response['bairro_id'];
                    $scope.municipioId = response['municipio_id'];
                }
            });
        } else {
            $scope.logradouroDenuncia = '';
            $scope.bairroDenuncia = '';
            $scope.bairroId = '';
            $scope.municipioId = '';
        }
    }

}
