$(function() {

    // Javascript of the order application.
    // **************************************

    $('.order-delete').click(function(){
        var order_id = $(this).attr('data-order-id');
        var selector = '.ui.basic.modal.order-' + order_id;
        $(selector).modal('show');
    });

    $('.ui.dropdown.order.status .menu > .item').click(function () {
        $('.ui.dropdown.order.status').addClass('loading');
        $.ajax({
            url: $('.ui.dropdown.order.status').attr('data-url'),
            type: "POST",
            data: {
                'status': $(this).data('value'),
                'csrfmiddlewaretoken': $('.ui.dropdown.order.status').attr('data-csrf-token'),
            },
            success: function(response) {
                $('.ui.dropdown.order.status').removeClass('loading');
            }
        });
    });
});
