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
        var $elem = $(this);
        if ($elem.val().length != 0) {
            $.ajax({
                url: '/ajax/check_username/',
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
        }
    });
};

var openidHandlers = function() {
    var oneClick = {
        'google': 'https://www.google.com/accounts/o8/id',
        'yahoo': 'https://yahoo.com',
        'myopenid': 'https://www.myopenid.com'
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

var attachFileUploadHandler = function($inputs) {
    var updatePicturePreview = function(path) {
        var $img = $('<img class="member-picture"></img>');
        $img.attr('src', path);
        $('p.picture-preview img').remove();
        $img.appendTo('p.picture-preview');
    };
    $(this).closest('form').removeAttr('enctype');
    $inputs.closest('fieldset').addClass('ajax-upload');
    $inputs.each(function() {
        $(this).ajaxSubmitInput({
            url: $(this).closest('form').attr('data-url'),
            beforeSubmit: function($input) {
                updatePicturePreview("/media/images/ajax-loader.gif");
                $options = {};
                $options.filename = $input.val().split(/[\/\\]/).pop();
                return $options;
            },
            onComplete: function($input, iframeContent, passJSON) {
                $input.closest('form')[0].reset();
                $input.trigger('clean');
                if (!iframeContent) {
                    return;
                }
                content = jQuery.parseJSON(iframeContent);
                updatePicturePreview("/media/" + content.filename);
            }
        });
    });
};

var batucada = {
    splash: {
        onload: function() {
        }
    },
    compose_message: {
        onload: function() {
            $('#id_recipient').autocomplete({
                source: '/ajax/following/',
                minLength: 2
            });
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
            $('.close_button').bind('click', function(e) {
                e.preventDefault();
                $('.welcome').animate({
                    opacity: 'hide',
                    height: 'hide',
                    paddingTop: 0,
                    paddingBottom: 0,
                    marginTop: 0,
                    marginBottom: 0
                }, 600, 'jswing', function() {
                    $.post('/broadcasts/hide_welcome/');
                });
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
    challenge_landing: {
        onload: function() {
            createPostTextArea();
            $('#post-challenge').bind('click', function() {
                $('#post-challenge-summary').submit();
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
    profile_edit: {
        onload: function() {
            var $inputs = $('input[type=file]');
            if ($inputs) {
                attachFileUploadHandler($inputs);
            }
        }
    },
    inbox: {
        onload: function() {
            loadMoreMessages();
        }
    },
    journalism: {
        onload: function() {
            VideoJS.setupAllWhenReady();
        }
    }
};

jQuery.fn.tabLinks = function(element) {
    var $modal = $(this).parents('.modal');
    $modal.addClass('tab-links');
    $(this).first().parent('li').addClass('active');
    
    var updateElement = function(e) {
        e.preventDefault();
        if($(e.target).closest('li').is('.active')) return;
        
        if ($(this).getOwnTab()) {
            $newTab = $(this).getOwnTab();
            $(element).replaceTab($newTab);
        } else {
            var href = $(this).attr('href');
            $('<div/>').load(href + ' ' + element, function() {
                $newTab = $(this).children().first();
                $(e.target).storeOwnTab($newTab);             
                $(element).replaceTab($newTab);
                $newTab.initForm();              
            });
        }
        $(this).parent('li').setActive();
    };
    $.fn.initForm = function() {
        attachFileUploadHandler($(this).find('input[type=file]'));
        $(this).attachDirtyOnChangeHandler();
        initWMD();
        return this;
    };
    var saveModal = function(e) {
        e.preventDefault();
        log('saveModal');
        
        $modal.find('.tabs .dirty a').each(function() {
            var tab = $(this).getOwnTab();
            if (tab) {
                var $forms = $(tab).find('form.dirty');
                $forms.each(function(){
                    $.ajax({
                        type: $(this).attr('method'),
                        url: $(this).attr('action'),
                        data: $(this).serialize(),
                        success: function(data) {
                            log(data);
                        }
                    });                    
                });
            }
        });
    };
    var closeModal = function(e) {
        e.preventDefault();
        log('closeModal');
    };
    // event handler fired when any modal input changes to mark that input as dirty
    // and fire a custom 'dirty' event to bubble up.
    var dirtyOnChange = function(e) {        
        $(e.target).addClass('dirty').trigger('dirty');
    };
    // event handler for cutome 'dirty' event
    var onInputDirty = function(e){
        if($(this).has(e.target).length > 0){
            $(this).addClass('dirty');
            if(e.data.tabLink){            
                e.data.tabLink.addClass('dirty');
            }                        
        }        
    };
    // input event handler for custom 'clean' event.
    var cleanInput = function(e){
        $(e.target).removeClass('dirty');
    };
    // event handler for custom 'clean' event
    var onInputClean = function(e){
        if(($(this).has(e.target).length > 0) && ($(this).has(':input.dirty').length == 0)){
            $(this).removeClass('dirty');
            if(e.data.tabLink){
                e.data.tabLink.removeClass('dirty');
            }
        }
    };
    // wire up the clean / dirty form element events and behaviours.
    $.fn.attachDirtyOnChangeHandler = function() {
        $tabLink =  $('li.' + $(this).attr('class').split(" ").join(", li."));
        $(this).find(':input')
            .bind('change', dirtyOnChange)
            .bind('clean', cleanInput)
            .end().find('form')
                .bind('dirty', {tabLink : $tabLink}, onInputDirty)
                .bind('clean', {tabLink : $tabLink}, onInputClean);
        return this;
    };
    $.fn.replaceTab = function($newTab) {
        this.parent().append($newTab).end().detach();
        return this;       
    };
    // onload activate the tab that corresponds to this tab group's sibling fieldset.
    $.fn.activateOnLoad = function() {
        if ( !this.is('a') ) return this;
        $tab = $modal.find('fieldset');
        $tabLink =  $('li.' + $tab.attr('class').split(" ").join(", li."));
        $tab.initForm();
        $tabLink
            .setActive()
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
    $.fn.storeOwnTab = function($tab) {
        if (!this.is('a')) return this;
        $(this).data('drumbeat.modal.tab', $tab);
        return this;
    };
    $.fn.getOwnTab = function() {
        if (!this.is('a')) return this; 
        return $(this).data('drumbeat.modal.tab');
    };
    $.fn.addButtons = function() {
        this.append(
            '<p class="ajax-buttons">'+
              '<a class="button close" href="#">Close</a>'+
              '<a class="button submit" href="#">Save</a>'+
            '</p>'
        ).find('a.close').bind('click', closeModal).parent().find('a.submit').bind('click', saveModal);
        return this;
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

var initWMD = function(){    
    $('textarea.wmd').not(function(){
        // we need to make sure this textarea hasn't been initialized already
        return ($(this).siblings('.wmd-button-bar').length != 0);
    }).wmd({'preview': false, 'helpLink' : '/editing-help/'});
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
    initWMD();

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
    
    $('.modal nav.tabs a').tabLinks('.tabpane');
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
