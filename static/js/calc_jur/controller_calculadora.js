$(document).ready(function () {

    $('#percentual_juros').mask('#0,00%', {reverse: true});
    $('#percentual-juros-periodo').mask('#0,00%', {reverse: true});
    adicionarDatasVencimento();

    var date = new Date();
    var anoMes = "";
    if (date.getMonth() < 9) {
        $("#mes-fim").attr("value", date.getFullYear() + "-0" + (date.getMonth() + 1));
    } else {
        $("#mes-fim").attr("value", date.getFullYear() + "-" + (date.getMonth() + 1));
    }

    $('[id^="btn-add-data-vencimento-"]').click(function () {
        //alert("btn add clicado");
        add_vencimento();
        //excluir_vencimento($(this).parent().parent().attr('id'));
    });

    $(".btn_vencimento_excluir").click(function () {
        //alert("btn add clicado");
        del_vencimento();
        //excluir_vencimento($(this).parent().parent().attr('id'));
    });

    $("#btn-calcular-periodo").on('click', function () {
        calcularParcelasPorPeriodo();
    });

    $("#btn_calcular").on('click', function () {
        calcularParcelasPorDatas();
    });

    $('#btn_calcular_penal').click(function() {
        if(validarInputsPenal()){
            calcularPenal();
        }
    });

    $("#btn_gerar_excel").click(function (e) {
        exportarExcel("calculo-pensao-datas", "tabela_parcelas", false);
    });

    $("#btn_gerar_excel_penal").on('click', function () {
        exportarExcel("calculo-penal", "tabela_parcelas_penal", true);
    });

    $("#btn-gerar-excel-periodo").on('click', function () {
        exportarExcel("calculo-pensao-periodo", "tabela_parcelas_periodo", false);
    });

    $(".input_calculo").change(function () {
        if (document.getElementById('btn-tab-datas-vencimento').value == 1) {
            if (document.getElementById("tabela_parcelas").rows[0]) {
                iniciarTabela('tab-datas-vencimento');
            }
        } else if (document.getElementById('btn-tab-periodo').value == 1) {
            if (document.getElementById("tabela-parcelas-periodo").rows[0]) {
                iniciarTabela('tab-periodo');
            }
        }
    });

    $('#select_valor_base').change(function () {
        if ($(this).val() == 'outro_valor' || $(this).val() == 'valor_fixo') {
            document.getElementById('outro_valor_base').disabled = false;
        } else {
            document.getElementById('outro_valor_base').disabled = true;
        }
        if ($(this).val() == 'valor_fixo') {
            document.getElementById('percentual').disabled = true;
        } else {
            document.getElementById('percentual').disabled = false;
        }
    });

    $('#select-valor-base-periodo').change(function () {
        if ($(this).val() == 'outro_valor' || $(this).val() == 'valor_fixo') {
            document.getElementById('outro-valor-base-periodo').disabled = false;
        } else {
            document.getElementById('outro-valor-base-periodo').disabled = true;
        }
        if ($(this).val() == 'valor_fixo') {
            document.getElementById('percentual-periodo').disabled = true;
        } else {
            document.getElementById('percentual-periodo').disabled = false;
        }
    });

});


function adicionarDatasVencimento() {
    var x = document.getElementById("dia-vencimento");

    for (i = 1; i <= 30; i++) {
        var option = document.createElement("option");
        option.text = i.toString();
        x.add(option);
    }
}

function exportarExcel(filename,table_alvo, isPenal){
    var a = document.createElement('a');
    var data_type = 'data:application/vnd.ms-excel';
    var table_div = document.getElementById(table_alvo);

    var tab_text="<table border='2px'>";

    input_ends = table_div.rows.length-1;
    for(j = 0 ; j < table_div.rows.length ; j++)
    {
        for(k = 0 ; k < table_div.rows[j].cells.length ; k++) {


            if(k == 2 && j > 0 && j < input_ends && !isPenal){
                tab_text=tab_text+'<td>R$ '+table_div.rows[j].cells[k].firstChild.value+"</td>";
            } else {
                tab_text=tab_text+'<td>'+table_div.rows[j].cells[k].innerHTML+"</td>";
            }
        }
        tab_text=tab_text+"</tr>";
    }

    tab_text=tab_text+"</table>";

    tab_text= tab_text.replace(/<A[^>]*>|<\/A>/g, "");//remove if u want links in your table

    a.href = data_type + ', ' + encodeURIComponent(tab_text);

    a.download = filename + '-' + printDateTime() + '.xlsx';
    a.click();
}

