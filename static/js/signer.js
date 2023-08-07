class AssinadorError extends Error{

    constructor(message){

        super(message);
        this.name = 'AssinadorError';
        this.message = message;

    }

}

class SolarAPIError extends Error{

    constructor(message){

        super(message);
        this.name = 'SolarAPIError';
        this.message = message;

    }

}

class SignerDOM{
        //obrigado!!! https://stackoverflow.com/questions/494143/creating-a-new-dom-element-from-an-html-string-using-built-in-dom-methods-or-pro
        static createElementFromHTML(htmlString) {
            var div = document.createElement('div');
            div.innerHTML = htmlString.trim();
            return div.firstChild; 
          }
    
        static ocultarElementos(container){
            document.querySelector(container).childNodes.forEach((element => {
                if(element.style) element.style.display = "none";
            }));
        }
    
        static inserirElemento(container, elemento){
            document.querySelector(container).appendChild(SignerDOM.createElementFromHTML(elemento));
        }
}


class SignerAPI {

    constructor() {
        this.URLBASE = `${location.origin}/api/v1/manifestacao_processual/${location.pathname.split('/')[3]}/documentos/?incluir_conteudo_em_base64=true`;
        this.URLASSINADOR = `${window.URL_DO_ASSINADOR}:${window.PORTA_DO_ASSINADOR}/sign`;
        this.DEBUG = false;
        this.ICONE_ERROR = '<div class="swal2-icon swal2-error swal2-animate-error-icon" style="display: flex;"><span class="swal2-x-mark"><span class="swal2-x-mark-line-left"></span><span class="swal2-x-mark-line-right"></span></span></div>';
        this.ICONE_SUCESSO = '<div class="swal2-icon swal2-success swal2-animate-success-icon" style="display: flex;"><div class="swal2-success-circular-line-left" style="background-color: rgb(255, 255, 255);"></div><span class="swal2-success-line-tip"></span><span class="swal2-success-line-long"></span><div class="swal2-success-ring"></div><div class="swal2-success-fix" style="background-color: rgb(255, 255, 255);"></div><div class="swal2-success-circular-line-right" style="background-color: rgb(255, 255, 255);"></div></div>';
        this.headers = new Headers({ 'Content-type': 'application/json; charset=UTF-8', 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value });
    }

    assinarDocumentos() {

        SignerDOM.ocultarElementos("#modal-manifestacao-confirmar .modal-body");     

        SignerDOM.inserirElemento("#modal-manifestacao-confirmar .modal-body", '<div class="containerassinador"><div class="lds-ripple"><div></div><div></div></div><p class="alert alert-info" style="margin-top: 20px; text-align: center">Informe a senha do seu token quando solicitado</p></div>');
        
        document.querySelector("#modal-manifestacao-confirmar .modal-header h3").innerHTML="<i class='fa fa-file-signature'></i> Assinando Documentos";

        this.obterDocumentosembase64daManifestacaoProcessualViaAPI()
            .then(documentos => documentos.results)
            .then(async documentos => {
                for(const documento of documentos){
                    if (documento.ja_foi_assinado) continue;
                    await this.enviarParaAssinador(documento.conteudo_em_base64)
                        .then(res => this.enviarDocumentoAssinadoParaSolar(res, documento.id));
                }
            }).then(res => {
                SignerDOM.ocultarElementos(".containerassinador");
                SignerDOM.inserirElemento(".containerassinador", this.ICONE_SUCESSO);
            })
            .then(res => document.querySelector("#btnpeticionar").form.submit());

    }

    async obterDocumentosembase64daManifestacaoProcessualViaAPI() {
        try {
            const response = await fetch(this.URLBASE, new Request({
                method: 'GET',
                headers: this.header
            }));

            const respostadosolaremjson = await response.json();
            return respostadosolaremjson;

        } catch (error) {
            throw new SolarAPIError(`Não foi possível obter os documentos da API do SOLAR: ${error.message}`); 
        }
    }

    async enviarParaAssinador(documentosembase64) {
        try {
            if (this.DEBUG) console.log(`Enviando Documento para Assinador: ${documentosembase64}`);
            const response = await fetch(this.URLASSINADOR,
                {
                    method: 'POST',
                    headers: this.headers,
                    body: JSON.stringify({ 'content': documentosembase64 })
                }
            );
    
            const respostadoassinadoremjson = await response.json();
            return respostadoassinadoremjson; 
        } catch (error) {
            SignerDOM.ocultarElementos(".containerassinador");
            SignerDOM.inserirElemento(".containerassinador", this.ICONE_ERROR);
            SignerDOM.inserirElemento(".containerassinador", '<p class="alert alert-error" style="margin-top: 20px; text-align: center">Falha ao fazer comunicação com assinador de documentos, por favor entre em contato com suporte</p>');
            document.querySelector("#btnpeticionar").innerHTML = '<i class="fa fa-university"></i> Tentar Novamente';
            document.querySelector("#btnpeticionar").class="btn btn-warning";
            document.querySelector("#btnpeticionar").disabled = false;
            throw new AssinadorError(`Não foi possível enviar ou receber documentos do assinador: ${error.message}`)
        }
    }

    async enviarDocumentoAssinadoParaSolar(documentoassinado, iddocumento) {
        try {
            if (this.DEBUG) console.log(`Devolvendo Documento Para SOLAR já Assinado: ${documentoassinado.signedContent}`);
            const response = await fetch(`${this.URLBASE}/${iddocumento}`, {
                method: 'PATCH',
                headers: this.headers,
                body: JSON.stringify({
                    'documento_assinado': documentoassinado.signedContent
                })
            });
            const respostadosolaremjson = await response.json();
            return respostadosolaremjson;
        } catch (error) {
            SignerDOM.ocultarElementos(".containerassinador");
            SignerDOM.inserirElemento(".containerassinador", this.ICONE_ERROR);
            SignerDOM.inserirElemento(".containerassinador", '<p class="alert alert-error" style="margin-top: 20px; text-align: center">Falha ao fazer comunicação com SOLAR, por favor entre em contato com suporte</p>');
            document.querySelector("#btnpeticionar").innerHTML = '<i class="fa fa-university"></i> Tentar Novamente';
            document.querySelector("#btnpeticionar").class="btn btn-warning";
            document.querySelector("#btnpeticionar").disabled = false;
            throw new SolarAPIError(`Não foi possível enviar os documentos assinados para o SOLAR: ${error.message}`);
        }
    }
}

if(document.querySelector("#btnpeticionar")){
    document.querySelector("#btnpeticionar").addEventListener("click", function (event) {
        //Desabilita botão Peticionar para evitar multiplos clicks pelo usuário
        this.disabled = true;    
        event.preventDefault();
        new SignerAPI().assinarDocumentos();
    });
}

