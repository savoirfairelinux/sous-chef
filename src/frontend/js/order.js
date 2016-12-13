$(function() {

    // Javascript of the order application.
    // **************************************

    $('.order-delete').click(function(){
        var order_id = $(this).attr('data-order-id');
        var selector = '.ui.basic.modal.order-' + order_id;
        $(selector).modal('show');
    });

    function updateOtherFieldStatus() {
        var value = $('input[name=reason_select]:checked', '#change-status-form').val();
        if (value !== 'other') {
            $('#reason_other_field textarea').attr('disabled', 'disabled');
        } else {
            $('#reason_other_field textarea').removeAttr('disabled');
        }
    }

    function addReasonSelectListener() {
        $('#reason_select_group input').on('change', updateOtherFieldStatus);
    }

    $('.ui.dropdown.order.status .menu > .item').click(function () {
        $('.ui.dropdown.order.status').addClass('loading');
        var value = $(this).data('value');
        var modalCtntURL = $('.ui.dropdown.status').attr('data-url');
        $.get(modalCtntURL, {status:value}, function(data, modalCtntURL){
            $('.ui.dropdown.order.status').removeClass('loading');
            $('.ui.modal.status').html(data).modal("setting", {
                closable: false,
                // Inside modal init
                onVisible: function () {
                    // Enable dropdown
                    $('.ui.status_to.dropdown').dropdown();
                    addReasonSelectListener();
                    updateOtherFieldStatus();
                },
                // When approvind modal, submit form
                onApprove: function($element, modalCtntURL) {
                    var origdata = $('#change-status-form').serializeArray();
                    var origdata_o = {};
                    $.each(origdata, function (idx, ele) {
                        origdata_o[ele.name] = ele.value;  // build object
                    });
                    if (origdata_o.reason_select !== 'other') {
                        origdata_o.reason = origdata_o.reason_select;
                    }
                    delete origdata_o.reason_select;
                    var data = $.param(origdata_o);

                    $.ajax({
                         type: 'POST',
                         url: $('.ui.dropdown.status').attr('data-url'),
                         data: data,
                         success: function (xhr, ajaxOptions, thrownError) {
                             if ( $(xhr).find('.errorlist').length > 0 ) {
                                 $('.ui.modal.status').html(xhr);
                                 $('.ui.status_to.dropdown').dropdown();
                                 addReasonSelectListener();
                                 updateOtherFieldStatus();
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
                    $('.ui.dropdown.status').dropdown('restore defaults');
                    $('.ui.modal.status').modal("hide");
                }
            }).modal('setting', 'autofocus', false).modal("show");
        });
    });

    $('#id_delivery_dates').hide();

    $('#id_client').change(function() {
        $.get($(this).attr('data-url'), function(data) {
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

});