function getIndices(codigoMes) {
    let indices = [];
    for (i = 0; i < codigoMes.length; i++) {
        url = "https://servicodados.ibge.gov.br/api/v3/agregados/1736/periodos/" + codigoMes[i] + "/variaveis/44?localidades=N1[1]";

        $.getJSON(url)
            .done(function (json) {
                var indice = {};
                var obj = jQuery.parseJSON(JSON.stringify(json));
                var serie = {};

                if (obj.length > 0) {
                    serie = obj[0].resultados[0].series[0].serie;
                    indice.valor = parseFloat(serie[Object.keys(serie)[0]]);
                    indice.codigo = Object.keys(serie)[0];
                } else {
                    indice.valor = 0;
                    indice.codigo = 'null';
                }

                indices.push(indice);
            })

            .fail(function (jqxhr, textStatus, error) {
                var err = textStatus + ", " + error;
                console.log("Request Failed: " + err);
            });
    }
    return indices;
}

function validarInputsPenal(){
    var pena_anos = document.getElementById('input_duracao_anos').value;
    var pena_meses = document.getElementById('input_duracao_meses').value;
    var pena_dias = document.getElementById('input_duracao_dias').value;
    var inicio_pena = document.getElementById('input_inicio_pena').value;
    if (pena_anos+pena_meses+pena_dias == 0 || inicio_pena == ''){
        alert('Favor inserir a pena e a data de início da condenação');
        return false;
    } else {
        return true;
    }

}

function calcularParcelasPorPeriodo() {
    if (validarCampos()) {
        document.getElementById('btn-calculando-periodo').style.display = 'initial';
        document.getElementById('btn-calcular-periodo').style.display = 'none';

        var mesInicio = document.getElementById('mes-inicio').value;
        var mesFim = document.getElementById('mes-fim').value;
        var diaVencimento = document.getElementById('dia-vencimento').value;

        if (parseInt(diaVencimento) <= 9) {
            diaVencimento = '0' + diaVencimento;
        }

        var dataAuxFev;
        var diaVencimentoAuxFev;
        var dataInicio;
        var dataFim;

        if ((mesInicio.substring(5)) == '02' && (diaVencimento == 29 || diaVencimento == 30)) {
            dataAuxFev = moment(mesInicio + "-01", 'YYYY-MM-DD');
            diaVencimentoAuxFev = dataAuxFev.endOf('month').format("DD");
            dataInicio = moment(mesInicio + "-" + diaVencimentoAuxFev, 'YYYY-MM-DD');
        } else {
            dataInicio = moment(mesInicio + "-" + diaVencimento, 'YYYY-MM-DD');
        }

        // var dataInicio = moment(mesInicio + "-" + diaVencimento, 'YYYY-MM-DD');
        if ((mesFim.substring(5)) == '02' && (diaVencimento == 29 || diaVencimento == 30)) {
            dataAuxFev = moment(mesFim + "-01", 'YYYY-MM-DD');
            diaVencimentoAuxFev = dataAuxFev.endOf('month').format("DD");
            dataFim = moment(mesFim + "-" + diaVencimentoAuxFev, 'YYYY-MM-DD');
        } else {
            dataFim = moment(mesFim + "-" + diaVencimento, 'YYYY-MM-DD');
        }

        var dataFimParaCorrecao = moment(new Date(), 'YYYY-MM-DD');

        var datasVencimento = [];
        var codigoMes = [];
        var indices = [];

        while (dataFimParaCorrecao > dataInicio || dataInicio.format('M') === dataFimParaCorrecao.format('M')) {
            codigoMes.push(dataInicio.format('YYYYMM'));
            dataInicio.add(1, 'month');
        }

        //restaurando data inicio
        var dataInicio;
        if (mesInicio.substring(5) == '02' && (diaVencimento == 29 || diaVencimento == 30)) {
            var diaVencimentoAux = moment(mesInicio + "-01", 'YYYY-MM-DD').endOf('month').format("DD");
            dataInicio = moment(mesInicio + "-" + diaVencimentoAux, 'YYYY-MM-DD');
        } else {
            dataInicio = moment(mesInicio + "-" + diaVencimento, 'YYYY-MM-DD');
        }

        while (dataFim > dataInicio || dataInicio.format('M') === dataFim.format('M')) {
            if (dataInicio.month() == 1 && (diaVencimento == 29 || diaVencimento == 30)) {
                diaVencimentoAux = dataInicio.endOf('month').format("DD");
                datasVencimento.push(dataInicio.format(diaVencimentoAux + '/MM/YYYY'));
            } else {
                datasVencimento.push(dataInicio.format(diaVencimento + '/MM/YYYY'));
            }
            dataInicio.add(1, 'month');
        }

        // indices = getIndices(codigoMes);
        indices = [];

        for (serie of codigoMes) {
            $.ajax({
                url: '/calcjur/inpc/' + serie, success: function (result) {
                    indices.push({"codigo": Object.keys(result)[0], "valor": parseFloat(Object.values(result)[0])});
                }
            });
        }


        var intervaloTempo = codigoMes.length * 500;

        var x = setTimeout(mostrarCalcular, intervaloTempo);

        function mostrarCalcular() {
            document.getElementById('btn-calculando-periodo').style.display = 'none';
            document.getElementById("btn-calcular-periodo").style.display = 'initial';
        }

        setTimeout(function () {
            popularParcelas(indices, datasVencimento, codigoMes, [], 'tab-periodo', []);
        }, intervaloTempo);
    }
}


