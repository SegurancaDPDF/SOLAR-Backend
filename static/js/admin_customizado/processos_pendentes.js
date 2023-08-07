(function ($) {
    $(document).ready(function () {
        let btn_pendentes = $(".consultar_pendentes");
        let url = btn_pendentes.attr("data-url");
        let target_element = btn_pendentes.attr("data-target");
        let atualizar = function () {
            btn_pendentes.attr("disabled", true);
            $.getJSON(url, function (data, status, xhr) {
                $(target_element).val(JSON.stringify(data, null, 1));
                btn_pendentes.attr("disabled", false);
            });
        };
        btn_pendentes.on("click", function (e) {
            atualizar();
        });
        setInterval(function () {
            let ativo = $("#atualizacao_automatica").is(":checked");
            if (ativo) {
                atualizar();
            }
        }, 2000);
    });
})(django.jQuery);
