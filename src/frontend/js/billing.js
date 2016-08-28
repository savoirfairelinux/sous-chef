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
                if (!date) return '';
                var month = date.getMonth() + 1;
                var year = date.getFullYear();
                if (month < 10) month = '0' + month;
                return year + '-' + month ;
            }
        }
    });

    $('.add.icon').popup();
});