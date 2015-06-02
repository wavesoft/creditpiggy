
(function(global) {

/**
 * Create creditpiggy namespace
 */
var cpjs = global.cpjs = {
	
};

/**
 * Initialize the javascript API
 */
cpjs.initialize = function( context ) {

	// Return TRUE if a method is safe for non-CSRF requests
	function csrfSafeMethod(method) { return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method)); }

	// Setup CSRF protection
	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
				xhr.setRequestHeader("X-CSRFToken", cpjs.getCookie('csrftoken'));
			}
		}
	});

	// Handle on x-blur-update fields
	$("input.x-blur-update").each(function(i,e) {
		// Perform AJAX Post
		$(e).blur(function() {
			var elm = $(this),
				url = elm.data('url'),
				name = elm.attr('name'),
				value = elm.val();

			// Prepare data
			var data = {};
			data[name] = value;

			// Send request
			$.ajax({
				method 		: "POST",
				url 		: "/ajax/"+url+'/',
				data 		: JSON.stringify(data),
				dataType	: "json"
			}).done(function(data) {
				console.info("AJAX: Updated "+url+"/"+name+" = ",value);
			})
			.fail(function() {
				console.error("AJAX: Could not perform "+url+"/"+name+" = ",value);
			});
		})

	})

}

/** 
 * Get a cookie
 */
cpjs.getCookie = function(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i]);
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) == (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

})(window);