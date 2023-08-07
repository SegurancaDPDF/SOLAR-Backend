function PerfilAdminCtrl($scope, $http, PeriodicTaskAPI, SettingServiceAPI)
{

    $scope.week_days = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
    $scope.hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23];
    $scope.intervals = [
        {
            'value': '*',
            'name': 'à cada 1 minuto'
        },
        {
            'value': '*/5',
            'name': 'à cada 5 minutos'
        },
        {
            'value': '*/10',
            'name': 'à cada 10 minutos'
        },
        {
            'value': '*/30',
            'name': 'à cada 30 minutos'
        },
        {
            'value': '0',
            'name': 'à cada hora'
        },
    ];
    $scope.services = [];

    $scope.set_service = function(service) {
        $scope.service = service;
    }

	$scope.init = function(services)
	{

        // Obtém estrutura geral dos serviços e tarefas
        $scope.services = services;

        // Obtém configurações
        SettingServiceAPI.get({}, function(data){
            $scope.aplicar_configuracoes(data);
        });

        $scope.set_service($scope.services[0]);

        // Obtém tasks
        PeriodicTaskAPI.get({}, function(data){
            $scope.aplicar_tasks(data.results);
        });

    }

    $scope.aplicar_configuracoes = function(data)
    {

        var params = {};
        for(var i = 0; i < data.results.length; i++)
        {
            params[data.results[i].key] = data.results[i];
        }

        for(var i = 0; i < $scope.services.length; i++)
        {

            // Aplica valores recebidos do constance
            for(var j = 0; j < $scope.services[i].arguments.length; j++)
            {
                var param = params[$scope.services[i].arguments[j].name];
                var value = param && param.value || $scope.services[i].arguments[j].value;
                $scope.services[i].arguments[j].value = value;
                $scope.services[i].arguments[j].help_text = param && param.help_text || '';
                $scope.services[i].arguments[j].constance = param != undefined;

                // Verifica se serviço está ativo a partir da configuração principal
                if($scope.services[i].active_argument === $scope.services[i].arguments[j].name)
                {
                    $scope.services[i].active = value;
                }

            }

        }
    }

    $scope.aplicar_tasks = function(tasks)
    {

        // Ajusta formato dos valores
        for(var k = 0; k < tasks.length; k++)
        {
            tasks[k].kwargs = JSON.parse(tasks[k].kwargs);
            tasks[k].crontab.hours = $scope.get_full_crontab(tasks[k].crontab.hours);
            tasks[k].crontab.days_of_week = $scope.get_full_crontab(tasks[k].crontab.days_of_week);
        }

        // Verifica e aplica valores nas tasks
        for(var i = 0; i < $scope.services.length; i++)
        {
            for(var j = 0; j < $scope.services[i].tasks.length; j++)
            {
                // Aplica valor inicial do crontab
                $scope.services[i].tasks[j].crontab = {
                    minute: '',
                    hours: [],
                    days_of_week: []
                }
                for(var k = 0; k < tasks.length; k++)
                {
                    if(tasks[k].task == $scope.services[i].tasks[j].task)
                    {
                        $scope.services[i].tasks[j].periodic_tasks.push(tasks[k]);
                        // Aplica valor do crontab
                        $scope.services[i].tasks[j].id = tasks[k].id;
                        $scope.services[i].tasks[j].enabled = tasks[k].enabled;
                        $scope.services[i].tasks[j].crontab = {
                            minute: tasks[k].crontab.minute,
                            hours: tasks[k].crontab.hours,
                            days_of_week: tasks[k].crontab.days_of_week
                        }
                        // Aplica valor dos argumentos
                        for(var l = 0; l < $scope.services[i].tasks[j].arguments.length; l++)
                        {
                            var arg = $scope.services[i].tasks[j].arguments[l];
                            arg.value = tasks[k].kwargs[arg.name];
                        }
                    }
                }
            }
        }
    }

    // Cria array com todos os valores do crontab
    $scope.get_full_crontab = function(values)
    {
        var array = [];
        for(var i = 0; i < values.length; i++)
        {
            array[values[i]] = true;
        }
        return array;
    }

    $scope.recuperar = function()
    {
        // Obtém configurações
        SettingServiceAPI.recuperar({}, function(data){
            $scope.aplicar_configuracoes(data);
            show_stack_success('Configurações recuperadas do disco com sucesso!');
        }, function(response){
            show_stack_error('Não foi possível recuperar as configurações do disco!');
        });
    }

    $scope.salvar = function()
    {
        var params = {};

        for(var i = 0; i < $scope.services.length; i++)
        {
            for(var j = 0; j < $scope.services[i].arguments.length; j++)
            {
                params[$scope.services[i].arguments[j].name] = $scope.services[i].arguments[j].value;
            }
        }

        SettingServiceAPI.save(params, function(data){
            show_stack_success('Salvo com sucesso!');
        });
    }

    $scope.salvar_periodic_task = function(task) {
        // Adiciona posição das horas selecionadas ao novo array
        var hours = [];
        for(var i=0; i < task.crontab.hours.length; i++)
        {
            if(task.crontab.hours[i]){
                hours.push(i);
            }
        }
        // Adiciona posição dos dias da semana selecionados ao novo array
        var days_of_week = [];
        for(var i=0; i < task.crontab.days_of_week.length; i++)
        {
            if(task.crontab.days_of_week[i]){
                days_of_week.push(i);
            }
        }

        // Adiciona argumentos ao novo objeto
        var kwargs = {};
        for(var i=0; i<task.arguments.length; i++)
        {
            kwargs[task.arguments[i].name] = task.arguments[i].value;
        }
        var params = {
            'id': task.id,
            'crontab': {
                'minute': task.crontab.minute,
                'hour': hours.join(','),
                'day_of_week': days_of_week.join(','),
                'day_of_month': '*',
                'month_of_year': '*',
            },
            'name': task.name,
            'task': task.task,
            'kwargs': JSON.stringify(kwargs),
            'queue': 'prioridade',
            'enabled': task.enabled
        };

        if(task.id)
        {
            PeriodicTaskAPI.update(params, function(data){
                task.id = data.id;
                show_stack_success('Salvo com sucesso!');
            });
        }
        else
        {
            PeriodicTaskAPI.save(params, function(data){
                task.id = data.id;
                show_stack_success('Salvo com sucesso!');
            });
        }
    }

}
