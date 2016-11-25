$(function() {
    // Javascript of the delivery application
    // ****************************************

    $('.ui.dropdown.maindish.selection').dropdown('setting', 'onChange', function(value, text, $selectedItem) {
        $url = $(".field.dish.selection").data('url');
        window.location.replace($url+value);
    });

    $('.button.orders').click(function(){
        $('.button.orders i').addClass('loading');
        var url = $(this).attr('data-url');
        $.get(url, function( data ) {
            window.location.reload();
        });
    });

});
