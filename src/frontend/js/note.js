$(function () {
    'use strict';
    var toggle_ids = {};

    $("button[data-batch-commit-btn]").click(function () {
        var self = this;
        var note_id = $(self).data('note-id');
        var orig_val = toggle_ids[note_id];
        if (orig_val) {
            // selected. then deselect it.
            $(self)
                .removeClass('active')
                .removeClass('labeled')
                .removeClass('icon')
                .addClass('basic')
                .blur()
                .find('> i').remove();
            delete toggle_ids[note_id];
            if ($.isEmptyObject(toggle_ids)) {
                $($(self).data('batch-commit-btn')).hide();
            }
        } else {
            // not selected. then select it.
            $(self)
                .addClass('active')
                .addClass('labeled')
                .addClass('icon')
                .removeClass('basic')
                .prepend('<i class="checkmark icon"></i>');
            toggle_ids[note_id] = true;

            var $btn = $($(self).data('batch-commit-btn'));
            $btn.show();
            var commit_url = $(self).data('batch-commit-url');
            do_once(function () {
                $btn.on('click', function (e) {
                    var $form = $btn.closest('form');
                    $.each(toggle_ids, function (k, v) {
                        $('<input>').attr({
                            type: 'hidden',
                            name: 'note',
                            value: k
                        }).appendTo($form);
                    });
                    return true; // form submit
                });
            });
        }
        return false;
    });

    function do_once(fn) {
        fn();
        do_once = function () {};
    }
});
