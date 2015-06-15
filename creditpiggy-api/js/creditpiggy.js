
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

		/**
		 * Cryptographic key used for various operations
		 */
		"__cryptokey": null,

	};

	//////////////////////////////////////////////////////////////////////////////
	// Internal API functions
	//////////////////////////////////////////////////////////////////////////////

	/**
	 * (Re-)open a pop-up window
	 *
	 * @param {string} url - The url of the window.
	 */
	CreditPiggy.__popup = function( url ) {
		// Calculate parent-call URL details
		var w = 770, h = 470,
			l = (screen.width - w) / 2,
			t = (screen.height - h)/ 2;

		// Close previous window
		if (this.loginWindow) this.loginWindow.close();

		// Open new one
		this.loginWindow = window.open(
				url,
				"creditpiggy-popup-window",
				"width="+w+",height="+h+",left="+l+",top="+t+",location=no,menubar=no,resizable=yes,scrollbars=yes,status=no,toolbar=no"
			);

	}

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
			"url": this.baseURL + "/api/" + action + ".jsonp",
			"dataType": "jsonp",
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
			$(this).triggerHandler("login", [ newSession["profile"] ]);
		} 
		// Trigger "logout" if we did have a profile and now we don"t
		else if ((!newSession || !newSession["profile"]) && (this.session && this.session["profile"])) {
			$(this).triggerHandler("logout", [ this.session["profile"] ]);
		}

		// Trigger the "profile" event if we have a profile
		if (newSession["profile"]) {
			$(this).triggerHandler("profile", [ newSession["profile"] ]);
		}

		// If we have a crypto-key, update it
		if (newSession['cryptokey'])
			this.__cryptokey = newSession['cryptokey'];

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
	CreditPiggy.showLogin = function( ) {

		// If the user is already logged in, just fire callback
		if (this.session && this.session["profile"]) {
			return false;
		}

		// Open pop-up
		this.__popup( this.baseURL + "/login/?project=" + escape(this.project) );

		// Register the callback for the "login" event, once
		return true;

	}

	/**
	 * Show user's profile
	 * 
	 * This functino returns 'false' if the user is not logged in
	 * or 'true' if the window was openned.
	 */
	CreditPiggy.showProfile = function( ) {

		// If the user is not logged in, just return false
		if (!this.session || !this.session["profile"]) {
			return false;
		}

		// Open pop-up
		this.__popup( this.baseURL + "/profile/?project=" + escape(this.project) );

		// Register the callback for the "login" event, once
		return true;

	}

	/**
	 * Show project's status page
	 */
	CreditPiggy.showProject = function( ) {

		// The project website is accessible without log-in
		this.__popup( this.baseURL + "/project/" + this.project + "/" );

		// Register the callback for the "login" event, once
		return true;

	}

	/**
	 * Claim a working unit
	 */
	CreditPiggy.claimWorker = function( vmid, callback ) {

		// Forward the claim request
		this.__api("lib/claim", { 'vmid': vmid }, function(data) {
			if (!callback) return;

			// According to the response, fire callback
			if (!data) {
				callback(false, "Unable to handle your request");
			} else {
				if (data['result'] != 'ok') {
					callback(false, data['error'])
				} else {
					callback(true);
				}
			}
		});

	}

	/**
	 * Release a working unit
	 */
	CreditPiggy.releaseWorker = function( vmid, callback ) {

		// Forward the release request
		this.__api("lib/release", { 'vmid': vmid }, function(data) {
			if (!callback) return;

			// According to the response, fire callback
			if (!data) {
				callback(false, "Unable to handle your request");
			} else {
				if (data['result'] != 'ok') {
					callback(false, data['error'])
				} else {
					callback(true);
				}
			}
		});

	}


	/**
	 * Try to log-in using an offline session key 
	 */
	CreditPiggy.resumeSesion = function( ckey, callback ) {

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
			} else if (data["action"] == "logout") {
				// [logout] - The user was disconnected
				this.__applySessionChanges( null );
			}

		} catch (e) {
			console.warn("CreditPiggy: Invalid message received");
			return;
		}

	}).bind(CreditPiggy));

	// Return creditpiggy namespace
	return CreditPiggy;

});
