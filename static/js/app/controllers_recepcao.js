function RecepcaoMarcadosCtrl($scope, fileUpload, $http, $timeout, AreaAPI, DefensoriaAPI, FormaAtendimentoAPI)
{

    $scope.filtro = {'query': null};
    $scope.atendimentos = null;
    $scope.guiche = null;
    $scope.atendendo_id = null;
    $scope.pnes = {'nome' : ''};

    $scope.carregando = null;
    $scope.carregando_atendimentos_qtd = false;
    $scope.carregando_aguardando = false;
    $scope.carregando_atrasados = false;
    $scope.carregando_liberados = false;
    $scope.carregando_em_atendimento = false;
    $scope.carregando_atendidos = false;

    $scope.atendimentos_assincrono = [];

    $scope.atendimentos_aguardando = [];
    $scope.atendimentos_atrasados = [];
    $scope.atendimentos_liberados = [];
    $scope.atendimentos_em_atendimento = [];
    $scope.atendimentos_atendidos = [];

    $scope.atendimentos_qtd = 0;
    $scope.atendimentos_aguardando_qtd = null;
    $scope.atendimentos_atrasados_qtd = null;
    $scope.atendimentos_liberados_qtd = null;
    $scope.atendimentos_em_atendimento_qtd = null;
    $scope.atendimentos_atendidos_qtd = null;

    // utilizado para carregar o popover com dados do atendimento
	$scope.atendimento_popover = null;
	$scope.atendimentos_popover = {};
	$scope.assistido = null;
	$scope.assistidos = {};
    $scope.motivos_exclusao = [];

	$scope.get_atendimento = function(atendimento)
	{
        $scope.atendimento_popover = null;

		if($scope.atendimentos_popover[atendimento]) {
            $scope.atendimento_popover = $scope.atendimentos_popover[atendimento];
        }
		else
		{
			$scope.atendimentos_popover[atendimento] = {};
			$http.get('/atendimento/'+atendimento+'/json/get/').success(function(data){
				$scope.atendimento_popover = data;
				$scope.atendimentos_popover[atendimento] = data;
				$scope.motivos_exclusao = data.motivos_exclusao;
			});
		}
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

    $scope.popover = function(obj)
    {

        var content = '';
        for(var i = 0; i < obj.telefones.length; i++) {
            content += '(' + obj.telefones[i].ddd + ') ' + obj.telefones[i].numero + '<br/>';
        }

        return {"title": obj.requerente, "content": content};
    };

    $scope.alterar_guiche = function() {
        $http.post('/atendimento/recepcao/alterar/guiche/').success(function(data){
            window.location = '/atendimento/recepcao/';
        });
    };

    $scope.excluir = function(atendimento)
    {
        $scope.atendimento = atendimento;
        $('#modal-excluir').modal();
    };

    $scope.realizar_pre_atendimento = function(atendimento_numero) {
        var prev = window.location.href.replace(/^(?:\/\/|[^\/]+)*\//, "");
        window.location = '/atendimento/recepcao/marcados/' + atendimento_numero + '?prev=/' + prev;
    };

    $scope.set_atendimento = function(atendimento) {
        $scope.atendimento = atendimento;
    };

    $scope.buscar_atendimentos = function(status, cont)
    {
        $scope.carregando_atendimentos_qtd = true;

        var url = 'get/?status=' + status;

        if (cont == true) {
            url += '&cont=1';
        }

        $http.get(url).success(function(data){
            if (status == 1) {
                if (cont == false) {
                    $scope.atendimentos_aguardando = data;
                    $scope.atendimentos = $scope.atendimentos_aguardando;

                    $scope.atendimentos_aguardando_qtd = $scope.atendimentos_aguardando.length;
                    $scope.buscar_atendimentos_qtd(status);
                }
                else {
                    $scope.atendimentos_aguardando_qtd = data['qtd'];
                }

                $scope.carregando_aguardando = false;
            }
            else if (status == 2) {
                if (cont == false) {
                    $scope.atendimentos_atrasados = data;
                    $scope.atendimentos = $scope.atendimentos_atrasados;

                    $scope.atendimentos_atrasados_qtd = $scope.atendimentos_atrasados.length;
                    $scope.buscar_atendimentos_qtd(status);
                }
                else {
                    $scope.atendimentos_atrasados_qtd = data['qtd'];
                }

                $scope.carregando_atrasados = false;
            }
            else if (status == 3) {
                if (cont == false) {
                    $scope.atendimentos_liberados = data;
                    $scope.atendimentos = $scope.atendimentos_liberados;

                    $scope.atendimentos_liberados_qtd = $scope.atendimentos_liberados.length;
                    $scope.buscar_atendimentos_qtd(status);
                }
                else {
                    $scope.atendimentos_liberados_qtd = data['qtd'];
                }

                $scope.carregando_liberados = false;
            }
            else if (status == 4) {
                if (cont == false) {
                    $scope.atendimentos_em_atendimento = data;
                    $scope.atendimentos = $scope.atendimentos_em_atendimento;

                    $scope.atendimentos_em_atendimento_qtd = $scope.atendimentos_em_atendimento.length;
                    $scope.buscar_atendimentos_qtd(status);
                }
                else {
                    $scope.atendimentos_em_atendimento_qtd = data['qtd'];
                }

                $scope.carregando_em_atendimento = false;
            }
            else if (status == 5) {
                if (cont == false) {
                    $scope.atendimentos_atendidos = data;
                    $scope.atendimentos = $scope.atendimentos_atendidos;

                    $scope.atendimentos_atendidos_qtd = $scope.atendimentos_atendidos.length;
                    $scope.buscar_atendimentos_qtd(status);
                }
                else {
                    $scope.atendimentos_atendidos_qtd = data['qtd'];
                }

                $scope.carregando_atendidos = false;
            }

            $scope.somar_atendimentos_qtd();
            $scope.carregando = false;
        });
    };

    $scope.buscar_atendimentos_aguardando = function()
    {
        if ($scope.atendimentos_aguardando.length !== $scope.atendimentos_aguardando_qtd) {
            $scope.carregando_aguardando = true;
            $scope.buscar_atendimentos(1, false);
        }
        $scope.atendimentos = $scope.atendimentos_aguardando;
    };

    $scope.buscar_atendimentos_atrasados = function()
    {
        if ($scope.atendimentos_atrasados.length !== $scope.atendimentos_atrasados_qtd) {
            $scope.carregando_atrasados = true;
            $scope.buscar_atendimentos(2, false);
        }
        $scope.atendimentos = $scope.atendimentos_atrasados;
    };

    $scope.buscar_atendimentos_liberados = function() {
        if ($scope.atendimentos_liberados.length !== $scope.atendimentos_liberados_qtd) {
            $scope.carregando_liberados = true;
            $scope.buscar_atendimentos(3, false);
        }
        $scope.atendimentos = $scope.atendimentos_liberados;
    };

    $scope.buscar_atendimentos_em_atendimento = function() {
        if ($scope.atendimentos_em_atendimento.length !== $scope.atendimentos_em_atendimento_qtd) {
            $scope.carregando_em_atendimento = true;
            $scope.buscar_atendimentos(4, false);
        }
        $scope.atendimentos = $scope.atendimentos_em_atendimento;
    };

    $scope.buscar_atendimentos_atendidos = function()
    {
        if ($scope.atendimentos_atendidos.length !== $scope.atendimentos_atendidos_qtd) {
            $scope.carregando_atendidos = true;
            $scope.buscar_atendimentos(5, false);
        }
        $scope.atendimentos = $scope.atendimentos_atendidos;
    };

    /**
     * Soma todas as variáveis de qtd para ter o total de atendimentos.
     */
    $scope.somar_atendimentos_qtd = function() {
        $scope.carregando_atendimentos_qtd = true;
        $scope.carregando_aguardando = true;
        $scope.carregando_atrasados = true;
        $scope.carregando_liberados = true;
        $scope.carregando_em_atendimento = true;
        $scope.carregando_atendidos = true;

        $scope.atendimentos_qtd = $scope.atendimentos_aguardando_qtd
            + $scope.atendimentos_atrasados_qtd
            + $scope.atendimentos_liberados_qtd
            + $scope.atendimentos_em_atendimento_qtd
            + $scope.atendimentos_atendidos_qtd;

        $scope.carregando_atendimentos_qtd = false;
        $scope.carregando_aguardando = false;
        $scope.carregando_atrasados = false;
        $scope.carregando_liberados = false;
        $scope.carregando_em_atendimento = false;
        $scope.carregando_atendidos = false;
    };

    /**
     * Busca as quantidades de todos os status menos o passado no parâmetro.
     * A ideia é atualizar a quantidade sempre que clicar em uma aba.
     * Caso a qtd da aba seja diferente do tamanho do array a lista de atendimentos será atualizada.
     * */
    $scope.buscar_atendimentos_qtd = function(status) {
        for (var i=1; i<=5; i++) {
            if (i !== status) {
                $scope.buscar_atendimentos(i, true);
            }
        }
    };

    $scope.filtro_personalizado = function(filter){

        var filter = {};

        if($scope.selected_cpf!= ""){
            filter['requerente'] = {'cpf': $scope.selected_cpf};
        }

        if($scope.selected_nome_requerente != ""){
            filter['requerente'] = {'nome': $scope.selected_nome_requerente};
        }

        if($scope.selected_area != null){
            filter['area'] = $scope.selected_area;
        }

        $scope.filtro_campos = filter;

    }

    $scope.init = function(comarca_id)
    {
        $scope.carregando_atendimentos_qtd = true;
        $scope.guiche = guiche;

        $scope.atendimentos = [];
        $scope.buscar_atendimentos_aguardando();

        $scope.formas_atendimento = {};
        $scope.defensorias = [];
        $scope.areas = [];

        $scope.selected_cpf = '';
        $scope.selected_nome_requerente = '';
        $scope.selected_area = null;
        $scope.selected_defensoria = null;

        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        AreaAPI.get({limit:1000}, function(data){
            $scope.areas = data.results;
        });

        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        DefensoriaAPI.get({comarca:comarca_id, limit:1000}, function(data){
            $scope.defensorias = data.results;
        });

        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        FormaAtendimentoAPI.get({limit:1000}, function(data){
            // Transforma array em object p/ facilitar consultas pelo id
            for(var i = 0; i < data.results.length; i++)
            {
                $scope.formas_atendimento[data.results[i].id] = data.results[i];
            }
        });

    }

    $scope.chamar = function(atendimento) {

        $http.post('/atendimento/recepcao/chamar/', {'atendimento': atendimento, 'tipo': 0}).success(function(data) {

            if (data['success']) {
                show_stack_success("Notificado");
            }
            else {
                if (data['msg'] !== '')
                    show_stack_error(data['msg']);
                else
                    show_stack_error("Erro!");
            }
        });
    }

}

function RecepcaoAtendimentoCtrl($scope, $http, fileUpload, ContribDocumentoServiceAPI)
{

    $scope.atuacao = null;
    $scope.atendimento = null;
    $scope.predicate = '-responsavel';
    $scope.form_buscar_requerido = false;
    $scope.form_buscar_requerente = false;
    $scope.filtro = {'query': null, 'request': 0, 'atendimento_id': null};
    $scope.last_filtro = '';
    $scope.resultado_busca = null;
    $scope.tipo_edicao = null;
    $scope.editar_cadastrado = null;
    $scope.pessoa_visualizacao = null;
    $scope.requerente_responsavel = null;
    $scope.documento_edicao = {};
    $scope.carregando = null;
    $scope.assistidos = {};

    $scope.tipo_busca_requerente_requerido = '';

    $scope.carregando_requerentes = false;
    $scope.carregando_requeridos = false;
    $scope.carregando_documentos = false;

    $scope.show_buscar = function(tipo)
    {
        $scope.tipo_busca_requerente_requerido = tipo;
        $scope.resultado_busca = null;
        $scope.filtro.query = null;
        $scope.buscou = false;

        $scope.limpar_ultima_busca_pessoa();

        if(tipo==='requerido') {
            $scope.msg_erro_busca_pessoa = null;

            $scope.form_buscar_requerido = !$scope.form_buscar_requerido;
            $scope.form_buscar_requerente = false;
        } else {
            $scope.msg_erro_busca_pessoa = null;

            $scope.form_buscar_requerente = !$scope.form_buscar_requerente;
            $scope.form_buscar_requerido = false;
        }
    };

    $scope.msg_erro_busca_pessoa = null;

    /* Utilizado para buscar pessoa, em adicionar requerente/requerido */
    $scope.buscar = function(visualizar)
    {
        //Continua se informar CPF OU nome OU filiacao maiores que 3 characteres
        if($scope.filtro.query && $scope.filtro.query.trim().length >= 3 && $scope.filtro.query.trim() !== $scope.last_filtro)
        {
            $scope.carregando = true;
            $scope.resultado_busca = null;
            $scope.filtro.request += 1;

            if($scope.filtro.query) {
                $scope.last_filtro = $scope.filtro.query.trim();
            }

            $scope.filtro['atendimento_id'] = $scope.atendimento.atendimento.id;

            $http.post('/atendimento/recepcao/buscar_pessoa/', $scope.filtro).success(function(data){

                if (data.request == $scope.filtro.request) {
                    if (data.sucesso) {
                        data = data.pessoas;

                        // transforma nome em array de nomes
                        if ($scope.filtro.query) {
                            var filtro_nome = removeDiacritics($scope.filtro.query).toUpperCase().split(' ');
                        }
                        else {
                            var filtro_nome = [];
                        }

                        // marca palavras do filtro que contenham no nome ou filiacao
                        for(var i=0; i < data.length; i++)
                        {
                            var pessoa = data[i];

                            pessoa.nome_mark = removeDiacritics(pessoa.nome_tratado);

                            for(var j = 0; j < filtro_nome.length; j++)
                            {
                                var aux = filtro_nome[j];

                                var re = new RegExp(aux, "g");
                                pessoa.nome_mark = pessoa.nome_mark.replace(re, '<mark>'+ aux +'</mark>');
                            }
                        }

                        var filtro = $scope.filtro.nome ? $scope.filtro.nome.toUpperCase() : '';
                        var result = [];

                        // Atribui nota aos resultados de acordo com a proximidade com o filtro
                        for (var i = 0; i < data.length; i++) {

                            var nome = removeDiacritics(pessoa.nome).split(' ');
                            var total = 0;

                            pessoa.nota = 0;

                            for (var f = 0; f < filtro_nome.length; f++) {

                                var nota = Math.pow(0.1, (f - 1));

                                for (var n = 0; n < nome.length; n++) {
                                    if (filtro_nome[f] === nome[n]) {
                                        nota = Math.pow(0.1, (f + 1)) * (n + 1);
                                        break;
                                    }
                                }

                                pessoa.nota = pessoa.nota + nota;
                            }
                        }

                        // Ordena resultado de acordo com a nota
                        data.sort(function (a, b) {
                            return a.nota - b.nota
                        });

                        // Ordena alfabeticamente resultados com a mesma nota
                        var i = 0;

                        while (data.length > 0) {
                            if (data.length === i || pessoa.nota !== data[0].nota) {
                                result = result.concat(splice_and_sort(data, i));
                                i = 0;
                            }
                            i++;
                        }

                        // Atualiza dados do angular;
                        $scope.resultado_busca = result;

                        if (result.length) {

                            if (($scope.filtro.cpf && $scope.filtro.cpf !== '') || visualizar) {

                                $scope.filtro = {
                                    'id': result[0].id,
                                    'nome': result[0].nome,
                                    'data_nascimento': result[0].data_nascimento,
                                    'filiacao': result[0].filiacao,
                                    'cpf': result[0].cpf
                                };

                            }

                        }

                        $scope.msg_erro_busca_pessoa = null;
                        $scope.buscou = true;
                    }
                    else {
                        $scope.msg_erro_busca_pessoa = data.mensagem;
                    }
                }
                else
                {
                    console.log('Request ' + data.request + ' ignorado! Registros: ' + data.pessoas.length);
                }

            $scope.carregando = false;

            });
        }

    };

    $scope.buscar_key = function(e)
    {
        // Busca automatico se enter (13)
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

    $scope.buscar_pessoa = function(tipo)
    {
        if($scope.filtro.query.length > 3) {
            $http.post('/atendimento/recepcao/buscar_pessoa/', $scope.filtro).success(function(data){
                $scope.resultado_busca = data;
            });
        }
    };

    $scope.visualizar_pessoa = function(assistido, tipo, index, editar_cadastrado)
    {
        $scope.pessoa_visualizacao = assistido;
        $scope.pessoa_visualizacao.index = index;
        $scope.editar_cadastrado = editar_cadastrado;

        // 0 = requerente; 1 = requerido;
        $scope.tipo_edicao = tipo;

        $('#modal-visualizar-pessoa').modal();
    };

    $scope.editar_cadastrado = false;

    $scope.remover_pessoa = function(pessoa)
    {
        if(pessoa === undefined) {
            pessoa = $scope.pessoa_visualizacao;

            if (pessoa.eh_requerente === true) {
                $scope.carregando_requerentes = true;
            }
            else if (pessoa.eh_requerido === true) {
                $scope.carregando_requeridos = true;
            }

            $http.post('/atendimento/recepcao/remover_pessoa/', {
                'pessoa_id': pessoa.pessoa_id,
                'atendimento_id': $scope.atendimento.atendimento.id
            }).success(function (data) {
                $('#modal-visualizar-pessoa').modal('hide');

                if (data.success) {
                    if (pessoa.eh_requerente === true) {
                        for (var p in $scope.requerentes) {
                            p = $scope.requerentes[p];
                            if (p.pessoa_id === pessoa.pessoa_id) {
                                $scope.requerentes.remove(p);
                            }
                        }

                        // utilizado para reinicializar o botão "Salvar e Liberar"
                        // TODO otimizar para trazer apenas a variável que trata o botão
                        $scope.init($scope.atendimento.atendimento.numero, null);
                        $scope.carregando_requerentes = false;
                    }
                    else {
                        for (var p in $scope.requeridos) {
                            p = $scope.requeridos[p];
                            if (p.pessoa_id === pessoa.pessoa_id) {
                                $scope.requeridos.remove(p);
                            }
                        }

                        $scope.carregando_requeridos = false;
                    }
                    show_stack_success("Pessoa desvinculada do atendimento");
                }
                else {
                    show_stack_error("Erro ao desvincar pessoa do atendimento");
                }
            }).error(function() {
                $('#modal-visualizar-pessoa').modal('hide');
                $scope.carregando_requerentes = false;
                $scope.carregando_requeridos = false;
                show_stack_error("Erro ao desvincar pessoa do atendimento");
            });
        }
        else {
            $scope.pessoa_visualizacao = pessoa;
            $scope.editar_cadastrado = true;
        }
    };

    /* Utilizado para alterar o interessado de atendimentos do Livre */
    $scope.alterar_interessado = function(pessoa_id)
    {
        $scope.carregando_requerentes = true;

        $http.post('/atendimento/recepcao/alterar_interessado/', {
            'pessoa_id': pessoa_id,
            'atendimento_id': $scope.atendimento.atendimento.id
        }).success(function(data){
            if (data.success) {
                for (var requerente in $scope.requerentes) {
                    requerente = $scope.requerentes[requerente];

                    if (requerente.pessoa_id === pessoa_id) {
                        requerente.interessado = true;
                    }
                    else {
                        requerente.interessado = false;
                    }
                }
                show_stack_success('Interessado alterado');
            }
            else {
                show_stack_error('Erro ao salvar interessado');
            }

            $scope.carregando_requerentes = false;
        }).error(function(){
            show_stack_error('Erro ao salvar interessado');
            $scope.carregando_requerentes = false;
        });
    };

    // TODO fazer tratamento para alterar responsável de Requerido e de Requerente
    $scope.alterar_responsavel = function(pessoa, index, editar_cadastrado)
    {
        if(pessoa===undefined) {
            pessoa = $scope.pessoa_visualizacao;
        }

        // requerente = 0; requerido = 1;
        var tipo_envolvido = 0;
        $scope.carregando_requerentes = true;

        if (pessoa.eh_requerido === true) {
            tipo_envolvido = 1;
            $scope.carregando_requeridos = true;
            $scope.carregando_requerentes = false;
        }

        $('#modal-visualizar-pessoa').modal('hide');

        $http.post('/atendimento/recepcao/alterar_responsavel/', {
            'pessoa_id': pessoa.pessoa_id,
            'atendimento_id': $scope.atendimento.atendimento.id,
            'tipo': tipo_envolvido
        }).success(function(data){
            if (pessoa.eh_requerente){
                $scope.requerente_responsavel = pessoa;

                for (var p in $scope.requerentes) {
                    p = $scope.requerentes[p];
                    if (p.pessoa_id === pessoa.pessoa_id){
                        p.responsavel = true;
                    }
                    else {
                        p.responsavel = false;
                    }
                }
                $scope.carregando_requerentes = false;
            }
            else if (pessoa.eh_requerido === true){
                for (var p in $scope.requeridos) {
                    p = $scope.requeridos[p];
                    if (p.pessoa_id === pessoa.pessoa_id){
                        p.responsavel = true;
                    }
                    else {
                        p.responsavel = false;
                    }
                }
                $scope.carregando_requeridos = false;
            }
            show_stack_success((pessoa.eh_requerente === true ? 'Requerente ' : 'Requerido ') + "responsável alterado.");
        });
    };

    // altera o tipo de pessoa envolvida. Se é requerente muda para requerido e vice-versa.
    $scope.alterar_tipo_pessoa_envolvida = function(pessoa)
    {
        var aux = {
            'pessoa_id': pessoa.pessoa_id,
            'atendimento_id': $scope.atendimento.atendimento.id
        };

        $http.post('/atendimento/recepcao/alterar_tipo_pessoa_envolvida/', aux).success(
            function(data){
                if (data.sucesso) {
                    var mensagem = pessoa.nome_tratado + ' movido(a) para';

                    pessoa.responsavel = false;

                    if (pessoa.eh_requerente) {
                        pessoa.eh_requerente = false;
                        pessoa.eh_requerido = true;

                        pessoa.interessado = false;

                        $scope.requeridos.push(pessoa);
                        $scope.requerentes.remove(pessoa);
                        mensagem += ' requeridos';
                    }
                    else if (pessoa.eh_requerido) {
                        pessoa.eh_requerente = true;
                        pessoa.eh_requerido = false;

                        $scope.requerentes.push(pessoa);
                        $scope.requeridos.remove(pessoa);
                        mensagem += ' requerentes';
                    }

                    show_stack_success(mensagem);
                    $scope.init($scope.atendimento.atendimento.numero, null);

                }
                else {
                    show_stack_error('Erro ao salvar pessoa envolvida');
                }
            }
        );
    };

    $scope.editar = function(assistido, tipo, index, editar_cadastrado, processo)
    {
        if(assistido===undefined) {
            assistido = $scope.pessoa_visualizacao;
        }

        if(tipo==undefined) {
            tipo = $scope.tipo_edicao;
        }

        if(editar_cadastrado==undefined) {
            editar_cadastrado = $scope.editar_cadastrado;
        }

        if(processo==undefined) {
            processo = false;
        }

        var responsavel = 0;

        if (assistido.responsavel === true) {
            responsavel = 1;
        }

        window.location = '/assistido/editar/' + assistido.pessoa_id +
            '?tipo=' + tipo +
            '&principal=' + (index==0) +
            '&processo=' + processo +
            '&next=/atendimento/recepcao/marcados/' + $scope.atendimento.atendimento.numero +
            '/tipo/' + tipo +
            '/responsavel/' + responsavel +
            '/cadastrado/' + editar_cadastrado +
            '/pessoa/';
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

	// lista da aba Documentos
	$scope.documentos = [];

	// Busca os documentos da aba Documentos
	$scope.buscar_documentos = function()
	{
	    $scope.documentos = [];
	    $scope.carregando_documentos = true;

        // carrega documentos vinculados ao atendimento
		$http.get('/atendimento/'+ $scope.atendimento.atendimento.numero + '/documento/').success(function(data){

			$scope.documentos = data.uploads;
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

		// carrega tipos de documentos
		ContribDocumentoServiceAPI.get({exibir_em_documento_atendimento:true, ativo:true}, function(data) {
			$scope.tipos = data.results;
		});

	};

	$scope.liberar_atendimento_pj_sem_pf = true;
    $scope.requerentes = [];
    $scope.requeridos = [];

    $scope.buscar_pessoas = function(tipo_pessoa, forcar){
        if (forcar) {
            $scope.buscar_pessoas(tipo_pessoa);
        }
        else {
            if ((tipo_pessoa === 0 && $scope.requerentes.length === 0) ||
                (tipo_pessoa === 1 && $scope.requeridos.length === 0)) {
                $scope.buscar_pessoas(tipo_pessoa);
            }
        }
    };
    /*
    * Busca requerentes e requeridos
    * */
    $scope.buscar_pessoas = function(tipo_pessoa){
        if (tipo_pessoa === 0) {
            $scope.carregando_requerentes = true;
        }
        else {
            $scope.carregando_requeridos = true;
        }

        $http.get('/atendimento/' + $scope.atendimento.atendimento.numero + '/json/get/pessoas/' + tipo_pessoa + '/').success(
            function (data) {
                if (tipo_pessoa === 0) {
                    $scope.requerentes = data.requerentes;
                    $scope.carregando_requerentes = false;
                }
                else {
                    $scope.requeridos = data.requeridos;
                    $scope.carregando_requeridos = false;
                }
            });
    };

    /* Limpar última busca de requerente e requerido */
    $scope.limpar_ultima_busca_pessoa = function() {
        $scope.last_filtro = '';
        $scope.msg_erro_busca_pessoa = null;
    };

    /* Alterna entre abas. Carrega os dados conforme a aba. */
    $scope.alterar_tab = function(tab){
        $scope.limpar_ultima_busca_pessoa();

        if (tab === 1){
            // carrega dados da aba Requentes
            $scope.buscar_pessoas(0, false);
        }
        else if (tab === 2) {
            // carrega dados da aba Requeridos
            $scope.buscar_pessoas(1, false);
        }
        else if (tab === 3) {
            // carrega dados da aba Documentos
            $scope.buscar_documentos();
        }

        // marca a aba selecionada para mostrar o conteúdo
        $('#myTab a:eq('+ tab + ')').tab('show');
    };

    // Status do upload de documento
    $scope.documento_status = {};

    /* Utilizado para monitorar o retorno do upload de documento */
	$scope.$watch('documento_status.success', function() {
		if(typeof($scope.documento_status.success) === 'boolean')
		{
			if($scope.documento_status.success)
			{
			    var editando = false;

			    // verifica se a lista de documentos já possui o documento
			    for (var d in $scope.documentos){
			        if ($scope.documentos[d].id === $scope.documento_status.data.documento.id) {
			            $scope.documentos[d] = $scope.documento_status.data.documento;

			            editando = true;
			            break;
                    }
                }

                if (editando === false){
			        $scope.documentos.push($scope.documento_status.data.documento);
                }

                $('#modal-documentos-atendimento').modal('hide');
				show_stack_success('Documento salvo com sucesso!');
			}
			else
			{
				show_stack_error('Erro ao salvar documento!');
			}

			$scope.documento_status = {};
		}
 	});

    // adicionar Documento por upload
    $scope.adicionar_documento = function() {
        fileUpload.upload(
            '/atendimento/'+ $scope.atendimento.atendimento.numero + '/documento/salvar/',
            $scope.documento_upload,
            $scope.documento_status
        );

        $scope.cancelar_update_documento();
        // a função de limpar o input file está no jQuery do atendimento
    };

    $scope.cancelar_update_documento = function() {
        // TODO: verifiar necessidade desta função

        $scope.documento_upload = {
            'id': null,
            'nome': '',
            'arquivo': null
        };
    };

    $scope.editar_documento = function(documento){
        $scope.documento_upload = angular.copy(documento);
    };

    /* Excluir documento do atendimento */
	$scope.excluir = function(obj)
	{
		if(obj===undefined)
		{
			$http.post('/atendimento/documento/excluir/', {id:$scope.documento_edicao}).success(
			    function(data){
                    if(data.success)
                    {
                        $('#modal-excluir-documento').modal('hide');
                        for (var d in $scope.documentos){
                            d = $scope.documentos[d];

                            if (d.id === $scope.documento_edicao){
                                $scope.documentos.remove(d);
                                break;
                            }
                        }
                        show_stack_success('Documento excluído com sucesso!');
                    }
                    else
                    {
                        show_stack_error('Erro ao excluir documento!');
                    }

                    $scope.documento_edicao = {
                        'nome': ''
                    };
			    }
            );
		}
		else
		{
			$scope.documento_edicao = obj;
		}
	};

    /* INICIO varáveis e funções para tratamento do envio de diligências
    * */

    $scope.defensorias = [];
    $scope.defensoria = null;

    $scope.atuacoes = [];
    $scope.atuacao = null;

    $scope.qualificacoes = [];

    $scope.carregar_dados_diligencia = function(defensor_id){
        $http.get('/nucleo/defensoria/listar/').success(function(data){
            $scope.defensorias = data.defensorias;
        });

        if(defensor_id > 0)
        {
            $http.get('/defensor/{0}/supervisores/atuacoes/'.replace('{0}', defensor_id)).success(function(data){
                $scope.atuacoes = data;
            });
        }
    };

    $scope.carregar = function(documento, agendar)
	{

        documento = angular.copy(documento);

        $scope.pessoa_id = documento.pessoa_id;
        $scope.tem_pessoa = ($scope.pessoa_id !== null);

        documento.modo = 1;

        if(agendar && documento.status_resposta === null) {
            documento.status_resposta = 0;
        }

        $scope.documento = documento;
        $scope.documento_upload = documento;

	};

    /* FIM diligências
    * */

    // adicionar requerente e requerido
    $scope.adicionar_pessoa = function(){
        var dados = {
            'pessoa_id': $scope.pessoa_visualizacao.pessoa_id,
            'atendimento_id': $scope.atendimento.atendimento.id,
            'tipo_edicao': $scope.tipo_edicao,
            'responsavel': 0,
            'cadastrado': 0,
            'tipo_envolvido': $scope.tipo_edicao
        };

        $http.post('/atendimento/recepcao/adicionar_pessoa/', dados).success(
            function(data){
                if (data.sucesso) {
                    if ($scope.tipo_edicao === 0) {
                        $scope.buscar_pessoas(0, true);

                        // se adicionar pessoa física já libera o botão Salvar
                        $scope.liberar_atendimento_pj_sem_pf = true;
                    }
                    else if ($scope.tipo_edicao === 1) {
                        $scope.buscar_pessoas(1, true);
                    }

                    $('#modal-visualizar-pessoa').modal('hide');
                    show_stack_success(data.pessoa.nome_tratado + ' vinculado(a)!');
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

        $scope.limpar_ultima_busca_pessoa();

        $scope.form_buscar_requerente = false;
        $scope.form_buscar_requerido = false;
    };

    // Altera defensoria do atendimento
    $scope.alterar_defensoria = function(atuacao_id)
    {

        var data = {
            'atendimento_numero': $scope.atendimento['atendimento']['numero'],
            'atuacao_id': atuacao_id
        }

        $http.post('/atendimento/recepcao/alterar_defensoria/', data).success(function(data){
            if(data['success'])
                show_stack_success('Defensoria alterada com sucesso!');
            else
                show_stack_error('Erro ao alterar a defensoria!');
            $scope.init($scope.atendimento['atendimento']['numero'], 0, 0);
        });

    }

    $scope.atendimentos_popover = [];

	$scope.get_atendimento = function(atendimento)
	{

        $scope.atendimento = null;
        $scope.atendimento_popover = null;

		if($scope.atendimentos_popover[atendimento]) {
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

    $scope.init = function (atendimento, tab, defensor_id)
    {
        $http.get('/atendimento/recepcao/marcados/'+ atendimento +'/json/get/liberacao/').success(function(data){
            $scope.atendimento = data;
            // $scope.filtro.atendimento_id = data.atendimento.id;

            $scope.requerente_responsavel = data.requerente_responsavel;

            $scope.alterar_tab(tab);

            if(tab!==1)
            {
                // carrega dados da aba Requentes
                $scope.buscar_pessoas(0, false);
            }

            $scope.liberar_atendimento_pj_sem_pf = data.liberar_atendimento_pj_sem_pf;
        });


        $scope.carregar_dados_diligencia(defensor_id);
    };
}

function RecepcaoPublicoCtrl($scope, $http, $socket, $timeout)
{

    $scope.atendimento = null;

    $socket.on('proximo', function (data) {
        $scope.atendimento = data;
        document.getElementById('beep').play();
    });

    function init()
    {
        $socket.emit('setcomarca', {comarca_id: comarca_id});
        $http.post('/comarca/guiches/', {comarca_id: comarca_id}).success(function(data){
            $scope.atendimentos = data;
            $socket.emit('get_atendendo', {comarca_id: comarca_id});
        });
    }

    init();

}
