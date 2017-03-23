$(function() {
    // LXYANG: rename this file as orderbatchcreate.js?
    // Place batch orders

    // Initialize delivery dates
    var orders = []
    var initial_dates = [];
    $.each(
        ($('#id_delivery_dates').val() || '').split('|'),
        function (idx, elem) {
            if (elem) initial_dates.push(elem);
        });

    var ordered_dates = [];
    $.each(
        ($("#delivery_dates").data("orderedDates") || '').split('|'),
        function (idx, elem) {
            if (elem) ordered_dates.push(elem);
        });
    var ordered_date_tooltip = $("#delivery_dates").data("orderedDateTooltip");


    // Make it possible to disable the highlight of today.
    // There are already two states: dates to create a new order, and dates with existing orders.
    // If we keep the highlight of today as the 3rd state, it would be confusing to the user.
    var __old_updateDatepicker = $.datepicker._updateDatepicker;
    $.datepicker._updateDatepicker = function (inst) {
        var retVal = __old_updateDatepicker.apply(this, arguments);
        var disableTodayHighlight = this._get(inst, 'disableTodayHighlight');
        if (disableTodayHighlight) {
            // Remove display classes
            var container = inst.dpDiv;
            var today_td = container.find('.ui-datepicker-today');
            if (today_td) {
                var today_a = today_td.find('a');
                today_a.removeClass('ui-state-highlight ui-state-active ui-state-hover');
            }
        }
        return retVal;
    };

    // --
    // Init multidatepicker on input directly would be simpler,
    // but a glitch would appear, so I init multidatespicker on an empty div#delivery_dates
    // and link it to an HTML input#id_delivery_dates using altField option
    // @see: https://github.com/dubrox/Multiple-Dates-Picker-for-jQuery-UI/issues/162
    var mdpConfig = {
        dateFormat: "yy-mm-dd",  // Example: 2017(yy)-03(mm)-24(dd).
        separator: "|",
        minDate: 0,
        numberOfMonths: 2,
        // Don't highlight today. It confuses the user. See the overriden _updateDatepicker method.
        disableTodayHighlight: true,
        // At the server side, the max length of the altField is 200.
        // Therefore 200/11 = 18.
        maxPicks: 18,
        altField: '#id_delivery_dates',
        onSelect: function (dateText, inst) {
            $('#form_create_batch #id_is_submit').val("0");
            $('#form_create_batch').submit();
        },
        beforeShowDay: function (date) {
            var dateStr = $.datepicker.formatDate('yy-mm-dd', date);
            if (ordered_dates.indexOf(dateStr) !== -1) {
                return [true, 'ordered-date', ordered_date_tooltip];
            } else {
                return [true, '', null];
            }
        }
    };
    if ($.isArray(initial_dates) && initial_dates.length > 0) {
        // Don't add this when initial_dates is an empty array.
        // MultiDatesPicker will raise an error in this case.
        mdpConfig.addDates = initial_dates;
    }
    $('#delivery_dates').multiDatesPicker(mdpConfig);

    $('.ui.accordion.meals').show();

    // fill in defaults
    (function fillInDefaults() {
        $("#form_create_batch .accordion[id^='date-']").each(function (idx, elem) {
            try {
                var client_meals_default = $(elem).data('client-meals-default');  // auto JSON
            } catch (e) {
                return;
            }
            var date = $(elem).attr('id').slice(5);
            // fill in data
            $.each(client_meals_default, function (key, value) {
                var selector = "#id_"+key+"_"+date+"_quantity";
                if (!$(selector).val()) {
                    $(selector).val(value);
                    dismissFieldError($(selector));
                }
            });
            if (client_meals_default.hasOwnProperty('size')) {
                var selector = "#id_size_"+date;
                if (!$(selector).dropdown('get value')[0]) {
                    $(selector).dropdown('set selected', client_meals_default.size);
                    dismissFieldError($(selector));
                }
            };
        });
    })();

    function dismissFieldError(elem) {
        $(elem).closest('.error').removeClass('error');
    }

    $('#form_create_batch #id_client .ui.dropdown').dropdown('setting', 'onChange', function (value, text, $selectedItem) {
        // on client change, update the form to update the client default.
        $('#form_create_batch #id_is_submit').val("0");
        $('#form_create_batch').submit();
    });

    $("#form_create_batch").on('submit', function collectInactiveAccordionsDates() {
        var dates = [];
        $('#form_create_batch #order_create_batch_items .accordion').has('.content:not(.active)').each(function (idx, elem) {
            var id = $(elem).attr('id');
            var date = id.slice(5);
            dates.push(date);
        });
        $('#form_create_batch #id_accordions_active').val(dates.join('|'));
    });
});
