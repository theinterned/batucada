(function() {
    $('#user-nav').find('li.menu').bind('click', function() {
	$(this).toggleClass('open');
    });

    $('#create-post').find('input').bind('focus', function() {
	$('#create-post').addClass('expanded');
	$('#create-post').find('textarea').trigger('focus');
    });

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

    $('#post-update').bind('click', function() {
	$('#post-status-update').submit();
    });
})();