function calcularParcelasPorDatas() {
    if (validarCampos()) {
        document.getElementById('btn_calcular').style.display = 'none';
        document.getElementById("btn-calculando-datas").style.display = "initial";

        var indices = [];
        var arrayDataVencimento = [...document.getElementsByClassName("data_vencimento")];
        var codigoMes = [];
        var mes = '';
        var datasVencimento = [];
        var data = "";
        var i;

        datasVencimento = arrayDataVencimento.map((x) => {
            return x.value;
        });

        datasVencimento = datasVencimento.sort();

        var dataInicio = moment(datasVencimento[0], 'YYYY-MM-DD');
        var dataFim = moment(new Date(), 'YYYY-MM-DD');
        var codigoMes = [];
        var mesNaoRetornado = [];

        while (dataFim > dataInicio || dataInicio.format('M') === dataFim.format('M')) {
            codigoMes.push(dataInicio.format('YYYYMM'));
            dataInicio.add(1, 'month');
        }

        mesNaoRetornado = codigoMes.map((x) => {
            return x;
        });

        for (i = 0; i < codigoMes.length; i++) {
            url = "https://servicodados.ibge.gov.br/api/v3/agregados/1736/periodos/" + codigoMes[i] + "/variaveis/44?localidades=N1[1]";

            $.getJSON(url)
                .done(function (json) {
                    var indice = {};
                    var obj = jQuery.parseJSON(JSON.stringify(json));
                    var serie = {};

                    if (obj.length > 0) {
                        serie = obj[0].resultados[0].series[0].serie;
                        indice.valor = parseFloat(serie[Object.keys(serie)[0]]);
                        indice.codigo = Object.keys(serie)[0];
                        mesNaoRetornado.splice(mesNaoRetornado.indexOf(indice.codigo.toString()), 1);
                    } else {
                        indice.valor = 0;
                        indice.codigo = 'null';
                    }

                    indices.push(indice);
                })
                .fail(function (jqxhr, textStatus, error) {
                    var err = textStatus + ", " + error;
                    console.log("Request Failed: " + err);
                });
        }

        var intervaloTempo = codigoMes.length * 500;

        var x = setTimeout(mostrarCalcular, intervaloTempo);

        function mostrarCalcular() {
            document.getElementById('btn-calculando-datas').style.display = 'none';
            document.getElementById("btn_calcular").style.display = 'initial';
        }

        setTimeout(function () {
            popularParcelas(indices, datasVencimento, codigoMes, [], 'tab-datas-vencimento', []);
        }, intervaloTempo);
    }
}


