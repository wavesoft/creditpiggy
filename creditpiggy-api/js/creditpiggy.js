
/*! CreditPiggy API v0.1 | Ioannis Charalampidis, Citizen Cyberlab EU Project | GNU GPL v2.0 License */

/**
 * Pick an initiator function according to AMD or stand-alone loading
 */
( window.define == undefined ? function(req, fn) { window.CreditPiggy = fn($ || jQuery); } : window.define )(["jquery"], function($) {

	/**
	 * Check if jQuery requirement was not available as expected.
	 */
	if (!$) {
		console.error("CreditPiggy: jQuery must available in order to use creditpiggy.js!");
		return null;
	}

	/**
	 * The creditpiggy namespace
	 */
	var CreditPiggy = {

		/**
		 * The version of the javascript library
		 */
		"version": 	"0.1",

		/**
		 * The API Endpoint
		 */
		"apiURL":  "http://127.0.0.1:8000/api", //"//creditpiggy.cern.ch/api",

		/**
		 * The user profile
		 */
		"profile": null,

		/**
		 * List of named callbacks
		 */
		"__callbacks": { },

		/**
		 * Session information
		 */
		"__session": null,

	};

	//////////////////////////////////////////////////////////////////////////////
	// Internal API functions
	//////////////////////////////////////////////////////////////////////////////

	/**
	 * Internal function to execute all the API requests
	 *
	 * @param {string} action - The action to execute.
	 * @param {object} data - The data to send aloing with the action.
	 * @param {function} callback - The callback to fire upon receiving a response.
	 */
	CreditPiggy.__api = function(action, data, callback) {
		// Perform AJAX API Request
		$.ajax({
			"url": this.apiURL + "/" + action + ".json",
			"contentType": "json",
			"data": data || {
				"version": this.version
			},
			"method": "GET",
		})
		.done((function( data, textStatus, jqXHR ) {
			// Fire callback
			if (callback) callback(data);
		}).bind(this))
		.fail((function( jqXHR, textStatus, errorThrown ) {
			// Fire callback
			if (callback) callback(null, textStatus);
		}).bind(this));
	}

	/**
	 * Initialize CreditPiggy API
	 */
	CreditPiggy.__initialize = function() {
		// Update Session Information
		this.__api("js/session", {}, (function(data) {

			// If there was an error, reset profile
			if (!data) {
				console.warn("CreditPiggy: Unable to obtain session information");
				this.__session = null;
				return;
			}

			// Update session details
			this.__session = data;

			// If we have a user profile, update it now
			if (this.__session['profile']) {

				// Keep a reference to the user profile
				this.profile = this.__session['profile'];

				// Trigger the 'user' event
				this.trigger('user', this.profile);

			}

		}).bind(this));
	}

	//////////////////////////////////////////////////////////////////////////////
	// External API functions
	//////////////////////////////////////////////////////////////////////////////

	/**
	 * Register a function to the named callback.
	 */
	CreditPiggy.on = function( callback, fn ) {
		// Allocate space
		if (!this.__callbacks[callback])
			this.__callbacks[callback] = [];

		// Register function
		this.__callbacks[callback].push(fn);

		// Return this for chained calls
		return this;
	}

	/**
	 * Unregister a function to the named callback.
	 */
	CreditPiggy.off = function( callback, fn ) {
		// Skip if missing
		if (!this.__callbacks[callback]) return this;

		// Remove function
		var i = this.__callbacks[callback].indexOf(fn);
		if (i < 0) return this;
		this.__callbacks[callback].splice(i,1);

		// Check if that was the last function in the array
		if (this.__callbacks[callback].length == 0)
			delete this.__callbacks[callback];

		// Return this for chained calls
		return this;
	}

	/**
	 * Fire all named callbacks
	 */
	CreditPiggy.trigger = function() {

		// Prepare arguments
		var args = Array.prototype.slice.call(arguments),
			name = args.shift();

		// If we don't have such callback, quit
		if (!this.__callbacks[name])
			return;

		// Trigger callbacks
		for (var i=0; i<this.__callbacks[name].length; i++) {
			try {
				this.__callbacks[name].apply(this, args);
			} catch (e) {
				console.error("CreditPiggy: Error triggering callback ", name);
				console.error(e.stack);
			}
		}

		// Return this for chained calls
		return this;
	}

	//////////////////////////////////////////////////////////////////////////////
	// Initiators
	//////////////////////////////////////////////////////////////////////////////

	// Initialize upon loading
	$(CreditPiggy.__initialize.bind(CreditPiggy));

	// Return creditpiggy namespace
	return CreditPiggy;

});
