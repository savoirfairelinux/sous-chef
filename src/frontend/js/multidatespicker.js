$(function() {

    // Place batch orders
    // --
    // Init multidatepicker on input directly would be simpler,
    // but a glitch would appear, so I init multidatespicker on an empty div#delivery_dates
    // and link it to an HTML input#id_delivery_dates using altField option
    // @see: https://github.com/dubrox/Multiple-Dates-Picker-for-jQuery-UI/issues/162
    $('#delivery_dates').multiDatesPicker({
        dateFormat: "yy-mm-dd",
        separator: "|",
        minDate: 0,
        numberOfMonths: 2,
        altField: '#id_delivery_dates'
    });

});
