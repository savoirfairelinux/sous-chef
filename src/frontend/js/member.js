$(function() {

    // Javascript of the member application.
    // **************************************
    var today = new Date();

    $('.ui.dropdown.member.status > .menu > .item').click(function () {
        // Don't change the dropdown content. There's a bug with two labels.
        // This prevents the default behavior.
        return false;
    });
    $('.ui.dropdown.member.status > .menu > .item.member-view-upcoming-changes').click(function () {
        location.replace($(this).data('url'));
    });
    $('.ui.dropdown.member.status > .menu > .item.member-cancel-this-upcoming-change').click(function () {
        var $form = $(this).find('form');
        if (window.confirm($(this).data('prompt'))) {
            $form.submit();
        }
    });

    $('.ui.dropdown.member.status > .menu > .item.member-update-status, .ui.dropdown.member.status > .menu > .item.member-reschedule-this-upcoming-change').click(function () {
        var modalCtntURL = $(this).data('url');
        var modalTarget = $(this).data('modalTarget').toString();

        $.get(modalCtntURL, function (data) {
            $(modalTarget).html(data).modal("setting", {
                closable: false,
                // Inside modal init
                onVisible: function () {
                    var $modal = $(this);
                    // Enable status confirmation dropdown
                    $modal.find('.ui.status_to.dropdown').dropdown();
                    // Init dates field (start and end)
                    $modal.find('#rangestart').calendar({
                        type: 'date',
                        on: 'click',
                        minDate: today,
                        formatter: {
                            date: function (date, settings) {
                                return date ? dateFormat(date, 'yyyy-mm-dd') : '';
                            }
                        },
                        endCalendar: $modal.find('#rangeend')
                    });
                    $modal.find('#rangeend').calendar({
                        type: 'date',
                        formatter: {
                            date: function (date, settings) {
                                return date ? dateFormat(date, 'yyyy-mm-dd') : '';
                            }
                        },
                        startCalendar: $modal.find('#rangestart')
                    });
                },
                // When approvind modal, submit form
                onApprove: function () {
                    var $modal = $(this);
                    $.ajax({
                         type: 'POST',
                         url: modalCtntURL,
                         data: $modal.find('#change-status-form').serialize(),
                         success: function (xhr, ajaxOptions, thrownError) {
                             if ( $(xhr).find('.errorlist').length > 0 ) {
                                 $modal.html(xhr);
                                 $modal.find('.ui.status_to.dropdown').dropdown();
                             } else {
                                 $modal.modal("hide");
                                 location.reload();
                             }
                         },
                     });
                    return false; // don't hide modal until we have the response
                },
                // When denying modal, restore default value for status dropdown
                onDeny: function () {
                    location.reload();
                }
            }).modal('setting', 'autofocus', false).modal("show");
        });
    });

    $('#wizard_form_birthdate').calendar({
        type: 'date',
        maxDate: today,
        formatter: {
            date: function (date, settings) {
                return date ? dateFormat(date, 'yyyy-mm-dd') : '';
            }
        },
    });

    if($('#dietary_restriction-delivery_type select').val() == 'E') {
        $('#form-meals-schedule').hide();
    } else {
        $('#form-meals-schedule').show();
    }

    $('#dietary_restriction-delivery_type .dropdown').dropdown(
        'setting', 'onChange', function(value, text, $selectedItem) {
            if($selectedItem.data('value') == 'E') {
                $('#form-meals-schedule').hide();
            } else {
                $('#form-meals-schedule').show();
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

    // Relationships formset
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
            'prefix': 'relationships',
            'addText': '<i class="plus icon"></i> ' + formsetContainer.data('addLabel'),
            'deleteText': '<i class="remove icon"></i> ' + formsetContainer.data('removeLabel'),
            'added': function (row) {
                initMemberQuickSearch(row.find('.ui.search'));
                row.find('.ui.calendar').calendar({
                    type: 'date',
                    formatter: {
                        date: function (date, settings) {
                            return date ? dateFormat(date, 'yyyy-mm-dd') : '';
                        }
                    }
                });
            },
            'formTemplate': '[x-template]'
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
});
