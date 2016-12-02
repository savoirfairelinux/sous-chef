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
        $.getJSON(url, function( data ) {
            $.each(data, function(key, value) {
                var id = '<td class="center aligned"><strong><i class="hashtag icon"></i>' + value.id + '</strong></td>';
                var name = '<td><a href="' + value.client_url + '">' + value.client_name +'</a><div class="ui label">new</div></td>';
                var date = '<td>' + value.delivery_date + '</td>';
                var route = '<td>' + value.route + '</td>';
                var status = '<td class="center aligned">' + value.status + '</td>';
                var price = '<td class="center aligned"><i class="dollar icon"></i>' + value.price + '</td>';
                var actions = '<td><a class="ui basic icon button" href="' + value.order_view_url + '"><i class="icon unhide"></i></a><a class="ui basic icon button" href="' + value.order_update_url + '"><i class="icon edit"></i></a><a class="ui basic icon button order-delete" href="#" data-order-id="' + value.id + '"><i class="icon trash"></i></a></td>';
                $('tbody').append('<tr>' + id + name + date + route + status + price + actions + '</tr>');
            });
            // Get the number of orders, to be able to add the newly created orders
            var count = parseInt($('.orders-count').attr('data-order-count'));
            count += data.length;
            $('.orders-count span').html(count);
            $('.orders-count').attr('data-order-count', count);

            $('.button.orders i').removeClass('loading');
        });
    });
});