function popularParcelas(indices, datasVencimento, codigo_mes, valores_pagos, tab, listaFatorCM) {
    $.ajax({
        url: '/calcjur/salarios', success: function (result) {
            var slr_minimo = {};
            slr_minimo = result;
            var tipoCalculo;
            var percentual;
            var percentualJuros;
            var outroValorBase;
            var parcelas = [];


            if (tab === 'tab-datas-vencimento') {
                tipoCalculo = document.getElementById('select_valor_base').value;
                percentual = (parseFloat(document.getElementById('percentual').value.replace(",", "."))) / 100;
                percentualJuros = (parseFloat(document.getElementById('percentual_juros').value.replace(",", "."))) / 100;
                outroValorBase = parseFloat(document.getElementById('outro_valor_base').value.replace(".", "").replace(",", "."));
            } else if (tab === 'tab-periodo') {
                tipoCalculo = document.getElementById('select-valor-base-periodo').value;
                percentual = (parseFloat(document.getElementById('percentual-periodo').value.replace(",", "."))) / 100;
                percentualJuros = (parseFloat(document.getElementById('percentual-juros-periodo').value.replace(",", "."))) / 100;
                outroValorBase = parseFloat(document.getElementById('outro-valor-base-periodo').value.replace(".", "").replace(",", "."));
            }

            for (i = 0; i < datasVencimento.length; i++) {
                var pensao = 0;

                switch (tipoCalculo) {
                    case 'salario_minimo':
                        if (tab === 'tab-datas-vencimento') {
//            pensao = percentual*slr_minimo[datasVencimento[i].split('-')[0]];
                            pensao = round(percentual * slr_minimo[datasVencimento[i].split('-')[0]], 2);
                        } else if (tab === 'tab-periodo') {
//            pensao = percentual*slr_minimo[datasVencimento[i].split('/')[2]];
                            pensao = round(percentual * slr_minimo[datasVencimento[i].split('/')[2]], 2);
                        }

                        break;
                    case 'outro_valor':
//        pensao = percentual*parseFloat(outroValorBase);
                        pensao = round(percentual * parseFloat(outroValorBase), 2);
                        break;
                    case 'valor_fixo':
//        pensao = parseFloat(outroValorBase);
                        pensao = round(parseFloat(outroValorBase), 2);
                }

                var pago = 0;
                var debito = pensao;

                if (valores_pagos.length > 0) {
                    pago = valores_pagos[i];
                    debito = pensao - pago;
                }

                //Calculo auxiliar para o percentual de juros
                var data = datasVencimento[i].split("-").reverse().join("/");
                var dataInicio = moment(data, 'DD/MM/YYYY');
                var dataFim = moment(new Date(), 'YYYY-MM-DD');

                var month1Teste = dataInicio.month();
                var month2Teste = dataFim.month();

                if (month1Teste === 0) {
                    month1Teste++;
                    month2Teste++;
                }

                var numberOfMonths = (dataFim.year() - dataInicio.year()) * 12 + (month2Teste - month1Teste) + 1;

                if (listaFatorCM.length > 0) {
                    var corrigido = round(debito * parseFloat(listaFatorCM[i]), 2);
                    var fatorCM = parseFloat(listaFatorCM[i]) - 1;
                } else {
                    // Calculo do fator correcao monetaria
                    var codigoMes = [];

                    while (dataFim > dataInicio || dataInicio.format('M') === dataFim.format('M')) {
                        codigoMes.push(dataInicio.format('YYYYMM'));
                        dataInicio.add(1, 'month');
                    }

                    var fatorCM = 1;

                    for (j = 0; j < codigoMes.length; j++) {
                        var index = indices.findIndex(x => x.codigo == codigoMes[j]);
                        var inpc = 0;

                        if (index != -1) {
                            inpc = indices[index].valor;
                        }

                        fatorCM = fatorCM * (1 + inpc / 100);
                    }


                    //correcao nao pode ser negativa

                    if (fatorCM > 1) {

                        fatorCM = fatorCM - 1;

                    } else {

                        fatorCM = 0;

                    }

                    var corrigido = round(debito + (debito * fatorCM), 2);
                }

                if (numberOfMonths === 0) {
                    var percentualJurosTotal = percentualJuros;
                } else {
                    var percentualJurosTotal = percentualJuros * numberOfMonths;
                }

                var juros = round(corrigido * percentualJurosTotal, 2);
                var total = round(corrigido + juros, 2);

                var p = {
                    mes_ano: data,
                    valor_pensao: pensao,
                    valor_pago: pago,
                    valor_debito: debito,
                    valor_corrigido: corrigido,
                    valor_inpc: fatorCM + 1,
                    valor_juros: juros,
                    valor_percentualJurosTotal: percentualJurosTotal * 100,
                    valor_total_bruto: total
                };

                parcelas.push(p);
            }

            iniciarTabela(tab);
            preencherTabela(parcelas, tab);

        }
    });
}

function calcularPenal(){
    var marcado = document.getElementById('dias_remidos_is_checked')

    document.getElementById('div-calculando-pena').style.display = 'initial';
    var mydata = {

      duracao_anos: $('#input_duracao_anos').val(),
      duracao_meses: $('#input_duracao_meses').val(),
      duracao_dias: $('#input_duracao_dias').val(),
      interrup_anos_remidos: $('#input_interrup_anos_remidos').val(),
      interrup_meses_remidos: $('#input_interrup_meses_remidos').val(),
      interrup_dias_remidos: $('#input_interrup_dias_remidos').val(),
      inicio_pena: $('#input_inicio_pena').val(),
      dias_remidos: $('#input_dias_remidos').val(),
      dias_remidos_is_checked: marcado.checked,
      fracao_numerador: $('#input_numerador').val(),
      fracao_denominador: $('#input_denominador').val(),
      detracao_anos: $('#input_detracao_anos').val(),
      detracao_meses: $('#input_detracao_meses').val(),
      detracao_dias: $('#input_detracao_dias').val(),
      span_percentual: $('#input_percentual').val(),
    }
    csrf = $('#tokencsrf').val(),
    fetch("/calcjur/calcjur_penal/", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf
      },
      body: JSON.stringify(mydata)
    })
    .then(response => {
      return response.json()
    })
    .then(data =>{
        $('#span_termino_pena').empty()
        $('#span_fracao_1_2').empty()
        $('#span_fracao_1_3').empty()
        $('#span_fracao_3_5').empty()
        $('#span_fracao_2_5').empty()
        $('#span_fracao_1_6').empty()
        $('#span_fracao_personalizada').empty()
        $('#span_percentual').empty()
        $('#percentual_valor').empty()
        $('#fracao_valor').empty()

        $('#span_termino_pena').append(' - Término da pena em ' + data.termino_pena)
        $('#span_fracao_1_2').append(data.fracao_1_2)
        $('#span_fracao_1_3').append(data.fracao_1_3)
        $('#span_fracao_3_5').append(data.fracao_3_5)
        $('#span_fracao_2_5').append(data.fracao_2_5)
        $('#span_fracao_1_6').append(data.fracao_1_6)
        $('#span_fracao_personalizada').append(data.fracao_personalizada)
        $('#span_percentual').append(data.span_percentual)
        $('#percentual_valor').append(document.getElementById("input_percentual").value+" %")
        $('#fracao_valor').append(document.getElementById("input_numerador").value + " / "+ document.getElementById("input_denominador").value)
    })
}

