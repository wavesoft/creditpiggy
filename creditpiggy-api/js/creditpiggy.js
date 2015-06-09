
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
		"baseURL":  "http://127.0.0.1:8000", //"//creditpiggy.cern.ch/api",

		/**
		 * The ID for the project we are focusing at
		 */
		"project": null,

		/**
		 * Session data
		 */
		"session": null,

		/**
		 * The user profile
		 */
		"profile": null,

		/**
		 * List of named callbacks
		 */
		"__callbacks": { },

		/**
		 * Indicator that the page is loaded
		 */
		"__initialised": false,

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
			"url": this.baseURL + "/api/" + action + ".json",
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
	 * Trigger appropriate events upon changing data in the session
	 */
	CreditPiggy.__applySessionChanges = function( newSession ) {

		// Trigger "login" if we didn"t have a profile before
		if ((!this.session || !this.session["profile"]) && newSession["profile"]) {
			this.trigger("login", newSession["profile"]);
		} 
		// Trigger "logout" if we did have a profile and now we don"t
		else if ((!newSession || !newSession["profile"]) && (this.session && this.session["profile"])) {
			this.trigger("logout", this.session["profile"]);
		}

		// Trigger the "profile" event if we have a profile
		if (newSession["profile"]) {
			this.trigger("profile", newSession["profile"]);
		}

		// Update session
		this.session = newSession;

	}

	/**
	 * Request as session update
	 */
	CreditPiggy.__updateSession = function() {
		// Update Session Information
		this.__api("lib/session", {
			"project": this.project
		}, (function(data) {

			// If there was an error, reset profile
			if (!data) {
				console.warn("CreditPiggy: Unable to obtain session information");
				this.session = null;
				return;
			}

			// Update session details
			this.__applySessionChanges( data );

		}).bind(this));
	}

	/**
	 * Initialize CreditPiggy API
	 */
	CreditPiggy.__initialize = function() {
		
		// Initialize only once
		if (this.__initialised) return;

		// Request initial session update
		this.__updateSession();
		// We are now initialised
		this.__initialised = true;

	}

	//////////////////////////////////////////////////////////////////////////////
	// External API functions
	//////////////////////////////////////////////////////////////////////////////

	// ---------------------------------------------------------------------------
	//  Low-Level APIs
	// ---------------------------------------------------------------------------

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
	 * Register a function to the named callback.
	 */
	CreditPiggy.onOnce = function( callback, fn ) {
		// Allocate space
		if (!this.__callbacks[callback])
			this.__callbacks[callback] = [];

		// Create a deregistrable function
		var onceCallback = (function() {
			// Remove listener
			this.off( callback, onceCallback );
			// Fire callback
			callback.apply( this, arguments );
		}).bind(this);

		// Register the once callback
		this.on( callback, onceCallback );

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
		console.log("Triggering",name,args);

		// If we don"t have such callback, quit
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

	// ---------------------------------------------------------------------------
	//  High-level APIs
	// ---------------------------------------------------------------------------

	/**
	 * Configure the CreditPiggy API 
	 */
	CreditPiggy.configure = function( parameters ) {

		// Update parameters
		if (parameters['project']) this.project = parameters['project'];

		// If the page was loaded but not initialized
		// initialize now, otherwise update session
		if (!this.__initialised) {
			this.__initialize();
		} else {
			this.__updateSession();
		}

	}

	/**
	 * Perform user log-in and fire callback upon completion
	 * 
	 * This functino returns 'false' if the user is already logged in
	 * or 'true' if the window was openned.
	 */
	CreditPiggy.showLogin = function( callback ) {

		// If the user is already logged in, just fire callback
		if (this.session && this.session["profile"]) {
			if (callback) callback(this.session["profile"]);
			return false;
		}

		// Calculate parent-call URL details
		var w = 770, h = 450,
			l = (screen.width - w) / 2,
			t = (screen.height - h)/ 2;

		// Dispose previous window and create new one
		if (this.loginWindow) this.loginWindow.close();
		this.loginWindow = window.open(
				this.baseURL + "/login/?next=/project/" + this.project + '/',
				"creditpiggy-login-window",
				"width="+w+",height="+h+",left="+l+",top="+t+",location=no,menubar=no,resizable=yes,scrollbars=yes,status=no,toolbar=no"
			);

		// Register the callback for the "login" event, once
		if (callback) this.onOnce( "login", callback );
		return true;

	}

	/**
	 * Show user's profile
	 * 
	 * This functino returns 'false' if the user is already logged in
	 * or 'true' if the window was openned.
	 */
	CreditPiggy.showProfile = function( ) {

	}

	//////////////////////////////////////////////////////////////////////////////
	// Initiators
	//////////////////////////////////////////////////////////////////////////////

	// Initialize upon loading
	$((function() {
		
		// If we don't have a project specified, don't initialize
		// wait until the user calls configure()
		if (!this.project) return;
		this.__initialize();

	}).bind(CreditPiggy));

	// Receive HTML5 messages
	$(window).on("message", (function(ev) {
		var e = ev.originalEvent;

		// Discard messages from invalid origins
		if (String(e.origin).indexOf(this.baseURL) == -1) {
			console.warn("CreditPiggy: Discarding incoming message from untrusted origin");
			return;
		}

		// Handle CreditPiggy messages
		try {
			
			// Parse data as JSON string
			var data = JSON.parse(e.data);

			// Handle actions:
			if (data["action"] == "session") {
				// [session] - Handle a session update
				this.__applySessionChanges( data["session"] );
			}

		} catch (e) {
			console.warn("CreditPiggy: Invalid message received");
			return;
		}

	}).bind(CreditPiggy));

	// Return creditpiggy namespace
	return CreditPiggy;

});
