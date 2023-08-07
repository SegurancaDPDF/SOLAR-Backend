function CadastrarAudienciaCtrl($scope, $http, $filter, DefensorAPI, DefensoriaAPI)
{
    $scope.fases = [];
    $scope.defensores = [];

	$scope.$watch('processo', function() {
        $scope.audiencia.processo = get_id_from_object($scope.processo);
	});

	$scope.$watch('parte', function() {
        $scope.audiencia.atendimento = get_key_from_object($scope.parte, 'atendimento');
	});

	$scope.$watch('defensoria', function() {
        $scope.audiencia.defensoria = get_id_from_object($scope.defensoria);
	});

	$scope.$watch('defensor', function() {
        $scope.audiencia.defensor_cadastro = get_id_from_object($scope.defensor);
	});

	$scope.$watch('tipo', function() {
        $scope.audiencia.tipo = get_id_from_object($scope.tipo);
	});

    $scope.novo = function()
    {
        var hoje = new Date();
        var hora_atual = (hoje.getHours() > 9 ? '' : '0') + hoje.getHours();
        var minuto_atual = (hoje.getMinutes() > 9 ? '' : '0') + hoje.getMinutes();
        var hora = hora_atual + ':' + minuto_atual;

        $scope.audiencia = {
            processo:null,
            audiencia_realizada:false,
            audiencia_status:0,
            data: hoje,
            hora: hora,
            data_termino: hoje,
            hora_termino: hora,
            descricao: ''
        };
        $scope.set_data_protocolo();
        $scope.set_data_termino_protocolo();
        aplicar_select2('modal-cadastrar-audiencia');


    };

    $scope.realizada = function()
    {
        if($scope.audiencia.audiencia_status == 1){
            $scope.audiencia.audiencia_realizada=true
        }
        else{
            $scope.audiencia.audiencia_realizada=false
        }
        
    }


    $scope.buscar_processo = function()
    {

        $scope.processo_error = null;

        if($scope.processo_numero)
        {
            var processo_numero = $scope.processo_numero.match(/\d+/g).join('');
            $http.get('/processo/' + processo_numero + '/get/json/?grau=' + $scope.processo_grau).success(function(data){
                if (data.error || data.processo.pre_cadastro)
                {
                    $scope.processo_error = true;
                    $scope.processo = null;
                }
                else
                {
                    $scope.processo = data.processo;
                    if($scope.processo.partes.length==1)
                    {
                        $scope.audiencia.parte = $scope.processo.partes[0];
                    }
                }
            });
        }

    };

    $scope.limpar_processo = function()
    {

        $scope.processo = null;
        $scope.audiencia.processo = null;
        $scope.processo_error = null;

    };

    $scope.salvar = function()
    {
        $scope.audiencia.salvando = true;
        $http.post('/processo/fase/salvar/', $scope.audiencia).success(function(data) {
            if(data.success)
            {
                var url = '?defensor=($0)&data_ini=($1)&data_fim=($1)'.replace('($0)', $scope.audiencia.defensor_cadastro);
                url = url.replace(/\(\$1\)/g, $filter('date')($filter('utc')($scope.audiencia.data), "dd/MM/yy"));
                window.location.assign(url);
            }
            else
            {
                $scope.errors = data.errors;
            }
            $scope.audiencia.salvando = false;
        });
    };

    $scope.set_data_protocolo = function()
    {
        $scope.audiencia.data_protocolo = $filter('date')($filter('utc')($scope.audiencia.data), "dd/MM/yyyy") + ' ' + $scope.audiencia.hora;
    };

    $scope.set_data_termino_protocolo = function()
    {
        if ($scope.audiencia && $scope.audiencia.data_termino) {
            $scope.audiencia.data_termino_protocolo = $filter('date')($filter('utc')($scope.audiencia.data_termino), "dd/MM/yyyy") + ' ' + $scope.audiencia.hora_termino;
        }
    };

    $scope.init = function()
    {

        if ($scope.defensores === undefined || $scope.defensores === null || $scope.defensores.length === 0)
        {
            // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
            DefensorAPI.get({incluir_atuacoes:false, ativo:true, limit:1000}, function(data){
                $scope.defensores = data.results;
            });

            // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
            DefensoriaAPI.get({limit:1000}, function(data){
                $scope.defensorias = data.results;
            });
        }

        $http.get('/processo/fase/tipo/listar/').success(function(data){
            $scope.fases = data;
        });

        $scope.novo();

    };

    $scope.init();

}

