function AtividadeExtraordinariaCtrl($scope, $http, $filter)
{

    $scope.params = {};
    $scope.perms = {};

    $scope.atividade = {};
    $scope.atividades = [];
    $scope.atividades_tipos = [];
    $scope.areas = [];
    $scope.atividades_tipos_filtrado = [];
    $scope.complemento = {};
    $scope.defensorias = [];
    $scope.defensores = [];

    $scope.carregando_atividades = true;

    $scope.carregar_atividades_extraordinarias = function()
    {
        $scope.carregando_atividades = true;

        $http.post('/atividade-extraordinaria/get/', $scope.params).success(function(json)
        {
            $scope.carregando_atividades = false;

            if( json.defensorias )
            {
                $scope.perms = json.perms;
                $scope.atividades = json.atividades;
                $scope.atividades_tipos = json.atividades_tipos;
                $scope.areas = json.areas;
                $scope.atividades_tipos_filtrado = $filter('filter')($scope.atividades_tipos, {eh_brinquedoteca: true});
                $scope.defensorias = json.defensorias;
                $scope.defensores = json.defensores;
            }
        });
    }

    $scope.limpar = function()
    {

        // força limpeza do campo de data
        $('[bs-datepicker]').val('');

        $scope.atividade = {};
        $scope.complemento = {};

        var agora = new Date();
        $scope.data_referencia = agora;
        $scope.hora_referencia = agora.toLocaleTimeString().substring(0, 5);
        $scope.data_encerrado = null;
        $scope.hora_encerrado = null;

        // pré-selecionar tipo se houver apenas um
        if($scope.atividades_tipos_filtrado.length==1)
        {
            $scope.atividade.tipo = $scope.atividades_tipos_filtrado[0].id;
        }

        // pré-selecionar defensoria se houver apenas uma
        if($scope.defensorias.length==1)
        {
            $scope.atividade.setor_criacao = $scope.defensorias[0].id;
        }

        // pré-selecionar participante se houver apenas um
        if($scope.defensores.length==1)
        {
            $scope.atividade.participantes = $scope.defensores[0].usuario_id;
        }

    }

    $scope.atividade_modal_cadastrar = function(modal_id)
    {
        var modal = $('#' + modal_id);
        var form = modal.find('form');
        var hoje = new Date();

        form[0].reset();
        form.find('[name="id"]').val('');
        form.find('[name="data_referencia"]').val(hoje.toLocaleDateString()).datepicker('setStartDate').val(hoje.toLocaleDateString());
        form.find('[name="participantes"]').attr('checked', false);

        // pré-selecionar defensoria se houver apenas uma
        if($scope.defensorias.length==1)
        {
            form.find('[name="setor_criacao"]').val($scope.defensorias[0].id).change();
        }

        // pré-selecionar participante se houver apenas um
        if($scope.defensores.length==1)
        {
            form.find('[name="participantes"]').val($scope.defensores[0].usuario_id);
        }

        // pré-selecionar participantes se houver mais de um
        for(var i = 0; i < $scope.defensores.length; i++)
        {
            form.find('#atividade-participantes-' + $scope.defensores[i].usuario_id).attr('checked', $scope.defensores[i].selecionar);
        }

        $scope.limpar();
        aplicar_select2(modal_id);

    }

    $scope.atividade_modal_editar = function(atividade)
    {

        $scope.limpar();

        if(atividade.tipo.eh_brinquedoteca)
        {

            $http.get('/api/v1/atividades-extraordinarias/'+atividade.id+'.json').success(function(data)
            {

                $scope.atividade = data;
                $scope.atividade.participantes = $scope.atividade.participantes[0];
                $scope.complemento = data.complemento;
                $scope.data_referencia = new Date(data.data_referencia);
                $scope.hora_referencia = $scope.data_referencia.toLocaleTimeString().substring(0, 5);
                if(data.encerrado_em)
                {
                    $scope.data_encerrado = new Date(data.encerrado_em);
                    $scope.hora_encerrado = $scope.data_encerrado.toLocaleTimeString().substring(0, 5);
                }

                $('#modal-atividade-brinquedoteca').modal('show');
                aplicar_select2('modal-atividade-brinquedoteca');

            });
        }
        else
        {

            var modal = $('#modal-atividade');
            var form = modal.find('form');

            form[0].reset();
            form.find('[name="id"]').val(atividade.id);
            form.find('[name="numero"]').val(atividade.numero);
            form.find('[name="titulo"]').val(atividade.titulo);
            form.find('[name="data_referencia"]').val(atividade.data_referencia_pt_br).datepicker('setStartDate').val(atividade.data_referencia_pt_br);
            form.find('[name="tipo"]').val(atividade.tipo.id);
            if(atividade.area !== null){
                form.find('[name="area"]').val(atividade.area.id);
            }
            form.find('[name="setor_criacao"]').val(atividade.setor_criacao.id).change();
            form.find('[name="historico"]').val(atividade.historico);

            // força limpeza dos checkboxes
            form.find('[name="participantes"]').attr('checked', false);

            for(var i = 0; i < atividade.participantes.length; i++)
            {
                // seleção de participante (em um select)
                form.find('#atividade-participantes').val(atividade.participantes[i].id);
                // seleção de participante (em um checkbox)
                form.find('#atividade-participantes-' + atividade.participantes[i].id).attr('checked', true);
            }

            modal.modal('show');
            aplicar_select2('modal-atividade');

        }

    }

    $scope.enviar_documentos_url = function(atividade, next)
    {
        var url = Urls['atividade_extraordinaria:editar'](atividade.id);
        return url + '?next=' + next;
    }

    $scope.callback_atividade_salvar = function(data)
    {
        if(document.getElementById('atividade-inserir-documentos').checked)
        {
            window.location.href = `/atividade-extraordinaria/${data.id}/editar/`;
        }
        else
        {
            $('#modal-atividade').modal('hide');
            $('#modal-atividade-brinquedoteca').modal('hide');
            $scope.carregar_atividades_extraordinarias();
        }
    }

    $scope.callback_atividade_confirmed_delete = function(id)
    {
        $http.post('/atividade-extraordinaria/excluir/', {atividade_id: id}).success(function(json)
        {
            $scope.carregar_atividades_extraordinarias();
        });
    }

    $scope.salvar = function()
    {

        // transforma valores para formatos válidos
        $scope.atividade.data_referencia = Date.combineToLocaleString($scope.data_referencia, $scope.hora_referencia);
        $scope.atividade.encerrado_em = Date.combineToLocaleString($scope.data_encerrado, $scope.hora_encerrado);
        $scope.atividade.complemento = JSON.stringify($scope.complemento);
        $scope.atividade.titulo = $scope.complemento.nome_crianca;

        $http.post('/atividade-extraordinaria/salvar/',
        getFormData($scope.atividade),
        {
            transformRequest: angular.identity,
            headers: {'Content-Type': undefined}
        }
        ).success(function(data)
        {
            if(data.success)
                $scope.callback_atividade_salvar(data);
            else
                show_stack_error('Erro ao salvar atividade!');
        });
    }

    $scope.encerrar = function(atividade)
    {
        $http.post('/atividade-extraordinaria/'+atividade.id+'/encerrar/').success(function(json)
        {
            $scope.carregar_atividades_extraordinarias();
        });
    }

    $scope.init = function(params)
    {

        if(params==undefined)
        {
            params = {};
        }

        $scope.params = params;
        $scope.params.data = new Date();
        $scope.carregar_atividades_extraordinarias();
    }

}
