function buscar_cep(cep, prefix)
{
	cep = cep.replace(/\D/g,'');
	$.get('/endereco/get_by_cep/'+cep, function(data){
		if(!data.erro)
		{
			$('#id_'+prefix+'estado').val(data.estado_id);
			$('#id_'+prefix+'municipio').val(data.municipio_id);
			$('#id_'+prefix+'bairro_nome').val(data.bairro);
			$('#id_'+prefix+'logradouro').val(data.logradouro);
		}
	},'json');
}

function listar_municipios(estado_id, obj)
{
	$.get('/estado/'+estado_id+'/municipios/', function(data){
		$(obj).html(json_to_options(data));
	}, 'json');
}

function json_to_options(options)
{
	var result = '';
	$(options).each(function(){
		result += '<option value="' + this.id + '">' + this.nome + '</option>';
	});
	return result;
}

(function($)
{
    $(document).ready(function()
    {
        var modal_confirm_delete = $('#modal-confirm-delete');

        $(document).on('submit', 'form[data-is-ajax]', function(e)
        {
            e.preventDefault();

            var form = $(this);
            form.find('button[type=submit]').button('loading');

            $.ajax({
                url: form.attr('action'),
                type: "POST",
                data: form.serialize() + '&csrfmiddlewaretoken='+ $('[name=csrfmiddlewaretoken]').val(),
                dataType: "json",
                success: function(json)
                {
                    form.find('.control-group.error').removeClass('error');
                    form.find('.help-inline').addClass('hide').html('');

                    if( json.success )
                    {
                        if( form.attr('data-inside-modal') !== undefined )
                            form.parents('.modal').modal('hide');

                        if( form.attr('data-callback-success') )
                        {
                            var metodo = angular.element($('#modal-atividade form').parents('[ng-controller]').first()).scope()[form.attr('data-callback-success')];
                            if( metodo !== undefined )
                                metodo(json);
                        }
                    }
                    else
                    {
                        for(var field_name in json.errors)
                        {
                            var field = form.find('[name='+ field_name +']');
                            field.parents('.control-group').addClass('error');
                            field.siblings('.help-inline').removeClass('hide').html(json.errors[field_name].join('<br/>'));
                        }
                    }

                    form.find('button[type=submit]').button('reset');
                }
            });
        });

        $(document).on('click', '.modal-confirm-delete', function(e)
        {
            e.preventDefault();

            var clicked = $(this);

            if( modal_confirm_delete.length )
            {
                modal_confirm_delete.data('callback', clicked.data('callback'));
                modal_confirm_delete.data('id', clicked.data('id'));

                var title = clicked.data('title') || 'Excluir';
                modal_confirm_delete.find('.modal-header .title').html(title);

                var message = clicked.data('message') || 'Tem certeza que deseja excluir o registro selecionado?';
                modal_confirm_delete.find('.modal-body').html(message);

                modal_confirm_delete.modal('show');
            }
        });

        $(document).on('click', '#confirm-delete', function ()
        {
            var metodo = angular.element($(this).parents('[ng-controller]').first()).scope()[modal_confirm_delete.data('callback')];
            if( metodo !== undefined )
                metodo(modal_confirm_delete.data('id'));

            modal_confirm_delete.modal('hide');
        });

        $(document).on('focus', '.datepicker:not(.hasDatepicker)', function()
        {
            $(this).datepicker().addClass('hasDatepicker');
        });

        $(document).on('change', 'select[data-child]', function()
        {
            var value = $(this).val();
            var child = $($(this).data('child'));

            child.prop('disabled', true).find("option").not('[value=]').hide();

            if(value)
            {
                var options = child.find('option[data-parent-id="'+ value +'"]');
                if(options.length)
                    child.prop('disabled', false);
                    options.show()
            };
        });
    });
})
(jQuery);