function sugerirPercentualOuFracao(){
    var data_fato = new Date(document.getElementById("input_data_fato").value);
    console.log('fato '+data_fato)
    var data_lei = new Date('2020-01-23'); // conforme fundamenta Lei n.º 13.964/2019.
    console.log('lei ' + data_lei)
    document.getElementById("span_sugestao_lei").innerText = ' ';
    if (data_fato < data_lei) {
        document.getElementById("span_sugestao_lei").innerText = 'Conforme fundamenta Lei n.º 13.964/2019, sugere-se utilizar FRAÇÕES';
    } else {
        document.getElementById("span_sugestao_lei").innerText = 'Conforme fundamenta Lei n.º 13.964/2019, sugere-se utilizar PORCENTAGENS';
    }
}

function fracionar(numerador, denominador) {

    var anos = document.getElementById("input_duracao_anos").value;
	var meses = document.getElementById("input_duracao_meses").value;
	var dias = document.getElementById("input_duracao_dias").value;
	//var numerador = document.getElementById("input_numerador").value;
	//var denominador = document.getElementById("input_denominador").value;

    var numeroAno01 = validarNumeroFracao(anos);
    var numeroMes01 = validarNumeroFracao(meses);
    var numeroDia01 = validarNumeroFracao(dias);
    var numeroDenominador = validarNumeroFracao(denominador);
    var numeroNumerador = validarNumeroFracao(numerador);

    var qtdDia01 = numeroAno01 * 360.0 + numeroMes01 * 30.0 + numeroDia01 * 1.0;
    var qtdAno = 0;
    var qtdMes = 0;
    var qtdDia = 0;

    if (numeroDenominador > 0 && numeroNumerador > 0)
    {
        var qtdDiaResultado = (qtdDia01 * numeroNumerador)/numeroDenominador;
        qtdAno = Math.floor(qtdDiaResultado / 360);
        var restoQtdAno = qtdDiaResultado % 360;

        qtdMes = Math.floor(restoQtdAno / 30);
        qtdDia = Math.floor(restoQtdAno % 30);
    }

    document.getElementById("input_duracao_anos").value = qtdAno;
    document.getElementById("input_duracao_meses").value = qtdMes;
    document.getElementById("input_duracao_dias").value = qtdDia;
}

function validarNumeroFracao(entradaCampo)
	{
		var listaNumeroValido = "0123456789";
		var valor= new String(entradaCampo);
		for( var i=0; i< valor.length; i++)
		{
			if( listaNumeroValido.indexOf(valor.charAt(i)) == -1)
			{
				return new Number(0);
			}
		}
		return new Number(entradaCampo);
	}

function validarInputPercentual(entradaCampo)
{
    var listaNumeroValido = "0123456789";
    var valor= new String(entradaCampo);
    for( var i=0; i< valor.length; i++)
    {
        if( listaNumeroValido.indexOf(valor.charAt(i)) == -1)
        {
            return new Number(0);
        }
    }
    return new Number(entradaCampo);
}

function fracionarPersonalizado(){
    dividendo = document.getElementById("input_numerador").value;
    divisor = document.getElementById("input_denominador").value;
    fracionar(dividendo, divisor);
}

function fracionarPercentual(){
    var anos = document.getElementById("input_duracao_anos").value;
	var meses = document.getElementById("input_duracao_meses").value;
	var dias = document.getElementById("input_duracao_dias").value;
    var porcentagem = document.getElementById("input_percentual").value;
    console.log(porcentagem)
    var numeroAno01 = validarNumeroFracao(anos);
    var numeroMes01 = validarNumeroFracao(meses);
    var numeroDia01 = validarNumeroFracao(dias);
    var numeroPorcentagem = validarInputPercentual(porcentagem);

    numeroPorcentagem = numeroPorcentagem * 0.01
    console.log(numeroPorcentagem)

    var qtdDia01 = numeroAno01 * 360.0 + numeroMes01 * 30.0 + numeroDia01 * 1.0;
    var qtdAno = 0;
    var qtdMes = 0;
    var qtdDia = 0;

    if (numeroPorcentagem > 0)
    {
        var qtdDiaResultado = qtdDia01 * numeroPorcentagem;
        qtdAno = Math.floor(qtdDiaResultado / 360);
        var restoQtdAno = qtdDiaResultado % 360;

        qtdMes = Math.floor(restoQtdAno / 30);
        qtdDia = Math.floor(restoQtdAno % 30);
    }

    document.getElementById("input_duracao_anos").value = qtdAno;
    document.getElementById("input_duracao_meses").value = qtdMes;
    document.getElementById("input_duracao_dias").value = qtdDia;
}

