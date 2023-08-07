class Utils{

    static gerarDV(numero, posicao)
    {

        let soma = 0;
        let multiplicador = 3 - posicao;

        for(i = 0; i < numero.length; i++){
            soma += numero[i] * multiplicador;
            multiplicador += 1;
            if(multiplicador==11)
            {
                multiplicador = 0;
            }
        }

        let resultado = soma % 11;
        resultado = resultado == 10 ? 1 : resultado;
        return resultado;

    }

    static gerarDV2(numero)
    {
        let d1 = Utils.gerarDV(numero, 1);
        let d2 = Utils.gerarDV(numero.concat(d1), 2);
        return `${d1}${d2}`;
    }

    static validarCertidao(matricula){
        // http://ghiorzi.org/DVnew.htm#zc

        matricula = matricula.replace(/[^\d]+/g,'');

        if (matricula.length != 32)
            return false;

        // Elimina números inválidos conhecidos
        if (matricula == "00000000000000000000000000000000" || 
            matricula == "11111111111111111111111111111111" || 
            matricula == "22222222222222222222222222222222" || 
            matricula == "33333333333333333333333333333333" || 
            matricula == "44444444444444444444444444444444" || 
            matricula == "55555555555555555555555555555555" || 
            matricula == "66666666666666666666666666666666" || 
            matricula == "77777777777777777777777777777777" || 
            matricula == "88888888888888888888888888888888" || 
            matricula == "99999999999999999999999999999999")
            return false;
             

        if (Utils.gerarDV(matricula.substring(0, 30), 1) != matricula.charAt(30))
            return false;

        if (Utils.gerarDV(matricula.substring(0, 31), 2) != matricula.charAt(31))
            return false;

        return true;

    }

    //https://www.geradorcnpj.com/javascript-validar-cnpj.htm
    static validarCNPJ(cnpj){
        let tamanho;
        let digitos;
        let soma;
        let pos;
        let numeros;
        let resultado;
        cnpj = cnpj.replace(/[^\d]+/g,'');
 
        if(cnpj == '') return false;
         
        if (cnpj.length != 14)
            return false;
     
        // Elimina CNPJs invalidos conhecidos
        if (cnpj == "00000000000000" || 
            cnpj == "11111111111111" || 
            cnpj == "22222222222222" || 
            cnpj == "33333333333333" || 
            cnpj == "44444444444444" || 
            cnpj == "55555555555555" || 
            cnpj == "66666666666666" || 
            cnpj == "77777777777777" || 
            cnpj == "88888888888888" || 
            cnpj == "99999999999999")
            return false;
             
        // Valida DVs
        tamanho = cnpj.length - 2
        numeros = cnpj.substring(0,tamanho);
        digitos = cnpj.substring(tamanho);
        soma = 0;
        pos = tamanho - 7;
        for (i = tamanho; i >= 1; i--) {
          soma += numeros.charAt(tamanho - i) * pos--;
          if (pos < 2)
                pos = 9;
        }
        resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
        if (resultado != digitos.charAt(0))
            return false;
             
        tamanho = tamanho + 1;
        numeros = cnpj.substring(0,tamanho);
        soma = 0;
        pos = tamanho - 7;
        for (i = tamanho; i >= 1; i--) {
          soma += numeros.charAt(tamanho - i) * pos--;
          if (pos < 2)
                pos = 9;
        }
        resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
        if (resultado != digitos.charAt(1))
              return false;
               
        return true;
    }
    //https://www.geradorcpf.com/javascript-validar-cpf.htm
    static validarCPF(cpf) {
        let add;
        let rev;	
        cpf = cpf.replace(/[^\d]+/g,'');	
        if(cpf == '') return false;	
        // Elimina CPFs invalidos conhecidos	
        if (cpf.length != 11 || 
            cpf == "00000000000" || 
            cpf == "11111111111" || 
            cpf == "22222222222" || 
            cpf == "33333333333" || 
            cpf == "44444444444" || 
            cpf == "55555555555" || 
            cpf == "66666666666" || 
            cpf == "77777777777" || 
            cpf == "88888888888" || 
            cpf == "99999999999")
                return false;		
        // Valida 1o digito	
        add = 0;	
        for (i=0; i < 9; i ++)		
            add += parseInt(cpf.charAt(i)) * (10 - i);	
            rev = 11 - (add % 11);	
            if (rev == 10 || rev == 11)		
                rev = 0;	
            if (rev != parseInt(cpf.charAt(9)))		
                return false;		
        // Valida 2o digito	
        add = 0;	
        for (i = 0; i < 10; i ++)		
            add += parseInt(cpf.charAt(i)) * (11 - i);	
        rev = 11 - (add % 11);	
        if (rev == 10 || rev == 11)	
            rev = 0;	
        if (rev != parseInt(cpf.charAt(10)))
            return false;		
        return true;   
    }
}

angular.module("SisatApp").directive('cpfCnpjValidator',function(){
    return {
        require: "ngModel",
        link: function(scope, element, attrs, ctrl){
            ctrl.$parsers.unshift(function (viewValue) {
                let value = viewValue.replace(/[^\d]+/g,'');
                let valid = false;
                if(value.length == 0){
                    valid = true;
                }
                else if(value.length == 11){
                    valid = Utils.validarCPF(value);
                }else {
                    valid = Utils.validarCNPJ(value);  
                }
                if(!valid){
                    element[0].style.background = "#F2DEDE";
                    element[0].style.borderColor = "#B94A48";
                }else if(valid && value.length != 0){
                    element[0].style.background = "white";
                    element[0].style.border = "1px solid #cccccc";
                }
                ctrl.$setValidity("cpfCnpjValidator",valid);
                return viewValue;
            });
        }
    }
});

angular.module("SisatApp").directive('certidaoValidator',function(){
    return {
        require: "ngModel",
        link: function(scope, element, attrs, ctrl){
            ctrl.$parsers.unshift(function (viewValue) {
                let value = viewValue.replace(/[^\d]+/g,'');
                let valid = false;
                if(value.length == 0){
                    valid = true;
                }else {
                    valid = Utils.validarCertidao(value);  
                }
                if(!valid){
                    element[0].style.background = "#F2DEDE";
                    element[0].style.borderColor = "#B94A48";
                }else if(valid && value.length != 0){
                    element[0].style.background = "white";
                    element[0].style.border = "1px solid #cccccc";
                }
                ctrl.$setValidity("certidaoValidator",valid);
                return viewValue;
            });
        }
    }
});
