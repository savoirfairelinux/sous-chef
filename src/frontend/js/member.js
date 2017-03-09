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
                                 $('.ui.status_to.dropdown').dropdown();
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

    if($('#dietary_restriction-delivery_type select').val() == 'E') {
        $('#form-meals-schedule').hide();
        showAllAccordionElements();
    } else {
        $('#form-meals-schedule').show();
        hideUiAccordionDays();
        showUiAccordionSelectedDays();
    }

    $('#dietary_restriction-delivery_type .dropdown').dropdown(
        'setting', 'onChange', function(value, text, $selectedItem) {
            if($selectedItem.data('value') == 'E') {
                $('#form-meals-schedule').hide();
                showAllAccordionElements();
            } else {
                $('#form-meals-schedule').show();
                hideUiAccordionDays();
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

    var body = $('body');
    body.delegate('.ui.button.add.member', 'click', function() {
        var $this = $(this),
            commonParent = $(this).closest('div.ui.segment');
        $this.transition('scale');
        commonParent.find('.ui.add.form.member').transition('scale');
        commonParent.find('.existing--member').val('').attr('disabled', 'disabled');
    });

    body.delegate('.ui.button.cancel.add.member', 'click', function() {
        var commonParent = $(this).closest('div.ui.segment');
        commonParent.find('.ui.button.add.member').not('cancel').transition('scale');
        commonParent.find('.existing--member').removeAttr('disabled');
    });

    // Emergency contact formset
    var formsetContainer = $('form.ui.form div.formset-container'),
        formsetItems = $('form.ui.form div.formset-item'),
        $search_url = $('.ui.search .ui.input').first().attr('data-url'),
        initMemberQuickSearch = function (selector) {
            selector.search({
                apiSettings: {
                    cache : false,
                    url: $search_url + '?name={query}',
                },
                minCharacters : 3,
                maxResults : 10
            });
        };

    if (formsetItems.length > 0) {
        formsetItems.formset({
            'prefix': 'emergency_contacts',
            'addText': '<i class="plus icon"></i> ' + formsetContainer.data('addLabel'),
            'deleteText': '<i class="remove icon"></i> ' + formsetContainer.data('removeLabel'),
            'added': function (row) {
                initMemberQuickSearch(row.find('.ui.search'));
            }
        });
    } else {
        if( $('.firstname').val() !== '' || $('.lastname').val() !== ''
            && $('.existing--member').val() === '' ) {
            $('.ui.button.add.member').transition('scale');
            $('.existing--member').attr('disabled', 'disabled');
            $('.ui.add.form.member').transition('scale');
        }
    }

    initMemberQuickSearch($('.ui.search'));



    function showOneAccordionElement(element, index, array) {
        selector = '.ui.accordion.meals.' + element;
        $(selector).show();
    }
    function showAllAccordionElements() {
        $('.ui.accordion.meals').not('.default').each(function () {
          $(this).show();
        });
    }
    function showUiAccordionSelectedDays() {
        var $selected = $("#form-meals-schedule select[multiple='multiple']").val();
        if ($selected) {
          $selected.forEach(showOneAccordionElement);
        }
    }
    function hideUiAccordionDays() {
        $('.ui.accordion.meals').not('.default').each(function () {
          $(this).hide();
        });
    }

    $("#form-meals-schedule select[multiple='multiple']").change(function () {
        hideUiAccordionDays();
        showUiAccordionSelectedDays();
    });
    var deliveryTypeSelect = $('#id_dietary_restriction-delivery_type, #id_delivery_type');
    deliveryTypeSelect.change(function () {
        if ($(this).val() == 'E') {
            $('#form-meals-schedule').hide();
            showAllAccordionElements();
            $('.ui.accordion.meals.default').hide();
        }
        else {
            $('#form-meals-schedule').show();
            hideUiAccordionDays();
            showUiAccordionSelectedDays();
            $('.ui.accordion.meals.default').hide();
        }
    });
    if (deliveryTypeSelect.val() == 'E') {
        $('#form-meals-schedule').hide();
        showAllAccordionElements();
        $('.ui.accordion.meals.default').hide();
    }
    else {
        $('#form-meals-schedule').show();
        hideUiAccordionDays();
        showUiAccordionSelectedDays();
        $('.ui.accordion.meals.default').hide();
    }
});
