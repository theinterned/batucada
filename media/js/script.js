var createPostTextArea = function() {
    $('#create-post').find('textarea').bind('keyup', function() {
        var max = 750;
        var counter = $('#create-post').find('div.post-char-count');
        var count = max - $(this).val().length;
        counter.html(count);

        if (count < 0) {
            counter.addClass('danger');
            counter.removeClass('warning');
        }
        else if (count < 50) {
            counter.removeClass('danger');
            counter.addClass('warning');
        }
        else {
            counter.removeClass('danger');
            counter.removeClass('warning');
        }
    });

    $('#create-post').find('textarea').bind('blur', function() {
        if (jQuery.trim($(this).val()).length === 0) {
            $('#create-post').removeClass('expanded');
        }
    });

    $('#create-post').find('input').bind('focus', function() {
        $('#create-post').addClass('expanded');
        $('#create-post').find('textarea').trigger('focus');
    });
};

var usernameHint = function() {
    var userurl = $('#username .hint b').html();
    $('#id_username').keyup(function() {
        $('#availability').removeClass('okay warning').html('');
        var val = (this.value) ? this.value : userurl;
        $(this).parent('p').find('.hint b').html(val);
    }).keyup();
};

var usernameAvailability = function() {
    $('#id_username').bind('blur', function() {
        $.ajax({
            url: '/check_username/',
            data: {
                username: this.value
            },
            success: function() {
                $('#availability').removeClass('okay')
                    .addClass('warning')
                    .html('not available');
            },
            error: function() {
                $('#availability').removeClass('warning')
                    .addClass('okay')
                    .html('available');
            }
        });
    });
};

var openidHandlers = function() {
    var oneClick = {
        'google': 'https://www.google.com/accounts/o8/id',
        'yahoo': 'http://yahoo.com',
        'myopenid': 'http://myopenid.com'
    };
    $.each(oneClick, function(key, value) {
        $('.openid_providers #' + key).bind('click', function(e) {
            e.preventDefault();
            $('#id_openid_identifier').val(value);
            $('#id_openid_identifier').parent().submit();
        });
    });
};

var batucada = {
    splash: {
        onload: function() {
        }
    },
    create_profile: {
        onload: function() {
            usernameHint();
            usernameAvailability();
        }
    },
    signup: {
        onload: function(){
            usernameHint();
            usernameAvailability();
        }
    },
    signup_openid: {
        onload: function() {
            openidHandlers();
        }
    },
    signin_openid: {
        onload: function() {
            openidHandlers();
        }
    },
    dashboard: {
        onload: function() {
            createPostTextArea();
            $('#post-update').bind('click', function() {
                $('#post-status-update').submit();
            });
            $('a.activity-delete').bind('click', function(e) {
                $(e.target).parent().submit();
                return false;
            });
        }
    },
    project_landing: {
        onload: function() {
            createPostTextArea();
            $('#post-project-update').bind('click', function() {
                $('#post-project-status-update').submit();
            });
        }
    },
    user_profile: {
        onload: function() {
            createPostTextArea();
            $('#post-user-update').bind('click', function() {
                $('#post-user-status-update').submit();
            });
        }
    },
    inbox: {
        onload: function() {
            $('a#inbox_more').bind('click', function(e) {
                e.preventDefault();
                var template = $('#message-template');
                var page = template.attr('page');
                var npages = template.attr('npages');
                var url = $(this).attr('href');
                $.getJSON(url, function(data) {
                    $(data).each(function(i, value) {
                        var msg = template.tmpl(value);
                        msg.hide();
                        $('#posts').append(msg);
                        $('li.post-container:last').fadeIn(function() {
                            $('html').animate({
                                'scrollTop': $('a#inbox_more').offset().top
                            }, 200);
                        });
                    });
                    nextPage = parseInt(page) + 1;
                    template.attr('page', nextPage);
                    if (nextPage > parseInt(npages)) {
                        $('a#inbox_more').hide();
                    }
                    // update more link. very hacky :( 
                    var href = $('a#inbox_more').attr('href');
                    var newHref = href.substr(0, href.length - 2) + nextPage + '/';
                    $('a#inbox_more').attr('href', newHref);
                });
            });
        }
    }
};

jQuery.fn.tabLinks = function(element){
    var links = $(this);
    
    
    var updateElement = function(e){
        var link = $(this), href = link.attr('href');

        $('<div/>').load(href + ' ' + element, function(){
            $(element).html($(this).children()[0].innerHTML);
        });

        /*  when you fix it so ajax requests return just the contents of
        fieldset, replace above with:
    jQuery.get(href, function(data){ $(element).html(data); });
    */
        e.preventDefault();
        return false;
    };

    links.each(function(){
        var me = $(this),
        href = me.attr('href');
        if (!href || href == '#') return;
        me.bind('click.tablinks', updateElement);
    });
};

$(document).ready(function() {
    // dispatch per-page onload handlers 
    var ns = window.batucada;
    var bodyId = document.body.id;
    if (ns && ns[bodyId] && (typeof ns[bodyId].onload == 'function')) {
        ns[bodyId].onload();
    }

    // attach handlers for elements that appear on most pages
    $('#user-nav').find('li.menu').bind('click', function(event) {
        $(this).toggleClass('open');
    });
    // modals using jQueryUI dialog
    $('.button.openmodal').live('click', function(){
        var url = this.href;
        var selector = '.modal';
        var urlFragment =  url + ' ' + selector;
        var dialog = $('<div style=""></div>').appendTo('body');
        // load remote content
        dialog.load(
            urlFragment,
            function (responseText, textStatus, XMLHttpRequest) {
                log(responseText);
                dialog.dialog({
                    draggable: true
                });
            }
        );
        //prevent the browser to follow the link
        return false;
    });

    $('.modal nav.tabs a').tabLinks('section fieldset');
});

