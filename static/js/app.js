var app = angular.module('SisatApp', ['ui.utils','ui.bootstrap','$strap.directives','ngSanitize','ngResource','maskMoney', 'platanus.keepValues']);

app.config(function($httpProvider){

    function _getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // https://docs.djangoproject.com/en/3.2/ref/csrf/
    let csrf_token =  $('input[name=csrfmiddlewaretoken]').val() || _getCookie('csrftoken');

    $httpProvider.defaults.headers.post['X-CSRFToken'] = csrf_token;
    $httpProvider.defaults.headers.patch['X-CSRFToken'] = csrf_token;
    $httpProvider.defaults.headers.put['X-CSRFToken'] = csrf_token;
    $httpProvider.defaults.headers.delete= { 'X-CSRFToken': csrf_token};
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
});

app.config(function($interpolateProvider){
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

app.directive('mask', ['$parse', function ($parse) {
	return {
		restrict: 'A',
		link: function (scope, elem, attrs) {
            $(elem).mask(attrs.mask);
		}
	};
}]);

app.directive('fileModel', ['$parse', function ($parse) {
	return {
		restrict: 'A',
		link: function (scope, element, attrs) {
			var model = $parse(attrs.fileModel);
			var modelSetter = model.assign;

			element.bind('change', function () {
				scope.$apply(function () {
					modelSetter(scope, element[0].files[0]);
				});
			});
		}
	};
}]);

app.directive('showRedactor', function () {
	return {
		restrict: "A",
		require: '?ngModel',
		link: function (scope, elem, attrs, ngModel) {
			var updateModel = function () {
				scope.$apply(ngModel.$setViewValue(elem.getCode()))
			};
			$(elem).redactor({
				keyupCallback: updateModel,
				keydownCallback: updateModel,
				execCommandCallback: updateModel,
				autosaveCallback: updateModel,
				buttons: [
					'bold',
					'italic',
					'underline',
					'|',
					'unorderedlist',
					'orderedlist',
				],
				lang: 'pt_br',
				plugins: ['fullscreen'],
				minHeight: 200
			});
		}
	}
});

app.directive("displayFile", function () {

    var updateElem = function (element) {
        return function (displayFile) {

            element.empty();

            var objectElem = {};
            var defaultContent = '<div class="text-error text-center helper-font-24"><p><i class="fa fa-exclamation-triangle"></i></p><p><b>Visualização não disponível</b></p><div>';

            if (displayFile && displayFile.type !== "") {
                objectElem = angular.element(document.createElement("object"));
                objectElem.attr("data", displayFile.url);
                objectElem.attr("type", displayFile.type);
                objectElem.attr("width", "100%");
                objectElem.attr("height", "700px");
                objectElem.html(defaultContent);
                element.append(objectElem);
            }
            else
            {
                element.html(defaultContent);
            }

        };
    };

    return {
        restrict: "EA",
        scope: {
            displayFile: "="
        },
        link: function (scope, element) {
            scope.$watch("displayFile", updateElem (element));
        }
    };
});

app.run(function ($rootScope) {
    $rootScope.gerar_link = function (view_name, params) {
        // Urls eh uma funcao da biblioteca
        // https://github.com/ierror/django-js-reverse
        if(Array.isArray(params))
            return Urls[view_name](...params);
        else
            return Urls[view_name](params);
    };
});

app.run(function ($rootScope) {
    $rootScope.get_url_processo_tj = function (url, numero, grau, chave) {
        grau = (grau==undefined ? '' : grau);
        chave = (chave==undefined ? '' : chave);
        return url.replace(/{numero}/g, numero).replace(/{grau}/g, grau).replace(/{chave}/g, chave);
    };
});

app.run(function ($rootScope) {
    $rootScope.solar_zeropad = function (n, c) {
        var s = String(n);
        if (s.length < c) {
            return zeropad("0" + n, c)
        }
        else {
            return s
        }
    };
});

app.run(function ($rootScope) {
    $rootScope.solar_identificador_doc = function (id_doc, versao_doc) {
        return $rootScope.solar_zeropad(id_doc, 8) + 'v' + $rootScope.solar_zeropad(versao_doc, 3);
    };
});

function getFormData(params){

    var data = new FormData();

    // Converte objeto para POST comum
    for(var key in params)
    {
        // Confirma existencia de key em params
        if (params.hasOwnProperty(key)) {
            // Converte objeto em chave e valor se nao for instancia de File
            if(typeof params[key] === "object" && !(params[key] instanceof File)){
                for(var item in params[key])
                {
                    if(params[key][item])
                    {
                        data.append(key, item);
                    }
                }
            }
            else
            {
                data.append(key, params[key]);
            }
        }
    }

    return data;

}

function aplicar_select2(object_id, auto_width)
{

    let inputs = $("#" + object_id + " select");

    let params = {
        width: '100%'
    }

    if(auto_width){
        inputs.addClass('ativar-select2');
        params = {
            dropdownAutoWidth : true
        }
    }

    // remove select2 antes de reaplicar
    inputs.select2('destroy');

    // aplica select2 após 1 segundo (necessário devido ao processamento do AngularJS)
    window.setTimeout(function()
    {
        inputs.select2(params);
    }
    , 1000);
}

app.service('fileUpload', ['$http', function ($http) {
	this.upload = function (url, params, status, on_success, on_error) {

        data = getFormData(params);
        status.uploading = true;

		$http.post(url, data, {
			transformRequest: angular.identity,
			headers: {'Content-Type': undefined}
		}).success(function (data) {
		    status.data = data;
            status.errors = (data instanceof Object && 'errors' in data ? data.errors: []);
            status.success = (data instanceof Object && 'success' in data ? data.success: false);
            status.uploading = false;
            if(on_success)
            {
                on_success(params, data);
            }
		}).error(function (data) {
            status.success = false;
            status.uploading = false;
            if(on_error)
            {
                on_error(params, data);
            }
		});

	}

    this.uploadPromise = function(url, params) {
        const data = getFormData(params);

		return $http.post(url, data, {
			transformRequest: angular.identity,
			headers: {'Content-Type': undefined}
		});
    }

}]);

app.filter('newLines', function(){
	return function(text) {
        if(text!=undefined)
            return text.replace(/\n/g, '<br />');
    }
});

app.filter('noHTML', function () {
    return function(text) {
        if(text!=undefined)
            return text
                    .replace(/&/g, '&amp;')
                    .replace(/>/g, '&gt;')
                    .replace(/</g, '&lt;');
    }
});

app.filter('hora_ini_fim', function () {
    return function(hora_ini, intervalo) {
        var hora_fim = new Date(hora_ini.getTime() + intervalo * 60000);
        return hora_ini.toLocaleTimeString().substring(0,5) + ' - ' + hora_fim.toLocaleTimeString().substring(0,5);
    }
});

app.filter('cpf_cnpj', function () {
    return function get_cpf_cnpj_formatado(input) {
        var str = input + '';
        if(str.length <= 11) {
            str = str.replace(/\D/g, '');
            str = str.replace(/(\d{3})(\d)/, "$1.$2");
            str = str.replace(/(\d{3})(\d)/, "$1.$2");
            str = str.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
        }
        else {
            str = str.replace(/\D/g, '');
            str = str.replace(/(\d{2})(\d)/, "$1.$2");
            str = str.replace(/(\d{3})(\d)/, "$1.$2");
            str = str.replace(/(\d{3})(\d)/, "$1/$2");
            str = str.replace(/(\d{4})(\d)/, "$1-$2");
            str = str.replace(/(\d{4})(\d{1,2})$/, "$1-$2");
        }
        return str;
    }
});

app.filter('cep', function () {
    return function get_cep_formatado(input) {
        var str = input + '';
        str = str.replace(/\D/g, '');
        str = str.replace(/(\d{2})(\d)/, "$1.$2");
        str = str.replace(/(\d{3})(\d)/, "$1-$2");
        return str;
    }
});

app.filter('telefone', function () {
    return function get_telefone_formatado(input) {
        var str = input + '';
        if(str.length == 9) {
            str = str.replace(/\D/g, '');
            str = str.replace(/(\d{5})(\d)/, "$1-$2");
        }
        else {
            str = str.replace(/\D/g, '');
            str = str.replace(/(\d{4})(\d)/, "$1-$2");
        }
        return str;
    }
});

app.filter('atendimento', function () {
    return function get_numero_atendimento_formatado(input) {
        var str = input + '';
        if(str.length === 12) {
            str = str.replace(/\D/g, '');
            str = str.replace(/(\d{6})(\d)/, "$1.$2");
            str = str.replace(/(\d{3})(\d{3})$/, "$1.$2");
        }
        return str;
    }
});

// formata número de processo judicial no padrão CNJ (https://www.cnj.jus.br/programas-e-acoes/numeracao-unica/perguntas-frequentes/)
app.filter('processo', function () {
    return function get_numero_processo_formatado(input) {
        var str = input + '';
        if(str.length === 20) {
            str = str.replace(/^(\d{7})(\d{2})(\d{4})(\d{1})(\d{2})(\d{4}).*/, '$1-$2.$3.$4.$5.$6');
        }
        return str;
    }
});

app.filter('exclude', function() {
  return function(input, item) {
    var out = [];
      if (input != null){
          for (var i = 0; i < input.length; i++){
              if(input[i].id != item.id)
                  out.push(input[i]);
          }
      }
    return out;
  };
});

app.filter('utc', function(){
    return function(d) {
        if(d==undefined) return 'Não informado(a)';
        date = new Date(d); //converte string em data
        date = new Date(date.getTime()+date.getTimezoneOffset()*60000); //soma diferenca de timezone
        if(d.length==10) date = new Date(date.getTime()+date.getTimezoneOffset()*60000); //soma diferenca de timezone
        return date;
    }
});

app.filter('default', function() {
	return function(input, defaultValue) {
		if (input == undefined || input == null)
		    return defaultValue;
		return input;
	};
});

app.filter('startsWith', function() {
    return function(input, value) {
        return input.sort(propComparator(value.toUpperCase()));
    };
});

app.filter('idEquals', function(){
    return function(input, filter, key) {
        if (filter == undefined || filter == null){
            return input;
        }
        var out = [];
        for(var i=0; i<input.length; i++){
            if(input[i][key].id==filter)
            {
                out.push(input[i]);
            }
        }
        return out;
    }
});

var latin_map={"Á":"A","Ă":"A","Ắ":"A","Ặ":"A","Ằ":"A","Ẳ":"A","Ẵ":"A","Ǎ":"A","Â":"A","Ấ":"A","Ậ":"A","Ầ":"A","Ẩ":"A","Ẫ":"A","Ä":"A","Ǟ":"A","Ȧ":"A","Ǡ":"A","Ạ":"A","Ȁ":"A","À":"A","Ả":"A","Ȃ":"A","Ā":"A","Ą":"A","Å":"A","Ǻ":"A","Ḁ":"A","Ⱥ":"A","Ã":"A","Ꜳ":"AA","Æ":"AE","Ǽ":"AE","Ǣ":"AE","Ꜵ":"AO","Ꜷ":"AU","Ꜹ":"AV","Ꜻ":"AV","Ꜽ":"AY","Ḃ":"B","Ḅ":"B","Ɓ":"B","Ḇ":"B","Ƀ":"B","Ƃ":"B","Ć":"C","Č":"C","Ç":"C","Ḉ":"C","Ĉ":"C","Ċ":"C","Ƈ":"C","Ȼ":"C","Ď":"D","Ḑ":"D","Ḓ":"D","Ḋ":"D","Ḍ":"D","Ɗ":"D","Ḏ":"D","ǲ":"D","ǅ":"D","Đ":"D","Ƌ":"D","Ǳ":"DZ","Ǆ":"DZ","É":"E","Ĕ":"E","Ě":"E","Ȩ":"E","Ḝ":"E","Ê":"E","Ế":"E","Ệ":"E","Ề":"E","Ể":"E","Ễ":"E","Ḙ":"E","Ë":"E","Ė":"E","Ẹ":"E","Ȅ":"E","È":"E","Ẻ":"E","Ȇ":"E","Ē":"E","Ḗ":"E","Ḕ":"E","Ę":"E","Ɇ":"E","Ẽ":"E","Ḛ":"E","Ꝫ":"ET","Ḟ":"F","Ƒ":"F","Ǵ":"G","Ğ":"G","Ǧ":"G","Ģ":"G","Ĝ":"G","Ġ":"G","Ɠ":"G","Ḡ":"G","Ǥ":"G","Ḫ":"H","Ȟ":"H","Ḩ":"H","Ĥ":"H","Ⱨ":"H","Ḧ":"H","Ḣ":"H","Ḥ":"H","Ħ":"H","Í":"I","Ĭ":"I","Ǐ":"I","Î":"I","Ï":"I","Ḯ":"I","İ":"I","Ị":"I","Ȉ":"I","Ì":"I","Ỉ":"I","Ȋ":"I","Ī":"I","Į":"I","Ɨ":"I","Ĩ":"I","Ḭ":"I","Ꝺ":"D","Ꝼ":"F","Ᵹ":"G","Ꞃ":"R","Ꞅ":"S","Ꞇ":"T","Ꝭ":"IS","Ĵ":"J","Ɉ":"J","Ḱ":"K","Ǩ":"K","Ķ":"K","Ⱪ":"K","Ꝃ":"K","Ḳ":"K","Ƙ":"K","Ḵ":"K","Ꝁ":"K","Ꝅ":"K","Ĺ":"L","Ƚ":"L","Ľ":"L","Ļ":"L","Ḽ":"L","Ḷ":"L","Ḹ":"L","Ⱡ":"L","Ꝉ":"L","Ḻ":"L","Ŀ":"L","Ɫ":"L","ǈ":"L","Ł":"L","Ǉ":"LJ","Ḿ":"M","Ṁ":"M","Ṃ":"M","Ɱ":"M","Ń":"N","Ň":"N","Ņ":"N","Ṋ":"N","Ṅ":"N","Ṇ":"N","Ǹ":"N","Ɲ":"N","Ṉ":"N","Ƞ":"N","ǋ":"N","Ñ":"N","Ǌ":"NJ","Ó":"O","Ŏ":"O","Ǒ":"O","Ô":"O","Ố":"O","Ộ":"O","Ồ":"O","Ổ":"O","Ỗ":"O","Ö":"O","Ȫ":"O","Ȯ":"O","Ȱ":"O","Ọ":"O","Ő":"O","Ȍ":"O","Ò":"O","Ỏ":"O","Ơ":"O","Ớ":"O","Ợ":"O","Ờ":"O","Ở":"O","Ỡ":"O","Ȏ":"O","Ꝋ":"O","Ꝍ":"O","Ō":"O","Ṓ":"O","Ṑ":"O","Ɵ":"O","Ǫ":"O","Ǭ":"O","Ø":"O","Ǿ":"O","Õ":"O","Ṍ":"O","Ṏ":"O","Ȭ":"O","Ƣ":"OI","Ꝏ":"OO","Ɛ":"E","Ɔ":"O","Ȣ":"OU","Ṕ":"P","Ṗ":"P","Ꝓ":"P","Ƥ":"P","Ꝕ":"P","Ᵽ":"P","Ꝑ":"P","Ꝙ":"Q","Ꝗ":"Q","Ŕ":"R","Ř":"R","Ŗ":"R","Ṙ":"R","Ṛ":"R","Ṝ":"R","Ȑ":"R","Ȓ":"R","Ṟ":"R","Ɍ":"R","Ɽ":"R","Ꜿ":"C","Ǝ":"E","Ś":"S","Ṥ":"S","Š":"S","Ṧ":"S","Ş":"S","Ŝ":"S","Ș":"S","Ṡ":"S","Ṣ":"S","Ṩ":"S","ẞ":"SS","Ť":"T","Ţ":"T","Ṱ":"T","Ț":"T","Ⱦ":"T","Ṫ":"T","Ṭ":"T","Ƭ":"T","Ṯ":"T","Ʈ":"T","Ŧ":"T","Ɐ":"A","Ꞁ":"L","Ɯ":"M","Ʌ":"V","Ꜩ":"TZ","Ú":"U","Ŭ":"U","Ǔ":"U","Û":"U","Ṷ":"U","Ü":"U","Ǘ":"U","Ǚ":"U","Ǜ":"U","Ǖ":"U","Ṳ":"U","Ụ":"U","Ű":"U","Ȕ":"U","Ù":"U","Ủ":"U","Ư":"U","Ứ":"U","Ự":"U","Ừ":"U","Ử":"U","Ữ":"U","Ȗ":"U","Ū":"U","Ṻ":"U","Ų":"U","Ů":"U","Ũ":"U","Ṹ":"U","Ṵ":"U","Ꝟ":"V","Ṿ":"V","Ʋ":"V","Ṽ":"V","Ꝡ":"VY","Ẃ":"W","Ŵ":"W","Ẅ":"W","Ẇ":"W","Ẉ":"W","Ẁ":"W","Ⱳ":"W","Ẍ":"X","Ẋ":"X","Ý":"Y","Ŷ":"Y","Ÿ":"Y","Ẏ":"Y","Ỵ":"Y","Ỳ":"Y","Ƴ":"Y","Ỷ":"Y","Ỿ":"Y","Ȳ":"Y","Ɏ":"Y","Ỹ":"Y","Ź":"Z","Ž":"Z","Ẑ":"Z","Ⱬ":"Z","Ż":"Z","Ẓ":"Z","Ȥ":"Z","Ẕ":"Z","Ƶ":"Z","Ĳ":"IJ","Œ":"OE","ᴀ":"A","ᴁ":"AE","ʙ":"B","ᴃ":"B","ᴄ":"C","ᴅ":"D","ᴇ":"E","ꜰ":"F","ɢ":"G","ʛ":"G","ʜ":"H","ɪ":"I","ʁ":"R","ᴊ":"J","ᴋ":"K","ʟ":"L","ᴌ":"L","ᴍ":"M","ɴ":"N","ᴏ":"O","ɶ":"OE","ᴐ":"O","ᴕ":"OU","ᴘ":"P","ʀ":"R","ᴎ":"N","ᴙ":"R","ꜱ":"S","ᴛ":"T","ⱻ":"E","ᴚ":"R","ᴜ":"U","ᴠ":"V","ᴡ":"W","ʏ":"Y","ᴢ":"Z","á":"a","ă":"a","ắ":"a","ặ":"a","ằ":"a","ẳ":"a","ẵ":"a","ǎ":"a","â":"a","ấ":"a","ậ":"a","ầ":"a","ẩ":"a","ẫ":"a","ä":"a","ǟ":"a","ȧ":"a","ǡ":"a","ạ":"a","ȁ":"a","à":"a","ả":"a","ȃ":"a","ā":"a","ą":"a","ᶏ":"a","ẚ":"a","å":"a","ǻ":"a","ḁ":"a","ⱥ":"a","ã":"a","ꜳ":"aa","æ":"ae","ǽ":"ae","ǣ":"ae","ꜵ":"ao","ꜷ":"au","ꜹ":"av","ꜻ":"av","ꜽ":"ay","ḃ":"b","ḅ":"b","ɓ":"b","ḇ":"b","ᵬ":"b","ᶀ":"b","ƀ":"b","ƃ":"b","ɵ":"o","ć":"c","č":"c","ç":"c","ḉ":"c","ĉ":"c","ɕ":"c","ċ":"c","ƈ":"c","ȼ":"c","ď":"d","ḑ":"d","ḓ":"d","ȡ":"d","ḋ":"d","ḍ":"d","ɗ":"d","ᶑ":"d","ḏ":"d","ᵭ":"d","ᶁ":"d","đ":"d","ɖ":"d","ƌ":"d","ı":"i","ȷ":"j","ɟ":"j","ʄ":"j","ǳ":"dz","ǆ":"dz","é":"e","ĕ":"e","ě":"e","ȩ":"e","ḝ":"e","ê":"e","ế":"e","ệ":"e","ề":"e","ể":"e","ễ":"e","ḙ":"e","ë":"e","ė":"e","ẹ":"e","ȅ":"e","è":"e","ẻ":"e","ȇ":"e","ē":"e","ḗ":"e","ḕ":"e","ⱸ":"e","ę":"e","ᶒ":"e","ɇ":"e","ẽ":"e","ḛ":"e","ꝫ":"et","ḟ":"f","ƒ":"f","ᵮ":"f","ᶂ":"f","ǵ":"g","ğ":"g","ǧ":"g","ģ":"g","ĝ":"g","ġ":"g","ɠ":"g","ḡ":"g","ᶃ":"g","ǥ":"g","ḫ":"h","ȟ":"h","ḩ":"h","ĥ":"h","ⱨ":"h","ḧ":"h","ḣ":"h","ḥ":"h","ɦ":"h","ẖ":"h","ħ":"h","ƕ":"hv","í":"i","ĭ":"i","ǐ":"i","î":"i","ï":"i","ḯ":"i","ị":"i","ȉ":"i","ì":"i","ỉ":"i","ȋ":"i","ī":"i","į":"i","ᶖ":"i","ɨ":"i","ĩ":"i","ḭ":"i","ꝺ":"d","ꝼ":"f","ᵹ":"g","ꞃ":"r","ꞅ":"s","ꞇ":"t","ꝭ":"is","ǰ":"j","ĵ":"j","ʝ":"j","ɉ":"j","ḱ":"k","ǩ":"k","ķ":"k","ⱪ":"k","ꝃ":"k","ḳ":"k","ƙ":"k","ḵ":"k","ᶄ":"k","ꝁ":"k","ꝅ":"k","ĺ":"l","ƚ":"l","ɬ":"l","ľ":"l","ļ":"l","ḽ":"l","ȴ":"l","ḷ":"l","ḹ":"l","ⱡ":"l","ꝉ":"l","ḻ":"l","ŀ":"l","ɫ":"l","ᶅ":"l","ɭ":"l","ł":"l","ǉ":"lj","ſ":"s","ẜ":"s","ẛ":"s","ẝ":"s","ḿ":"m","ṁ":"m","ṃ":"m","ɱ":"m","ᵯ":"m","ᶆ":"m","ń":"n","ň":"n","ņ":"n","ṋ":"n","ȵ":"n","ṅ":"n","ṇ":"n","ǹ":"n","ɲ":"n","ṉ":"n","ƞ":"n","ᵰ":"n","ᶇ":"n","ɳ":"n","ñ":"n","ǌ":"nj","ó":"o","ŏ":"o","ǒ":"o","ô":"o","ố":"o","ộ":"o","ồ":"o","ổ":"o","ỗ":"o","ö":"o","ȫ":"o","ȯ":"o","ȱ":"o","ọ":"o","ő":"o","ȍ":"o","ò":"o","ỏ":"o","ơ":"o","ớ":"o","ợ":"o","ờ":"o","ở":"o","ỡ":"o","ȏ":"o","ꝋ":"o","ꝍ":"o","ⱺ":"o","ō":"o","ṓ":"o","ṑ":"o","ǫ":"o","ǭ":"o","ø":"o","ǿ":"o","õ":"o","ṍ":"o","ṏ":"o","ȭ":"o","ƣ":"oi","ꝏ":"oo","ɛ":"e","ᶓ":"e","ɔ":"o","ᶗ":"o","ȣ":"ou","ṕ":"p","ṗ":"p","ꝓ":"p","ƥ":"p","ᵱ":"p","ᶈ":"p","ꝕ":"p","ᵽ":"p","ꝑ":"p","ꝙ":"q","ʠ":"q","ɋ":"q","ꝗ":"q","ŕ":"r","ř":"r","ŗ":"r","ṙ":"r","ṛ":"r","ṝ":"r","ȑ":"r","ɾ":"r","ᵳ":"r","ȓ":"r","ṟ":"r","ɼ":"r","ᵲ":"r","ᶉ":"r","ɍ":"r","ɽ":"r","ↄ":"c","ꜿ":"c","ɘ":"e","ɿ":"r","ś":"s","ṥ":"s","š":"s","ṧ":"s","ş":"s","ŝ":"s","ș":"s","ṡ":"s","ṣ":"s","ṩ":"s","ʂ":"s","ᵴ":"s","ᶊ":"s","ȿ":"s","ɡ":"g","ß":"ss","ᴑ":"o","ᴓ":"o","ᴝ":"u","ť":"t","ţ":"t","ṱ":"t","ț":"t","ȶ":"t","ẗ":"t","ⱦ":"t","ṫ":"t","ṭ":"t","ƭ":"t","ṯ":"t","ᵵ":"t","ƫ":"t","ʈ":"t","ŧ":"t","ᵺ":"th","ɐ":"a","ᴂ":"ae","ǝ":"e","ᵷ":"g","ɥ":"h","ʮ":"h","ʯ":"h","ᴉ":"i","ʞ":"k","ꞁ":"l","ɯ":"m","ɰ":"m","ᴔ":"oe","ɹ":"r","ɻ":"r","ɺ":"r","ⱹ":"r","ʇ":"t","ʌ":"v","ʍ":"w","ʎ":"y","ꜩ":"tz","ú":"u","ŭ":"u","ǔ":"u","û":"u","ṷ":"u","ü":"u","ǘ":"u","ǚ":"u","ǜ":"u","ǖ":"u","ṳ":"u","ụ":"u","ű":"u","ȕ":"u","ù":"u","ủ":"u","ư":"u","ứ":"u","ự":"u","ừ":"u","ử":"u","ữ":"u","ȗ":"u","ū":"u","ṻ":"u","ų":"u","ᶙ":"u","ů":"u","ũ":"u","ṹ":"u","ṵ":"u","ᵫ":"ue","ꝸ":"um","ⱴ":"v","ꝟ":"v","ṿ":"v","ʋ":"v","ᶌ":"v","ⱱ":"v","ṽ":"v","ꝡ":"vy","ẃ":"w","ŵ":"w","ẅ":"w","ẇ":"w","ẉ":"w","ẁ":"w","ⱳ":"w","ẘ":"w","ẍ":"x","ẋ":"x","ᶍ":"x","ý":"y","ŷ":"y","ÿ":"y","ẏ":"y","ỵ":"y","ỳ":"y","ƴ":"y","ỷ":"y","ỿ":"y","ȳ":"y","ẙ":"y","ɏ":"y","ỹ":"y","ź":"z","ž":"z","ẑ":"z","ʑ":"z","ⱬ":"z","ż":"z","ẓ":"z","ȥ":"z","ẕ":"z","ᵶ":"z","ᶎ":"z","ʐ":"z","ƶ":"z","ɀ":"z","ﬀ":"ff","ﬃ":"ffi","ﬄ":"ffl","ﬁ":"fi","ﬂ":"fl","ĳ":"ij","œ":"oe","ﬆ":"st","ₐ":"a","ₑ":"e","ᵢ":"i","ⱼ":"j","ₒ":"o","ᵣ":"r","ᵤ":"u","ᵥ":"v","ₓ":"x"};

function latinise(str){
      if(str !== undefined) {
          return str.replace(/[^A-Za-z0-9\[\] ]/g, function (x) {
              return latin_map[x] || x;
          });
      }
}

window.latinise = latinise;

app.filter('latinise', function () {
    return function (text) {
        if(text !== undefined){
            return latinise(text);
        }
    }
});


app.directive('upperText', function() {
   return {
     require: 'ngModel',
     link: function(scope, element, attrs, modelCtrl) {
        var capitalize = function(inputValue) {
            if(inputValue !== undefined){
               var capitalized = inputValue.toUpperCase();
               var caretPosition = getCaretPosition(element.get(0));
               if(capitalized !== inputValue) {
                  modelCtrl.$setViewValue(capitalized);
                  modelCtrl.$render();
                }
                setCaretPosition(element.get(0), caretPosition);
                return capitalized;
            }
         }
         modelCtrl.$parsers.push(capitalize);
         capitalize(scope[attrs.ngModel]);  // capitalize initial value
     }
   };
});

app.factory('HttpRequestInterceptor', function ($q, $location) {
    return {
        'responseError': function(rejection) {
            if(rejection.status === 404){
                $location.path('/');
            }
            return $q.reject(rejection);
         }
     };
});

app.factory('$socket', function($rootScope){

    var socket = io.connect(NODE_SERVER);

    return {
        on : function (eventName, callback) {
            socket.on(eventName, function(){
                var args = arguments;
                $rootScope.$apply(function(){
                    callback.apply(socket, args);
                });
            });
        },
        emit : function (eventName, data, callback) {
            socket.emit(eventName, data, function(){
                var args = arguments;
                $rootScope.$apply(function(){
                    if (callback)
                        callback.apply(socket, args);
                });
            });
        }
    };

});

app.factory('Shared', function(){
	return {};
});

function ImprimirCtrl($scope, $http, fileUpload)
{

    $scope.defaults = {};
    $scope.relatorios = [];
    $scope.docSelecionado = null;

	$scope.meses = [
		{id:1, nome:'Janeiro'},
		{id:2, nome:'Fevereiro'},
		{id:3, nome:'Março'},
		{id:4, nome:'Abril'},
		{id:5, nome:'Maio'},
		{id:6, nome:'Junho'},
		{id:7, nome:'Julho'},
		{id:8, nome:'Agosto'},
		{id:9, nome:'Setembro'},
		{id:10, nome:'Outubro'},
		{id:11, nome:'Novembro'},
		{id:12, nome:'Dezembro'}];

    // ao alterar campo 'data_final', aplicar data/hora final do dia selecionado no parametro dos relatórios
	$scope.$watch('fields.data_final', function() {
        if($scope.fields.data_final)
        {
            $scope.fields.datahora_final = $scope.fields.data_final.getMaxUTCDateTime();
        }
    });

    $scope.imprimir = function(data, report_name, report_resource, format)
    {

        // sobrescreve os valores padrão dos parâmetros pelos valores padrão informados na página
        for(var key in $scope.fields.defaults)
        {
            data.params.defaults[key] = $scope.fields.defaults[key];
        }

        $scope.relatorio = data;
        Chronus.generate($scope, data.user, report_name, report_resource, data.params, format);

    };

    $scope.init = function(defaults)
    {

        if(defaults===undefined)
        {
            defaults = {};
        }

        var agora = new Date();

        $scope.fields = {
            format: 'pdf',
            defaults: defaults,
            data_inicial: new Date(Date.UTC(agora.getFullYear(), agora.getMonth(), 1)),
            data_final: new Date(Date.UTC(agora.getFullYear(), agora.getMonth() + 1, 0, 23, 59, 59)),
            ano: agora.getFullYear(),
            mes: agora.getMonth() + 1
        };

    }

    $scope.add_relatorio = function(data){
        $scope.relatorios.push(data);
    }

     /*
    ATENÇÃO!!!
    As funções abaixo são do arquivo controllers_recepcao.js. Foi preciso colocar neste controller para o upload de
    arquivos na página 'Detalhes do Atendimento' voltar a funcionar, visto que ela usa este controller sobreposto ao
    controller 'RecepcaoAtendimentoCtrl'
     */

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
				show_stack_error('Erro ao salvar o documento: ' + $scope.documento_status.data.errors[0][1]);
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

    $scope.selecionaDocumento = function (doc) {
        $scope.docSelecionado = doc;
    }

    $scope.salvarNivelSigilo = function () {
        const data = JSON.stringify({
            id: $scope.docSelecionado.id,
            nome: $scope.docSelecionado.nome,
            nivel_sigilo: $scope.docSelecionado.nivelSigilo            
        });        
        const url = '/core/altera-sigilo-documento/'
        $http.post(url, data, {
			transformRequest: angular.identity,
			headers: {'Content-Type': undefined}
		}).success(function (data, response) {
            if (response == 200) {
                show_stack_success(data.message);
            }
            window.location.reload(true);		    
		}).error(function (data, response) {
            const statusCodes = [400, 403, 404]
            if (statusCodes.includes(response) && data.message)
                show_stack_error(data.message);
            else {
                show_stack_error('Ocorreu um erro ao alterar o nível de sigilo do documento selecionado.');
            }    
		});
    }

    $scope.limparDocumentoSelecionado = function () {
        $scope.docSelecionado = null;
    }

    // $scope.init(); <- usar init apenas no html pois usar aqui sobrescreve a chamada no html

}

function propComparator(filter)
{
    return function(a, b)
    {
        var indexA = a.nome.indexOf(filter);
        var indexB = b.nome.indexOf(filter);

        if(indexA <= indexB && a.nome.substring(indexA) <= b.nome.substring(indexB))
            return -1;
        else if(indexA >= indexB && a.nome.substring(indexA) >= b.nome.substring(indexB))
            return 1;
        else
            return 0;

    }
}

Date.prototype.getDayOnYear = function(){
  var onejan = new Date(this.getFullYear(),0,1);
  return Math.ceil((this - onejan) / 86400000);
}

Date.prototype.getDaysInYear = function(){
  var fev = new Date(this.getFullYear(),2,0);
  return (fev.getDate()==29 ? 366 : 365);
}

Date.prototype.getMaxUTCDateTime = function(){
    return new Date(Date.UTC(this.getUTCFullYear(), this.getUTCMonth(), this.getUTCDate(), 23, 59, 59, 999));
}

Date.combine = function(date_obj, time_str)
{

    var timeFormat = /^([0-9]{2})\:([0-9]{2})$/;
    var params = [0, 0];
    var result = null;

    if(Object.prototype.toString.call(date_obj) === '[object Date]')
    {

        if(timeFormat.test(time_str)){
            params = time_str.split(':')
        }

        result = new Date(
            date_obj.getUTCFullYear(),
            date_obj.getUTCMonth(),
            date_obj.getUTCDate(),
            ...params
        )

    }

    return result;

}

Date.combineToLocaleString = function(date_obj, time_str)
{

    var result = Date.combine(date_obj, time_str);

    if(result!=null)
    {
        result = result.toLocaleString().replace(',', '');
    }

    return result;

}

Array.prototype.remove = function(obj)
{
    if(this.indexOf(obj)!=-1)
    {
        this.splice(this.indexOf(obj), 1);
        return true;
    }
    return false;
}