function AudienciaCtrl($scope, $http, $filter, $interval, $sanitize, $sce, DefensorAPI, DefensoriaAPI, ProcapiAvisoServiceAPI)
{

    const MAX_TENTATIVAS = 30;

    $scope.processo = null;
    $scope.processo_atual = null;
    $scope.documentos = null;
    $scope.tipos = [];
    $scope.defensores = [];
    $scope.defensorias = [];
    $scope.acoes = [];
    $scope.areas = [];
    $scope.comarcas = [];
    $scope.varas = [];
    $scope.lista_tipo = [{id: 1, nome: 'Físico'}, {id: 2, nome: 'Eletrônico'}];
    $scope.lista_custodia = [
        {id: 0, nome: '(Não se aplica)'},
        {id: 10, nome: '1. Relaxamento de Flagrante'},
        {id: 21, nome: '2.1. Liberdade Provisória - Com Fiança'},
        {id: 22, nome: '2.2. Liberdade Provisória - Sem Fiança'},
        {id: 23, nome: '2.3. Liberdade Provisória - Com medida cautelar'},
        {id: 24, nome: '2.4. Liberdade Provisória - Sem medida cautelar'},
        {id: 30, nome: '3. Manteve a Prisão'}];
    $scope.busca = {grau: 1};
   
    $scope.$watch('processo.numero', function() {
        if($scope.processo && $scope.processo.numero) {
            $scope.processo.numero_puro = $scope.processo.numero.replace(/\D/g, '');
        }
    });

    $scope.$watch('processo.grau', function() {
        aplicar_select2('modal-dados-processo');
    });

    $scope.$watch('processo.comarca', function() {
        aplicar_select2('modal-dados-processo');
    });
    $scope.$watch('processo.sistema_webservice', function() {
        aplicar_select2('modal-dados-processo');
    });

    $scope.$watch('parte.atuacao_cadastro', function(){
        // Marca mesma defensoria como cadastro se pode atender grau informado

        if($scope.parte && $scope.parte.atuacao_cadastro!=null)
        {
            $scope.parte.defensoria = null;
            for(var i = 0; i < $scope.defensorias.length; i ++)
            {
                if($scope.defensorias[i].id==$scope.parte.atuacao_cadastro.defensoria_id) {
                    $scope.parte.defensoria = $scope.defensorias[i];
                    break;
                }
            }
            aplicar_select2('modal-dados-processo');
        }
    });

    $scope.listar_documentos = function() {
        $http.get('json/get/documentos/').success(function(data){
            $scope.documentos = data.documentos;
        });
    }

    $scope.novo = function()
    {

        if(!$scope.tipos.length)
        {
            $http.get('/processo/fase/tipo/listar/').success(function(data){
                $scope.tipos = data;
            });
        }


        var hoje = new Date();
        var hora_atual = (hoje.getHours() > 9 ? '' : '0') + hoje.getHours();
        var minuto_atual = (hoje.getMinutes() > 9 ? '' : '0') + hoje.getMinutes();
        var hora = hora_atual + ':' + minuto_atual;
        var defensoria = null;
        var defensor = null;

        // Preenche defensoria responsável automaticamente
        if( $scope.processo_atual.parte.defensoria && typeof $scope.processo_atual.parte.defensoria.id !== 'undefined' )
        {
            for(var d in $scope.defensorias)
            {
                var dd = $scope.defensorias[d];
                if($scope.processo_atual.parte.defensoria.id === dd.id)
                {
                    defensoria = dd;
                    break;
                }
            }
        }

        // Define como Defensor Responsável o Primeiro Lotado na Defensoria do Processo
        if($scope.defensores_atuando_na_defensoria.length == 1){

            let defensor_atuando_na_defensoria = $scope.defensores_atuando_na_defensoria[0];
            for(let defensor_index in $scope.defensores){
                let defensor_object = $scope.defensores[defensor_index];
                if(defensor_atuando_na_defensoria.defensor.id == defensor_object.id){
                    defensor = defensor_object;
                    break;
                }
            }

        }

        // Remove soma de horas do timezone
        hoje = new Date(Date.UTC(hoje.getFullYear(), hoje.getMonth(), hoje.getDate()));

        $scope.audiencia = {
            data: hoje,
            hora: hora,
            data_termino: hoje,
            hora_termino: hora,
            defensoria: defensoria,
            defensor: defensor,
            processo: null,
            audiencia_realizada: false,
            audiencia_status: 0,
            custodia: 0,
            honorario: {possivel: 0}
        };

        $scope.parte = {parte: {tipo: 0}};

        $('#tabFase a:first').tab('show');
        aplicar_select2('modal-dados-fase');

    };

    $scope.$watch('audiencia.data', function() {
        $scope.set_data_protocolo();
    });

    $scope.$watch('audiencia.hora', function() {
        $scope.set_data_protocolo();
    });

    $scope.$watch('audiencia.data_termino', function() {
        $scope.set_data_termino_protocolo();
    });

    $scope.$watch('audiencia.hora_termino', function() {
        $scope.set_data_termino_protocolo();
    });

    $scope.carregar = function(fase)
    {

        var fase = angular.copy(fase);

        // Aplica objeto tipo a fase selecionada
        for(var i = 0; i < $scope.tipos.length; i ++)
        {
            if($scope.tipos[i].id==fase.tipo.id) {
                fase.tipo = $scope.tipos[i];
            }
        }

        // Aplica objeto defensoria a fase selecionada
        if(fase.defensoria!=null)
        {
            for(var i = 0; i < $scope.defensorias.length; i ++)
            {
                if($scope.defensorias[i].id==fase.defensoria.id) {
                    fase.defensoria = $scope.defensorias[i];
                }
            }
        }

        // Aplica objeto defensor a fase selecionada
        if(fase.defensor_cadastro!=null)
        {
            for(var i = 0; i < $scope.defensores.length; i ++)
            {
                if($scope.defensores[i].id==fase.defensor_cadastro.id) {
                    fase.defensor = $scope.defensores[i];
                }
            }
        }

        fase.data = fase.data_protocolo;
        fase.hora = $filter('date')($filter('utc')(fase.data_protocolo), "HH:mm");

        fase.data_termino = fase.data_termino_protocolo;
        fase.hora_termino = $filter('date')($filter('utc')(fase.data_termino_protocolo), "HH:mm");

        $scope.audiencia = fase;
        $scope.set_data_protocolo();
        $scope.set_data_termino_protocolo();
        $scope.listar_documentos();

        $('#tabFase a:first').tab('show');
        aplicar_select2('modal-dados-fase');

    };

    $scope.buscar = function(auto)
    {
        $scope.limpar_busca();

        if($scope.busca.numero) {
            processo_numero = $scope.busca.numero.match(/\d+/g);
        }
        else {
            processo_numero = null;
        }

        if(processo_numero)
        {

            processo_numero = processo_numero.join('');

            if(processo_numero.length != 20 && auto) {
                return;
            }

            $scope.buscar_numero(processo_numero);

        }

    };

    $scope.buscar_numero = function(processo_numero, processo_grau)
    {
        let numero_processo_valido = validarNumeroUnicoProcesso(processo_numero);

        // Na hipotese de o usuário digitar um número eletrônico inválido emite mensagem de erro
        if (!numero_processo_valido && processo_numero.length == 20){
            $scope.busca.eproc = {};
            $scope.busca.eproc.mensagem = 'Número de processo eletrônico é inválido, por favor conferir digitação e tentar novamente';
            $scope.busca.existe = false;
            return
        }

        $scope.carregando = true;

        if(processo_grau==undefined)
        {
            processo_grau = $scope.busca.grau;
        }

        $http.get('/processo/' + processo_numero + '/get/json/?grau=' + processo_grau).success(function(data){

            if (data.processo){
                if(!data.processo.pre_cadastro && data.processo.partes.length) {
                    data.processo.editavel = false;
                }
                else {
                    data.processo.editavel = true;
                }

                if(data.processo.pre_cadastro && data.processo.partes.length) {
                    $scope.parte = data.processo.partes[0];
                }
            }


            $scope.processo = (data.processo == null ? {editavel:true} : data.processo);
            $scope.busca.processo = data.processo;
            $scope.busca.existe = !data.error && !data.processo.pre_cadastro;
            $scope.busca.eproc = data.eproc;
            $scope.pode_preencher_classe_comarca_vara = data.pode_preencher_classe_comarca_vara;
            $scope.ATIVAR_ESAJ = data.ATIVAR_ESAJ;
            $scope.carregando = false;

            if($scope.processo.tipo==undefined)
            {
                if(data.eproc==null || !data.eproc.sucesso)
                {
                    $scope.processo.tipo = $scope.lista_tipo[0];
                }
                else{
                    $scope.processo.tipo = $scope.lista_tipo[1];
                }
            }

            if($scope.processo.grau==undefined)
            {
                $scope.processo.grau = data.eproc && data.eproc.processo ? data.eproc.processo.grau : processo_grau;
            }
        });
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
    
    $scope.editar_processo = function(processo, parte)
    {

        $scope.processo = processo;
        $scope.parte = parte;
        $scope.carregando = false;

        $scope.processo.area = get_object_by_id($scope.areas, processo.area ? processo.area.id:null);
        $scope.processo.acao = get_object_by_id($scope.acoes, processo.acao.id);
        $scope.processo.comarca = get_object_by_id($scope.comarcas, processo.comarca.id);
        $scope.processo.vara = get_object_by_id($scope.varas, processo.vara.id);
        $scope.parte.defensoria = get_object_by_id($scope.defensorias, parte.defensoria.id);

        for(var i = 0; i < $scope.atuacoes.length; i++)
        {
            if($scope.atuacoes[i].defensoria_id == parte.defensoria.id && $scope.atuacoes[i].defensor_id == parte.defensor.id)
            {
                $scope.parte.atuacao_cadastro = $scope.atuacoes[i];
                break;
            }
        }

        aplicar_select2('modal-dados-processo');

    };

    /* Transferir a Parte para outro atendimento
    * */
    $scope.transferir_processo = function(parte)
    {
        $scope.parte = parte;
    };

    $scope.carregar_processo_permissao_botoes = function() {

        $http.get('/processo/parte/' + $scope.processo_atual.parte.id + '/json/get/permissao/').success(function(data){
            if (data.sucesso) {
                $scope.permissao_botoes = data.permissao_botoes;
            }
            else {
                $scope.permissao_botoes = {};
            }
        });
    };

    // Recupera informacoes do processo e fases processuais
    $scope.carregar_processo = function(processo_numero, processo_grau, atendimento_numero, fase_id)
    {

        if(processo_numero && atendimento_numero)
        {

            $scope.carregando_processo = true;
            $scope.processo_atual = null;

            // Recupera informacoes do processo
            $http.get('/processo/' + processo_numero + '/get/json/?grau=' + processo_grau).success(function(data){

                $scope.eproc = data.eproc;

                $scope.processo_error = data.error;

                if(data.error)
                {
                    $scope.carregando_processo = false;
                }
                else
                {

                    $scope.processo_atual = data.processo;

                    //Procura parte vinculada ao atendimento
                    for(var i = 0; i < data.processo.partes.length; i++)
                    {
                        if(data.processo.partes[i].atendimento==atendimento_numero || data.processo.partes[i].atendimento_inicial==atendimento_numero) {
                            $scope.processo_atual.parte = data.processo.partes[i];
                        }
                    }

                    if($scope.processo_atual.parte) {
                        $scope.processo_atual.editavel = ($scope.processo_atual.parte.id == data.processo.partes[0].id);

                        // busca as permissões dos botões da aba Processos
                        $scope.carregar_processo_permissao_botoes();
                    }

                    $scope.fase = fase_id;
                    $scope.fases = null;

                    $scope.EM_ANDAMENTO = $scope.processo_atual.tipos_status.EM_ANDAMENTO;
                    $scope.SOBRESTADO = $scope.processo_atual.tipos_status.SOBRESTADO;
                    $scope.FINALIZADO = $scope.processo_atual.tipos_status.FINALIZADO;
                    $scope.ativar_acompanhamento_processo = data.ativar_acompanhamento_processo;

                    // Recupera informacoes das fases processuais
                    $http.get('/processo/' + $scope.processo_atual.numero_puro + '/fase/listar/?grau=' + $scope.processo_atual.grau).success(function(data){

                        $scope.fases = data;

                        for(var i = 0; i < data.length; i++)
                        {
                            if($scope.fases[i].id==$scope.fase)
                            {
                                $scope.carregar($scope.fases[i]);
                                $('#modal-dados-fase').modal();
                                $('#tabFase a:last').tab('show');
                            }
                        }

                        $('#copiar_numero_processo').click(function(){

                            var _this = this;
                            var copyData = $(_this).attr('clipboard-text');

                            copyTextToClipboard(copyData, function(){
                                show_stack_success('Copiou número do processo');
                            }, function(err){
                                show_stack_error('Falha ao copiar número do processo: '+err);
                            });

                        })

                        $scope.carregando_processo = false;

                    });

                    $http.get(`/api/v1/atuacoes?defensoria_id=${$scope.processo_atual.parte.defensoria.id}&ativo=true&apenas_vigentes=true&apenas_defensor=true`).success(function(atuacoes){
                        $scope.defensores_atuando_na_defensoria = atuacoes.results;
                    });
                }

            });

        }

    };

    $scope.carregar_eproc = function(processo)
    {

        $scope.processo_atual = processo;

        if(processo.numero_puro.length)
        {
            $scope.eproc = null;
            $scope.carregando_processo = 1;
            $scope.escutar_eproc(processo.numero_puro + processo.grau);
        }

    };

    $scope.carregar_eproc_vinculado = function(processo, tentativas)
    {
        $http.get('/procapi/processo/' + processo.numero + '/consultar/').success(function(data){
            if(!data.sucesso || data.processo.atualizado || tentativas==MAX_TENTATIVAS)
            {
                processo.eproc = data;
                processo.carregando = false;
            }
            else
            {
                setTimeout(function () {
                    $scope.carregar_eproc_vinculado(processo, tentativas+=1);
                }, 1000);
            }
        });
    }

    $scope.carregar_prazos_vinculados = function(processo_numero)
    {
        $scope.prazos = [];
        ProcapiAvisoServiceAPI.get({processo_numero: processo_numero}, function(data){
            $scope.prazos = data.results;
        });
    };

    $scope.escutar_eproc = function(numero_processo)
    {
        $http.get('/procapi/processo/' + numero_processo + '/consultar/').success(function(data){
            if((!data.sucesso || data.processo.atualizado) || $scope.carregando_processo==MAX_TENTATIVAS)
            {

                $scope.eproc = data;
                $scope.carregar_prazos_vinculados($scope.eproc.processo.numero);
                $scope.carregando_processo = false;

                if(data.sucesso)
                {
                    for(var i = 0; i < data.processo.vinculados.length; i++)
                    {
                        data.processo.vinculados[i].carregando = true;
                        $scope.carregar_eproc_vinculado(data.processo.vinculados[i], 0);
                    }
                }

            }
            else
            {
                setTimeout(function () {
                    $scope.carregando_processo+=1;
                    $scope.escutar_eproc(numero_processo);
                }, 1000);
            }
        });
    };

    //INICIO CONSULTA TJAM
    $scope.carregar_tjam = function (processo) {
        $scope.processo_atual = processo;

        if (processo.numero.length) {
            $scope.eproc = null;
            $scope.carregando_processo = true;
            $scope.escutar_tjam(processo.numero_puro);
        }

    }

    $scope.escutar_tjam = function (numeroDoProcesso) {
        $http.post('/scrapy_tj/consultar_tjam/', {numeroDoProcesso}).success(function (data) {
            $scope.tjam_sucesso = ''
            console.log(data[0].error)
            if(!data[0].error){
                $scope.nao_encontrado = false;
                $scope.carregando_processo = false;
                $scope.tjam_sucesso = true
                $scope.eproc = data;
            }else{
                $scope.eproc = data;
                $scope.tjam_sucesso = false
                $scope.carregando_processo = false;
                $scope.nao_encontrado = true;
            }

        });
    }
    //FIM CONSULTA

    $scope.carregar_substitutos = function()
    {
        $scope.substitutos = [];
        $scope.audiencia.substituto = null;

        $http.get('/defensor/' + $scope.audiencia.defensor.id + '/substitutos/').success(function(data){
            $scope.substitutos = data;
            $scope.audiencia.substituto = data[0];
        });
    };

    $scope.set_data_protocolo = function()
    {
        if($scope.audiencia && $scope.audiencia.data && $scope.audiencia.hora)
        {
            var data_protocolo = $filter('date')($filter('utc')($scope.audiencia.data), "dd/MM/yyyy") + ' ' + $scope.audiencia.hora;
            $scope.audiencia.data_protocolo = $scope.audiencia.data_hora_protocolo = data_protocolo;
        }
    };

    $scope.set_data_termino_protocolo = function()
    {
        if ($scope.audiencia && $scope.audiencia.data_termino && $scope.audiencia.hora_termino)
        {
            var data_protocolo = $filter('date')($filter('utc')($scope.audiencia.data_termino), "dd/MM/yyyy") + ' ' + $scope.audiencia.hora_termino;
            $scope.audiencia.data_termino_protocolo = data_protocolo;
        }
    };

    $scope.realizada = function()
    {
        if($scope.audiencia.audiencia_status == 1){
            $scope.audiencia.audiencia_realizada=true
        }
        else{
            $scope.audiencia.audiencia_realizada=false
        }
        
    }

    $scope.carregar_defensorias = function(defensor_id)
    {

        $scope.defensorias = [];

        if(defensor_id!=undefined)
        {
            $http.get('/defensor/'+defensor_id+'/atuacoes/').success(function(data){
                for(var i = 0; i < data.length; i++) {
                    $scope.defensorias.push(data[i].defensoria);
                }
            });
        }

    };

    $scope.limpar_busca = function(forcar, numero)
    {

        $scope.load_data();
        $scope.carregando = false;

        if($scope.busca.numero==undefined || forcar==true) {
            $scope.busca.numero = null;
        }

        if(numero!=undefined)
        {
            $scope.busca.numero = numero;
            $scope.buscar();
        }

        $scope.busca = {numero: $scope.busca.numero, grau: $scope.busca.grau};

        $scope.processo = {editavel: true};
        $scope.parte = {parte: {tipo: 0}};

    };

    $scope.load_data = function()
    {

        if(!$scope.acoes.length)
        {
            $http.get('/processo/acao/listar/').success(function(data){
                $scope.acoes = data;
            });
        }

        if(!$scope.areas.length)
        {
            $http.get('/area/listar/').success(function(data){
                $scope.areas = data;
            });
        }

        if(!$scope.comarcas.length)
        {
            $http.get('/comarca/listar/').success(function(data){
                $scope.comarcas = data;
            });
        }

        if(!$scope.varas.length)
        {
            $http.get('/vara/listar/').success(function(data){
                $scope.varas = data;
            });
        }

    };

    $scope.init = function(processo_sem_atendimento, processo_numero, processo_grau, pre_cadastro, carregar_processos, consulta_eproc)
    {

        $scope.load_data();
        $scope.pre_cadastro = (pre_cadastro == 'true' ? true : false);
        $scope.processo_sem_atendimento = processo_sem_atendimento;

        if(carregar_processos)
        {
            $http.get('atender/processos/get/').success(function(data){
                $scope.processos = data;
                if(consulta_eproc)
                {
                    var encontrado = false;
                    for(var i = 0; i < data.length; i++){
                        if(data[i].numero_puro == processo_numero && data[i].grau == processo_grau)
                        {
                            encontrado = true;
                            $scope.carregar_eproc(data[i]);
                        }
                    }
                    if(!encontrado)
                    {
                        $scope.carregar_eproc({'numero_puro': processo_numero, 'grau': 1});
                    }
                }
            });

        }

        if(!carregar_processos){
            $http.get('atender/processos/get/').success(function (data){
                $scope.processos = data;
            });
        }

        if(!consulta_eproc)
        {

            $http.get('/processo/acao/listar/').success(function(data){
                $scope.acoes = data;
            });

            $http.get('/defensor/atuacao/supervisores/listar/').success(function(data){
                $scope.atuacoes = data;
            });

            if($scope.defensores === undefined || $scope.defensores === null || $scope.defensores.length === 0)
            {
                // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
                DefensorAPI.get({incluir_atuacoes:false, ativo:true, limit:1000}, function(data){
                    $scope.defensores = data.results;
                });

                // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
                DefensoriaAPI.get({limit:1000}, function(data){
                    $scope.defensorias = data.results;
                });
            }

            if(!$scope.tipos.length)
            {
                $http.get('/processo/fase/tipo/listar/').success(function(data){
                    $scope.tipos = data;
                });
            }

            if(processo_numero && pre_cadastro)
            {
                $('#modal-dados-processo').modal('show');
                $scope.buscar_numero(processo_numero, processo_grau);
                $scope.load_data();
            }

        }

    }

    $scope.removerNaoNumericos = function (e, variavel, chave) {

        e.preventDefault();
        var content;
        if (e.originalEvent && e.originalEvent.clipboardData) {
            content = (e.originalEvent || e).clipboardData.getData('text/plain');
        }
        else if (window.clipboardData) {
            content = window.clipboardData.getData('Text');
        }
        var new_value = content.replace(/[^0-9.\-\/]+/g, '');
        if (variavel) {
            variavel[chave] = new_value;
        }
    };

    $scope.novo_processo = function(params){

        for(var key in params){
            $scope.processo[key] = params[key];
        }

        aplicar_select2('modal-dados-processo');

    }

    $scope.novo_processo_extrajudicial = function(defensoria_id, defensor_id){

        $scope.limpar_busca();

        $scope.parte.defensor = get_object_by_id($scope.defensores, defensor_id);
        $scope.parte.defensoria = get_object_by_id($scope.defensorias, defensoria_id);

        aplicar_select2('modal-dados-processo-extra');

    }

    $scope.set_pessoa = function(pessoa){
        $scope.pessoa = pessoa;
        $scope.pessoa.endereco = $scope.pessoa.enderecos[0];
    }

    // recebe uma str no formato dd/mm/YYYY e retorna a data correspondente em milisegundos
    function dateInMiliseconds(dateString){
        const regex = /^(0?[1-9]|[12][0-9]|3[01])[\/](0?[1-9]|1[012])[\/]\d{4}$/;
        // testa se a str está no formato dd/MM/YYYY, se está entre 1 e 31 dias e 1 a 12 meses
        if (regex.test(dateString)) {
            const dateSplit = dateString.split('/')
            // altera para o formato YYYY-mm-dd
            const dateStrFormatISO = `${dateSplit[2]}-${dateSplit[1]}-${dateSplit[0]}`
            const date = new Date(dateStrFormatISO)
            const dateInMiliseconds = date.getTime()
            if(!isNaN(dateInMiliseconds)){
                return dateInMiliseconds
            }else{
                return NaN
            }
        }else{
            return NaN
        }
    }

    $scope.salvar_situacao_parte = (processo_parte_id, tipo_status) => {

        try{

            const now = new Date();
            const currentDay = String(now.getDate()).padStart(2, '0');
            const currentMonth = String(now.getMonth() + 1).padStart(2, '0'); // mais 1 porque janeiro é zero
            const currentYear = String(now.getFullYear());

            const data_inicio =  tipo_status == $scope.SOBRESTADO ? `${currentDay}/${currentMonth}/${currentYear}` : null
            const data_fim = $scope.processo_atual.parte?.situacao?.data_final_sobrestamento ?? null
            const motivo = $scope.processo_atual.parte?.situacao?.motivo ?? null


            if(!data_fim && tipo_status === $scope.SOBRESTADO) {
                throw new Error('Data final do sobrestamento deve ser informada.')
            } else if(!motivo && tipo_status === $scope.SOBRESTADO){
                throw new Error('Motivo não pode estar vazio.')
            } else if(
                (dateInMiliseconds(data_fim) <= dateInMiliseconds(data_inicio))
                && (tipo_status === $scope.SOBRESTADO)
            ){
                throw new Error('Data final não pode ser menor ou igual a hoje.');
            }else{
                $http.post('/processo/parte/situacao/salvar', {
                    tipo_status,
                    processo_parte_id,
                    data_inicio,
                    data_fim,
                    motivo,
                }).success((data) => {
                    if (data['success']){
                        $scope.processo_atual.parte.situacao_atual = data.novo_status

                        show_stack_success('Salvo com sucesso!');
                    } else {
                        throw new Error('Erro ao salvar!');
                    }
                }).error(function(){
                    throw new Error('Erro ao salvar!');
                });

                // fecha a modal
                const modalIds = ['#modal-sobrestar-parte-processo', '#modal-finalizar-acompanhamento-processo'];
                modalIds.forEach((modalId) => {
                    if ($(modalId).is(':visible')) {
                        $(modalId).modal('hide');
                    }
                });

                // reseta os valores para não serem inclusos caso o usuário altere o status sem atualizar a página.
                if(data_fim && motivo){
                    $scope.processo_atual.parte.situacao.data_final_sobrestamento = null;
                    $scope.processo_atual.parte.situacao.motivo = null;
                }
            }
        } catch(error){
            return show_stack_error(error.message);
        }
    }

}

function BuscarProcessoCtrl($scope, $http, DefensorAPI, DefensoriaAPI)
{

    $scope.filtro = {ultima:true, total:0};

    // utilizado para carregar o popover com dados do atendimento
	$scope.requerente_popover = null;
	$scope.requerentes_popover = {};

	$scope.$watch('defensor', function() {
		if($scope.defensor && $scope.defensor.id) {
            $scope.filtro.defensor = $scope.defensor.id;
        }
		else {
            $scope.filtro.defensor = '';
        }
		$scope.validar();
	});

	$scope.$watch('defensoria', function() {
		if($scope.defensoria && $scope.defensoria.id) {
            $scope.filtro.defensoria = $scope.defensoria.id;
        }
		else {
            $scope.filtro.defensoria = '';
        }
		$scope.validar();
	});

	$scope.get_pessoa = function(pessoa_id)
	{
		$scope.assistido = null;

		if($scope.requerentes_popover[pessoa_id]) {
            $scope.assistido = $scope.requerentes_popover[pessoa_id];
        }
		else
		{
			$scope.requerentes_popover[pessoa_id] = {};
			$http.get('/assistido/'+pessoa_id+'/json/get/').success(function(data){
				$scope.assistido = data;
				$scope.requerentes_popover[pessoa_id] = data;
			});
		}
	};

	$scope.init = function(filtro)
	{

        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        DefensorAPI.get({incluir_atuacoes:false, ativo:true, limit:1000}, function(data){
            $scope.defensores = data.results;
            $scope.defensor = get_object_by_id($scope.defensores, filtro.defensor);
            aplicar_select2('BuscarProcessoForm', true);
        });

        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        DefensoriaAPI.get({limit:1000}, function(data){
            $scope.defensorias = data.results;
            $scope.defensoria = get_object_by_id($scope.defensorias, filtro.defensoria);
            aplicar_select2('BuscarProcessoForm', true);
        });

		for(var key in filtro) {
            $scope.filtro[key] = filtro[key];
        }

        $scope.filtro.data_ini = DataConversao(filtro['data_ini']);
        $scope.filtro.data_fim = DataConversao(filtro['data_fim']);

		$scope.validar();
		$scope.buscar(0);

	};

	$scope.buscar = function(pagina, recarregar) {

		$scope.filtro.pagina = (pagina==undefined ? 0 : pagina);
		$scope.carregando = true;

		if(pagina==0 && recarregar)
        {
            var url = gerar_url($scope.filtro, ['defensor', 'defensoria', 'filtro', 'data_ini', 'data_fim', 'situacao']);
            window.location.assign(url);
            return;
        }

        var filtro = {...$scope.filtro}; // copia valor para alterar formato das datas
		filtro['data_ini'] = date_to_string_ddmmyyyy(filtro['data_ini']);
		filtro['data_fim'] = date_to_string_ddmmyyyy(filtro['data_fim']);

		$http.post('/processo/listar/', filtro).success(function (data) {

			$scope.LISTA = data.LISTA;
			$scope.filtro.ultima = data.ultima;
			$scope.filtro.paginas = data.paginas;

			if(data.processos.length && !data.ultima) {
                data.processos[data.processos.length - 1].ultimo = true;
            }

			if(data.pagina==0)
			{
				$scope.processos = data.processos;
				$scope.filtro.total = data.total;
			}
			else
			{
				for(var i = 0; i < data.processos.length; i++) {
                    $scope.processos.push(data.processos[i]);
                }
			}

			$scope.carregando = false;

		});
	};

	$scope.validar = function () {
		var filtro = $scope.filtro;
		var data_ini = (filtro.data_ini != undefined && filtro.data_ini);
        var data_fim = (filtro.data_fim != undefined && filtro.data_fim);
        var datas = (data_ini && data_fim && data_ini <= data_fim) || (!data_ini && !data_fim);
		$scope.valido = datas && (data_ini || data_fim || filtro.defensor || filtro.defensoria || filtro.filtro) && (!$scope.defensor || $scope.defensor.id) && (!$scope.defensoria || $scope.defensoria.id);
	};

}

function BuscarAudienciaCtrl($scope, $http, $filter, DefensorAPI, DefensoriaAPI)
{

	$scope.filtro = {ultima:true, total:0};
	$scope.assistidos ={};

	$scope.$watch('defensor', function() {
		if($scope.defensor) {
            $scope.filtro.defensor = $scope.defensor.id;
        }
		else {
            $scope.filtro.defensor = null;
        }
		$scope.validar();
	});

	$scope.$watch('defensoria_cadastro', function() {
        if($scope.audiencia && $scope.defensoria_cadastro) {
            $scope.audiencia.defensoria = get_id_from_object($scope.defensoria_cadastro);
        }
    });

    $scope.$watch('defensor_cadastro', function() {
        if($scope.audiencia && $scope.defensor_cadastro) {
            $scope.audiencia.defensor_cadastro = get_id_from_object($scope.defensor_cadastro);
        }
	});

	$scope.$watch('defensoria', function() {
		if($scope.defensoria) {
            $scope.filtro.defensoria = $scope.defensoria.id;
        }
		else {
            $scope.filtro.defensoria = null;
        }
		$scope.validar();
	});

    $scope.$watch('sel', function() {
        if($scope.registros)
        {
            for(var i = 0; i < $scope.registros.length; i++)
            {
                if($scope.registros[i].perm_edicao && $scope.registros[i].editavel && !$scope.registros[i].audiencia_realizada) {
                    $scope.registros[i].sel = $scope.sel;
                }
            }
        }
    });

    $scope.realizada = function()
    {
        if($scope.audiencia.audiencia_status == 1){
            $scope.audiencia.audiencia_realizada=true
        }
        else{
            $scope.audiencia.audiencia_realizada=false
        }
        
    }

    $scope.$watch('data_protocolo', function() {
        $scope.set_data_protocolo();
    });

    $scope.$watch('hora_protocolo', function() {
        $scope.set_data_protocolo();
    });

    $scope.$watch('data_termino', function() {
        $scope.set_data_termino_protocolo();
    });

    $scope.$watch('hora_termino', function() {
        $scope.set_data_termino_protocolo();
    });

    $scope.set_data_protocolo = function()
    {
        if($scope.data_protocolo && $scope.hora_protocolo) {
            $scope.audiencia.data_protocolo = getDataHoraFormatada($scope.data_protocolo + $scope.hora_protocolo);
        }

    };

    $scope.set_data_termino_protocolo = function()
    {
        if ($scope.data_termino) {
            $scope.audiencia.data_termino_protocolo = getDataHoraFormatada($scope.data_termino + $scope.hora_termino);
        }
    };

	$scope.init = function(filtro)
	{

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensorAPI.get({incluir_atuacoes:false, ativo:true, limit:1000}, function(data){
			$scope.defensores = data.results;
			$scope.defensor = get_object_by_id($scope.defensores, filtro.defensor);
		});

		// TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensoriaAPI.get({limit:1000}, function(data){
			$scope.defensorias = data.results;
			$scope.defensoria = get_object_by_id($scope.defensorias, filtro.defensoria);

		});

        $http.get('/processo/fase/tipo/listar/').success(function(data){
            $scope.fases = data;
        });

		for(var key in filtro) {
            $scope.filtro[key] = filtro[key];
        }

		$scope.validar();
		$scope.buscar(0);

	};

	$scope.validar = function () {
		var filtro = $scope.filtro;
		var data_ini = (filtro.data_ini != undefined && filtro.data_ini.length > 0);
		var data_fim = (filtro.data_fim != undefined && filtro.data_fim.length > 0);
		var datas = (data_ini && data_fim) || (!data_ini && !data_fim);
		$scope.valido = datas && (data_ini || data_fim || filtro.defensor || filtro.defensoria || filtro.filtro) && (!$scope.defensor || $scope.defensor.id) && (!$scope.defensoria || $scope.defensoria.id);
	};

    $scope.selecionar = function(obj)
    {
        $scope.audiencia = angular.copy(obj);
        $scope.data_protocolo = $filter('date')(obj.data_protocolo, "ddMMyyyy");
        $scope.hora_protocolo = $filter('date')(obj.data_protocolo, "HHmm");

        $scope.data_termino = $filter('date')(obj.data_termino_protocolo, "ddMMyyyy");
        $scope.hora_termino = $filter('date')(obj.data_termino_protocolo, "HHmm");

        $scope.tipo = get_object_by_id($scope.fases, obj.tipo);
        $scope.defensoria_cadastro = get_object_by_id($scope.defensorias, obj.defensoria);
        $scope.defensor_cadastro = get_object_by_id($scope.defensores, obj.defensor_cadastro);
    };

    $scope.show_alterar = function(obj)
    {
        $scope.selecionar(obj);
        $('#modal-alterar-audiencia').modal();
        aplicar_select2('modal-alterar-audiencia');
    };

    $scope.alterar = function()
    {
        $scope.audiencia.salvando = true;
        $http.post('/processo/fase/salvar/', $scope.audiencia).success(function(data) {
            if(data.success)
            {
                var data_protocolo = dataHoraFormatadaParaUTC($scope.audiencia.data_protocolo);
                var url = '?defensor=($0)&data_ini=($1)&data_fim=($1)'.replace('($0)', $scope.audiencia.defensor_cadastro);
                url = url.replace(/\(\$1\)/g, $filter('date')($filter('utc')(data_protocolo), "dd/MM/yy"));
                window.location.assign(url);
            }
            else
            {
                $scope.errors = data.errors;
            }
            $scope.audiencia.salvando = false;
        });
    };

    $scope.show_excluir = function(obj)
    {
        $scope.selecionar(obj);
        $('#modal-excluir-audiencia').modal();
    };

    $scope.excluir = function()
    {
        $scope.audiencia.excluindo = true;
        $http.post('/processo/fase/($0)/excluir/'.replace('($0)', $scope.audiencia.id)).success(function (data) {
            if(data.success)
            {
                $('#modal-excluir-audiencia').modal('hide');
                $scope.buscar(0);
            }
        });
    };

    $scope.show_realizar = function(obj)
    {
        $scope.selecionar(obj);
        $('#modal-realizar-audiencia').modal();
        aplicar_select2('modal-realizar-audiencia');
    };

    $scope.realizar = function()
    {

        $scope.audiencia.salvando = true;
        $scope.errors = [];

        $http.post('/processo/audiencia/($0)/realizar/'.replace('($0)', $scope.audiencia.id), $scope.audiencia).success(function (data) {
            if(data.success)
            {
                $('#modal-realizar-audiencia').modal('hide');
                $scope.buscar(0);
            }
            $scope.audiencia.salvando = false;
            $scope.errors = data.errors;
        });
    };


	$scope.buscar = function(pagina, recarregar) {

		$scope.filtro.pagina = (pagina==undefined ? 0 : pagina);
		$scope.carregando = true;
        $scope.audiencia = null;

		if(pagina==0 && recarregar)
        {
            var url = gerar_url($scope.filtro, ['defensor', 'defensoria', 'data_ini', 'data_fim', 'filtro']);
            window.location.assign(url);
        }

		$http.post('/processo/audiencia/listar/', $scope.filtro).success(function (data) {

			$scope.LISTA = data.LISTA;
			$scope.filtro.ultima = data.ultima;
			$scope.filtro.paginas = data.paginas;
            $scope.usuario = data.usuario;

			for(var i = 0; i < data.registros.length; i++) {
                $scope.perm_edicao(data.registros[i], data.usuario);
            }

			if(data.registros.length && !data.ultima) {
                data.registros[data.registros.length - 1].ultimo = true;
            }

			if(data.pagina==0)
			{
				$scope.registros = data.registros;
				$scope.filtro.total = data.total;
			}
			else
			{
				for(var i = 0; i < data.registros.length; i++) {
                    $scope.registros.push(data.registros[i]);
                }
			}

			$scope.carregando = false;

		});
	};

    $scope.show_remanejar = function()
    {
        $('#modal-remanejar-audiencias').modal();
    };

    $scope.remanejar = function()
    {

        $scope.salvando = true;

        var dados = {defensor_cadastro:$scope.defensor_cadastro.id, registros:[]};

        for(var r in $scope.registros)
        {
            if($scope.registros[r].sel) {
                dados.registros.push($scope.registros[r].id);
            }
        }

		$http.post('/processo/audiencia/remanejar/', dados).success(function(data) {

            $scope.filtro.defensor = $scope.defensor_cadastro.id;

            var url = gerar_url($scope.filtro, ['defensor', 'defensoria', 'data_ini', 'data_fim', 'filtro']);
            window.location.assign(url);

        });

    };

	$scope.perm_edicao = function(registro, usuario)
	{
        registro.perm_edicao = (
            usuario.defensor == registro.defensor_cadastro ||
            usuario.comarca == registro.processo__comarca_id ||
            $filter('filter')(usuario.supervisores, registro.defensor_cadastro).length > 0 ||
            $filter('filter')(usuario.defensorias, registro.defensoria).length > 0
        );
	};

}

