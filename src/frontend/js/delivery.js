$(function() {
    // Javascript of the delivery application
    // ****************************************

    $('.ui.dropdown.maindish.selection').dropdown('setting', 'onChange', function(value, text, $selectedItem) {
        $url = $(".field.dish.selection").data('url');
        window.location.replace($url+value);
    });

    $('.button.orders').click(function(){
        $('.button.orders i').addClass('loading');
        $.ajax({
            type: 'GET',
            url: $(this).attr('data-url'),
            success: function (xhr, ajaxOptions, thrownError) {
                $("#generated-orders").html(xhr)
                var count = $("#generated-orders tbody tr").length;
                $('.orders-count span').html(count);
                $('.orders-count').attr('data-order-count', count);
                $('.button.orders i').removeClass('loading');
            },
        });
    });

    $('.ui.order.cancel.button').click(function () {
        var self = this;
        var modalCtntURL = $(self).attr('data-url');
        $.get(modalCtntURL, {status:'C'}, function(data, modalCtntURL){
            $('.ui.modal.status').html(data).modal("setting", {
                closable: false,
                // When approving modal, submit form
                onApprove: function($element, modalCtntURL) {
                    var data = $('#change-status-form').serializeArray();

                    $.ajax({
                         type: 'POST',
                         url: $(self).attr('data-url'),
                         data: data,
                         success: function (xhr, ajaxOptions, thrownError) {
                             if ( $(xhr).find('.errorlist').length > 0 ) {
                                 $('.ui.modal.status').html(xhr);
                             } else {
                                 $('.ui.modal.status').modal("hide");
                                 location.reload();
                             }
                         },
                     });
                    return false; // don't hide modal until we have the response
                },
                // When denying modal, restore default value for status dropdown
                onDeny: function($element) {
                    $('.ui.modal.status').modal("hide");
                }
            }).modal('setting', 'autofocus', false).modal("show");
        });
    });

    $('input[name=include_a_bill]').change(function () {
        var self = this;
        var url = $(self).data('url');
        var checked = $(self).is(':checked');
        $.ajax({
            type: (checked) ? 'POST' : 'DELETE',
            url: url,
            success: function (xhr, ajaxOptions, thrownError) {
                $(self).removeAttr('disabled');
            }
        });
        $(self).attr('disabled', 'disabled');
    });
});
