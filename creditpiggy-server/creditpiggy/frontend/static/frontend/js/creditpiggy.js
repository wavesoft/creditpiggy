
(function(global) {

/**
 * Create creditpiggy namespace
 */
var cpjs = global.cpjs = {
};

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

/**
 * Initialize the javascript API
 */
cpjs.initialize = function( webid ) {

	// Return TRUE if a method is safe for non-CSRF requests
	function csrfSafeMethod(method) { return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method)); }

	// Set suffix
	cpjs.webid = webid;

	// Setup CSRF protection
	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
				xhr.setRequestHeader("X-CSRFToken", cpjs.getCookie('csrftoken'));
			}
			if (cpjs.webid) {
				xhr.setRequestHeader("X-Web-ID", cpjs.webid);
			}
		}
	});

	// Register x-blur-update elements
	$("input.x-blur-update").each((function(i,e) {
		this.dyn_blur_update($(e));
	}).bind(this))

	// Register x-click-update elements
	$("input.x-click-update").each((function(i,e) {
		this.dyn_click_update($(e));
	}).bind(this))

	// Register x-paginated elements
	$(".x-paginated").each((function(i,e) {
		new this.dyn_paginator($(e));
	}).bind(this))

	// Register x-graphs elements
	$(".x-graphs").each((function(i,e) {
		new this.dyn_graphs($(e));
	}).bind(this))

	// Register x-pin-login elements
	$(".x-pin-login").each((function(i,e) {
		new this.dyn_pin_login($(e));
	}).bind(this))

	// Enable popovers on achievements
	$(".achievements > div").click(function(e) {
		var msg = $(this).data('popup-id');
		if (!msg) return;

		$(msg).modal();
	});

	// Opt-in to tooltips
	$(function () {
	  $('[data-toggle="tooltip"]').tooltip({container: 'body'})
	})

}

/**
 * Handle elements that update something upon click.
 */
cpjs.dyn_click_update = function( hostDOM ) {

	// Perform AJAX Post
	hostDOM.click(function() {
		var elm = $(this),
			url = elm.data('url'),
			name = elm.attr('name'),
			value = elm.is(":checked") ? 1 : 0;

		// Prepare data
		var data = {};
		data[name] = value;

		// Send request
		$.ajax({
			method 		: "POST",
			url 		: "/ajax/"+url+"/",
			data 		: JSON.stringify(data),
			dataType	: "json"
		}).done(function(data) {
			console.info("AJAX: Updated "+url+"/"+name+" = ",value);
			field_value = value;
		})
		.fail(function() {
			console.error("AJAX: Could not perform "+url+"/"+name+" = ",value);
		});
	});

}

/**
 * Handle elements that update something upon blur.
 */
cpjs.dyn_blur_update = function( hostDOM ) {

	// Chek for value changes
	var field_value = hostDOM.val();

	// Perform AJAX Post
	hostDOM.blur(function() {
		var elm = $(this),
			url = elm.data('url'),
			name = elm.attr('name'),
			value = elm.val();

		// If value is the same, do nothing
		if (value == field_value)
			return;

		// Prepare data
		var data = {};
		data[name] = value;

		// Send request
		$.ajax({
			method 		: "POST",
			url 		: "/ajax/"+url+"/",
			data 		: JSON.stringify(data),
			dataType	: "json"
		}).done(function(data) {
			console.info("AJAX: Updated "+url+"/"+name+" = ",value);
			field_value = value;
		})
		.fail(function() {
			console.error("AJAX: Could not perform "+url+"/"+name+" = ",value);
		});
	});

}

/**
 * Paginator handler that renders data on the specified container DOM
 * Configuration parameters are obtained as DOM data properties.
 */
