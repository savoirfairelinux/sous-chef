$(function() {
    // Javascript of the billing application
    // ****************************************

    $('.billing-delete').click(function(){
        var billing_id = $(this).attr('data-billing-id');
        var selector = '.ui.basic.modal.billing-' + billing_id;
        $(selector).modal('show');
    });

    $('#billing_delivery_date').calendar({
        type: 'month',
        formatter: {
            date: function (date, settings) {
                return date ? dateFormat(date, 'yyyy-mm') : '';
            }
        }
    });

    $('.add.icon').popup();

    $("#create_billing").click(function(e){
        $(".ui.dimmer").show();
    });
});
