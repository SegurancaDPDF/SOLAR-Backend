function EventoCtrl($scope, $http, $filter, DefensorAPI, DefensoriaAPI, AtuacaoAPI)
{

    $scope.eventos = [];
    $scope.comarcas = [];
    $scope.atuacoes = ['Substituição', 'Acumulação', 'Titular'];
    $scope.dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'];
    $scope.evento = {'titulo':null, 'diretoria':null, 'comarcas':[], 'data_ini':(new Date()), 'data_fim':(new Date())};
    $scope.carregando = false;
    $scope.usuario = {};
    $scope.utcTimeFormat = "yyyy-MM-dd'T'HH:mm:ss.sss'Z'";

    $scope.defensorias_disponiveis = [];
    $scope.defensorias_selecionadas = [];
    $scope.hora_ini_default = "00:00";
    $scope.simultaneos_default = 0;
    $scope.errors = [];
    
    $scope.marcar_extra = function(index)
    {
        if($scope.evento.agenda.dias[index])
        {
            $scope.evento.agenda.extra[index] = true;
        }
    };

    $scope.popover = function(obj)
    {

        var content = '<small>Cadastro em: <b>' + $filter('date')($filter('utc')(obj.data_cadastro), "dd/MM/yyyy hh:mm") + '</b><br/>';
        content += 'Data Início: <b>' + $filter('date')($filter('utc')(obj.data_ini), "dd/MM/yyyy") + '</b><br/>';
        content += 'Data Término: <b>' + $filter('date')($filter('utc')(obj.data_fim), "dd/MM/yyyy") + '</b></small>';

        return {'title': obj.titulo, 'content': content};
    };

    $scope.carregar_defensor = function(obj)
    {

        if(obj==undefined)
        {
            $scope.listar_diretorias();
            $scope.listar();
            return;
        }

        $scope.evento.defensor = obj;
        $scope.evento.defensor.atuacoes = null;
        $scope.carregando = true;

        $http.get('/defensor/'+obj.id+'/atuacoes/').success(function(data){
            obj.atuacoes = $filter('filter')(data, {defensoria: {possui_categoria_agenda:true}});;
            $scope.validar_datas();

            for(var i = 0; i < obj.atuacoes.length; i++) {
                $scope.carregar_defensoria(obj.atuacoes[i]);
            }

            if(obj.atuacoes.length)
            {
                $scope.set_agenda(obj.atuacoes[0]);
            }

            $http.get('/defensor/'+obj.id+'/comarcas/'+(new Date()).getFullYear()+'/').success(function(data){

                $scope.comarcas = data;

                $http.get('/evento/defensor/'+obj.id+'/listar/').success(function(data){
                    $scope.agendas = data;
                    $scope.filtrar_eventos();
                    $scope.carregando = false;
                });

            });

        });

        $http.get('/atendimento/agendamento/conflitos/defensor/'+obj.id+'/total/').success(function(data){
            $scope.conflitos = data.qtd;
        });

    };

    $scope.set_agenda = function(agenda)
    {
        $scope.evento.agenda = agenda;
        $scope.evento.agenda.dia = agenda.horarios[0];
        $scope.carregar_categoria_de_agenda(agenda.defensoria.categorias_de_agendas[0]);
    }

    $scope.filtrar_eventos = function()
    {

        $scope.eventos_defensor = [];

        for(var i = 0; i < $scope.eventos.length; i++)
        {
            if($scope.eventos[i].comarca.id)
            {
                var adiciona = false;
                for(var j = 0; j < $scope.comarcas.length; j++)
                {
                    if($scope.eventos[i].comarca.id==$scope.comarcas[j].id) {
                        adiciona = true;
                    }
                    else
                    {
                        for(var k = 0; k < $scope.eventos[i].eventos.length; k++)
                        {
                            if($scope.eventos[i].eventos[k].comarca.id==$scope.comarcas[j].id) {
                                adiciona = true;
                            }
                        }
                    }
                }
                if(adiciona) {
                    $scope.eventos_defensor.push($scope.eventos[i]);
                }
            }
            else
            {
                if($scope.eventos[i].defensor == null || ($scope.evento.defensor && $scope.eventos[i].defensor == $scope.evento.defensor.id)) {
                    $scope.eventos_defensor.push($scope.eventos[i]);
                }
            }
        }

    };

    $scope.carregar_defensoria = function(agenda)
    {

        if(agenda==undefined) {
            agenda = $scope.evento.agenda;
        }

        if(agenda.dias==undefined)
        {

            agenda.dias = [];
            agenda.extra = [];
            agenda.horarios = [];
            agenda.presencial = [];
            agenda.remoto = [];
            agenda.vagas = 0;
            agenda.simultaneos = $scope.simultaneos_default;
            agenda.duracao = 0;
            agenda.hora_ini = $scope.hora_ini_default;
            agenda.hora_fim = "00:00";

            for(var i = 0; i < $scope.dias_semana.length; i++)
            {

                var conciliacao = {};
                for(var j = 0; j < agenda.defensoria.categorias_de_agendas.length; j++)
                {
                    conciliacao[agenda.defensoria.categorias_de_agendas[j].id] = [];
                }

                var dia_util = i < 5;
                agenda.dias.push(dia_util);
                agenda.extra.push(dia_util);
                agenda.presencial.push(dia_util);
                agenda.remoto.push(false);
                agenda.horarios.push({dia: $scope.dias_semana[i], horarios:[], conciliacao:conciliacao, ativo: true});

            }

            for(var j = 0; j < agenda.defensoria.categorias_de_agendas.length; j++)
            {
                var categoria = agenda.defensoria.categorias_de_agendas[j];
                categoria.hora_ini = agenda.hora_ini;
                categoria.hora_fim = agenda.hora_fim;
                categoria.duracao = agenda.duracao;
                categoria.vagas = agenda.vagas;
                categoria.dias = angular.copy(agenda.dias);
                categoria.extra = angular.copy(agenda.extra);
                categoria.presencial = angular.copy(agenda.presencial);
                categoria.remoto = angular.copy(agenda.remoto);
                $scope.recalcular(agenda, categoria);
            }
            
            if(agenda.defensoria.categorias_de_agendas.length){
                agenda.categoria_de_agenda = agenda.defensoria.categorias_de_agendas[0];
            }

        }

    };

    $scope.carregar_categoria_de_agenda = function(categoria){
        var agenda = $scope.evento.agenda;
        agenda.categoria_de_agenda = categoria;
        agenda.hora_ini = categoria.hora_ini;
        agenda.hora_fim = categoria.hora_fim;
        agenda.duracao = categoria.duracao;
        agenda.vagas = categoria.vagas;
        agenda.dias = categoria.dias;
        agenda.extra = categoria.extra;
        agenda.presencial = categoria.presencial;
        agenda.remoto = categoria.remoto;
    }

    $scope.excluir = function(obj)
    {
        if(obj==undefined)
        {
            $http.post('/evento/excluir/', $scope.selecionado).success(function(data){
                if(data.success)
                {
                    $scope.listar();
                    $scope.carregar_defensor($scope.evento.defensor);
                    $('#modal-excluir-evento').modal('hide');
                    show_stack_success('Registro excluído com sucesso!');
                }
                else {
                    show_stack_error('Ocorreu um erro ao excluir o registro!');
                }
            });
        }
        else {
            $scope.selecionado = obj;
        }
    };

    $scope.remover = function()
    {
        $http.post('/evento/excluir-parcial/', $scope.selecionado).success(function(data){
            if(data.success)
            {
                $scope.listar();
                $scope.carregar_defensor($scope.evento.defensor);
                $('#modal-excluir-evento').modal('hide');
                show_stack_success('Registros removidos do evento com sucesso!');
            }
            else {
                show_stack_error('Ocorreu um erro ao removers registros do evento!');
            }
        });
    };

    $scope.listar = function()
    {
        $http.get('/evento/listar/').success(function(data){
            $scope.eventos = data;
            $scope.filtrar_eventos();
        });
        $http.get('/evento/desbloqueio/listar/').success(function(data){
            $scope.desbloqueios = data;
            $scope.desbloqueios_pendentes = $filter('filter')($scope.desbloqueios, {autorizado_por:null}).length;
        });
    };

    $scope.listar_diretorias = function()
    {
        $http.get('/diretoria/listar/').success(function(data){

            $scope.diretorias = data;
            $scope.comarcas = [];

            for(key in data)
            {
                if(data[key].id==$scope.params.diretoria || $scope.params.superuser)
                {
                    $scope.comarcas = $scope.comarcas.concat(data[key].comarcas);
                }
                if(!$scope.evento.diretoria || data[key].id==$scope.evento.diretoria)
                {
                    data[key].selected = true;
                }
                if(!$scope.evento.diretoria)
                {
                    for(var i = 0; i < data[key].comarcas.length; i++)
                    {
                        $scope.evento.comarcas.push(data[key].comarcas[i].id);
                    }
                }
            }

        });
    };

    // TODO: Refatorar: a view '/defensor/listar/' foi substituída por '/api/v1/defensores/' que não retorna os ids dos núcleos
    $scope.filtra_defensores_by_nucleo = function (nucleo) {
        nucleo.forEach(el => {
            if ($scope.defensores) {
                $scope.defensores = $scope.defensores.filter(defensor => defensor.nucleos.includes(el));
            }
        });
    }

    $scope.listar_defensores = function(defensor_id)
    {
        $scope.defensores = null;
        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
		DefensorAPI.get({ativo:true, limit:1000}, function(data){
			$scope.defensores = data.results;
            $scope.set_defensor(defensor_id);
		});
    };

    $scope.listar_defensorias = function() {
        $scope.defensorias = null;
        // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
        DefensoriaAPI.get({limit:1000}, function(data){
            $scope.defensorias = data.results;
            $scope.filtrar_defensorias_por_comarca();
            $scope.filtrar_defensorias_por_diretoria();
        });
    }

    $scope.filtrar_defensorias_por_comarca = function()
    {
        for(var i = 0; i < $scope.defensorias.length; i++)
        {
            for(var j = 0; j < $scope.evento.comarcas.length; j++)
            {
                if($scope.defensorias[i].comarca==$scope.evento.comarcas[j])
                {
                    var index = $scope.defensorias_selecionadas.indexOf($scope.defensorias[i]);
                    if(index==-1)
                    {
                        $scope.defensorias_selecionadas.push($scope.defensorias[i]);
                    }
                }
            }
        }
    };

    $scope.filtrar_defensorias_por_diretoria = function()
    {
        var comarcas = [];
        for(key in $scope.diretorias)
        {
            if($scope.diretorias[key].selected)
            {
                for(var i = 0; i < $scope.diretorias[key].comarcas.length; i++)
                {
                    comarcas.push($scope.diretorias[key].comarcas[i].id);
                }
            }
        }

        $scope.disponiveis = [];
        $scope.defensorias_disponiveis = [];

        for(var i = 0; i < $scope.defensorias.length; i++)
        {
            for(var j = 0; j < comarcas.length; j++)
            {
                if($scope.defensorias[i].comarca.id==comarcas[j])
                {
                    var index = $scope.defensorias_selecionadas.indexOf($scope.defensorias[i]);
                    if(index==-1)
                    {
                        $scope.defensorias_disponiveis.push($scope.defensorias[i]);
                    }
                }
            }
        }

    };

    $scope.set_defensor = function(defensor_id)
    {
        for(var i = 0;  i < $scope.defensores.length; i++)
        {
            if($scope.defensores[i].id==defensor_id)
            {
                $scope.evento.defensor = $scope.defensores[i];
                $scope.carregar_defensor($scope.evento.defensor);
            }
        }
    };

    $scope.possui_comarcas_selecionadas = function()
    {
        if($scope.evento.diretoria && $scope.evento.diretoria.comarcas)
        {
            for(var i = 0; i < $scope.evento.diretoria.comarcas.length; i++)
            {
                if($scope.evento.diretoria.comarcas[i].selected) {
                    return true;
                }
            }
        }
    };

    // passa por todas as atuações e categorias de agenda para verificar se tem alguma selecionada
    $scope.possui_categorias_selecionadas = function()
    {
        if($scope.evento.defensor && $scope.evento.defensor.atuacoes)
        {
            for(var i = 0; i < $scope.evento.defensor.atuacoes.length; i++)
            {
                for(var j = 0; j < $scope.evento.defensor.atuacoes[i].defensoria.categorias_de_agendas.length; j++)
                {
                    if($scope.evento.defensor.atuacoes[i].defensoria.categorias_de_agendas[j].selected) {
                        return true;
                    }
                }
            }
        }
    };


    $scope.show = function(tipo)
    {

        $scope.evento = {'titulo':null, 'diretoria':null, 'comarcas':[], 'data_ini':(new Date()), 'data_fim':(new Date()), 'defensor':$scope.evento.defensor, 'tipo':tipo, 'defensorias':[]};

        if($scope.defensorias==undefined) {
            return;
        }

        for(var i = 0; i < $scope.diretorias.length; i++)
        {
            for(var j = 0; j < $scope.diretorias[i].comarcas.length; j++)
            {
                $scope.diretorias[i].comarcas[j].selected = null;
            }
        }

    };

    $scope.salvar = function(avancado)
    {

        $scope.salvando = true;
        $scope.errors = [];

        $scope.evento.defensorias = [];

        if(avancado)
        {
            for(var i = 0; i < $scope.defensorias_selecionadas.length; i++)
            {
                $scope.evento.defensorias.push($scope.defensorias_selecionadas[i].id);
            }
        }

        $http.post('/evento/salvar/', $scope.evento).success(function(data){
            if(data.success)
            {
                if(avancado)
                {
                    window.location.href = "/evento/";
                }
                else
                {
                    $('#modal-cadastrar-evento').modal('hide');
                    $scope.listar();
                }
            }
            else
            {
                $scope.errors = data.errors;
            }
            $scope.salvando = false;
        });

    };

    $scope.validate_form = function() {
        if(!$scope.evento.titulo){
            show_stack_error('Preencha o campo título da Agenda!');
            return false;
        }
        if($scope.evento.agenda.vagas <= 0){
            show_stack_error('Entre com um número válido de vagas!');
            return false;
        }
        if($scope.evento.agenda.duracao <= 0){
            show_stack_error('Entre com uma duração válida de atendimento!');
            return false;
        }
        if($scope.evento.agenda.simultaneos <= 0){
            show_stack_error('Entre com um número válido de simultâneos!');
            return false;
        }
        return true;
    }

    $scope.salvar_agenda = function () {
        if($scope.validate_form()){
            $scope.errors = [];
            $http.post('/evento/agenda/salvar/',$scope.evento).success(function(data){
                if(data.success)
                {
                    window.location.href = "/evento/?defensor=" + $scope.evento.defensor.id;
                }
                else
                {
                    $scope.errors = data.errors;
                }
            });
        }
    }

    $scope.ver_agenda = function(obj)
    {
        $scope.selecionado = obj;
    };

    $scope.chart_margin = function(val,index)
    {

        var ini = new Date(val.data_ini);
        var fim = new Date(val.data_fim);

        if(index==undefined) {
            index = 0;
        }

        return({'left':(ini.getDayOnYear()*20)+'px','width':((fim.getDayOnYear()-ini.getDayOnYear()+1)*20)+'px', 'top':((index*25)+50)+'px'});

    };

    function day_in_year(val)
    {
        var start = new Date(val.getFullYear(), 0, 0);
    }

    $scope.validar = function()
    {
        if($scope.evento && $scope.evento.defensor && $scope.evento.defensor.atuacoes.length)
        {
            var conflitos_hora = $filter('filter')($scope.evento.defensor.atuacoes, {conflito:true});
            return (conflitos_hora && conflitos_hora.length==0);
        }
    };

    $scope.validar_datas = function()
    {

        var errors = false;
        var evento = $scope.evento;
        var atuacoes = $scope.evento.defensor.atuacoes;

        for(var i = 0; i < atuacoes.length; i++)
        {

            if(!atuacoes[i].pode_criar_agenda)
            {
                atuacoes[i].errors = 3;
                atuacoes[i].error_description = 'A defensoria não aceita a criação de novas agendas';
            }
            else if(
                (new Date(atuacoes[i].data_ini) > evento.data_ini && new Date(atuacoes[i].data_ini) <= evento.data_fim) ||
                (new Date(atuacoes[i].data_fim) < evento.data_fim && new Date(atuacoes[i].data_fim) >= evento.data_ini))
            {
                errors = true;
                atuacoes[i].errors = 2;
                atuacoes[i].error_description = 'A atuação começa ou termina no meio do período da agenda';
            }
            else if(new Date(atuacoes[i].data_ini) > evento.data_fim || (atuacoes[i].data_fim && new Date(atuacoes[i].data_fim) < evento.data_ini)) {
                atuacoes[i].errors = 1;
                atuacoes[i].error_description = 'A atuação começa depois ou termina antes do período da agenda';
            }
            else {
                atuacoes[i].errors = 0;
            }
        }

        $scope.sel_primeira_aba();
        $scope.conflitos = errors;

    };

    $scope.sel_primeira_aba = function()
    {
        var atuacoes = $filter('filter')($scope.evento.defensor.atuacoes, {agendamento:true, errors:0});
        
        if (atuacoes.length){
            var atuacao = atuacoes[0];
            $scope.evento.agenda = atuacao;
            $scope.recalcular(atuacao);
            $scope.carregar_categoria_de_agenda(atuacao.defensoria.categorias_de_agendas[0]);
        }
    };

    $scope.validar_horarios = function()
    {

        // Continua se defensor selecionado e possui atuacoes
        if($scope.evento.defensor && $scope.evento.defensor.atuacoes)
        {

            // Cria atalho para as agendas
            var agendas = $filter('filter')($scope.evento.defensor.atuacoes, {agendamento:true, errors:0});

            // Passa por todas agendas
            for(var i = 0; i < agendas.length; i++)
            {

                // Reinicia registro de conflitos
                agendas[i].conflitos = [];

                // Transforma string hora inicio/termino em data
                var ini_1 = time_to_date(agendas[i].hora_ini);
                var fim_1 = time_to_date(agendas[i].hora_fim);

                // Passa pelas proximas agendas
                for(var j = i + 1; j < agendas.length; j++)
                {
                    // Continua se existem dias marcados marcados nas duas agendas
                    if(agendas[i].dias && agendas[j].dias && agendas[i].defensoria.nucleo == null && agendas[j].defensoria.nucleo == null)
                    {
                        // Transforma string hora inicio/termino em data
                        var ini_2 = time_to_date(agendas[j].hora_ini);
                        var fim_2 = time_to_date(agendas[j].hora_fim);
                        // Passa por todos dias da semana
                        for(var k = 0; k < agendas[i].dias.length; k++)
                        {
                            // Conflito se: mesmo dia marcado nas duas agendas e intervalo de inicio/termino coincidem
                            if(agendas[i].dias[k] && agendas[j].dias[k] && ((ini_1 >= ini_2 && ini_1 < fim_2) || (fim_1 <= fim_2 && fim_1 > ini_2))) {
                                agendas[i].conflitos.push({
                                    'dia': k,
                                    'hora_ini': agendas[j].hora_ini,
                                    'hora_fim': agendas[j].hora_ini,
                                    'defensoria': agendas[j].defensoria.nome
                                });
                            }
                        }

                    }
                }

                // Ativa conflito se houve mais de um adicionado
                agendas[i].conflito = (agendas[i].conflitos.length > 0);

            }

        }

    };

    $scope.recalcular = function(agenda, categoria_de_agenda)
    {

        if(agenda==undefined) {
            agenda = $scope.evento.agenda;
        }
        
        if(categoria_de_agenda==undefined) {
            categoria_de_agenda = $scope.evento.agenda.categoria_de_agenda;
        }

        if(agenda && agenda.hora_ini && agenda.dias && categoria_de_agenda)
        {
            
            agenda.hora_fim = agenda.hora_ini;
            
            // Guarda configurações para uso posterior
            categoria_de_agenda.hora_ini = agenda.hora_ini;
            categoria_de_agenda.hora_fim = agenda.hora_fim;
            categoria_de_agenda.duracao = agenda.duracao;
            categoria_de_agenda.vagas = agenda.vagas;

            var ini = time_to_date(agenda.hora_ini);
            var fim = new Date(ini.getTime() + parseInt(agenda.duracao) * parseInt(agenda.vagas) * 60000);
            
            agenda.hora_fim = $filter('date')(fim, "HH:mm");

            for(var i = 0; i < agenda.dias.length; i++)
            {

                var horarios = [];

                if(agenda.dias[i])
                {
                    for(var j = 0; j < agenda.vagas; j++)
                    {
                        var horario = new Date(ini.getTime() + parseInt(agenda.duracao) * j * 60000);
                        horarios.push($filter('date')(horario, "HH:mm"));
                    }
                }

                if(agenda.extra[i] && !horarios.length)
                {
                    horarios.push("00:00");
                }

                agenda.horarios[i].ativo = agenda.dias[i];
                agenda.horarios[i].horarios = horarios;
                agenda.horarios[i].conciliacao[categoria_de_agenda.id] = horarios;

            }

            agenda.dia = agenda.horarios[0];

        }

        $scope.validar_horarios();

    };

    function time_to_date(str)
    {
        if(str) return new Date(2000, 0, 1, str.substring(0, 2), str.substring(3, 5));
    }

    $scope.adicionar_horario = function(array, value)
    {
        if (value){
            for(var i in array)
            {
                if(array[i]==value)
                {
                    return false;
                }
            }

            array.push(value);
            array.sort();
        }
    };

    $scope.remover_horario = function(array, index)
    {
        array.splice(index, 1);
    };

    $scope.mudar_dia = function(d)
    {
        $scope.dia = d;
    };

    $scope.listar_defensores_por_lotacao_do_usuario = function(servidor_id, defensor_id){
  
        AtuacaoAPI.get({ativo:true, apenas_vigentes:true, servidor_id:servidor_id}, function(data){
           
            let resultados = data.results;
            let resultadoIds = [];

            resultados.forEach( item =>{
                resultadoIds.push(item.defensoria.id);
            })

            // TODO: trocar limit por paginação p/ garantir q todos registros sejam consultados
            AtuacaoAPI.get({ativo:true, apenas_defensor:true, defensoria_id:resultadoIds.join(), incluir_defensorias_filhas:true, limit:1000}, function(data){

                let defensores = data.results;
                defensores = defensores.map(item=>{
                    if(item.defensor.id)
                        return item.defensor;
                })

                defensores = defensores.filter( (elem, index)=>
                    defensores.findIndex(obj =>(obj.id === elem.id)) === index)

                $scope.defensores = defensores;
                $scope.set_defensor(defensor_id);

            })

        })

    }

    $scope.init = function(defensor_id, params)
    {
    
        $scope.params = params;

        if(params.usuario_id && !params.superuser)
            $scope.listar_defensores_por_lotacao_do_usuario(params.usuario_id, defensor_id);
        else
            $scope.listar_defensores(defensor_id);

        $scope.listar_defensorias();
        $scope.listar_diretorias();
        $scope.listar();

        $scope.meses = [];
        $scope.colunas = [];

        var ano = new Date().getFullYear();
        var meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];

        for(var mes = 1; mes <= meses.length; mes++)
        {
            var dias_mes = new Date(ano, mes, 0).getDate();
            $scope.meses.push({'nome':meses[mes-1],'dias':dias_mes});

            for(var dia = 1; dia <= dias_mes; dia++)
            {
                $scope.colunas.push(new Date(ano, mes-1, dia));
            }
        }

    };

    $scope.disponiveis = [];
    $scope.selecionadas = [];
    $scope.filtro_disponiveis = null;
    $scope.filtro_selecionadas = null;

    $scope.adicionar_todas_defensorias = function()
    {

        var defensorias = $filter('filter')($scope.defensorias_disponiveis, $scope.filtro_disponiveis);
        $scope.defensorias_selecionadas = $scope.defensorias_selecionadas.concat(defensorias);
        $scope.disponiveis = [];

        for(var i = 0; i < defensorias.length; i++)
        {
            var index = $scope.defensorias_disponiveis.indexOf(defensorias[i]);
            $scope.defensorias_disponiveis.splice(index, 1);
        }

    };

    $scope.adicionar_defensorias = function()
    {

        $scope.defensorias_selecionadas = $scope.defensorias_selecionadas.concat($scope.disponiveis);

        for(var i = 0; i < $scope.disponiveis.length; i++)
        {
            var index = $scope.defensorias_disponiveis.indexOf($scope.disponiveis[i]);
            $scope.defensorias_disponiveis.splice(index, 1);
        }

        $scope.disponiveis = [];

    };

    $scope.remover_todas_defensorias = function()
    {

        var defensorias = $filter('filter')($scope.defensorias_selecionadas, $scope.filtro_selecionadas);
        $scope.defensorias_disponiveis = $scope.defensorias_disponiveis.concat(defensorias);
        $scope.selecionadas = [];

        for(var i = 0; i < defensorias.length; i++)
        {
            var index = $scope.defensorias_selecionadas.indexOf(defensorias[i]);
            $scope.defensorias_selecionadas.splice(index, 1);
        }

    };

    $scope.remover_defensorias = function()
    {

        $scope.defensorias_disponiveis = $scope.defensorias_disponiveis.concat($scope.selecionadas);

        for(var i = 0; i < $scope.selecionadas.length; i++)
        {
            var index = $scope.defensorias_selecionadas.indexOf($scope.selecionadas[i]);
            $scope.defensorias_selecionadas.splice(index, 1);
        }

        $scope.selecionadas = [];

    }

    $scope.autorizar = function(obj)
    {
        if(obj==undefined)
        {
            $scope.selecionado.conflitos = null;
            $http.post('autorizar/', $scope.selecionado).success(function(data){
                if(data.success)
                {
                    $scope.listar();
                    $('#modal-autorizar-evento').modal('hide');
                    show_stack_success('Registro autorizado com sucesso!');
                }
                else {
                    show_stack_error('Ocorreu um erro ao autorizar o registro!');
                }
            });
        }
        else {
            $scope.selecionado = obj;
        }
    };

    $scope.atualizar_simultaneos = function () {
        $http.post('/evento/agenda/atualizar/', $scope.selecionado).success(function (data) {
            if (data.success) {
                window.location.href = "/evento/?defensor=" + $scope.evento.defensor.id;
            }
        });
    };

}