cpjs.dyn_paginator = function( hostDOM ) {

	// Define the url to load data from
	this.url = hostDOM.data('url');
	this.host = hostDOM;

	// Check what container to use as container
	this.container = this.host;
	var container = hostDOM.data('container');
	if (container) {
		this.container = this.host.find( container )
	}

	// Check what to use as template
	var template = hostDOM.data('template');
	if (!template) {
		console.error("Paginator: Template was not specified");
		return;
	}

	// Fetch template body
  	var templateDOM = $(template);
  	if (templateDOM.length == 0) {
		console.error("Paginator: Could not locate template DOM", template);
		return;
  	}

  	// Setup template and empty container
  	this.template = templateDOM.html();
	this.container.empty();
  	Mustache.parse(this.template);

	// Insert data to the DOM
	var insert_data = (function(data) {
		// Render template
		var rendered = Mustache.render( this.template, data );
		// Insert to DOM
		$(rendered).appendTo(
			this.container
			);
	}).bind(this);

	// Prepare a reusable 'loading' indicator
	this.loadingIndicator = $('<div class="loading-indicator"></div>');

	// Fetch next page
	this.page = 1;
	this.numpages = 0;
	this.loading = false;
	var fetch_next_page = (function(cb_more) {

		// Do not fetch more pages than accepted
		if ((this.numpages != 0) && (this.page > this.numpages))
			return;

		// If already loading, do nothing
		if (this.loading)
			return;

		// We are now loading
		this.loading = true;
		this.loadingIndicator.appendTo( this.container );

		// Send request
		$.ajax({
			method 		: "GET",
			url 		: "/ajax/"+this.url+"/",
			data 		: JSON.stringify({ 'page': this.page }),
			dataType	: "json"
		}).done((function(data) {

			// Update pages
			this.numpages = data.pages || 0;

			// Inject data
			for (var i=0; i<data.list.length; i++) {
				insert_data(data.list[i]);
			}

			// Increment page
			this.page += 1;			

			// We are ready for more if needed
			if (cb_more)
				setTimeout(cb_more, 100);

		}).bind(this))
		.fail((function(data) {

			// Log error
			console.error("AJAX: Pagination error", data);

		}).bind(this))
		.always((function() {
			
			// When we are done performing I/O, remove loading indicator
			this.loading = false;
			this.loadingIndicator.detach();

		}).bind(this));

	}).bind(this);

	// Check if DOM is visible
	var edge_reached = (function() {

		// Get DOM position and size
		var bottom_edge = this.container.offset().top + this.container.height(),
			scroll_edge = $(window).height() + $("body").scrollTop();

		// Return TRUE if bottom_edge is above scroll_edge
		return (bottom_edge <= scroll_edge);

	}).bind(this);

	// Helper for infinitely looping until edge
	// is not visible any more.
	var load_next = function() {
		// If edge is reached, fetch next page
		if (edge_reached()) {
			fetch_next_page(load_next);
		}
	};

	// Bind on window scroll
	$(window).scroll(function() {

		// Don't do anything if already loading
		if (this.loading) return;

		// Fetch next page
		load_next();

	});

	// Fetch initial page
	load_next();

}

/**
 * Dynamic graph handler for creating one or more plots inside the specified host dom,
 * dynamically updating them with a periodical function.
 */
cpjs.dyn_graphs = function( hostDOM ) {

	// Fetch details
	this.url = hostDOM.data('url');
	this.metrics = hostDOM.data('metrics');
	this.ts = hostDOM.data('ts');
	this.plotClass = hostDOM.data('plot-class') || "";

	// Loading indicator
	this.loading = false;

	// Store hostDOM
	this.hostDOM = hostDOM;

	// Create chartist DOM
	this.chartistDOM = $('<div class="ct-chart ct-major-tenth"></div>')
		.addClass(this.plotClass)
		.appendTo(hostDOM);

	// Create chartist
	this.chartist = new Chartist.Line(this.chartistDOM[0], { 'labels':[''], 'series':[[0]] }, {
		showPoint: true,
		lineSmooth: false,
		showArea: true,
		axisY: {
		    onlyInteger: true,			
		}
	});

	// The function to call in order to generate plots
	var gen_plots = (function() {

		// If already loading, quit
		if (this.loading) return;
		this.loading = true;

		// Send request
		$.ajax({
			method 		: "GET",
			url 		: "/ajax/"+this.url,
			data 		: { 'metrics': this.metrics, 'ts': this.ts },
			dataType	: "json"
		}).done((function(data) {

			// // Get plots
			// var data_plots = data.plots;

			// // Process results
			// var i =0;
			// for (var plot_name in data_plots) {
			// 	var plot = data_plots[plot_name];

			// 	// Prepare plot layout
			// 	var plotDOM = $('<div class="plot '+this.plotClass+'"></div>').appendTo(this.hostDOM),
			// 		innerPlot = $('<div class="plot-graph"></div>').appendTo(plotDOM);

			// 	// Prepare plot data
			// 	var plots = [];
			// 	for (var i=0; i<plot.series.length; i++) {

			// 		// Record values
			// 		var values = [];
			// 		for (var j=0; j<plot.series[i].length; j++) {
			// 			values.push([ plot.labels[j], plot.series[i][j] ]);
			// 		}

			// 		// create plot
			// 		plots.push({
			// 			'data': values,
			// 			'lines': { show: true }
			// 		});

			// 	}

			// 	console.log(plots);

			// 	// Create plot
			// 	$.plot( innerPlot, plots, {
			// 		'grid': {
			// 			'minBorderMargin': 40
			// 		},
			// 		'xaxis': {
			// 			'mode': "time",
			// 			'timeformat': "%H:%S",
			// 		},
			// 		'yaxis': {
			// 			'tickFormatter': function (val, axis) {
			// 				return parseInt(val);
			// 			}
			// 		}
			// 	});

			// 	// Increment index
			// 	i += 1;
			// }

			var plot = data.plot;
			this.chartist.update( plot );


		}).bind(this))
		.fail((function(data) {
			// Log error
			console.error("AJAX: Graph error", data);
		}).bind(this))
		.always((function() {
			// When we are done performing I/O, remove loading indicator
			this.loading = false;
			//this.loadingIndicator.detach();
		}).bind(this));

	}).bind(this);

	// Generate plots
	gen_plots();

}

