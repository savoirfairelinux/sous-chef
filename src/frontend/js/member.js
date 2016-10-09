$(function() {

    // Javascript of the member application.
    // **************************************

    $('.ui.dropdown.member.status > .menu > .item').click(function () {
        var value = $(this).data('value');
        var today = new Date();
        var modalCtntURL = $('.ui.dropdown.status').attr('data-url');
        $.get(modalCtntURL, {status:value}, function(data, modalCtntURL){
            $('.ui.modal.status').html(data).modal("setting", {
                closable: false,
                // Inside modal init
                onVisible: function () {
                    // Enable status confirmation dropdown
                    $('.ui.status_to.dropdown').dropdown();
                    // Init dates field (start and end)
                    $('#rangestart').calendar({
                        type: 'date',
                        on: 'click',
                        minDate: new Date(
                            today.getFullYear(),
                            today.getMonth(),
                            today.getDate()),
                        formatter: {
                            date: function (date, settings) {
                                if (!date) return '';
                                var day = date.getDate();
                                var month = date.getMonth() + 1;
                                var year = date.getFullYear();
                                if (month < 10) month = '0' + month;
                                if (day < 10) day = '0' + day;
                                return year + '-' + month + '-' + day;
                            }
                        },
                        endCalendar: $('#rangeend'),
                    });
                    $('#rangeend').calendar({
                        type: 'date',
                        formatter: {
                            date: function (date, settings) {
                                if (!date) return '';
                                var day = date.getDate();
                                var month = date.getMonth() + 1;
                                var year = date.getFullYear();
                                if (month < 10) month = '0' + month;
                                if (day < 10) day = '0' + day;
                                return year + '-' + month + '-' + day;
                            }
                        },
                        startCalendar: $('#rangestart'),
                    });
                },
                // When approvind modal, submit form
                onApprove: function($element, modalCtntURL) {
                    $.ajax({
                         type: 'POST',
                         url: $('.ui.dropdown.status').attr('data-url'),
                         data: $('#change-status-form').serialize(),
                         success: function (xhr, ajaxOptions, thrownError) {
                             if ( $(xhr).find('.errorlist').length > 0 ) {
                                 $('.ui.modal.status').html(xhr);
                                 console.log('show modal..')
                                 $('.ui.modal.status').modal("show");
                             } else {
                                 location.reload();
                             }
                         },
                     });
                },
                // When denying modal, restore default value for status dropdown
                onDeny: function($element) {
                    $('.ui.dropdown.status').dropdown('restore defaults');
                }
            }).modal("show");
        });
    });

    if($('#dietary_restriction-delivery_type select').val() == 'E') {
        $('#form-meals-schedule').hide();
        hideUiAccordionDays();
    } else {
        $('#form-meals-schedule').show();
        showUiAccordionSelectedDays();
    }

    $('#dietary_restriction-delivery_type .dropdown').dropdown(
        'setting', 'onChange', function(value, text, $selectedItem) {
            if($selectedItem.data('value') == 'E') {
                $('#form-meals-schedule').hide();
                hideUiAccordionDays();
            } else {
                $('#form-meals-schedule').show();
                showUiAccordionSelectedDays();
            }
        }
    );

    var same_as_client = $('#id_payment_information-same_as_client');
    // Initial state
    if (same_as_client && same_as_client.checked) {
        $('#billing_select_member').hide();
    }
    $("#id_payment_information-same_as_client").on("change", function() {
        if (this.checked) {
            $('#billing_select_member').hide();
        } else {
            $('#billing_select_member').show();
        }
    });

    $('.ui.button.add.member').on('click', function() {
        $('.existing--member').val('').attr('disabled', 'disabled');
        $(this).transition('scale');
        $('.ui.add.form.member').transition('scale');
    });

    $('.ui.button.cancel.add.member').on('click', function() {
        $('.ui.button.add.member').transition('scale');
        $('.existing--member').removeAttr('disabled');
    });

    if( $('.firstname').val() !== '' || $('.lastname').val() !== ''
        && $('.existing--member').val() === '' ) {
        $('.ui.button.add.member').transition('scale');
        $('.existing--member').attr('disabled', 'disabled');
        $('.ui.add.form.member').transition('scale');
    }

    $search_url = $('.ui.search').attr('data-url')
    $('.ui.search').search({
        apiSettings: {
            cache : 'local',
            url: $search_url + '?name={query}',
        },
        minCharacters : 3,
    });

    function showOneAccordionElement(element, index, array) {
        selector = '.ui.accordion.meals.' + element;
        $(selector).show();
    }
    function showUiAccordionSelectedDays() {
        var $selected = $("#form-meals-schedule select[multiple='multiple']").val();
        if ($selected) {
          $selected.forEach(showOneAccordionElement);
        }
    }
    function hideUiAccordionDays() {
        $('.ui.accordion.meals').each(function () {
          $(this).hide();
        });
    }

    $("#form-meals-schedule select[multiple='multiple']").change(function () {
        hideUiAccordionDays();
        showUiAccordionSelectedDays();
    });
    hideUiAccordionDays();
    showUiAccordionSelectedDays();

});
