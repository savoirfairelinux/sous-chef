$(function() {

    // Javascript of the sous-chef application.
    // **************************************

    $('.ui.open-menu').on('click', function() {
        $('.ui.sidebar').sidebar('toggle');
    });

    $('.help-text').popup();

    $('.message .close').on('click', function() {
        $(this).closest('.message').transition('fade');
    });

    $('.ui.accordion').accordion();
    $('.ui.dropdown').dropdown({
        transition: 'drop',
        fullTextSearch: 'exact',
        forceSelection: false
    });

    $('.ui.calendar').calendar({
        type: 'date',
        formatter: {
            date: function (date, settings) {
                return date ? dateFormat(date, 'yyyy-mm-dd') : '';
            }
        }
    });

});
