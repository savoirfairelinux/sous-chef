$(function() {

    // Javascript of the order application.
    // **************************************

    var $overrideModal = $('.ui.order-override.modal');

    $('#form_create_batch').submit(function(event) {
      if(event.originalEvent && $('#id_is_submit').val() === '1') {
        var originalTarget = $(event.originalEvent.explicitOriginalTarget);
        var deliveryDates = ($('#id_delivery_dates').val() || '').split('|');
        var overrideDates = ($('#id_override_dates').val() || '').split('|');
        if(originalTarget.attr('id') === 'original-form-submit' &&
           $overrideModal.length && !arraysEqual(deliveryDates, overrideDates)) {
          event.preventDefault();
          $overrideModal.modal('show');
        }
      }
    });

    $('.order-override.cancel.button').click(function() {
      var deliveryDates = ($('#id_delivery_dates').val() || '').split('|');
      var datesToRemove = $overrideModal.data('orderDates').split('|');
      var newDeliveryDates = deliveryDates.filter(function(i) {
        return datesToRemove.indexOf(i) === -1;
      });

      $('#id_delivery_dates').val(newDeliveryDates.join('|'));
      $('#form_create_batch #id_is_submit').val("0");
      $('#form_create_batch').submit();
    });

    $('.order-override.override.button').click(function() {
      $('#id_override_dates').val($('#id_delivery_dates').val());
      $('#form_create_batch #id_is_submit').val("1");
      $('#form_create_batch').submit();
    });

    $('.order-delete').click(function(){
        var order_id = $(this).data('orderId');
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

    function arraysEqual(a, b) {
        var sortA = a.map(function(i) { return !!i; }).sort();
        var sortB = b.map(function(i) { return !!i; }).sort();
        for (var i = 0; i < a.length; ++i) {
          if (a[i] !== b[i]) {
            return false;
          }
        }
        return true;
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
                // When approving modal, submit form
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
});
