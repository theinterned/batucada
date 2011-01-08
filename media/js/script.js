var createPostTextArea = function() {
    $('#create-post').find('textarea').bind('keydown', function() {
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

var username_hint = function() {
    var userurl = $('#username .hint b').html();
    $('#id_username').keyup(function() {
	$('#availability').removeClass('okay warning').html('');
	var val = (this.value) ? this.value : userurl;
	$(this).parent('p').find('.hint b').html(val);
    }).keyup();
};

var username_availability = function() {
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


var openid_handlers = function() {
    var one_click = {
	'google': 'https://www.google.com/accounts/o8/id',
	'yahoo': 'http://yahoo.com',
	'myopenid': 'http://myopenid.com',
    };
    $.each(one_click, function(key, value) {
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
	username_hint();
	username_availability();
    }
  },
  signup: {
    onload: function(){
	username_hint();
	username_availability();
    }
  },
  signup_openid: {
    onload: function() {
      openid_handlers();
    }
  },
  signin_openid: {
    onload: function() {
      openid_handlers();
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
            next_page = parseInt(page) + 1;
            template.attr('page', next_page);
            if (next_page > parseInt(npages)) {
              $('a#inbox_more').hide();
            }
            // update more link. very hacky :( 
              var href = $('a#inbox_more').attr('href');
              var new_href = href.substr(0, href.length - 2) + next_page + '/';
              $('a#inbox_more').attr('href', new_href);
            });
          });
      }
    }
};

$(document).ready(function() {
    // dispatch per-page onload handlers 
    var ns = window.batucada;
    var body_id = document.body.id;
    if (ns && ns[body_id] && (typeof ns[body_id].onload == 'function')) {
	ns[body_id].onload();
    }

    // attach handlers for elements that appear on most pages
    $('#user-nav').find('li.menu').bind('click', function(event) {
	$(this).toggleClass('open');
    });

    // find submit buttons and bind them to an event that submits their form
    $('.submit-button').bind('click', function(e) {
	$(e.target).parent('form[method="post"]').first().submit();
    });
});