function preencherTabela(parcelas, tab) {
    var formato = {minimumFractionDigits: 2, style: 'currency', currency: 'BRL'};
    iniciarTabela(tab);
    var tabela;
    var stringValorPago = '';

    if (tab === 'tab-datas-vencimento') {
        tabela = document.getElementById("tabela_parcelas");
        tabela.style.width = '100%';
        stringValorPago = 'valorPagoDatas-';
    } else if (tab === 'tab-periodo') {
        tabela = document.getElementById("tabela_parcelas_periodo");
        tabela.style.width = '100%';
        stringValorPago = 'valorPagoPeriodo-';
    }

    var row = tabela.insertRow(-1);
    row.insertCell(0).innerHTML = '<b> Data da Parcela </b>';
    row.insertCell(1).innerHTML = '<b> Valor Devido </b>';
    row.insertCell(2).innerHTML = '<b> R$ Pago </b>';
    row.insertCell(3).innerHTML = '<b> Valor Débito </b>';
    row.insertCell(4).innerHTML = '<b> Valor Corrigido (Índice de correção) </b>';
    row.insertCell(5).innerHTML = '<b> Juros </b>';
    row.insertCell(6).innerHTML = '<b> Total da Parcela </b>';

    var total_debito = 0;
    var total_corrigido = 0;
    var total_juros = 0;
    var total_bruto = 0;

    for (i = 0; i < parcelas.length; i++) {
        var row = tabela.insertRow(-1);
        row.insertCell(0).innerHTML = parcelas[i].mes_ano;
        row.insertCell(1).innerHTML = parcelas[i].valor_pensao.toLocaleString('pt-br', formato);

        var valor_pago = document.createElement("INPUT");
        valor_pago.setAttribute("type", "text");
        valor_pago.setAttribute("id", stringValorPago + i.toString());
        valor_pago.setAttribute("placeholder", '0,00');
        valor_pago.setAttribute("class", "input_valor_pago")

        //    Atualizar os valores da tabela quando um valor pago for digitado
        valor_pago.onchange = function () {
            atualizarTabela();
        };

        if (parcelas[i].valor_pago > 0) {
            valor_pago.setAttribute("value", parcelas[i].valor_pago.toLocaleString('pt-br', formato).substring(3));
        }

        row.insertCell(2).appendChild(valor_pago);
        $('.input_valor_pago').maskMoney({
            prefix: 'R$ ',
            allowNegative: true,
            thousands: '.',
            decimal: ',',
            affixesStay: false
        });

        row.insertCell(3).innerHTML = parcelas[i].valor_debito.toLocaleString('pt-br', formato);
        row.insertCell(4).innerHTML = parcelas[i].valor_corrigido.toLocaleString('pt-br', formato) + ' (' + parcelas[i].valor_inpc.toFixed(7) + ')';
        row.insertCell(5).innerHTML = parcelas[i].valor_juros.toLocaleString('pt-br', formato) + ' (' + parcelas[i].valor_percentualJurosTotal.toLocaleString(formato) + '%)';
        row.insertCell(6).innerHTML = parcelas[i].valor_total_bruto.toLocaleString('pt-br', formato);

        total_debito = total_debito + parcelas[i].valor_debito;
        total_corrigido = total_corrigido + parcelas[i].valor_corrigido;
        total_juros = total_juros + parcelas[i].valor_juros;
        total_bruto = total_bruto + parcelas[i].valor_total_bruto;
    }

    var row_total = tabela.insertRow(-1);
    row_total.insertCell(0).innerHTML = '<b> Total </b>';
    row_total.insertCell(1);
    row_total.insertCell(2);
    row_total.insertCell(3).innerHTML = '<b>' + total_debito.toLocaleString('pt-br', formato) + '</b>';
    row_total.insertCell(4).innerHTML = '<b>' + total_corrigido.toLocaleString('pt-br', formato) + '</b>';
    row_total.insertCell(5).innerHTML = '<b>' + total_juros.toLocaleString('pt-br', formato) + '</b>';
    row_total.insertCell(6).innerHTML = '<b>' + total_bruto.toLocaleString('pt-br', formato) + '</b>';

    if (document.getElementById('btn-tab-datas-vencimento').value == 1) {
        document.getElementById('btn_gerar_excel').style.display = 'inline-block';
    } else if (document.getElementById('btn-tab-periodo').value == 1) {
        document.getElementById('btn-gerar-excel-periodo-rodape').style.display = 'inline-block';
        document.getElementById('btn-gerar-excel-periodo-cabecalho').style.display = 'inline-block';
    }
}