function DistribuirListCtrl($scope, $http, $filter){
    // Cache dos processos já consultados
    $scope.processos = {};

    $scope.get_processo = function(processo_numero, tentativas=0){
        // Dados do processo atual
        $scope.processo = null;
        // Se já possui os dados em cache, retorna valor armazenado
		if($scope.processos[processo_numero] && tentativas==0) {
            $scope.processo = $scope.processos[processo_numero];
        }
        // Senão, consulta dados no servidor
        else
		{
            $scope.processos[processo_numero] = {};
			$http.get('/procapi/processo/'+processo_numero+'/consultar/').success(function(data){
                // Se processo está atualizado, retorna dados dos eventos da defensoria
                if(data.processo.atualizado)
                {
                    var eventos_defensoria = $filter('filter')(data.processo.eventos, {defensoria: true});
                    $scope.processo = {eventos: eventos_defensoria};
                    $scope.processos[processo_numero] = {eventos: eventos_defensoria};
                }
                // Senão, faz uma nova tentativa a cada minuto até conseguir
                else
                {
                    setTimeout(function () {
                        $scope.get_processo(processo_numero, tentativas+=1);
                    }, 1000);
                }
			});
		}
    };

}

function VisualizarCtrl($scope, $http, $filter, $interval, DefensorAPI, DefensoriaAPI)
{

    const MAX_TENTATIVAS = 30;
    $scope.processo_atual = null;

    $scope.init = function(numero, grau)
    {

        let processo = {'numero_puro': numero, 'grau': grau};
        $scope.processo_atual = processo;

        if(processo.numero_puro.length)
        {
            $scope.eproc = null;
            $scope.carregando_processo = 1;
            $scope.escutar_eproc(processo.numero_puro + processo.grau);
        }

    };

    $scope.carregar_eproc_vinculado = function(processo, tentativas)
    {
        $http.get('/procapi/processo/' + processo.numero + '/consultar/').success(function(data){
            if(!data.sucesso || data.processo.atualizado || tentativas==MAX_TENTATIVAS)
            {
                processo.eproc = data;
                processo.carregando = false;
            }
            else
            {
                setTimeout(function () {
                    $scope.carregar_eproc_vinculado(processo, tentativas+=1);
                }, 1000);
            }
        });
    }

    $scope.escutar_eproc = function(numero_processo)
    {
        $http.get('/procapi/processo/' + numero_processo + '/consultar/').success(function(data){
            if((!data.sucesso || data.processo.atualizado) || $scope.carregando_processo==MAX_TENTATIVAS)
            {

                $scope.eproc = data;
                $scope.carregando_processo = false;

                if(data.sucesso)
                {
                    for(var i = 0; i < data.processo.vinculados.length; i++)
                    {
                        data.processo.vinculados[i].carregando = true;
                        $scope.carregar_eproc_vinculado(data.processo.vinculados[i], 0);
                    }
                }

            }
            else
            {
                setTimeout(function () {
                    $scope.carregando_processo+=1;
                    $scope.escutar_eproc(numero_processo);
                }, 1000);
            }
        });
    };

}

