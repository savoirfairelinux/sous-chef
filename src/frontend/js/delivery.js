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
});
