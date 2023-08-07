/**
 * Creted by luzfcb on 05/07/17.
 */

/**
 * @preserve jquery-param (c) 2015 KNOWLEDGECODE | MIT
 */
(function (global) {
    'use strict';
    // https://github.com/ydeshayes/jquery-param

    var param = function (a) {
        var s = [], rbracket = /\[\]$/,
            isArray = function (obj) {
                return Object.prototype.toString.call(obj) === '[object Array]';
            }, add = function (k, v) {
                v = typeof v === 'function' ? v() : v === null ? '' : v === undefined ? '' : v;
                s[s.length] = encodeURIComponent(k) + '=' + encodeURIComponent(v);
            }, buildParams = function (prefix, obj) {
                var i, len, key;

                if (prefix) {
                    if (isArray(obj)) {
                        for (i = 0, len = obj.length; i < len; i++) {
                            if (rbracket.test(prefix)) {
                                add(prefix, obj[i]);
                            } else {
                                buildParams(prefix + '[' + (typeof obj[i] === 'object' ? i : '') + ']', obj[i]);
                            }
                        }
                    } else if (obj && String(obj) === '[object Object]') {
                        for (key in obj) {
                            if (obj[key]) {
                                buildParams(prefix + '[' + key + ']', obj[key]);
                            }
                        }
                    } else {
                        add(prefix, obj);
                    }
                } else if (isArray(obj)) {
                    for (i = 0, len = obj.length; i < len; i++) {
                        add(obj[i].name, obj[i].value);
                    }
                } else {
                    for (key in obj) {
                        if (obj[key]) {
                            buildParams(key, obj[key]);
                        }
                    }
                }
                return s;
            };

        return buildParams('', a).join('&').replace(/%20/g, '+');
    };

    if (typeof module === 'object' && typeof module.exports === 'object') {
        module.exports = param;
    } else if (typeof define === 'function' && define.amd) {
        define([], function () {
            return param;
        });
    } else {
        global.param = param;
    }

}(this));

// ----------------------------
var clean_form_errors = function (serialized_array, form) {

    for (var item in serialized_array) {
        if (serialized_array.hasOwnProperty(item)) {
            var input_id = 'id_' + serialized_array[item].name;
            var label_search = "label[for='" + input_id + "']";
            $(label_search).parents('div:first').removeClass('has-error').removeClass('error');
            $('.autoadded', form).remove();
        }
    }
};

var mark_fields_with_errors = function (errors, form) {
    for (var key in errors) {
        if (errors.hasOwnProperty(key)) {
            var el_text = '<p id="error_1_id_' + key + '" class="help-block autoadded"> <strong>' + errors[key] + '</strong></p>';
            var p_element = $(el_text);
            var input_id = 'id_' + key;
            var label_search = "label[for='" + input_id + "']";
            $('#hint_id_' + key, form).before(p_element);

            $(label_search).parents('div:first').removeClass('has-error').removeClass('error').addClass('has-error').addClass('error');
        }
    }
};


