$(function() {

    // Javascript of the page application.
    // **************************************

    var form = $('.ui.large.form'),
        usernameEmptyMsg = form.data('usernameEmptyMsg'),
        passwordEmptyMsg = form.data('passwordEmptyMsg'),
        passwordMinLengthMsg = form.data('passwordMinLengthMsg');

    $('.ui.large.form').form({
        on: 'submit',
        revalidate: 'false',
        fields: {
            username: {
                identifier: 'username',
                rules: [{
                    type   : 'empty',
                    prompt : usernameEmptyMsg
                }]
            },
            password: {
                identifier: 'password',
                rules: [{
                    type   : 'empty',
                    prompt : passwordEmptyMsg
                    },{
                    type   : 'minLength[6]',
                    prompt : passwordMinLengthMsg
                }]
            }
        }
    })
});