function atualizarTabela() {
    var tabName = "";
    var count_parcelas = 0;
    var tabela;
    var stringValorPago = '';
    var fatorCM = [];

    if (document.getElementById('btn-tab-datas-vencimento').value == 1) {
        tabName = 'tab-datas-vencimento';
    } else if (document.getElementById('btn-tab-periodo').value == 1) {
        tabName = 'tab-periodo';
    }

    if (tabName === 'tab-datas-vencimento') {
        tabela = document.getElementById('tabela_parcelas');
        stringValorPago = 'valorPagoDatas-';
    } else if (tabName === 'tab-periodo') {
        tabela = document.getElementById('tabela_parcelas_periodo');
        stringValorPago = 'valorPagoPeriodo-';
    }

    count_parcelas = tabela.rows.length - 2;
    var parcelas = [];
    var valores_pagos = [];
    var indices = [];
    var datasVencimento = [];
    var codigo_mes = [];

    for (i = 0; i < count_parcelas; i++) {
        var data = tabela.rows[i + 1].cells[0].innerText;

        if (data.length > 10) {
            data = data.substring(0, data.length - 1);
        }

        str_valor_pago = document.getElementById(stringValorPago + i.toString()).value;
        if (str_valor_pago == null) {
            str_valor_pago = document.getElementById(stringValorPago + i.toString()).innerHTML.substring(3);
        }

        var valor = parseFloat(str_valor_pago.replace(".", "").replace(",", "."));

        if (!isNaN(valor)) {
            valores_pagos.push(valor);
        } else {
            valores_pagos.push(0);
        }

        var regExp = /\(([^)]+)\)/;
        var matches = regExp.exec(tabela.rows[i + 1].cells[4].innerText);

        fatorCM.push(matches[1]);

        // inpc.valor = document.getElementById('tabela_parcelas').rows[i+1].cells[4].innerText;
//        inpc.valor = parseFloat(indice_inpc.replace(',','.'));
//        inpc.codigo = codigo;

//        indices.push(inpc);
//        console.log(inpc);

        if (tabName === 'tab-datas-vencimento') {
            datasVencimento.push(data.substring(6, 10) + '-' + data.substring(3, 5) + '-' + data.substring(0, 2));
        } else if (tabName === 'tab-periodo') {
            datasVencimento.push(data);
        }
//        codigo_mes.push(codigo);
    }
    popularParcelas(indices, datasVencimento, [], valores_pagos, tabName, fatorCM);
}


function iniciarTabela(tab) {
    if (tab === 'tab-datas-vencimento') {
        document.getElementById('tabela_parcelas').innerHTML = '';
        document.getElementById('resultado_parcelas').style.display = 'flex';
        document.getElementById('btn_gerar_excel').style.display = 'none';
    } else {
        document.getElementById('tabela_parcelas_periodo').innerHTML = '';
        document.getElementById('resultado_parcelas_periodo').style.display = 'flex';
        document.getElementById('btn_gerar_excel').style.display = 'none';
        //var tabela = document.getElementById("tabela_parcelas_periodo");
    }
}


function validarCampos() {
    var campos_validos = false;
    var datasValidas = true;
    var tipoCalculo;
    var outroValorBase = 0;
    var percentual = 0;

    if (document.getElementById('btn-tab-datas-vencimento').value == 1) {
        tabName = 'tab-datas-vencimento';
        tipoCalculo = document.getElementById('select_valor_base').value;
        outroValorBase = document.getElementById('outro_valor_base');
        percentual = document.getElementById('percentual');
        percentualJuros = document.getElementById('percentual_juros');
    } else if (document.getElementById('btn-tab-periodo').value == 1) {
        tabName = 'tab-periodo';
        document.getElementById('select-valor-base-periodo').value;
        outroValorBase = document.getElementById('outro-valor-base-periodo');
        percentual = document.getElementById('percentual-periodo');
        percentualJuros = document.getElementById('percentual-juros-periodo');
    }

    if (tabName === 'tab-periodo') {
        if (document.getElementById('mes-inicio').value === "" || document.getElementById('mes-fim').value === "") {
            datasValidas = false;
        } else if ((moment(document.getElementById('mes-inicio').value + "-01", 'YYYY-MM-DD')) >= (moment(document.getElementById('mes-fim').value + "-01", 'YYYY-MM-DD'))) {
            datasValidas = false;
        }
    } else if (tabName === 'tab-datas-vencimento') {
        var arrayDataVencimento = document.getElementsByClassName("data_vencimento");
        for (i = 0; i < arrayDataVencimento.length; i++) {
            data = arrayDataVencimento[i].value;
            if (data.length === 0) {
                datasValidas = false;
            }
        }
    }

    if (!datasValidas) {
        alert('Datas de Vencimento inválidas ou período de cobrança inválido.');
    } else if ((tipoCalculo == 'outro_valor' || tipoCalculo == "valor_fixo") &&
        ((parseFloat(outroValorBase.value.replace(",", ".").replace(".", "")) < 0) || isNaN(parseFloat(outroValorBase.value)))) {
        alert('Valor inváĺido.');

    } else if (((parseFloat(percentual.value.replace(",", "."))) / 100) <= 0 && tipoCalculo != 'valor_fixo') {
        alert('Percentual inváĺido.');

    } else if (isNaN(parseFloat(percentualJuros.value.replace(",", "."))) || parseFloat(percentualJuros.value.replace(",", ".")) < 0) {
        alert('Percentual de juros inválido');

    } else {
        campos_validos = true;

    }

    return campos_validos;
}