// https://gist.github.com/gabrielpeixoto/474c5f231206018211bd4b765f7f79cb
function validarNumeroUnicoProcesso(numero) {
    const bcmod = (x, y) =>
    {
      const take = 5;
      let mod = '';

      do
      {
        let a = parseInt(mod + x.substr(0, take));
        x = x.substr(take);
        mod = a % y;
      }
      while (x.length);

      return mod;
    };

    // remove todos os pontos e traços
    const numeroProcesso = numero.replace(/[.-]/g, '')

    if (numeroProcesso.length < 14 || isNaN(numeroProcesso)) {
      return false;
    }

    const digitoVerificadorExtraido = parseInt(numeroProcesso.substr(-13, 2));

    const vara = numeroProcesso.substr(-4, 4);  // (4) vara originária do processo
    const tribunal = numeroProcesso.substr(-6, 2);  // (2) tribunal
    const ramo = numeroProcesso.substr(-7, 1);  // (1) ramo da justiça
    const anoInicio = numeroProcesso.substr(-11, 4);  // (4) ano de inicio do processo
    const tamanho = numeroProcesso.length - 13;
    const numeroSequencial = numeroProcesso.substr(0, tamanho).padStart(7, '0');  // (7) numero sequencial dado pela vara ou juizo de origem

    const digitoVerificadorCalculado = 98 - bcmod((numeroSequencial + anoInicio + ramo + tribunal + vara + '00'), '97');

    return digitoVerificadorExtraido === digitoVerificadorCalculado;
}
