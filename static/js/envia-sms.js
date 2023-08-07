function removeCaracteresEspeciais(texto) {
    var caracteresNaoEspeciais = [" ","(","0","8","@","H","P","X","`","h","p","x","!",")","1","9","A","I","Q","Y","a","i","q","y","“","*","2",":","B","J","R","Z","b","j","r","z","#","+","3",";","C","K","S","{","c","k","s","~","$",",","4","<","D","L","T","\\","d","l","t","%","-","5","=","E","M","U","}","e","m","u","&",".","6",">","F","N","V","^","f","n","v","‘","/","7","?","G","O","W","_","g","o","w", "\n"];
    for (var i = 0; i < texto.length; i++) {
        if(!caracteresNaoEspeciais.includes(texto.charAt(i))){
            texto = texto.slice(0, i) + texto.slice(i+1);
        }
    }
    return texto;
}

$( document ).ajaxComplete(function() {

    var historico = $('#modal-anotacao [name="historico"]');
    var qualificacao = $('#modal-anotacao [name="qualificacao"]');

    if(historico.length > 0){
        if($('#remover-acentos').val() == 'true'){

            normaliza_sms = function(){
                qualificacao_text = qualificacao.find(':selected').text();
                if(qualificacao_text.toLowerCase() == 'sms'){
                    if($('#usar-sms').val() == 'false'){
                        alert("Atenção, o envio de SMS está desabilitado no sistema. \n"+
                        "Entre em contato com o administrador para mais informações.");
                    }
                    old_value = historico.val();
                    new_value = removeCaracteresEspeciais(old_value.normalize("NFD").replace(/[\u0300-\u036f]/g, ""));
                    if(new_value != old_value){
                        alert("Atenção, os acentos e caracteres especiais não podem ser utilizados.")
                    }
                    historico.val(new_value); // stackoverflow.com/questions/990904
                }
            }

            historico.on('keyup', normaliza_sms);
            qualificacao.on('click', normaliza_sms);
        }
    }
});