/**
 * Pin-based e-mail login sequence
 */
cpjs.dyn_pin_login = function( hostDOM ) {

	// Lookup hosts
	var panelEmail = hostDOM.find(".login-panel-email"),
		panelPIN = hostDOM.find(".login-panel-pin"),
		inpEmail = hostDOM.find(".login-email"),
		inpPIN = hostDOM.find(".login-pin"),
		inpToken = hostDOM.find(".login-token"),
		lblEmail = hostDOM.find(".login-label-email"),
		btnContinue = hostDOM.find(".login-btn-continue"),
		btnBack = hostDOM.find(".login-btn-back"),
		btnState = 0,
		errorTitles = [ 'Ow snap!', 'Dang it!', 'Ooops!', 'Howdy!' ];

	// Show pin panel
	var showPinPanel = function( cb ) {
		// Don't do anything if visible
		if (panelPIN.is(":visible")) return;
		// Fade out email panel
		panelEmail.fadeOut(125, function() {
			// Fade in pin panel
			panelPIN.fadeIn(125, function() {
				// Focus on pin field
				inpPIN.focus();
				if (cb) cb();
			});
		});
	}

	// Show email panel
	var showEmailPanel = function( cb ) {
		// Don't do anything if visible
		if (panelEmail.is(":visible")) return;
		// Fade out pin panel
		panelPIN.fadeOut(125, function() {
			// Fade in email panel
			panelEmail.fadeIn(125, function() {
				if (cb) cb();
			});
		});
	}

	// Reset states
	var setButtonState = function( state ) {
		btnState = state;

		// [0] Reset button state
		if (state == 0) {
			btnContinue.text("Continue");
			btnContinue.attr("type", "button");
			btnContinue.attr("class", "btn btn-default pull-right");
			inpEmail.removeClass("disabled");
		}

		// [1] Primary continue
		else if (state == 1) {
			btnContinue.text("Continue");
			btnContinue.attr("type", "submit");
			btnContinue.attr("class", "btn btn-primary pull-right");
		}

	}

	// Show error
	var showError = function( errorMessage ) {
		var errorDOM = $("#modal-error");
		errorDOM.modal('show');
		errorDOM
			.find(".modal-title")
			.html('<i class="glyphicon glyphicon-warning-sign"></i> '+errorTitles[Math.floor(Math.random()*errorTitles.length)]);
		errorDOM
			.find(".modal-body > p")
			.empty()
			.html( errorMessage );
	}

	// Start with hidden host
	panelPIN.hide();
	setButtonState(0);

	// Bind on input changes and if it matches a stored
	// e-mail address hash, change from 'continue' to 'login'
	inpEmail.keyup(function() {
		var email = Sha256.hash( inpEmail.val() ),
			emailHash = localStorage.getItem("creditpiggy-pin-hash");

		// Change classes
		if (email == emailHash) {
			if (!btnContinue.hasClass("btn-primary")) {
				btnContinue.text("Login");
				btnContinue.removeClass("btn-default");
				btnContinue.addClass("btn-primary");
			}
		} else {
			if (!btnContinue.hasClass("btn-default")) {
				btnContinue.text("Continue");
				btnContinue.addClass("btn-default");
				btnContinue.removeClass("btn-primary");
			}
		}

	});

	// Bind on BACK clicks
	btnBack.click(function(e) {
		setButtonState(0);
		showEmailPanel();
	});

	// Bind on PIN login clicks
	btnContinue.click(function(e) {
		if (btnState == 0) {
			e.preventDefault();
			e.stopPropagation();

			// Check if we have a local authentication token
			var token = localStorage.getItem("creditpiggy-pin-token");
			btnContinue.addClass("disabled");
			inpEmail.addClass("disabled");
			lblEmail.text( inpEmail.val() );

			// Send request
			$.ajax({
				method 		: "POST",
				url 		: "/ajax/login.pin/",
				data 		: JSON.stringify({ 'email': inpEmail.val(), 'token': token }),
				dataType	: "json"
			})
			.done((function(data) {

				// Handle errors
				if (data['result'] != 'ok') {
					showError("There was an error while sending a PIN to your . "+data['error']);
					return;
				}

				// Handle according to login action
				if (data['login'] == 'token') {

					// We can log-in with token
					inpToken.attr("value", token);
					hostDOM.submit();

				} else {

					// Ask for pin
					showPinPanel();
					setButtonState(1);

				}

			}).bind(this))
			.fail((function(error) {

				// Server error
				var errMessage = "If anyone asks, the error code is #"+error.status+".";
				if (error.responseJSON && error.responseJSON['message']) {
					errMessage = error.responseJSON['message']+".";
				}
				showError("There was an error while communicating with the server. "+errMessage);

				// Reset button state
				setButtonState(0);

			}).bind(this))

		} else if (btnState == 1) {

			// Allow submitting

		}
	});

}

})(window);