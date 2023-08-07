function Chronus() {}

Chronus.base_url = "";
Chronus.base_scope = null;

Chronus.generate = function($scope, user, name, resource, params, format, filename) {

    Chronus.base_scope = $scope;
    Chronus.pending();

    var params = angular.copy(params);

    // remove parâmtros com valores inválidos
    for(var param in params)
    {
        if(params[param]==null || params[param]=='')
            delete params[param];
    }

    // assume valores padrão dos parâmetros se não forem informados:
    for(var key in params.defaults)
    {
        if(!(key in params))
        {
            params[key] = params.defaults[key];
        }
    }

    delete params['defaults'];

    // altera nome padrão do parâmetro para nome usado no relatório
    for(var key in params.aliases)
    {
        params[params.aliases[key]] = params[key];
        delete params[key];
    }

    delete params['aliases'];

    if(format==undefined)
    {
        format = 'pdf';
    }

    var ignorePaginationXLSX = false;

    if(format=='xlsx_unpaginated')
    {
        format = 'xlsx';
        ignorePaginationXLSX = true;
    }

    $.ajax({
        url: Chronus.base_url + 'reports.json',
        data: {
            'report': {
                "app": 'solar',
                "user": user,
                "name": name,
                "resource": resource,
                "format": format,
                "filename": filename,
                "ignorePagination": ignorePaginationXLSX,
                "params": JSON.stringify(params)
            }
        },
        type: 'POST',
        crossDomain: true,
        dataType: 'json',
        success: function (data) {
            Chronus.getReport(data)
        },
        error: function (xhr) {
            Chronus.fail('Erro ao conectar com servidor')
        }
    });

}

Chronus.getReport = function(data) {

    var id = data['id'];
    var report_uri = Chronus.base_url + "reports/" + id + ".json";

    var listenReport = function () {

        $.getJSON(report_uri, {})
            .done(function (rData) {
                switch (rData['status']) {
                    case 'done':
                        Chronus.success(rData['file']);
                        clearInterval(intervalReport);
                        break;
                    case 'pending':
                        Chronus.pending();
                        break;
                    case 'failed':
                        Chronus.fail(rData['reason']);
                        clearInterval(intervalReport);
                        break;
                    default:
                        Chronus.base_scope.relatorio.status = null;
                        clearInterval(intervalReport);
                }
            });
    };

    intervalReport = setInterval(listenReport, 1000);

}

Chronus.pending = function()
{
    Chronus.base_scope.relatorio.status = {pending: true};
    // Chronus.base_scope.$apply();
}

Chronus.success = function(report) {
    Chronus.base_scope.relatorio.status = {success: true, report: report};
    Chronus.base_scope.$apply();
};

Chronus.fail = function(reason) {
    Chronus.base_scope.relatorio.status = {fail: true, reason: reason};
    Chronus.base_scope.$apply();
}
