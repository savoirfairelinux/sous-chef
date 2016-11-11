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

    $('#id_delivery_dates').hide();

    $('#id_client').change(function() {
        $.get('/member/client/' + $(this).val() + '/meals/preferences', function(data) {
            if (!$.isEmptyObject(data)) {
                $('#id_main_dish_default_quantity').val(data['maindish_q']);
                $('#id_size_default').dropdown('set selected', data['maindish_s']);
                $('#id_dessert_default_quantity').val(data['dst_q']);
                $('#id_diabetic_default_quantity').val(data['diabdst_q']);
                $('#id_fruit_salad_default_quantity').val(data['fruitsld_q']);
                $('#id_green_salad_default_quantity').val(data['greensld_q']);
                $('#id_pudding_default_quantity').val(data['pudding_q']);
                $('#id_compote_default_quantity').val(data['compot_q']);
            }
            else {
                $('#id_main_dish_default_quantity').val('');
                $('#id_size_default').val('');
                $('#id_dessert_default_quantity').val('');
                $('#id_diabetic_default_quantity').val('');
                $('#id_fruit_salad_default_quantity').val('');
                $('#id_green_salad_default_quantity').val('');
                $('#id_pudding_default_quantity').val('');
                $('#id_compote_default_quantity').val('');
            }
        });
    });
    // --
});