function add_vencimento() {
    const qtd_data_vencimento = document.getElementsByClassName("data_vencimento").length;

    var LastDataVencimento = "dataVencimento-" + (qtd_data_vencimento-1);
    var strDataVencimento = document.getElementById(LastDataVencimento).value;
    if (strDataVencimento.length !== 0) {
        validarData = true;
    } else {
        validarData = false;
        alert("Data de vencimento inválida.");
    }

    if(validarData){
        var proximaDataVencimento = moment(strDataVencimento, 'YYYY-MM-DD').add(1, 'month').format("YYYY-MM-DD");
        var data_vencimento = document.createElement("INPUT");
        data_vencimento.setAttribute("type", "date");
        data_vencimento.setAttribute("placeholder", 'dd/mm/aaaa');
        data_vencimento.setAttribute("value", proximaDataVencimento);
        data_vencimento.setAttribute("class", 'data_vencimento');
        var NextDataVencimento = "dataVencimento-" + (qtd_data_vencimento);
        data_vencimento.setAttribute("id", NextDataVencimento.toString());

        var div = $('#div-datas-vencimento');
        div.append(data_vencimento);
    }

};

function del_vencimento() {
    const qtd_data_vencimento = document.getElementsByClassName("data_vencimento").length;
    if(qtd_data_vencimento == 1) {
        alert("É preciso indicar ao menos uma data de vencimento para o cálculo");
    } else {
        var LastDataVencimento = "dataVencimento-" + (qtd_data_vencimento-1);
        var div = $('#div-datas-vencimento');
        document.getElementById(LastDataVencimento).remove();
    }
};

function excluir_vencimento(rowId) {
    var countVencimentos = document.getElementById('tabela_vencimento').rows.length;
    if (countVencimentos > 1) {
        var row = document.getElementById(rowId);
        row.parentNode.removeChild(row);
    }
    countVencimentos = document.getElementById('tabela_vencimento').rows.length;
    if (countVencimentos === 1) {
        var btnExcluir = document.getElementsByClassName("btn_vencimento_excluir");
        btnExcluir[0].disabled = true;
    }
}


//https://www.w3schools.com/howto/howto_js_tabs.asp
function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");

    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    tablinks = document.getElementsByClassName("tablinks");

    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace("active", "");
    }

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");

    if (tabName === 'tab-datas-vencimento') {
        document.getElementById('btn-tab-datas-vencimento').value = 1;
        document.getElementById('btn-tab-periodo').value = 0;
        document.getElementById('btn-tab-executoria').value = 0;
    } else if (tabName === 'tab-periodo') {
        document.getElementById('btn-tab-datas-vencimento').value = 0;
        document.getElementById('btn-tab-periodo').value = 1;
        document.getElementById('btn-tab-executoria').value = 0;
    } else if (tabName === 'tab-executoria') {
        document.getElementById('btn-tab-datas-vencimento').value = 0;
        document.getElementById('btn-tab-periodo').value = 0;
        document.getElementById('btn-tab-executoria').value = 1;
    }
}


function round(value, decimals) {
    return Number(Math.round(value + 'e' + decimals) + 'e-' + decimals);
}

function printDateTime() {
    var currentdate = new Date();
    var dia = '';
    if(currentdate.getDate() < 10) {
        dia = '0' + currentdate.getDate();
    } else {
        dia = currentdate.getDate();
    }


    if(currentdate.getMonth()+1 < 10) {
        var mes_inteiro = 0;
        mes_inteiro = currentdate.getMonth() + 1;
        mes = '0' + mes_inteiro;
    } else {
        var mes_inteiro = 0;
        mes_inteiro = currentdate.getMonth() + 1;
        mes = mes_inteiro;
    }

    var datetime = dia + "-"
                + mes  + "-"
                + currentdate.getFullYear() + "_"
                + currentdate.getHours() + "-"
                + currentdate.getMinutes() + "-"
                + currentdate.getSeconds();
    return datetime;
}
