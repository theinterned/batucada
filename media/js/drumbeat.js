var resetErrors = function() {
    if ($('div.error').length != 0) {
        $('div.error').remove();
    }
};

var openidLogin = function() {
    $('p#username_field').hide();
    $('p#password_field').hide();
    $('a#openid_signin').hide();
    $('p#openid_field').show();
    $('a#password_signin').show();
    resetErrors();
    return false;
};

var passwordLogin = function() {
    $('p#openid_field').hide();
    $('a#password_signin').hide();
    $('p#username_field').show();
    $('p#password_field').show();
    $('a#openid_signin').show();
    resetErrors();
    return false;
};

var openidSignin = function() {
    $('fieldset#uname_form').hide();
    $('fieldset#openid_form').show();
    return false;
};

var passwordSignin = function() {

};