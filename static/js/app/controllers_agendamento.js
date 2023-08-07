
function AgendamentoCtrl($scope, $http, $filter)
{
    $scope.diasSemana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];
    $scope.atuacao = null;
    $scope.remarcando = false;

    $scope.set_categoria = function()
    {
        if($scope.atuacao!=undefined)
        {
            if($scope.atuacao.categorias_de_agendas[0])
            {
                $scope.categoria_de_agenda = $scope.atuacao.categorias_de_agendas[0].id;
            }
            $scope.carregarMes($scope.ano, $scope.mes);
        }
    };

    $scope.set_itinerante = function(value)
    {
        $scope.atuacao = null;
        $scope.itinerante = value;
    };

    $scope.init = function(params={})
    {

        if(params.comarca!=undefined) {
            $scope.comarca = params.comarca;
        }

        if(params.defensoria!=undefined) {
            $scope.defensoria = params.defensoria;
        }

        if(params.defensor!=undefined) {
            $scope.defensor = params.defensor;
        }

        if(params.categoria_de_agenda!=undefined) {
            $scope.categoria_de_agenda = params.categoria_de_agenda;
        }

        if(params.ano!=undefined && params.mes!=undefined)
        {
            $scope.carregarMes(params.ano, params.mes-1);
        }
        else
        {
            var dia = new Date();
            $scope.carregarMes(dia.getFullYear(), dia.getMonth());
        }

        $scope.prazo = params.prazo;
        $scope.prioridade = params.prioridade;
        $scope.anotacoes = params.anotacoes;

    };

    $scope.getMesStr = function()
    {
        var meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
        return meses[$scope.mes] + ' - ' + $scope.ano;
    };

    $scope.prevMes = function()
    {
        if($scope.mes==0) {
            $scope.carregarMes($scope.ano - 1, 11);
        }
        else {
            $scope.carregarMes($scope.ano, $scope.mes - 1);
        }
    };

    $scope.nextMes = function()
    {
        if($scope.mes==11) {
            $scope.carregarMes($scope.ano + 1, 0);
        }
        else {
            $scope.carregarMes($scope.ano, $scope.mes + 1);
        }
    };

    $scope.carregarMes = function(ano, mes)
    {

        var agora = new Date();
        $scope.hoje = new Date(agora.getFullYear(), agora.getMonth(), agora.getDate());

        $scope.ano = ano;
        $scope.mes = mes;

        var ini = new Date(ano, mes, 1);
        var fim = new Date(ano, mes + 1, 0);

        $scope.data_ini = ini;
        $scope.data_fim = fim;

        var last = new Date(ano, mes, 1);
        last.setHours(-24);

        var diasMes = fim.getDate();
        var diaSemana = ini.getDay();

        var semana = [];
        var semanas = [];

        semanas = [];
        semanas.push(semana);

        for(var i = 0; i < diaSemana; i++) {
            semana.push(last.getDate() - (diaSemana - i - 1));
        }

        for(var dia = 1; dia <= diasMes; dia++)
        {

            if(diaSemana==0)
            {
                semana = [];
                semanas.push(semana);
            }

            semana.push({data:new Date(ano, mes, dia), horarios:null, eventos:[]});

            diaSemana++;
            if(diaSemana==7) {
                diaSemana = 0;
            }

        }

        if(diaSemana!=0)
        {
            for(var i = diaSemana; i < 7; i++) {
                semana.push(i - diaSemana + 1);
            }
        }

        $scope.semanas = semanas;
        $scope.carregando = true;

        $http.post('', {
                'comarca':$scope.comarca,
                'atuacao':($scope.atuacao ? $scope.atuacao.id : null),
                'defensor':($scope.defensor ? $scope.defensor : null),
                'defensoria':($scope.defensoria ? $scope.defensoria : null),
                'ano':$scope.ano,
                'mes':$scope.mes+1,
                'categoria_de_agenda': $scope.categoria_de_agenda,
                'itinerante': $scope.itinerante,
                'encaminhar': $scope.encaminhar,
                'distribuir': $scope.distribuir
            }).success(function(data){

            $scope.carregando = false;

            $scope.comarca = data.comarca;
            $scope.comarcas = data.comarcas;
            $scope.atuacoes = data.atuacoes;
            $scope.atuacao = data.atuacao;
            $scope.agendas = data.agendas;
            $scope.eventos = data.eventos;
            $scope.desbloqueios = data.desbloqueios;
            $scope.agendamentos = data.agendamentos;
            $scope.indeferimentos = data.indeferimentos;
            $scope.extra = data.extra;
            $scope.consulta = data.consulta;
            $scope.categoria_de_agenda = data.categoria_de_agenda;
            $scope.pode_agendar_com_bloqueio = data.pode_agendar_com_bloqueio;
            $scope.pode_agendar_pauta = data.pode_agendar_pauta;
            $scope.pode_agendar_extra = data.pode_agendar_extra;
            $scope.itinerante = data.itinerante;
            $scope.grupo_agendamento = data.grupo_agendamento;

            var hoje = $filter('utc')(data.hoje);
            var semanas = $scope.semanas;
            var agendas = $scope.agendas;
            var eventos = $scope.eventos;
            var desbloqueios = $scope.desbloqueios;

            if($scope.atuacoes)
            {

                for(var i = 0; i < $scope.atuacoes.length; i++)
                {
                    if($scope.atuacao && $scope.atuacao == $scope.atuacoes[i].id)
                    {
                        $scope.atuacao = $scope.atuacoes[i];
                    }
                }

                if(!isNaN($scope.atuacao)) {
                    $scope.atuacao = null;
                }

                if($scope.defensoria) {
                    $scope.defensoria = null;
                }

                if($scope.atuacao)
                {
                    let params = {'categoria_de_agenda': $scope.categoria_de_agenda};
                    $http.get('/atendimento/agendamento/conflitos/defensor/'+$scope.atuacao.defensor_id+'/total/'+$scope.ano+'/'+($scope.mes+1)+'/', {'params': params}).success(function(data){
                        $scope.conflitos = data.qtd;
                    });
                }
                else
                {
                    $scope.conflitos = null;
                }

            }

            for(var k = 0; k < agendas.length; k++)
            {
                agendas[k].data_ini = $filter('utc')(agendas[k].data_ini);
                agendas[k].data_fim = $filter('utc')(agendas[k].data_fim);
            }

            for(var k = 0; k < eventos.length; k++)
            {
                eventos[k].data_ini = $filter('utc')(eventos[k].data_ini);
                eventos[k].data_fim = $filter('utc')(eventos[k].data_fim);
            }

            for(var k = 0; k < desbloqueios.length; k++)
            {
                desbloqueios[k].data_ini = $filter('utc')(desbloqueios[k].data_ini);
                desbloqueios[k].data_fim = $filter('utc')(desbloqueios[k].data_fim);
            }

            // Passa por todas semanas do mes
            for(var i = 0; i < semanas.length; i++)
            {
                // Passa por todos dias da semana
                for(var j = 0; j < semanas[i].length; j++)
                {
                    // Vincula dia a um evento de bloqueio
                    for(var k = 0; k < eventos.length; k++)
                    {
                        if(semanas[i][j].data >= eventos[k].data_ini && semanas[i][j].data <= eventos[k].data_fim)
                        {
                            // Evento geral
                            if(eventos[k].defensor == null && eventos[k].defensoria == null) {
                                semanas[i][j].evento = k;
                            }
                            // Evento para defensor
                            else if (eventos[k].defensor == $scope.atuacao.defensor_id && (!eventos[k].defensoria || eventos[k].defensoria == $scope.atuacao.defensoria_id)) {
                                // Aplica se válido pra todas categorias ou para a categoria selecionada
                                if(eventos[k].categoria_de_agenda == null || eventos[k].categoria_de_agenda == $scope.categoria_de_agenda){
                                    semanas[i][j].evento = k;
                                }
                            }
                            // Evento para defensoria
                            else if (eventos[k].defensoria == $scope.atuacao.defensoria_id && (!eventos[k].defensor || eventos[k].defensor == $scope.atuacao.defensor_id)) {
                                // Aplica se válido pra todas categorias ou para a categoria selecionada
                                if(eventos[k].categoria_de_agenda == null || eventos[k].categoria_de_agenda == $scope.categoria_de_agenda){
                                    semanas[i][j].evento = k;
                                }
                            }
                            else {
                                semanas[i][j].eventos.push(k);
                            }
                        }
                    }

                    // Vincula dia a um evento de desbloqueio
                    for(var k = 0; k < desbloqueios.length; k++)
                    {
                        if(semanas[i][j].data >= desbloqueios[k].data_ini && semanas[i][j].data <= desbloqueios[k].data_fim)
                        {
                            semanas[i][j].desbloqueado = true;
                        }
                    }

                    // Vincula dia a uma agenda
                    for(var k = 0; k < agendas.length; k++)
                    {
                        if(semanas[i][j].data >= agendas[k].data_ini && semanas[i][j].data <= agendas[k].data_fim)
                        {
                            $scope.carregarDia(semanas[i][j], k, hoje);
                            break;
                        }
                    }

                }
            }

            if(!$scope.indeferimento && $scope.indeferimentos.length)
            {
                $('#modal-indeferimento').modal();
            }

            $('#agenda-defensoria, #agenda-categoria').find('option:eq(0)').attr('selected', '').change();

        });

    };

    $scope.carregarDia = function(dia, agenda, hoje)
    {

        var horarios = null;
        var forma_atendimento = null;

        // Se domingo (0), pega posicao 6 (no banco de dados semana começa na segunda-feira)
        if(dia.data.getDay()==0)
        {
            horarios = $scope.agendas[agenda].horarios[6];
            forma_atendimento = $scope.agendas[agenda].forma_atendimento[6];
        }
        else
        {
            horarios = $scope.agendas[agenda].horarios[dia.data.getDay()-1];
            forma_atendimento = $scope.agendas[agenda].forma_atendimento[dia.data.getDay()-1];
        }

        var agendamentos = $scope.agendamentos[dia.data.getDate()];
        var conflitos = 0;

        if((dia.data < hoje && dia.desbloqueado==undefined) || horarios==undefined || horarios.length==0) {
            return false;
        }

        horarios = horarios.slice();

        if(horarios[0]=="00:00") {
            horarios = [];
        }

        var total_pauta = $scope.agendas[agenda].simultaneos * horarios.length;
        var total_extra = $scope.extra[dia.data.getDate()];

        var vagas = {};
        for(var i = 0; i < horarios.length; i++) {
            vagas[horarios[i]] = $scope.agendas[agenda].simultaneos;
        }

        if(agendamentos!=undefined)
        {
            for(hora in agendamentos)
            {
                existe = false;
                if(hora != 'length')
                {
                    for(var i = 0; i < horarios.length; i++)
                    {
                        if(hora == horarios[i])
                        {
                            if(agendamentos[hora] >= $scope.agendas[agenda].simultaneos) {
                                horarios.splice(i, 1);
                            }
                            else {
                                vagas[hora] -= agendamentos[hora];
                            }
                            existe = true;
                            break;
                        }
                    }
                    if(!existe) {
                        conflitos += 1;
                    }
                }
            }
        }

        if($scope.atuacao && $scope.atuacao.defensor_id != $scope.agendas[agenda].defensor)
        {

            dia.substituto = $scope.get_substituto(dia);

            for(var i = 0; i < dia.eventos.length; i++)
            {
                if($scope.eventos[dia.eventos[i]].defensor == null || $scope.eventos[dia.eventos[i]].defensor == $scope.agendas[agenda].defensor) {
                    dia.evento = dia.eventos[i];
                }
            }

        }

        if(dia.evento != undefined && total_extra) {
            conflitos += total_extra;
        }

        // aplica conflitos apenas se não estiver remarcando atendimento
        if(conflitos && !$scope.remarcando)
        {
            dia.conflitos = conflitos;
            horarios = [];
        }

        // se possui horarios, valida se ainda são válidos
        if(horarios.length)
        {

            // se data passada só agenda na extra-pauta
            if(dia.data < hoje)
            {
                horarios = [];
            }

            // se hoje, remove horarios passados
            else if(dia.data.getTime() == hoje.getTime())
            {

                var continuar = true;
                var agora = new Date();

                while(continuar && horarios.length)
                {
                    var horario = new Date(hoje.getFullYear(), hoje.getMonth(), hoje.getDate(), horarios[0].substring(0, 2), horarios[0].substring(3, 5));
                    if(horario.getTime() <= agora.getTime()){
                        horarios.splice(0, 1);
                    }
                    else
                    {
                        continuar = false;
                    }
                }

            }
        }

        if(total_extra!=undefined) {
            dia.total_extra = total_extra;
        }

        // Obtém id da atuação da agenda (em caso de substituição a atuação não é a mesma da requisição)
        dia.atuacao_id = $scope.agendas[agenda].atuacao;
        dia.horarios = horarios;
        dia.total_pauta = total_pauta;
        dia.agendamentos = agendamentos;
        dia.vagas = vagas;
        dia.simultaneos = ($scope.agendas[agenda].simultaneos > 1);
        dia.forma_atendimento = forma_atendimento;

        if(dia.agendamentos && dia.agendamentos.length > dia.total_pauta || dia.evento!=null || !$scope.pode_agendar_pauta)
        {
            dia.total_pauta = 0;
            dia.horarios = [];
            dia.forma_atendimento = null;
        }

    };

    $scope.visualizar = function(dia)
    {
        if($scope.grupo_agendamento.BLOQUEAR_AGENDAMENTO_ENTRE_DEFENSORIAS) {
            if(!$scope.grupo_agendamento.aceitar_agend_pauta && dia.horarios.length > 0){
                show_stack_error("Não permitido agendamento na pauta!");
                return false;
            }
            if(!$scope.grupo_agendamento.aceitar_agend_extrapauta && dia.horarios.length === 0){
                show_stack_error("Não é permitido agendamento extra-pauta!");
                return false;
            }

        }

        // impede agendar se modo consulta ou se não tem permissão pra agendar em dia bloqueado (sem horário, com evento ou com indeferimento)
        if($scope.consulta || (!$scope.pode_agendar_com_bloqueio && (dia.horarios==undefined || dia.evento!=null || $scope.indeferimentos.length))) {
            return false;
        }

        // impede agendar na extra-pauta se não tiver permissão
        if(!$scope.pode_agendar_com_bloqueio && !dia.horarios.length && !$scope.pode_agendar_extra)
        {
            return false;
        }

        // impede agendar na pauta se não tiver permissão (obs: quando não há permissão os horários são removidos no backend)
        if(!$scope.pode_agendar_com_bloqueio && dia.horarios.length && !$scope.pode_agendar_pauta)
        {
            return false;
        }

        $scope.dia = dia;
        $scope.horario = new Date($scope.ano, $scope.mes, dia.data.getDate());
        $scope.horario_str = null;
        $scope.atuacao.substituto = $scope.get_substituto(dia);

        $('#modal-agendar').modal();

    };

    $scope.get_substituto = function(dia)
    {
        for(var i = 0; i < $scope.atuacao.substituicoes.length; i++)
        {
            if(dia.data >= $filter('utc')($scope.atuacao.substituicoes[i].data_ini) && dia.data <= $filter('utc')($scope.atuacao.substituicoes[i].data_fim)) {
                return $scope.atuacao.substituicoes[i].defensor;
            }
        }
    };

    $scope.selecionar = function(horario)
    {
        if(horario==undefined)
        {
            $scope.horario_str = null;
            $scope.horario = null;
        }
        else
        {
            $scope.horario_str = horario;
            $scope.horario = new Date($scope.ano, $scope.mes, $scope.dia.data.getDate(), parseInt(horario.substring(0,2)), parseInt(horario.substring(3,5)), 0);
        }
    };

    $scope.formatarDia = function(dia)
    {

        var agora = new Date();
        var hoje = new Date(agora.getFullYear(), agora.getMonth(), agora.getDate());

        if(dia.evento!=null)
        {
            if($scope.pode_agendar_com_bloqueio)
            {
                return 'error';
            }
            else
            {
                return 'error disabled';
            }
        }
        else if(dia.horarios && dia.horarios.length && $scope.indeferimentos.length == 0)
        {
            if(!$scope.pode_agendar_pauta)
            {
                return 'disabled';
            }
            if(dia.substituto)
            {
                return 'info';
            }
            else
            {
                return 'success';
            }
        }
        else if(dia.horarios && $scope.indeferimentos.length == 0 && $scope.pode_agendar_extra)
        {
            return 'warning';
        }
        else
        {
            return 'disabled';
        }

    };

    $scope.popover = function(obj)
    {

        var title = '[[ dia.data|date:\'dd/MM/yyyy\' ]]<small class="label label-success pull-right" ng-hide="dia.substituto">T</small><small class="label label-info pull-right" ng-show="dia.substituto">S</small><br><b>[[ eventos[dia.evento].titulo ]]</b>';
        var content = '<small class="muted" ng-show="dia.substituto">[[ dia.substituto ]]</small>';
        content += '<p class="text-success">Pauta: <b>[[(dia.agendamentos.length?dia.agendamentos.length+\' agendada(s)\':\'Nenhuma\')]]</b></p>';
        content += '<p class="text-warning">Extra Pauta: <b>[[(dia.total_extra?dia.total_extra+\' agendada(s)\':\'Nenhuma\')]]</b></p>';
        content += '<p class="text-error" ng-show="dia.conflitos">Conflitos: <b>[[(dia.conflitos?dia.conflitos+\' conflitos(s)\':\'Nenhum\')]]</b></p>';

        return {"title": title, "content": content};

    };

    $scope.justificar = function()
    {

        $scope.carregando = true;
        $http.post('/atendimento/agendamento/justificar/',{'justificativa':$scope.justificativa}).success(function(data){
            $('modal-indeferimento').modal('toggle');
            $scope.indeferimentos = [];
            $scope.carregando = false;
        });

    }

}
