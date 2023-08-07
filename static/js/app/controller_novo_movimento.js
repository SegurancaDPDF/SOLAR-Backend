var novo_movimento_app = angular.module('novoMovimentoApp', ['SisatApp', 'ngRoute', 'ui.utils', 'ui.bootstrap', '$strap.directives', 'ngSanitize', 'maskMoney']);

function NovoMovimentoCtrl($scope, $route, $routeParams, $location,
                           fileUpload, PropacTarefaService) {

    $scope.$route = $route;
    $scope.$location = $location;
    $scope.$routeParams = $routeParams;
    $scope.mostrar = false;
    $scope.clicou_btn_salvar = false;
    $scope.clicou_btn_cancelar = false;
    $scope.tipos_anexo = {};

    $scope.init = function (documentos) {

        $scope.movimento = {
            documentos: []
        };
        $scope.documento = null;
        $scope.documento_atendimento = documentos.atendimentos;

        $scope.documentosTarefas = documentos.documentos_tarefas;
        $scope.tipos_anexo = documentos.tipos_anexo;

        for (var i = 0; i < documentos.documentos.length; i++) {

            var doc = {
                modo: !documentos.documentos[i]['anexo'],
                tipo_anexo_str: documentos.documentos[i]['tipo_anexo'],
                anexo_str: documentos.documentos[i]['anexo'],
                ativo: true,
                documento_propac_pk: documentos.documentos[i]['documento_propac_pk'],
                cancelar_doc_propac_url: documentos.documentos[i]['cancelar_doc_propac_url'],
                documento: documentos.documentos[i]['documento'],
                novo_doc: false,
                status: {
                    success: true
                }
            };
            doc['novo_doc'] = false;
            $scope.movimento.documentos.push(doc);
            // break;
        }
        $scope.jquery_form_novo_movimento = jQuery('#form-novo-movimento');
        $scope.jquery_form_novo_movimento.find(':input').each(function (key, value) {
            jQuery(this).change(function () {

                var el = jQuery(this);
                el.addClass('dirty');
                // el.attr('data-dirty', 'true')

            });
        });
        $scope.documento_anexo_resultado = null;
    };
    $scope.$watch('documento.documento', function () {

        if ($scope.documento && $scope.documento.documento) {
            $scope.salvar_anexo();
        }
    });
    $scope.$watch('documento.anexo', function () {

        if ($scope.documento && $scope.documento.anexo) {
            var ext = $scope.documento.anexo.name.split('.').pop();
            switch(ext)
            {
                case 'doc':
                case 'docx':
                    console.log('extensao invalida: ' + ext);
                    $("#id_anexo").val('');
                    $scope.documento.anexo = null;
                    $scope.documento_anexo_resultado = true;

                    break;
                default:
                    $scope.documento_anexo_resultado=null;
            }
        }
    });
    // TODO Remover este watch, a princípio não é mais utilizado.
    $scope.$watch('clicou_btn_salvar', function () {
        if ($scope.clicou_btn_salvar) {

        }
        //console.log('clicou_btn_salvar == ' + $scope.clicou_btn_salvar);
    });
    $scope.deletar_documento = function (url) {
        function success(posted, returned) {
            //Remove o item da lista
            var index = $scope.movimento.documentos.indexOf($scope.movimento.documento_remover);
            $scope.movimento.documentos.splice(index , 1);
            // fecha modal
            jQuery('#modal-remover-documento-item').modal('hide');
            $scope.movimento.documento_remover = null;
        }

        function error(posted, returned) {
            //console.log('error');
        }

        fileUpload.upload(url, {}, {}, success, error);
    };

    $scope.novo_arquivo = function (modo) {
        //console.log('novo_anexo');
        $scope.documento = {
            modo: modo,
            tipo_anexo: null,
            anexo: null,
            ativo: true,
            status: {},
            novo_doc: false
        }
    };

    $scope.verifica_tipo_anexo_informado = function (e){
        return e.tipo_anexo === '' || e.tipo_anexo === null
    }

    $scope.salvar_anexo_atendimento = function() {
        function success(enviado, recebido) {

            doc_recebido = {
                modo: !recebido['anexo'],
                tipo_anexo_str: recebido['tipo_anexo'],
                anexo: recebido['anexo'],
                ativo: true,
                documento_propac_pk: recebido['documento_propac_pk'],
                cancelar_doc_propac_url: recebido['cancelar_doc_propac_url'],
                documento: recebido['documento'],
                novo_doc: true,
                status: {
                    success: true
                }
            };

            $scope.movimento.documentos.push(doc_recebido);
            //Remove o item da lista
            var index = $scope.documento_atendimento.indexOf(enviado);
            $scope.documento_atendimento.splice(index , 1);

            for (var key in doc_recebido) {
                enviado[key] = doc_recebido[key];
            }

        }

        function falhou(enviado, recebido) {
            console.log('falhou enviar dados');

        }
        $scope.documento_atendimento.forEach(function(el, index, array){
            var form_action = jQuery('#form-novo-documentopropac').attr("action").replace(/\s/g, "");
            fileUpload.upload(form_action, el, el.status, success, falhou);
        })
    }

    $scope.salvar_anexo_tarefa = function() {
        PropacTarefaService.salvarDocumentosTarefasPropac($scope.documentosTarefas)
        .success(function(data, response) {
            if (response == 201) {
                data.forEach(function(doc) {
                    $scope.movimento.documentos.push({
                        modo: !doc.modo,
                        tipo_anexo_str: doc.tipo_anexo_nome,
                        anexo: doc.anexo_original_nome_arquivo,
                        ativo: true,
                        documento_propac_pk: doc.id,
                        cancelar_doc_propac_url: doc.cancelar_doc_propac_url,
                        documento: doc.documento,
                        novo_doc: true,
                        status: {
                            success: true
                        }
                    });
                });
                //Remove o item da lista
                $scope.documentosTarefas = [];
            } else {
                cosole.info("Nenhum documento anexado: ", response)
            }
        }).error(function(data, response, status) {
            cosole.error("ocorreu um erro ao salvar os documentos propac, código: ", response)
        });

    };

    $scope.salvar_anexo = function () {
        var doc = false;

        if ($scope.documento.documento) {
            doc = angular.fromJson($scope.documento.documento);
            $scope.documento.documento = doc.value;
        }

        var doc_recebido = {};
        var form_action = jQuery('#form-novo-documentopropac').attr("action").replace(/\s/g, "");

        function success(enviado, recebido) {

            doc_recebido = {
                modo: !recebido['anexo'],
                tipo_anexo_str: recebido['tipo_anexo'],
                anexo: recebido['anexo'],
                ativo: true,
                documento_propac_pk: recebido['documento_propac_pk'],
                cancelar_doc_propac_url: recebido['cancelar_doc_propac_url'],
                documento: recebido['documento'],
                novo_doc: true,
                status: {
                    success: true
                }
            };

            //$scope.movimento.documentos.push(doc_recebido);

            for (var key in doc_recebido) {
                enviado[key] = doc_recebido[key];
            }

        }

        function falhou(enviado, recebido) {
            console.log('falhou enviar dados');

        }

        $scope.documento.tipo_anexo_str = $scope.tipos_anexo[$scope.documento.tipo_anexo];
        if($scope.documento.anexo){
            $scope.documento.anexo_str = $scope.documento.anexo.name;
        }

        $scope.movimento.documentos.push($scope.documento);
        fileUpload.upload(form_action, $scope.documento, $scope.documento.status, success, falhou);

        $scope.modo_anterior = $scope.documento.modo;
        $("#id_anexo").val('');
        $scope.documento = null;
        $scope.novo_arquivo($scope.modo_anterior);
    };

    $scope.verificar_itens_nao_salvos = function () {
        var item_nao_salvo = false;

        if (!$scope.clicou_btn_salvar || !$scope.clicou_btn_cancelar) {
            for (var i = 0; i < $scope.movimento.documentos.length; i++) {

                if ($scope.movimento.documentos[i].novo_doc) {
                    item_nao_salvo = true;
                }
            }
            if ($scope.jquery_form_novo_movimento.find('.dirty').length > 0) {
                item_nao_salvo = true;
            }
        }
        return item_nao_salvo;
    };

    $scope.register_windows_page_events = function () {
        //executado antes do mudar/sair/fecha a pagina
        var antes_de_sair_da_pagina = function (evt) {

            var msg_nao_salvo = "O documento possui modificações e ainda não foi salvo. Clique em Salvar Movimento.";

            evt.preventDefault();
            $scope.clicou_btn_salvar = false;
            $scope.clicou_btn_cancelar = false;
            //console.log('Antes de sair');
            if ($scope.verificar_itens_nao_salvos()) {
                //console.log('executando_exit');
                $scope.mostrar_modal = true;
                evt.returnValue = msg_nao_salvo;
                return msg_nao_salvo;
            }

        };
        //console.log('registrando evento de saida');
        if (window.addEventListener) {
            //evento executado ao sair da pagina/fechar a pagina ou janela
            window.addEventListener('beforeunload', antes_de_sair_da_pagina, false);
        }
        else {
            window.attachEvent('onbeforeunload', antes_de_sair_da_pagina);
        }

    };

}