function CadastroServidorCtrl($scope, $http, $filter) {

    var transform = function (data) {
        return param(data);
    };
    var com_non_form_erros = function () {
        return $scope.errors && $scope.errors.hasOwnProperty('__all__') && $scope.errors['__all__'].length >= 1
    };
    var editaveis_padrao = {
        "password1": true,
        "password2": true,
        "papel": true,
        "comarca": true
    };
    $scope.errors = {"__all__": []};
    $scope.botoes = [];
    $scope.editaveis = {};
    $scope.pesquisa = {};
    $scope.eh_pesquisa = true;
    $scope.non_form_error = false;
    $scope.formulario_com_erros = false;

    $scope.dados_usuario_recem_criado = null;
    $scope.origem = "";

    $scope.utcTimeFormat = "yyyy-MM-dd'T'HH:mm:ss.sss'Z'";
    $scope.reiniciar_cadastro = function (e) {
        e.preventDefault();
        editaveis_padrao = {
            "password1": true,
            "password2": true,
            "papel": true,
            "comarca": true
        };
        $scope.errors = {"__all__": []};
        $scope.botoes = [];
        $scope.editaveis = {};
        $scope.pesquisa = {};
        $scope.eh_pesquisa = true;
        $scope.non_form_error = false;
        $scope.formulario_com_erros = false;

        $scope.dados_usuario_recem_criado = null;
        $scope.origem = "";

        $scope.utcTimeFormat = "yyyy-MM-dd'T'HH:mm:ss.sss'Z'";

        $(".ativar-select2").select2("data", null);

    };

    $scope.mostrar_erros = function (e) {
        if (com_non_form_erros() || $scope.botoes.length >= 1) {
            return true;
        }
        return false;

    };
    $scope.mostrar_pesquisa = function (e) {
        return $scope.eh_pesquisa;
    };

    $scope.mostrar_cadastrar_novo = function (e) {

        if ($scope.eh_pesquisa || com_non_form_erros() || $scope.botoes.length >= 1 || $scope.dados_usuario_recem_criado) {
            return false;
        } else {
            return true;
        }
    };
    $scope.removerNaoNumericos = function (e, variavel, chave) {

        e.preventDefault();
        var self = $(this);
        var content;
        if (e.originalEvent && e.originalEvent.clipboardData) {
            content = (e.originalEvent || e).clipboardData.getData('text/plain');
        }
        else if (window.clipboardData) {
            content = window.clipboardData.getData('Text');
        }
        var new_value = content.replace(/([\D]*)/g, "");
        if (variavel) {

            variavel[chave] = new_value;
        }
    };


    $scope.pesquisar = function (e) {
        e.preventDefault();
        $scope.carregando = true;
        $scope.errors = {"__all__": []};
        $scope.botoes = [];
        var formElement = angular.element(e.target);
        var form_action = formElement.attr("action").replace(/\s/g, "");


        $http.post(form_action, $scope.pesquisa, {
            headers: {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
            transformRequest: transform
        }).success(function (data) {
            $scope.carregando = false;
            $scope.errors = data.errors;
            $scope.botoes = data.botoes;
            $scope.servidor = data.dados_servidor;
            if (!$scope.servidor.cpf) {
                var cpf_matricula_limpo = $scope.pesquisa.cpf_matricula;
                cpf_matricula_limpo = cpf_matricula_limpo.replace(/([\D]*)/g, "");

                if (cpf_matricula_limpo.length >= 11 || CPF.validate(cpf_matricula_limpo)) {
                    $scope.servidor.cpf = cpf_matricula_limpo;
                } else {
                    if (!$scope.servidor.matricula) {
                        $scope.servidor.matricula = $scope.pesquisa.cpf_matricula;
                    }
                }
            }
            if (!$scope.servidor.nome) {
                if ($scope.pesquisa.nome_completo) {
                    $scope.servidor.nome = $scope.pesquisa.nome_completo
                }
            }
            $scope.eh_pesquisa = false;
            $scope.origem = data.origem;

            $scope.editaveis = Object.assign(editaveis_padrao, data.editaveis);

            if (data.pode_cadastrar && hopscotch.getState() === "servidor_cadastrar:2") {
                setTimeout(function(){
                    hopscotch.startTour(tours['servidor_cadastrar'], 3);
                }, 500);
            }

        });

    };
    $scope.salvar = function (e) {
        e.preventDefault();
        $scope.carregando = true;
        $scope.non_form_error = false;
        $scope.dados_usuario_recem_criado = null;
        var formElement = angular.element(e.target);
        var form_action = formElement.attr("action").replace(/\s/g, "");
        var $the_formElement = $(formElement);
        var form_data = $the_formElement.serializeArray();
        clean_form_errors(form_data, $the_formElement);

        $http.post(form_action, $scope.servidor, {
            headers: {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
            transformRequest: transform
        }).success(function (data, status, headers, config) {
            $scope.carregando = false;
            $scope.dados_usuario_recem_criado = data.object_instance;
            $scope.errors = data.errors;
            if (data.object_instance.enviar_email_ao_cadastrar_servidor){
                var csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
                $scope.carregandoEmail = true;
                $.ajaxSetup({
                    headers: {
                        "X-CSRFToken": csrf_token
                    }
                });
                $.ajax({
                    url: "/core/email_info_acesso/",
                    data: {
                        email: $scope.dados_usuario_recem_criado.email,
                        username: $scope.dados_usuario_recem_criado.username,
                    },
                    type: 'POST',
                    tryCount: 0,
                    retryLimit: 3,
                    success: function (data) {
                        if (data['error']) {
                            this.tryCount++;
                            if (this.tryCount <= this.retryLimit) {
                                //try again
                                $.ajax(this);
                                return;
                            } else {
                                show_stack_error('Não foi possível enviar o email. Problema de conexão.');
                                $scope.carregandoEmail = false;
                                return;
                            }
                        }
                        $scope.carregandoEmail = false;
                        show_stack_success('Email enviado com sucesso.');
                    },
                    error: function (xhr, textStatus, errorThrown) {
                        if (textStatus === 'timeout') {
                            this.tryCount++;
                            if (this.tryCount <= this.retryLimit) {
                                //try again
                                $.ajax(this);
                                return;
                            }
                        }
                        if (xhr.status === 500) {
                            //handle error
                            this.tryCount++;
                            if (this.tryCount <= this.retryLimit) {
                                //try again
                                $.ajax(this);
                                return;
                            }
                        } else {
                            //handle error
                            this.tryCount++;
                            if (this.tryCount <= this.retryLimit) {
                                //try again
                                $.ajax(this);
                                return;
                            }
                        }
                        show_stack_error('Não foi possível enviar o email. Problema de conexão.');
                        $scope.carregandoEmail = false;
                    }
                });
            }
        }).error(function (data, status, headers, config) {
            $scope.carregando = false;
            $scope.errors = data.errors;
            mark_fields_with_errors(data.errors, $(formElement));

        });

    };

}

function CadastroTelefoneCtrl($scope)
{
    $scope.telefone = '';
    $scope.init = function(telefone)
    {
        $scope.telefone = telefone;
    }
}