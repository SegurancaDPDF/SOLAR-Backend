angular.module("SisatApp").controller(
    "CadastrarPessoaModel", 
    ['$scope', '$http', '$filter', 'fileUpload', 'patrimonioAPI', 'ContribDocumentoServiceAPI', 'EstadoAPI', 'MunicipioAPI', 'CartorioAPI', 'SituacaoServiceAPI', 'TipoRendaServiceAPI',
    ($scope, $http, $filter, fileUpload, patrimonioAPI, ContribDocumentoServiceAPI, EstadoAPI, MunicipioAPI, CartorioAPI, SituacaoServiceAPI, TipoRendaServiceAPI) =>
{
	$scope.salvando = false;
	$scope.tipo_telefone = ['Celular', 'Residencial', 'Comercial', 'Recado', 'WhatsApp', 'SMS'];
	$scope.tipo_membro = ['Cônjuge/Companheiro(a)', 'Pai/Mãe', 'Filho/Filha', 'Irmão/Irmã', 'Tio/Tia', 'Primo/Prima', 'Avô/Avó', 'Outro'];
    $scope.tipo_situacao = []
    $scope.tipo_renda_dependente = []
    SituacaoServiceAPI.get({}, function(data) {
        $scope.tipo_situacao = data.results;			
    });
    TipoRendaServiceAPI.get({}, function(data) {
        $scope.tipo_renda_dependente = data.results;
    });
    $scope.tipo_filiacao = ['Mãe', 'Pai'];
	$scope.tipo_fisica = 0;
	$scope.tipo_juridica = 1;
	$scope.relatorio = null;
    $scope.eh_pessoa_fisica = true;
    $scope.calcular_renda_familiar_e_membros_assistido = false;
    $scope.tipo_telefone_padrao = 0;

    $scope.listaDocumentosEscolhidos = [];
	$scope.listaDocumentosEnviando = [];

	$scope.limparDocumentosSelecionadosUpload = function () {
		// Reseta apenas a lista de documentos para upload e não a lista de documentos sendo enviados.
		$scope.listaDocumentosEscolhidos = [];
	}

	$scope.validaDocumentoTemNome = function (documento) {
		return documento.nome? true : false;
	}

	$scope.removerDocumento = function (index) {
		$scope.listaDocumentosEscolhidos.splice(index, 1);
	}

    $scope.selecionaArquivosUpload = function (e) {
		$scope.$apply(function () {
			for (var i = 0; i < e.files.length; i++) {

				let nome = e.files[i].name;
				nome = nome.substring(0, nome.lastIndexOf('.')).replaceAll('_', ' ');

				$scope.listaDocumentosEscolhidos.push({
					id: null,
					nome: nome,
					documento: null,
					arquivo: e.files[i]
				});

			}
		});
	};

	// adicionar múltiplos documentos por upload
	$scope.adicionarMultiplosDocumentos = function(atendimento_numero) {
		const url = '/assistido/'+ $scope.pessoa.id + '/documento/adicionar/';
        $scope.documentos_com_erro = false;

		for(const [index, documento] of $scope.listaDocumentosEscolhidos.entries()) {

			const tipoDocumento = documento.documento ? documento.documento.id : null;
			documento.documento = tipoDocumento;

			const identificadorArquivo = index + documento.arquivo.name;
			$scope.listaDocumentosEnviando.push(identificadorArquivo);

			fileUpload.uploadPromise(
				url,
				documento
			).success(function(data) {
                $scope.listaDocumentosEnviando.pop();
                if(data.sucesso)
                {
                    $scope.documentos.push(data.documento);
                    show_stack_success('Documento ' + documento.arquivo.name + ' salvo com sucesso!', false);
                }
                else{
                    $scope.documentos_com_erro = true;
                    show_stack_error('Erro ao salvar o documento ' + documento.arquivo.name + ': ' + data.errors[0][1], false);
                }
			}).error(function(data) {
                $scope.documentos_com_erro = true;
				$scope.listaDocumentosEnviando.pop();
				show_stack_error('Erro ao salvar o documento!', false);
			});

		}
	};

	$scope.$watch('estaEnviando', function(newValue, oldValue) {
        const estavaEnviando = !newValue && oldValue;

        if (estavaEnviando) {
			$('#modal-upload-documentos').modal('hide');
            $scope.limparDocumentosSelecionadosUpload();
            if(!$scope.documentos_com_erro)
			    show_stack_success('Todos os documentos foram enviados com sucesso!', false);
		}
	});

	Object.defineProperty($scope, 'estaEnviando', {
		/*
			Simula uma computed property para indicar o status do upload.
			Compatível com os browsers:
			Chrome >= 5
			Edge >= 12
			Firefox >= 4
			Internet Explorer >= 9
			Opera >= 11.6
			Safari >= 5.1
		*/
		get: function() {
			if (!$scope.listaDocumentosEnviando) {return false};
			return $scope.listaDocumentosEnviando.length > 0 ? true : false;
		}
	});

    $scope.$watch('pessoa.estado_civil', function() {

        $scope.pessoa.casada = false;

        if($scope.pessoa.estado_civil == 1 || $scope.pessoa.estado_civil == 4)
        {
            // marca flag para verificações
            $scope.pessoa.casada = true;
        }
        else
        {
            // verifica se existe conjuge/companheiro cadastrado e remove dados
            var conjuges = $filter('filter')($scope.pessoa.membros, {parentesco: 0}, true);
            for(var i = 0; i < conjuges.length; i++)
            {
                conjuges[i].nome = '';
                conjuges[i].renda = 0;
            }
        }

        $scope.recalcular_membros();
        $scope.avaliar();

    });

    // Utilizado para auxiliar no carregamento da página.
	$scope.unbind_wathch_pessoa_tipo = 0;

	$scope.definir_tipo_pessoa = function(){
	    $scope.eh_pessoa_fisica = $scope.pessoa.tipo !== 1;
    };

	$scope.listar_bens = function ()
	{
		//cria array a partir do conjunto de inputs especificado
		$('input[name="bens"]').each(function(i){
			if($scope.pessoa.bens[$(this).val()]==undefined) {
                $scope.pessoa.bens[$(this).val()] = false;
            }
		});
	};

	$scope.listar_estrutura_moradia = function ()
	{
		//cria array a partir do conjunto de inputs especificado
		$('input[name="estrutura"]').each(function(i){
			if($scope.pessoa.estrutura[$(this).val()]==undefined) {
                $scope.pessoa.estrutura[$(this).val()] = false;
            }
		});
    };

	$scope.listar_documentos = function ()
	{
        $http.get('/assistido/'+$scope.pessoa.id+'/documento/listar/').success(function(data){
            $scope.documentos = data;
        });
	};

	/*
	* Utilizado para buscar os endereços do assistido na tela de visualização da lista de endereços em Assistido Editar
	* */
	$scope.assistido_enderecos = null;
	$scope.assistido_enderecos_historico = null;
	$scope.endereco_selecionado = {};
	$scope.endereco_selecionado_posicao_array = null;
	$scope.modo_edicao_endereco = false;
	$scope.carregando_enderecos = false;

	$scope.get_pessoa_enderecos = function()
	{

		if ($scope.assistido_enderecos == undefined || $scope.assistido_enderecos == null) {

		    $scope.carregando_enderecos = true;

		    var pessoa_id = 0;

            if ($scope.pessoa !== null && $scope.pessoa.id !== null) {
                pessoa_id = $scope.pessoa.id;
            }

            $http.get('/assistido/' + pessoa_id + '/endereco/json/get/').success(
                function (data) {
                    if (data.sucesso) {
                        $scope.assistido_enderecos = data.dados.enderecos;
                        $scope.lista_tipo = data.dados.lista_tipo;
                        $scope.lista_tipo_area = data.dados.lista_tipo_area;
                    }
                    else {
                        show_stack_error(data.mensagem);
                    }

                    $scope.carregando_enderecos = false;
                }
                ).error(
                    function (data) {
                        $scope.carregando_enderecos = false;
                        show_stack_error('Erro ao buscar endereços');
                    }
                );
		}
	};

	$scope.carregando_enderecos_historico = false;

	/* Busca o histórico de endereços do assistido */
	$scope.get_pessoa_enderecos_historico = function()
	{
        $scope.carregando_enderecos_historico = true;

		if ($scope.assistido_enderecos_historico === undefined || $scope.assistido_enderecos_historico === null) {
            if ($scope.pessoa !== null && $scope.pessoa.id !== null) {
                $http.get('/assistido/' + $scope.pessoa.id + '/endereco/historico/json/get/').success(
                    function (data) {
                        if (data.sucesso) {
                            $scope.assistido_enderecos_historico = data.dados.enderecos_historico;
                        }
                        else {
                            show_stack_error(data.mensagem);
                        }

                        $scope.carregando_enderecos_historico = false;
                    }
                ).error(
                    function (data) {
                        $scope.carregando_enderecos_historico = false;
                        show_stack_error('Erro ao buscar histórico de endereços');
                    }
                );
            }
		}
	};

	$scope.set_endereco = function(endereco){
	    /* Utilizado para definir o endereço selecionado para edição ou criação */

	    if (endereco !== undefined && endereco !== null) {
            
	        $scope.endereco_selecionado.index = endereco.index;
	        $scope.endereco_selecionado.id = endereco.id;

            $scope.endereco_selecionado.cep = endereco.cep;
            $scope.endereco_selecionado.estado = endereco.estado_id;

            $scope.endereco_selecionado.municipio = endereco.municipio_id;
            $scope.endereco_selecionado.bairro = endereco.bairro;
            $scope.endereco_selecionado.logradouro = endereco.logradouro;
            $scope.endereco_selecionado.numero = endereco.numero;
            $scope.endereco_selecionado.complemento = endereco.complemento;
            $scope.endereco_selecionado.tipo_area = endereco.tipo_area.id;

            $scope.endereco_selecionado.tipo = endereco.tipo.id;
            $scope.endereco_selecionado.tipo_nome = endereco.tipo.nome;

            $scope.endereco_selecionado.principal = endereco.principal;

            for (var key in $scope.endereco_selecionado) {  
                if (key !== 'tipo_area') {
                    if ($scope.modificado_hoje) {
                        if (!$scope.endereco_selecionado[key]) {
                            $scope.nao_possui[key] = true;
                        }
                        else {
                            $scope.nao_possui[key] = false;
                        }
                    }
                    else {
                        $scope.nao_possui[key] = false;
                    }
                }
            }
        }
        else {
	        $scope.endereco_selecionado = {
                'estado': $scope.initial.estado,
                'municipio': $scope.initial.municipio
            };
	        // tratamento para nao_possui de tipo de imóvel. Gera conflito com o de endereço
            $scope.nao_possui['tipo'] = undefined;
        }
        $scope.endereco_selecionado.is_cep_correto = true;
        $scope.endereco_selecionado.cep_consultado = null;
        $scope.listar_municipios();

    };

    $scope.habilita_sigilo = function(codigo_situacao, check_id) {
        situacoes_configuradas = $scope.situacoes_configuradas
        if ($scope.eh_sigiloso) {
            // carrega situações sigilosas da página de configuração
            if (situacoes_configuradas.search(',') > 0) {
                situacoes_configuradas = situacoes_configuradas.split(',');
            } else {
                situacoes_configuradas = ['',situacoes_configuradas];
            }
            for (i = 0; i < situacoes_configuradas.length; i++) {
                if (codigo_situacao == situacoes_configuradas[i]) {
                    if (document.getElementById(check_id).checked) { // Quando checked
                        if ($scope.pessoa.id == null) { // Caso esteja criando o assistido
                            document.getElementById("alerta_sigilo").hidden = false;
                        } else { // Caso esteja editando o assistido
                            document.getElementById("vinculo_assistido_defensoria").hidden = false;
                            $scope.listar_acesso();
                        }
                    } else { // Quando unchecked
                        div_check_box_situacoes = document.getElementById('check_box_situacoes');
                        check_boxes_situacoes = div_check_box_situacoes.getElementsByTagName('input');
                        check_boxes_situacoes_array = [];
                        
                        // cria array com os checked
                        for (j = 0; j < check_boxes_situacoes.length; j++) {
                            if (check_boxes_situacoes[j].checked) {
                                check_boxes_situacoes_array.push(check_boxes_situacoes[j].name)
                            }
                        }
                        
                        foi_marcado_situacao_sigilosa = situacoes_configuradas.some(v=> check_boxes_situacoes_array.indexOf(v) !== -1)
                        if (!foi_marcado_situacao_sigilosa) {
                            document.getElementById("vinculo_assistido_defensoria").hidden = true;
                            document.getElementById("alerta_sigilo").hidden = true;
                        }

                    }
                }
            }
        }        
    };

    $scope.init_config_sigilo = function() {
        $http.get('/perfil/config/').success(function(data) {
            $scope.eh_sigiloso = data['sigiloso'];
            $scope.situacoes_configuradas = data['situacoes'].replace(/\s/g, '');
        });
    }

    $scope.init_situacao_sigilo = function() {
        if ($scope.eh_sigiloso) {
            $scope.listar_acesso();  // lista acessos daquele assistido
            
            // carrega situações sigilosas da página de configuração
            situacoes_configuradas = $scope.situacoes_configuradas;
            if (situacoes_configuradas.search(',') > 0) {
                situacoes_configuradas = situacoes_configuradas.split(',');
            } else {
                situacoes_configuradas = ['',situacoes_configuradas];
            }

            // carrega situações ativadas para o assitido
            codigos_situacoes = Object.keys($scope.pessoa.codigos_situacoes);
            for (i = 0; i < situacoes_configuradas.length; i++) {
                if (codigos_situacoes.includes(situacoes_configuradas[i])) {
                    $scope.get_defensorias(); // carrega lista de defensorias para modal
                    if (document.getElementById("vinculo_assistido_defensoria")) {
                        document.getElementById("vinculo_assistido_defensoria").hidden = false;
                    }
                }
            }
        }
    }

    $scope.get_defensorias = function() {
        $scope.defensorias = null;
        $http.get('/defensoria/listar/').success(function(data){
            $scope.defensorias = data;
        });
    }

	$scope.listar_acesso = function() {
        $scope.acessos = null;
        $http.get('acesso/').success(function(data){
			$scope.acessos = data;
		});
	};    

    $scope.conceder_acesso = function(id, tipo) {
		$scope.acessos = null;
		$http.post('acesso/conceder/', {id:id, tipo:tipo}).success(function(data){
			$scope.listar_acesso();
		});
	};

    $scope.solicitar_acesso = function(defensor_id) {
		$scope.acessos = null;
		$http.post('acesso/solicitar/', {defensor:defensor_id}).success(function(data){
			location.reload();
		});

	};

	$scope.revogar_acesso = function(id, tipo) {
		$scope.acessos = null;
		$http.post('acesso/revogar/', {id:id, tipo:tipo}).success(function(data){
			$scope.listar_acesso();
		});
	};    

	$scope.habilitar_modo_edicao_endereco = function(endereco) {
        $scope.set_endereco(endereco);
        $scope.modo_edicao_endereco = true;
    };

	$scope.desabilitar_modo_edicao_endereco = function(){
	    if ($scope.modo_edicao_endereco) {
            $scope.modo_edicao_endereco = false;
            $scope.set_endereco(null, null);
        }
    };

	$scope.falta_salvar_assistido_para_concluir = false;

	$scope.salvar_endereco = function(){

	    // tratamento para mostrar o tipo de endereço na listagem de endereços
	    $scope.endereco_selecionado.tipo = {
            'id': $scope.endereco_selecionado.tipo,
            'nome': $scope.lista_tipo[$scope.endereco_selecionado.tipo]
        };

	    // tratamento para mostrar o tipo de área na listagem de endereços
	    $scope.endereco_selecionado.tipo_area = {
            'id': $scope.endereco_selecionado.tipo_area,
            'nome': $scope.lista_tipo_area[$scope.endereco_selecionado.tipo_area]
        };

        // tratamento para salvar ID e dados de visualização de Estado na lista de endereços
        $scope.endereco_selecionado.estado_id = $scope.endereco_selecionado.estado;
        $scope.endereco_selecionado.estado = document.getElementById("id_estado").item(
            document.getElementById("id_estado").selectedIndex
        ).text;

        // tratamento para salvar ID e dados de visualização de Município na lista de endereços
        $scope.endereco_selecionado.municipio_id = $scope.endereco_selecionado.municipio;
        $scope.endereco_selecionado.municipio = document.getElementById("id_municipio").item(
            document.getElementById("id_municipio").selectedIndex
        ).text;

        if ($scope.endereco_selecionado.principal === undefined || $scope.endereco_selecionado.principal === null){
            // se a variável Principal não estiver definida será marcada com false por default

            $scope.endereco_selecionado.principal = false;
        }
        else if ($scope.endereco_selecionado.principal === true) {
            // caso defina o endereco_selecionado Principal como True irá redefinir todos os outros com Principal False

            for (var i in $scope.assistido_enderecos) {
                $scope.assistido_enderecos[i].principal = false;
            }
        }

	    if ($scope.endereco_selecionado.index === undefined || $scope.endereco_selecionado.index === null) {
	        // se estiver fazendo o cadastro de um novo endereço

	        $scope.endereco_selecionado.index = $scope.assistido_enderecos.length;

	        if ($scope.assistido_enderecos.length === 0) {
	            $scope.endereco_selecionado.principal = true;
            }

            $scope.assistido_enderecos.push($scope.endereco_selecionado);
        }
        else {
	        // se estiver editando o endereço

            if ($scope.assistido_enderecos.length === 1) {
	            $scope.endereco_selecionado.principal = true;
            }

            for (var i in $scope.assistido_enderecos) {
                var endereco = $scope.assistido_enderecos[i];

                if (endereco.index === $scope.endereco_selecionado.index) {
                    $scope.assistido_enderecos[i] = $scope.endereco_selecionado;
                    break;
                }
            }
        }

        $scope.falta_salvar_assistido_para_concluir = true;

        $scope.modificado_hoje = true;
        show_stack_info('Endereço adicionado! Salve o Assistido para concluir.');

        $scope.desabilitar_modo_edicao_endereco();
    };

	$scope.excluir_endereco = function(){
	    try {
            for (var i in $scope.assistido_enderecos) {
                var endereco = $scope.assistido_enderecos[i];

                if (endereco.index === $scope.endereco_selecionado.index) {
                    $scope.assistido_enderecos.remove(endereco);
                    break;
                }
            }

            $scope.falta_salvar_assistido_para_concluir = true;
            show_stack_info('Endereço removido! Salve o Assistido para concluir.');

        } catch (e) {
            show_stack_error('Erro ao excluir o endereço!');
        }
        $('#modal-excluir-endereco').modal('hide');
    };

    /* Excluir documento do atendimento */
	$scope.excluir = function(obj)
	{
		if(obj===undefined)
		{
            var url = $scope.gerar_link('assistido_excluir_documento', {pessoa_id:$scope.pessoa.id, documento_id:$scope.documento_edicao})
			$http.post(url).success(
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

    $scope.$watch('endereco_selecionado.municipio', function() {
        /* TODO otimizar busca de municípios e bairros.
            Conforme ir selecionando o estado e/ou município preencher uma estrutura para não fazer a busca no banco
            de dados repetidamente de um estado e/ou município que já foi carregado
         */
        $scope.listar_bairros();
        $scope.listar_logradouros();
	});
   
    $scope.listar_bairros = function()
    {
        $scope.bairros = [];
        if($scope.endereco_selecionado.municipio!==undefined)
        {
            $http.get('/municipio/'+$scope.endereco_selecionado.municipio+'/bairros/').success(function(data){
                $scope.bairros = data;
            });
        }
    };

	$scope.listar_logradouros = function()
	{
	    $scope.logradouros = [];
	    if($scope.endereco_selecionado.municipio!==undefined)
        {
            $http.get('/municipio/'+$scope.endereco_selecionado.municipio+'/logradouros/').success(function(data){
                $scope.logradouros = data;
            });
        }
	};

	$scope.listar_municipios = function(query, callback)
	{

		if(query==undefined)
		{

			if($scope.endereco_selecionado.estado==undefined) {
                $scope.endereco_selecionado.estado = $scope.initial.estado;
            }

			$http.get('/estado/' + $scope.endereco_selecionado.estado + '/municipios/').success(function(data){
				$scope.municipios = data;
			});

		}
		else
		{
			if($scope.municipios_all==undefined)
			{
				$http.get('/municipio/listar/').success(function(data){
					$scope.municipios_all = data;
					return $scope.listar_municipios(query, callback);
				});
			}
			else
			{
				callback($filter('filter')($scope.municipios_all, query));
			}
		}

	};

	$scope.listar_estados = function(query, callback)
	{
		if($scope.estados_all==undefined)
		{
			$http.get('/estado/listar/').success(function(data){
				$scope.estados_all = data;
				return $scope.listar_estados(query, callback);
			});
		}
		else
		{
			callback(array_to_list($filter('filter')($scope.estados_all, query),'nome'));
		}
	};

	$scope.listar_profissoes = function(query, callback)
	{
		if($scope.profissoes_all==undefined)
		{
			$http.get('/assistido/profissao/listar/').success(function(data){
				$scope.profissoes_all = data;
				return $scope.listar_profissoes(query, callback);
			});
		}
		else
		{
			callback($filter('filter')($scope.profissoes_all, query));
		}
	};

	$scope.listar_renda = function()
	{
		$scope.renda_max = $('select[name="renda"] option:last').val();
	};

	$scope.buscar_cep = function()
	{

		var cep = $scope.endereco_selecionado.cep;

		if(cep != undefined && cep.length == 8)
		{
			$http.get('/endereco/get_by_cep/'+cep+'/').success(function(data){

				$scope.endereco_selecionado.estado = data.estado_id;
				$scope.listar_municipios();

				$scope.endereco_selecionado.cep_consultado = data.erro ? null : data;
				$scope.endereco_selecionado.municipio = data.municipio_id;
				$scope.endereco_selecionado.bairro = data.bairro;
				$scope.endereco_selecionado.logradouro = data.logradouro;
                $scope.endereco_selecionado.complemento = data.complemento;
                $scope.endereco_selecionado.is_cep_correto = data.erro ? false: true;
                $scope.msg_erro_cep = data.erro ? data.msg : 'O CEP informado não pôde ser validado!';
			});
		}

	};

	$scope.buscar_cpf =  function()
	{

		if($scope.pessoa.cpf)
		{
			$http.post('/assistido/cpf/existe/', {'id':$scope.pessoa.id, 'cpf':$scope.pessoa.cpf}).success(function(data){
				$scope.cpf = data;
			});
		}
		else
		{
			$scope.cpf = null;
		}

	};

	$scope.salvar = function(ultimo, next)
	{

		if(next === undefined) {
            next = true;
        }

        $scope.salvando = true;
        $scope.pessoa.tipo_cadastro = 20; // cadastro completo
        $scope.processar_telefone($scope.pessoa.telefones); // telefone > ddd, numero
        //necessario adicionar 2 casas decimais para resolver bug de front de formatação de valores monetários da biblioteca do angular.
        $scope.pessoa.patrimonios.map((item) => {
            item.valor = item.valor.toFixed(2);
            return item;
        });
        var dados = {
            'pessoa': $scope.pessoa,
            'enderecos': $scope.assistido_enderecos
        };
		$http.post($('#AssistidoForm').attr('action'), dados).success(function(data){

			if(data.success)
			{
			    // se tiver link informado, irá redirecionar
				if(next && $('#next').val()) {
                    var prefix = $('#next').val().includes('?') ? '&' : '?';
                    window.location = $('#next').val() + prefix + 'pessoa_id=' + data.id;
                }
				else
				{
                    $scope.salvando = false;
                    $scope.pessoa = data.pessoa;

                    $scope.salvo = ($scope.pessoa.id > 0);

                    // limpa as variáveis de endereço para buscar os dados atualizados, caso necessário
                    $scope.assistido_enderecos = null;
                    $scope.assistido_enderecos_historico = null;

                    $scope.modificado_hoje = true;
                    $scope.preencher_nao_possui($scope.pessoa);

                    $scope.init_telefone();
                    $scope.init_membro();

                    show_stack_success('Salvo com sucesso!');
				}
			}
			else
			{
                if(data.id) {
                    $scope.pessoa.id = data.id;
                }

				var errors = '<b>Erro ao salvar!</b> Verifique se todos os campos foram preenchidos corretamente:';
				errors += '<ul>';

				for(var i = 0; i < data.errors.length; i++)
				{
					errors += '<li><b>' + data.errors[i][0] + '</b> - ' + data.errors[i][1] + '</li>';
				}

				errors += '</ul>';
				show_stack_error(errors);
			}

			$scope.salvando = false;

		}).error(function(){

			show_stack_error('Erro ao salvar! Verifique se todos os campos foram preenchidos corretamente.');
			$scope.salvando = false;

		});

	};

	$scope.verificar_renda = function()
	{
		//se valor é o mesmo do ultimo item, exibe mensagem, senão, esconde mensagem
		if($scope.pessoa.renda==$scope.renda_max) {
            $('select[name="renda"]').next().removeClass('hidden');
        }
		else {
            $('select[name="renda"]').next().addClass('hidden');
        }
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
		$scope.salvando = true;
		$http.post('/assistido/filiacao/excluir/', $scope.pessoa.filiacao[index]).success(function(data){
			$scope.pessoa.filiacao.splice(index, 1);
			$scope.salvando = false;
		});
	};

	// TELEFONE
	$scope.init_telefone = function()
	{

		if($scope.pessoa.telefones == undefined) {
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
		if($scope.pessoa.id)
		{
			$scope.salvando = true;
			$http.post('/assistido/(_0)/telefone/excluir/'.replace('(_0)', $scope.pessoa.id), $scope.pessoa.telefones[index]).success(function(data){
				$scope.pessoa.telefones.splice(index, 1);
				$scope.salvando = false;
			});
		}
		else
		{
			$scope.pessoa.telefones.splice(index, 1);
		}
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

    $scope.remover_mascara_telefone = function(e)
    {
        const selection = document.getSelection().toString();
        e.originalEvent.clipboardData.setData('text/plain', selection.replace(/\D/g,''));
        e.originalEvent.preventDefault();
    }

    $scope.init_tipo_patrimonio = () => {
        patrimonioAPI.get_patrimonios_tipo().then((response) => {
            // TODO: falta implementar cenario se de erro
            var grupos_patrimonio = {};
            for(var i = 0; i < response.data.results.length; i++)
            {
                var tipo = response.data.results[i];
                grupos_patrimonio[tipo['grupo']] = {nome: tipo['grupo_nome'], valor: 0};
            }
            $scope.tipos_patrimonio = response.data.results;
            $scope.grupos_patrimonio = grupos_patrimonio;
            // Só carrega patrimônios depois de carregar os tipos
            $scope.init_patrimonio();
        });
    }

    $scope.init_tipo_documento = () => {        
        ContribDocumentoServiceAPI.get({exibir_em_documento_assistido:true, ativo:true}, function(data) {
			$scope.tipos = data.results;			
		});
    }

    //PATRIMONIO
    $scope.init_patrimonio = () => {
        if(!$scope.pessoa.id){
            $scope.pessoa.patrimonios = new Array();
            $scope.adicionar_patrimonios();
        }else{
            // TODO: falta implementar cenario se de erro
            patrimonioAPI.get_patrimonio_assistido($scope.pessoa.id).then((response) => {
                $scope.pessoa.patrimonios = response.data.results;
                $scope.adicionar_patrimonios();
            });
        }

    }

    // Adiciona patrimônios iniciais, possibilitando o usuário ver as opções disponíveis e remover as indesejadas
    $scope.adicionar_patrimonios = () => {
        for(var i = 0; i < $scope.tipos_patrimonio.length; i++)
        {
            var val = $scope.tipos_patrimonio[i].id;
            var found = $scope.pessoa.patrimonios.find(e => e.tipo.id == val);
            if(found==undefined)
            {
                $scope.adicionar_patrimonio($scope.tipos_patrimonio[i], $scope.pessoa.patrimonios.length);
            }
        }
    }

    $scope.adicionar_patrimonio = (obj, index) => {
        if($scope.pessoa.patrimonios) $scope.pessoa.patrimonios.splice(index, 0, {
            tipo: obj,
            valor: 0
        });
    }

    $scope.remover_patrimonio = (patrimonio) => {

        // Conta quantos itens são do mesmo tipo do item que está sendo excluído
        var total_patrimonios_mesmo_tipo = $filter('filter')($scope.pessoa.patrimonios, {tipo: {id: patrimonio.tipo.id}}, false).length;

        // Se só tem ele, impede a exclusão
        if(total_patrimonios_mesmo_tipo==1)
        {
            show_stack_error('Não é possível excluir: este é último item do tipo!');
            return;
        }

        let indice_patrimonio_array_patrimonios = $scope.pessoa.patrimonios.findIndex((element) => {
            return element.$$hashKey == patrimonio.$$hashKey;
        });
        if($scope.pessoa.id){
                patrimonioAPI.delete_patrimonio_assistido($scope.pessoa.patrimonios[indice_patrimonio_array_patrimonios].id).then((response) => {
                    if(response.status === 200 && response.data.success){
                        show_stack_success('Patrimônio deletado com sucesso!!!');
                    }else{
                        show_stack_error(response.data.error);
                    }
                }
            );
        }
        $scope.pessoa.patrimonios.splice(indice_patrimonio_array_patrimonios, 1);
        $scope.avaliar();
    }

    // MEMBROS
    $scope.init_membro = function()
	{

		if($scope.pessoa.membros == undefined) {
            $scope.pessoa.membros = [];
        }

        // verifica se existe conjuge/companheiro cadastrado
        var membros = $filter('filter')($scope.pessoa.membros, {parentesco: 0}, true).length;

        // se não existe, adiciona conjuge/companheiro
		if(membros == 0){
            $scope.adicionar_membro(0);
        }

	};

    $scope.get_situacao = function(obj)
	{
		if(obj.situacao_dependente) {
            return $filter('filter')($scope.tipo_situacao, {id: obj.situacao_dependente}, true)[0]['nome'];
        }
	};

    $scope.set_situacao = function(val, obj)
	{
		if(obj) {
            obj.situacao_dependente = val;
        }
	};

    $scope.get_tipo_renda = function(obj)
	{
		if(obj.tipo_renda) {
            return $filter('filter')($scope.tipo_renda_dependente, {id: obj.tipo_renda}, true)[0]['nome'];
        }
	};

    $scope.set_tipo_renda = function(val, obj)
	{
		if(obj) {
            obj.tipo_renda = val;
        }
	};

	$scope.get_membro = function(obj)
	{
		if(obj) {
            return $scope.tipo_membro[obj.parentesco];
        }
	};

	$scope.set_membro = function(val, obj)
	{
		if(obj) {
            obj.parentesco = val;
        }
	};

	$scope.adicionar_membro = function(parentesco)
	{
        // objeto inicial
        var membro = {id:null, nome: null, renda: 0, parentesco: parentesco, desativado_em: null};
        // se conjuge/companheiro, sempre adiciona na posição 0
        if(parentesco==0)
        {
            $scope.pessoa.membros.splice(0, 0, membro);
        }
        // se outro parentesco, adiciona no final da lista
        else
        {
            $scope.pessoa.membros.push(membro);
        }
        $scope.recalcular_membros();
	};

	$scope.remover_membro = function(obj)
	{
        obj.desativado_em = true;
        $scope.recalcular_membros();
    };

    $scope.recalcular_membros = function()
    {
        if($scope.calcular_renda_familiar_e_membros_assistido)
        {
            // obtém lista de membros ativos
            var membros = $filter('filter')($scope.pessoa.membros, {desativado_em:null}, true);

            var numero_membros_economicamente_ativos = 0;
            var ganho_mensal_membros = 0.0;

            // se assistido tem renda, soma como membro economicamente ativos
            if($scope.pessoa.ganho_mensal > 0)
            {
                ganho_mensal_membros += parseFloat($scope.pessoa.ganho_mensal);
                numero_membros_economicamente_ativos++;
            }

            // calcula total de membros economicamente ativos e ganho mensal dos membros
            for(var i = 0; i < membros.length; i++)
            {
                if(membros[i].renda > 0)
                {
                    numero_membros_economicamente_ativos++;
                    ganho_mensal_membros += parseFloat(membros[i].renda);
                }
            }

            // atualiza valores do objeto
            $scope.pessoa.numero_membros = membros.length + ($scope.pessoa.casada ? 1: 0); // se não casado, ignora conjuge
            $scope.pessoa.numero_membros_economicamente_ativos = numero_membros_economicamente_ativos;
            $scope.pessoa.ganho_mensal_membros = ganho_mensal_membros.toFixed(2);
        }
    }

	$scope.init_assistido = function(assistido_id, tab, modificado_hoje, initial, tipo_pessoa) {
	    var url = assistido_id ? '/assistido/'+assistido_id+'/json/get/' : '/assistido/json/get/';

	    $scope.modificado_hoje = modificado_hoje;

        $http.get(url).success(function(data){

            $scope.pessoa = data;
            $scope.pessoa.tipo = tipo_pessoa;
            // define nome social caso identidade de gênero tenha sido definida
            if ($scope.pessoa.declara_identidade_genero == true) {
                $scope.pessoa.nome_visualizacao = $scope.pessoa.nome_social;
            } else {
                $scope.pessoa.nome_visualizacao = $scope.pessoa.nome;
            }
            
            $scope.set_initial_values(data, initial);
            // validTab();

            $scope.definir_tipo_pessoa();

            $scope.init_filiacao();
            $scope.init_telefone();
            $scope.init_tipo_patrimonio();
            $scope.init_tipo_documento();
            $scope.init_membro();
            $scope.init_situacao_sigilo();

			$scope.listar_bens();
            $scope.listar_estrutura_moradia();
            $scope.listar_documentos();

			$scope.carregando = false;

			//Recupera nome default caso não possuir
			if(!$scope.pessoa.nome) {
                $scope.pessoa.nome = $('#id_nome').val();
            }

			//Recupera nome default caso não possuir
			if(!$scope.pessoa.cpf) {
                $scope.pessoa.cpf = $('#id_cpf').val();
            }

            // Se tab for a ultima e pessoa existe, libera upload de arquivos
            if(tipo_pessoa===1)
            {
                $scope.salvo = ($scope.pessoa.id && tab===4);
            }
            else
            {
                $scope.salvo = ($scope.pessoa.id && tab===6);
            }

            $scope.preencher_nao_possui($scope.pessoa);
		});
    };

    $scope.verifica_check_box_bem_familia = function(id_patrimonio, indice_selecionado) {
        var array_check = document.getElementsByClassName('check_box_eh_bem_familia');
        for (i = 0; i < array_check.length; i++) {
            if (document.getElementById(indice_selecionado).id != array_check[i].id) {
                array_check[i].checked = false;
            }
        }
        
        patrimonios = $scope.pessoa.patrimonios
        for (i = 0; i < patrimonios.length; i++) {
            if (!patrimonios[i].id && patrimonios[i].tipo.id == 1) {
                patrimonios[i].eh_bem_familia = false;
            }
            if (patrimonios[i].id && patrimonios[i].tipo.id == 1) {
                if (patrimonios[i].id != id_patrimonio) {
                    patrimonios[i].eh_bem_familia = false;
                } 
                if (patrimonios[i].id == id_patrimonio) {
                    patrimonios[i].eh_bem_familia = document.getElementById(indice_selecionado).checked;
                }
            }
            
        }
    }

	$scope.preencher_nao_possui = function(dicionario_pessoa){
	    /* Utilizado para preencher o dicionário de nao_possui */

	    if($scope.modificado_hoje)
        {
            var campos_endereco = ["cep", "bairro", "complemento", "estado", "municipio", "municipio_nome", "numero", "principal"];

            for(var key in dicionario_pessoa)
            {
                if (campos_endereco.indexOf(key) === -1) {
                    if (dicionario_pessoa[key] === undefined || dicionario_pessoa[key] === null || dicionario_pessoa[key] === '' ) {
                        $scope.nao_possui[key] = true;
                    }
                    else {
                        $scope.nao_possui[key] = false;
                    }
                }
            }
        }
    };

	$scope.avaliar = function() {

        // Faz cálculos internos de patrimoniais
        var grupos_patrimonio = $scope.grupos_patrimonio;
        for(var key in grupos_patrimonio)
        {
            grupos_patrimonio[key].valor = 0;
        }

        for(var i = 0; i < $scope.pessoa.patrimonios.length; i++)
        {
            var patrimonio = $scope.pessoa.patrimonios[i];
            var grupo = patrimonio.tipo.grupo;
            grupos_patrimonio[grupo].valor += patrimonio.valor;
        }

        $scope.grupos_patrimonio = grupos_patrimonio;

        // Envia dados para avaliação e retorna resultado
        if (!$scope.carregando) {
            $http.post('/assistido/avaliar/', $scope.pessoa).success(function (data) {
                if (data.success) {
                    $scope.avaliacao = data;
                }
                else {
                    $scope.avaliacao = {};
                }
            });
        }

	};

	// CONTROLES
	$scope.avancar = function()
	{
        tabMove(1);
	};

	$scope.voltar = function()
	{
        tabMove(-1);
	};

	//Move para proxima tab (i=1) ou para a tab anterior (i=-1)
	function tabMove(i)
	{
		validTab();
		var index = tabIndex + i;

        if(index >=0 && index < tabs.length)
        {
            if (tabs[index].hash === '#endereco') {
		        $scope.get_pessoa_enderecos();
            }

            $scope.desabilitar_modo_edicao_endereco();
            tabs.eq(index).tab('show');
        }
    }

    function input_to_array(filter)
	{
		return objects_to_array('input[name="'+filter+'"]');
	}

	function select_to_array(filter)
	{
		return objects_to_array('select[name="'+filter+'"] option');
	}

	function objects_to_array(filter)
	{
		arr = [];
		$(filter).each(function(i){
			arr[$(this).val()]=$(this).text();
		});
		return arr;
	}

	function array_to_list(array, field)
	{
		var arr = [];
		for(var i = 0; i < array.length; i++)
			arr.push(array[i][field]);
		return arr;
	}

	$scope.init = function(id, tab, modificado_hoje, initial, tipo_pessoa, calcular_renda_familiar_e_membros_assistido, tipo_telefone_padrao)
	{

		$scope.initial = initial;
		$scope.carregando = true;
		$scope.pessoa = {'bens' : {}, 'estrutura' : {}, 'patrimonios': []};
        $scope.tipo_telefone_padrao = tipo_telefone_padrao;
        $scope.init_documento();
		$scope.init_filiacao();
        $scope.init_telefone();
        $scope.init_membro();
		$scope.init_municipios();
        $scope.bairros = [];
        $scope.nao_possui = {};
        $scope.calcular_renda_familiar_e_membros_assistido = calcular_renda_familiar_e_membros_assistido;

        $scope.modificado_hoje = modificado_hoje;

        $scope.init_assistido(id, tab, modificado_hoje, initial, tipo_pessoa);
        $scope.init_config_sigilo();

	};

	$scope.set_initial_values = function(obj, values)
	{
		for(var key in values)
		{
			if(!(key in obj) || !obj[key])
			{
				obj[key] = values[key];
			}
		}
	};

    $scope.gerar_declaracao_hipossuficiencia = function(data)
    {
		$scope.relatorio = data;
        Chronus.generate($scope, $scope.relatorio.user, 'hipossuficiencia', 'atendimento/atendimento/hipossuficiencia', $scope.relatorio.params);
    };

    $scope.gerar_declaracao_comprovante_agendamento = function(data)
    {
		$scope.relatorio = data;
        Chronus.generate($scope, $scope.relatorio.user, 'comprovante', 'atendimento/atendimento/agendamento', $scope.relatorio.params);
    };

    $scope.gerar_declaracao_mudanca_endereco = function(data)
    {
		$scope.relatorio = data;
        Chronus.generate($scope, $scope.relatorio.user, 'mudanca_endereco', 'atendimento/atendimento/declaracao', $scope.relatorio.params);
    }

	// lista da aba Documentos
	$scope.documentos = [];

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
            '/assistido/'+ $scope.pessoa.id + '/documento/adicionar/',
            $scope.documento_upload,
            $scope.documento_status
        );

        $scope.cancelar_update_documento();
        // a função de limpar o input file está no jQuery do atendimento
    };

    $scope.init_documento = function() {
        // TODO: verifiar necessidade desta função

        $scope.tipo_documento_selecionado = null;
        $scope.documento_upload = {
            'id': null,
            'nome': '',
            'arquivo': null
        };
    };

    $scope.init_certidao = function(){

        if(typeof($scope.certidao) == 'object')
            return;

        let data_nascimento = $scope.pessoa.data_nascimento;

        // Força conversão da data de nascimento para Date
        if(typeof(data_nascimento) == 'string')
            data_nascimento = new Date(data_nascimento);

        // Dados iniciais
        $scope.certidao = {
            'ano': (data_nascimento ? data_nascimento.getUTCFullYear() : null)
        }

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		EstadoAPI.get({'ordering': 'uf', limit:1000}, function(data){
			$scope.certidao_estados = data.results;
            $scope.certidao.estado = get_object_by_id(data.results, parseInt($scope.initial.estado));
            $scope.carregar_municipios_certidao(parseInt($scope.initial.municipio));
		});

    }

    $scope.carregar_municipios_certidao = function(municipio_id = null)
    {

        $scope.certidao.municipio = null;
		$scope.certidao_municipios = [];

        if(!$scope.certidao.estado)
            return;

		MunicipioAPI.get({estado: $scope.certidao.estado.id, limit:1000}, function(data){

			$scope.certidao_municipios = data.results;

            if(municipio_id)
                $scope.certidao.municipio = get_object_by_id(data.results, municipio_id);

            $scope.carregar_cartorios_certidao();

		});

    }

    $scope.carregar_cartorios_certidao = function()
    {

        $scope.certidao.cartorio = null;
        $scope.certidao_cartorios = [];

        if(!$scope.certidao.municipio)
            return;

        CartorioAPI.get({municipio: $scope.certidao.municipio.id, limit:1000}, function(data){

            $scope.certidao_cartorios = data.results;

            if($scope.certidao_cartorios.length == 1)
                $scope.certidao.cartorio = $scope.certidao_cartorios[0].cns;

        });

    }

    $scope.converter_certidao = function(){
        let certidao = $scope.certidao;
        let cartorio = certidao.cartorio.toString().padStart(6, '0');
        let acervo = '01'; // Acervo próprio
        let servico = '55'; // Serviço de registro civil das pessoas naturais
        let ano = certidao.ano.toString().padStart(4, '0');
        let tipo = ($scope.pessoa.certidao_tipo == 'CC' ? '2' : '1'); // Livro A (1: Nascimento), B (2: Casamento)
        let livro = certidao.livro.toString().padStart(5, '0');
        let folha = certidao.folha.toString().padStart(3, '0');
        let registro = certidao.registro.toString().padStart(7, '0');

        let matricula = `${cartorio}${acervo}${servico}${ano}${tipo}${livro}${folha}${registro}`;
        let dv = Utils.gerarDV2(matricula);

        $scope.certidao.matricula = `${matricula}${dv}`;
        $scope.pessoa.certidao_numero = `${matricula}${dv}`;
        $scope.pessoa.certidao_tipo = (tipo == '2' ? 'CC' : 'CN');
        $scope.nao_possui['certidao_numero'] = false;
        $scope.nao_possui['certidao_tipo'] = false;

        if(!$scope.pessoa.naturalidade)
        {
            $scope.pessoa.naturalidade = certidao.municipio.nome;
            $scope.pessoa.naturalidade_estado = certidao.estado.nome;
            $scope.nao_possui['naturalidade'] = false;
            $scope.nao_possui['naturalidade_estado'] = false;
        }

        $('#modal-converter-certidao-civil').modal('hide');

    }

    $scope.alertar_alteracao = function(){
        if($scope.pessoa.id && !$scope.pessoa.cadastro_protegido && !$scope.alteracao_confirmado){
            $('#modal-confirmar-alteracao').modal();
        }
    }

}]);

function clone(obj)
{

    if(obj===null || typeof obj !== 'object') {
        return obj;
    }

    var temp = obj.constructor();

    for(var key in obj) {
        temp[key] = clone(obj[key]);
    }

    return temp;

}

function BuscarPessoaModel($scope, $http)
{

    $scope.salvo = false;
    $scope.salvando = false;
    $scope.assistidos = {};

	$scope.init = function(filtro)
	{

		for(var key in filtro) {
            $scope.filtro[key] = filtro[key];
        }

        $scope.buscar(false);

	};

    $scope.limpar = function()
    {
        $scope.filtro = {id:null, nome:'', cpf:'', filiacao:''};
        $scope.last_filtro = '';
    };

    $scope.buscar = function(recarregar)
    {

        if(recarregar)
        {
            var url = gerar_url($scope.filtro, ['cpf', 'nome', 'filiacao', 'next', 'route']);
            window.location.assign(url);
        }

        else if($scope.filtro.id || $scope.filtro.cpf ||
            ($scope.filtro.nome && $scope.filtro.nome.trim().length >= 3 && $scope.filtro.nome.trim() != $scope.last_filtro) ||
            ($scope.filtro.filiacao && $scope.filtro.filiacao.trim().length >= 3))
        {

            if($scope.filtro.nome) {
                $scope.last_filtro = $scope.filtro.nome.trim();
            }

            $scope.msg_erro_busca_pessoa = null;
        	$scope.carregando = true;
        	$scope.pessoas = [];

            $http.post('', $scope.filtro).success(function(data){

                if(!data.sucesso){
                    $scope.msg_erro_busca_pessoa = data.mensagem;
                    $scope.carregando = false;
                    return;
                }

                data = data.pessoas;

                // TODO tratar busca por Nome Fantasia de PJ
                // transforma nome em array de nomes
                var filtro_nome = [];
                if ($scope.filtro.nome) {
                    filtro_nome = removeDiacritics($scope.filtro.nome).toUpperCase().split(' ');
                }

                // transforma nome da filiacao em array de nomes
                var filtro_mae = [];
                if ($scope.filtro.filiacao) {
                    filtro_mae = removeDiacritics($scope.filtro.filiacao).toUpperCase().split(' ');
                }

                // marca palavras do filtro que contenham no nome ou filiacao
                for(var i = 0; i < data.length; i++)
                {

                    var nome_mark = '';

                    if(data[i].tipo===0) //Pessoa Fisica
                    {
                        if(data[i].nome_social!==null && data[i].nome_social.trim()!=='')
                        {
                            nome_mark = data[i].nome_social;
                        }
                    }
                    else
                    {
                        if(data[i].apelido!==null && data[i].apelido.trim()!=='')
                        {
                            nome_mark = data[i].apelido;
                        }
                    }

                    if(nome_mark==='')
                    {
                        nome_mark = data[i].nome;
                    }

                    data[i].nome_mark = removeDiacritics(nome_mark);

                    for(var j = 0; j < filtro_nome.length; j++)
                    {
                        var re = new RegExp(filtro_nome[j], "g");
                        data[i].nome_mark = data[i].nome_mark.replace(re, '<mark>'+filtro_nome[j]+'</mark>');
                    }

                    for(var mae = 0; mae < data[i].filiacao.length; mae++)
                    {
                        data[i].filiacao[mae].nome_mark = removeDiacritics(data[i].filiacao[mae].nome);

                        for (var j=0; j < filtro_mae.length; j++)
                        {
                            data[i].filiacao[mae].nome_mark = data[i].filiacao[mae].nome_mark.replace(filtro_mae[j],'<mark>'+filtro_mae[j]+'</mark>');
                        }
                    }
                }

                //var filtro = $scope.filtro.nome ? $scope.filtro.nome.toUpperCase() : '';
                var result = [];

                // Atribui nota aos resultados de acordo com a proximidade com o filtro
                for(var i = 0; i < data.length; i++)
                {

                    var nome = removeDiacritics(data[i].nome).split(' ');
                   // var total = 0;

                    data[i].nota = 0;

                    for(var f = 0; f < filtro_nome.length; f++)
                    {

                        var nota = Math.pow(0.1, (f - 1));

                        for(var n = 0; n < nome.length; n++)
                        {
                            if(filtro_nome[f]==nome[n])
                            {
                                nota = Math.pow(0.1, (f + 1)) * (n + 1);
                                break;
                            }
                        }

                        data[i].nota = data[i].nota + nota;

                    }

                }

                // Ordena resultado de acordo com a nota
                data.sort(function(a,b){return a.nota-b.nota});

                // Ordena alfabeticamente resultados com a mesma nota
                var i = 0;

                while(data.length > 0)
                {
                    if(data.length == i || data[i].nota != data[0].nota)
                    {
                        result = result.concat(splice_and_sort(data, i));
                        i = 0;
                    }
                    i++;
                }

                // Atualiza dados do angular;
                $scope.pessoas = result;
                $scope.carregando = false;

            });
        }

    };

    $scope.buscar_key = function(e)
    {
        // Busca automatico se enter (13)
        if(e.which==13)
        {
            $scope.buscar(true);
            // Cancela evento padrao do enter (limpar form)
            e.preventDefault();
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

    function splice_and_sort(arr, qtd)
    {

        var arr_sort = arr.splice(0, qtd);

        arr_sort.sort(function(a,b){
            return (a.nome < b.nome) ? -1 : (a.nome > b.nome) ? 1 : 0;
        });

        return arr_sort;
    }

    function init()
    {
        $scope.limpar();
    }

    init();

}

function PreCadastro($scope, $http)
{

	$scope.erro = true;
	$scope.pessoa = {};

	$scope.procurar = function()
	{
		$http.post('', $scope.pessoa).success(function(data){

			$scope.erro = (data.erro?true:false);

			if(!data.erro)
			{
				$scope.pessoa = data.pessoa;
				$scope.telefones = data.telefones;
				if(data.telefones) {
                    $scope.pessoa.telefone = data.telefones[0].ddd + data.telefones[0].numero;
                }
			}

		});
	}
}
