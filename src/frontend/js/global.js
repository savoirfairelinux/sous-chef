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
                if (!date) return '';
                var day = date.getDate();
                var month = date.getMonth() + 1;
                var year = date.getFullYear();
                if (month < 10) month = '0' + month;
                if (day < 10) day = '0' + day;
                return year + '-' + month + '-' + day;
            }
        }
    });

});
