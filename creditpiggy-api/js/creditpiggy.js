
/*! CreditPiggy API v0.1 | Ioannis Charalampidis, Citizen Cyberlab EU Project | GNU GPL v2.0 License */

/**
 * Pick an initiator function according to AMD or stand-alone loading
 */
( window.define == undefined ? function(req, fn) { window.CreditPiggy = fn($ || jQuery); } : window.define )(["jquery"], function($) {

	/**
	 * Check if jQuery requirement was not available as expected.
	 */
	if (!$) {
		console.error("CreditPiggy: jQuery must loaded prior to creditpiggy.js!");
		return null;
	}

	/**
	 * The creditpiggy namespace
	 */
	var CreditPiggy = {

		/**
		 * The version of the javascript library
		 */
		"version": 	"0.2",

		/**
		 * The API Endpoint
		 */
		"baseURL":  "http://127.0.0.1:8000",// "//creditpiggy.cern.ch",

		/**
		 * Session data
		 */
		"session": null,

		/**
		 * The user profile
		 */
		"profile": null,

		/**
		 * Indicator that the page is loaded
		 */
		"__initialised": false,

		/**
		 * Cryptographic key used for various operations
		 */
		"__cryptokey": null,

		/**
		 * Stack of claimed workers
		 */
		"__claimedWorkers": [],

		/**
		 * The ID of the VM
		 */
		"__webid": null,

		/**
		 * One-time initialization
		 */
		"__oneTimeInitEnabled": false,

		/**
		 * Periodic polling timer
		 */
		"__pollingTimer": null,

	};

	//////////////////////////////////////////////////////////////////////////////
	// Internal API functions
	//////////////////////////////////////////////////////////////////////////////

	/**
	 * Check if two object properties are the same
	 */
	var __same = function( a, b ) {

		// Check for undefined match
		if ((a == undefined) && (b == undefined)) return true;
		if ((a == undefined) || (b == undefined)) return false;

		// Check if properties of 'a' do not exist in 'b'
		// and for the ones found common, check if they match
		for (var k in a) {
			if (a.hasOwnProperty(k)) {
				if (b.hasOwnProperty(k)) {
					// Property types do not match? return
					if (typeof(a[k]) != typeof(b[k])) return false;
					// If properties are objects, perform nested __same call
					if (typeof(a[k]) == 'object')
						if (!__same(a[k], b[k])) return false;
					// Otherwise if values are not the same, return false
					if (a[k] != b[k]) return false;
				} else {
					// Property of 'a' not in 'b'				
					return false
				}
			}
		}

		// If for any reason a property of b is 
		// not in a, quit anyways.
		for (var k in b)
			if (b.hasOwnProperty(k) && !a.hasOwnProperty(k))
				return false;

		// All checks passed
		return true;

	}

	/**
	 * Trigger 'thaw' handlers and callbak
	 */
	var __thawStatusCallback = null;
	CreditPiggy.__thawFirst = function( callback ) {
		var thawListeners = jQuery._data(this,"events")['thaw'];

		// If nobody is listening for 'thaw', fire callback right away
		if (!thawListeners || !thawListeners.length) {
			callback();
			return;
		}

		// Register a thaw callback
		__thawStatusCallback = (function(success) {
			// If successful, 'login' will be fired.
			// Otherwise we will need to do the current log-in.
			if (!success) {
				callback();
			} else {
				this.session = null;				
			}
		}).bind(this);

		// Fire the thaw handler and expect a
		// thaw event to be fired within scope
		var cToken = null;
		if (this.session && this.session['auth_token'])
			cToken = this.session['this.session'];

		// Trigger thaw
		$(this).triggerHandler("thaw", [ cToken ]);

	}

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
		// Update parameters that always should pass through
		var data = data || { };
		data['version'] = this.version;
		data['webid'] = this.__webid;
		// Perform AJAX API Request
		$.ajax({
			"url": this.baseURL + "/api/" + action + ".jsonp",
			"dataType": "jsonp",
			"data": data,
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
	CreditPiggy.__applySessionChanges = function( newSession, userAction, initAction ) {
		var currProfile = this.profile,
			currSession = this.session,
			userAction = !!userAction;

		// Update session
		this.session = newSession;

		// Split actions in functions
		var f_checkForLogin = (function() {

			// If that's an init action, give a chance to thaw the session first, before caling
			// the 'login' event. This way there is only one 'login' event fired, with the 
			// appropriate credentials.
			if (initAction) {
				this.__thawFirst( f_continueChecks );
			} else {
				f_continueChecks();
			}

			}).bind(this),
			f_continueChecks = (function() {

			// Trigger "login" if we didn"t have a profile before
			if ((!currSession || !currSession["profile"]) && newSession && newSession["profile"]) {
				this.profile = newSession['profile'];
				$(this).triggerHandler("login", [ newSession["profile"], userAction ]);

			// Trigger "logout" if we did have a profile and now we don"t
			} else if ((!newSession || !newSession["profile"]) && (currSession && currSession["profile"])) {
				$(this).triggerHandler("logout", [ currSession["profile"], userAction ]);
				this.profile = null;
			}

			// Trigger the "profile" event if we have a profile
			if (newSession && newSession["profile"]) {
				if (!__same(newSession['profile'], currProfile)) {
					this.profile = newSession['profile'];
					$(this).triggerHandler("profile", [ newSession["profile"] ]);
				}
			}

			// Check if we have a new freeze information
			if (!currSession && !newSession) {
				// No changed
			} else if (currSession && !newSession) {
				// Went offline
				$(this).triggerHandler("token", [ null, userAction ]);
			} else if ( ((!currSession && newSession) || (currSession['auth_token'] != newSession['auth_token'])) && newSession['auth_token'] ) {
				// Changed
				$(this).triggerHandler("token", [ newSession['auth_token'] || null, userAction ]);
			}

			// If we have a crypto-key, update it
			if (newSession && newSession['cryptokey'])
				this.__cryptokey = newSession['cryptokey'];

			}).bind(this);

		// Start function stack
		f_checkForLogin();

	}

	/**
	 * Request as session update
	 */
	CreditPiggy.__updateSession = function( fromInit ) {		

		// Update Session Information
		this.__api("lib/session", {
		}, (function(data) {

			// If there was an error, reset profile
			if (!data) {
				console.warn("CreditPiggy: Unable to obtain session information");
				this.session = null;
				return;
			}

			// If we are from thaw and no user was defined, perform
			// one-time initial action.
			if (!fromInit && (!this.session || !this.session["profile"])) {
				fromInit = this.__oneTimeInitEnabled;
				this.__oneTimeInitEnabled = false;
			}

			// Update session details
			this.__applySessionChanges( data, false, fromInit );

		}).bind(this));
	}

	/**
	 * Initialize CreditPiggy API
	 */
	CreditPiggy.__initialize = function() {
		
		// Initialize only once
		if (this.__initialised) return;

		// Request initial session update
		this.__scheduleUpdate( true );		

		// We are now initialised
		this.__initialised = true;
	}

	/**
	 * Check and/or refresh session
	 */
	CreditPiggy.__checkSession = function( callback ) {

		// If we have a profile, we are logged in
		if (this.profile) {
			if (callback)
				callback(true);
		} else {
			if (callback)
				callback(false);
		}
	}
 
 	/**
	 * Schedule next periodical update
	 */
	CreditPiggy.__scheduleUpdate = function( polling ) {

		// Clear a previous timeout
		clearTimeout(CreditPiggy.__pollingTimer);

		// Perform update
		this.__updateSession( polling === true );

		// Schedule next update in a minute
		CreditPiggy.__pollingTimer = setTimeout(
				CreditPiggy.__scheduleUpdate.bind(this),
				60000
			);

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
	CreditPiggy.configure = function( webid ) {

		// Update parameters
		this.__webid = webid;

		// If the page was loaded but not initialized
		// initialize now, otherwise update session
		if (!this.__initialised) {
			this.__initialize();
		} else {
			this.__scheduleUpdate( true );
		}

	}

	/**
	 * Perform user log-out
	 * 
	 * This function returns 'false' if the user is already logged in
	 * or 'true' if the window was openned.
	 */
	CreditPiggy.logout = function( ) {

		// If the user is already logged out, just fire callback
		if (!this.session || !this.session["profile"]) {
			return false;
		}

		// Open pop-up
		this.__api("lib/logout");

		// We are done logging out.
		return true;

	}

	/**
	 * Perform user log-in and fire callback upon completion
	 * 
	 * This function returns 'false' if the user is already logged in
	 * or 'true' if the window was openned.
	 */
	CreditPiggy.showLogin = function( ) {

		// If the user is already logged in, just fire callback
		if (this.session && this.session["profile"]) {
			return false;
		}

		// Open pop-up
		this.__popup( this.baseURL + "/login/?webid=" + escape(this.__webid) );

		// Register the callback for the "login" event, once
		return true;

	}

	/**
	 * Show user's profile
	 * 
	 * This function returns 'false' if the user is not logged in
	 * or 'true' if the window was openned.
	 */
	CreditPiggy.showProfile = function( ) {

		// If the user is not logged in, just return false
		if (!this.session || !this.session["profile"]) {
			return false;
		}

		// Open pop-up
		this.__popup( this.baseURL + "/profile/?webid=" + escape(this.__webid) );

		// Register the callback for the "login" event, once
		return true;

	}

	/**
	 * Show user's status
	 * 
	 * This function returns 'false' if the user is not logged in
	 * or 'true' if the window was openned.
	 */
	CreditPiggy.showWebsiteStatus = function( ) {

		// Open pop-up
		this.__popup( this.baseURL + "/website/?webid=" + escape(this.__webid) );

		// Register the callback for the "login" event, once
		return true;

	}

	/**
	 * Claim a working unit
	 */
	CreditPiggy.claimWorker = function( vmid, callback ) {
		this.__checkSession((function(is_valid) {
			if (!is_valid) {

				// If we don't have a session, fire error callback
				if (callback)
					callback(false, "You are not logged in!");

			} else {

				// Forward the claim request
				this.__api("lib/claim", { 'vmid': vmid }, (function(data) {
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
				}).bind(this));
			}

		}).bind(this));
	}

	/**
	 * Release a working unit
	 */
	CreditPiggy.releaseWorker = function( vmid, callback ) {
		this.__checkSession((function(is_valid) {
			if (!is_valid) {

				// If we don't have a session, fire error callback
				if (callback)
					callback(false, "You are not logged in!");

			} else {

				// Forward the claim request
				this.__api("lib/release", { 'vmid': vmid }, (function(data) {
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
				}).bind(this));
			}

		}).bind(this));
	}

	/**
	 * Try to log-in using an offline session key
	 *
	 * If the log-in was successfful, a new authentication token is allocated
	 * and passed as a first parameter in the callback function.
	 */
	CreditPiggy.thawSession = function( token, callback ) {

		// If token is wrong, exit
		if (!token) {
			// Inform local thaw status callback listeners first
			if (__thawStatusCallback) {
				__thawStatusCallback( false );
				__thawStatusCallback = null;
			}
			return;
		}

		// Forward the release request
		this.__api("lib/thaw", { 'token': token }, (function(data) {
			// According to the response, fire callback
			if (!data) {

				// Inform local thaw status callback listeners first
				if (__thawStatusCallback) {
					__thawStatusCallback( false );
					__thawStatusCallback = null;
				}
				// Then user callback
				if (callback)
					callback(false, "Unable to handle your request");

			} else {

				// Inform local thaw status callback listeners first
				if (__thawStatusCallback) {
					__thawStatusCallback( (data['result'] == 'ok') );
					__thawStatusCallback = null;
				}

				// Handle result
				if (data['result'] != 'ok') {
					if (callback) callback(false, data['error'])
				} else {
					// Handle session information
					this.__applySessionChanges( data );
					// Callback the new authentication token
					if (callback) callback(data['auth_token']);
				}

			}
		}).bind(this));

	}

	//////////////////////////////////////////////////////////////////////////////
	// Initiators
	//////////////////////////////////////////////////////////////////////////////

	// Initialize upon loading
	$((function() {
		
		// If we don't have a webid specified, don't initialize
		// wait until the user calls configure()
		if (!this.__webid) return;
		this.__initialize();

	}).bind(CreditPiggy));

	// Refresh profile on focus
	$(window).on("focus", (function(ev) {
		// Update session and schedule periodical updates
		this.__scheduleUpdate();
	}).bind(CreditPiggy));
	$(window).on("blur", (function(ev) {
		// Enable one time-init when we get focused
		this.__oneTimeInitEnabled = true;
		// Clear polling timer
		clearTimeout( this.__pollingTimer );
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
		var data;
		try {
			// Parse data as JSON string
			data = JSON.parse(e.data);
		} catch (e) {
			console.warn("CreditPiggy: Invalid message received");
			return;
		}

		// Handle actions:
		if (data["action"] == "session") {
			// [session] - Handle a session update
			this.__applySessionChanges( data["session"], true );
		} else if (data["action"] == "logout") {
			// [logout] - The user was disconnected
			this.__applySessionChanges( null, true );
		}

	}).bind(CreditPiggy));

	// Return creditpiggy namespace
	return CreditPiggy;

});
