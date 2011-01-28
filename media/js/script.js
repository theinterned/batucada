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
        $(this).parent('.field').find('.hint b').html(val);
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

var loadMoreMessages = function() {
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
            $('.close_button').bind('click', function(){
                $('.welcome').animate(
                    {
                        opacity: 'hide',
                        height: 'hide',
                        paddingTop: 0,
                        paddingBottom: 0,
                        marginTop: 0,
                        marginBottom: 0
                    }, 
                    600, 'jswing');        
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
            loadMoreMessages();
        }
    }
};

jQuery.fn.tabLinks = function(element){
    var $modal = $(this).parents('.modal');
    $modal.addClass('tab-links');
    $(this).first().parent('li').addClass('active');
    
    var updateElement = function(e) {
        e.preventDefault();
        log('updateElement', $(this).getOwnTab());
        if ( $(this).getOwnTab() ){
            $newTab = $(this).getOwnTab();
            log("$newTab retrieved from data", $newTab);
            replaceTab($(element), $newTab);
        }        
        else {
            log('data not found');
            var href = $(this).attr('href');
            $('<div/>').load(href + ' ' + element, function() {            
                $newTab = $(this).children()[0];                
                $(e.target).storeOwnTab($newTab);
                // $(element).replaceWith($tab);
                replaceTab($(element), $newTab);
                $('textarea.wmd').wmd({'preview': false});            
            });
            
        }
        $(this).parent('li').setActive();
    };
    var replaceTab = function($oldTab, $newTab){
        log($oldTab, $newTab);
        $oldTab.parent().append($newTab).end().detach();
        
    }
    // onload activate the tab that corresponds to this tab group's sibling fieldset.
    $.fn.activateOnLoad = function(){
        if ( !this.is('a') ) return this;
        $tab = $modal.find('fieldset');
        activeSelector =  'li.' + $tab.attr('class').split(" ").join(", li.");
        $(activeSelector).setActive()
            .find('a').storeOwnTab($tab);
        return this;
    };
    // deactivate all siblings, then activate the passed element
    $.fn.setActive = function() {        
        this.siblings('li').each(function(i, e) {
            $(e).removeClass('active');
        });
        this.addClass('active');
        return this;
    };
    $.fn.storeOwnTab = function($tab){
        console.log(this);
        if ( !this.is('a') ) return this; 
        $(this).data('drumbeat.modal.tab', $tab);    
        return this;
    };
    $.fn.getOwnTab = function() {
        if ( !this.is('a') ) return this; 
        return $(this).data('drumbeat.modal.tab');
    };
    // hook it up!
    $(this).each(function() {
        var me = $(this),
        href = me.attr('href');
        if (!href || href == '#') 
            return;
        me.bind('click.tablinks', updateElement);        
    }).activateOnLoad();
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

    // wire up any RTEs with wmd
    $('textarea.wmd').wmd({'preview': false});

    // modals using jQueryUI dialog
    $('.button.openmodal').live('click', function(){
        var url = this.href;
        var selector = '.modal';
        var urlFragment =  url + ' ' + selector;
        var dialog = $('<div></div>').appendTo('body');
        // load remote content
        dialog.load(
            urlFragment,
            function (responseText, textStatus, XMLHttpRequest) {
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

// Recaptcha
var RecaptchaOptions = { theme : 'custom' };

$('#recaptcha_different').click(function(e) {
    e.preventDefault();
    Recaptcha.reload();
});

$('#recaptcha_audio').click(function(e) {
    e.preventDefault();
    Recaptcha.switch_type('audio');
});

$('#recaptcha_help').click(function(e) {
    e.preventDefault();
    Recaptcha.showhelp();
});