(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
function corslite(url, callback, cors) {
    var sent = false;

    if (typeof window.XMLHttpRequest === 'undefined') {
        return callback(Error('Browser not supported'));
    }

    if (typeof cors === 'undefined') {
        var m = url.match(/^\s*https?:\/\/[^\/]*/);
        cors = m && (m[0] !== location.protocol + '//' + location.domain +
                (location.port ? ':' + location.port : ''));
    }

    var x = new window.XMLHttpRequest();

    function isSuccessful(status) {
        return status >= 200 && status < 300 || status === 304;
    }

    if (cors && !('withCredentials' in x)) {
        // IE8-9
        x = new window.XDomainRequest();

        // Ensure callback is never called synchronously, i.e., before
        // x.send() returns (this has been observed in the wild).
        // See https://github.com/mapbox/mapbox.js/issues/472
        var original = callback;
        callback = function() {
            if (sent) {
                original.apply(this, arguments);
            } else {
                var that = this, args = arguments;
                setTimeout(function() {
                    original.apply(that, args);
                }, 0);
            }
        }
    }

    function loaded() {
        if (
            // XDomainRequest
            x.status === undefined ||
            // modern browsers
            isSuccessful(x.status)) callback.call(x, null, x);
        else callback.call(x, x, null);
    }

    // Both `onreadystatechange` and `onload` can fire. `onreadystatechange`
    // has [been supported for longer](http://stackoverflow.com/a/9181508/229001).
    if ('onload' in x) {
        x.onload = loaded;
    } else {
        x.onreadystatechange = function readystate() {
            if (x.readyState === 4) {
                loaded();
            }
        };
    }

    // Call the callback with the XMLHttpRequest object as an error and prevent
    // it from ever being called again by reassigning it to `noop`
    x.onerror = function error(evt) {
        // XDomainRequest provides no evt parameter
        callback.call(this, evt || true, null);
        callback = function() { };
    };

    // IE9 must have onprogress be set to a unique function.
    x.onprogress = function() { };

    x.ontimeout = function(evt) {
        callback.call(this, evt, null);
        callback = function() { };
    };

    x.onabort = function(evt) {
        callback.call(this, evt, null);
        callback = function() { };
    };

    // GET is the only supported HTTP Verb by XDomainRequest and is the
    // only one supported here.
    x.open('GET', url, true);

    // Send the request. Sending data is not supported.
    x.send(null);
    sent = true;

    return x;
}

if (typeof module !== 'undefined') module.exports = corslite;

},{}],2:[function(require,module,exports){
var polyline = {};

// Based off of [the offical Google document](https://developers.google.com/maps/documentation/utilities/polylinealgorithm)
//
// Some parts from [this implementation](http://facstaff.unca.edu/mcmcclur/GoogleMaps/EncodePolyline/PolylineEncoder.js)
// by [Mark McClure](http://facstaff.unca.edu/mcmcclur/)

function encode(coordinate, factor) {
    coordinate = Math.round(coordinate * factor);
    coordinate <<= 1;
    if (coordinate < 0) {
        coordinate = ~coordinate;
    }
    var output = '';
    while (coordinate >= 0x20) {
        output += String.fromCharCode((0x20 | (coordinate & 0x1f)) + 63);
        coordinate >>= 5;
    }
    output += String.fromCharCode(coordinate + 63);
    return output;
}

// This is adapted from the implementation in Project-OSRM
// https://github.com/DennisOSRM/Project-OSRM-Web/blob/master/WebContent/routing/OSRM.RoutingGeometry.js
polyline.decode = function(str, precision) {
    var index = 0,
        lat = 0,
        lng = 0,
        coordinates = [],
        shift = 0,
        result = 0,
        byte = null,
        latitude_change,
        longitude_change,
        factor = Math.pow(10, precision || 5);

    // Coordinates have variable length when encoded, so just keep
    // track of whether we've hit the end of the string. In each
    // loop iteration, a single coordinate is decoded.
    while (index < str.length) {

        // Reset shift, result, and byte
        byte = null;
        shift = 0;
        result = 0;

        do {
            byte = str.charCodeAt(index++) - 63;
            result |= (byte & 0x1f) << shift;
            shift += 5;
        } while (byte >= 0x20);

        latitude_change = ((result & 1) ? ~(result >> 1) : (result >> 1));

        shift = result = 0;

        do {
            byte = str.charCodeAt(index++) - 63;
            result |= (byte & 0x1f) << shift;
            shift += 5;
        } while (byte >= 0x20);

        longitude_change = ((result & 1) ? ~(result >> 1) : (result >> 1));

        lat += latitude_change;
        lng += longitude_change;

        coordinates.push([lat / factor, lng / factor]);
    }

    return coordinates;
};

polyline.encode = function(coordinates, precision) {
    if (!coordinates.length) return '';

    var factor = Math.pow(10, precision || 5),
        output = encode(coordinates[0][0], factor) + encode(coordinates[0][1], factor);

    for (var i = 1; i < coordinates.length; i++) {
        var a = coordinates[i], b = coordinates[i - 1];
        output += encode(a[0] - b[0], factor);
        output += encode(a[1] - b[1], factor);
    }

    return output;
};

if (typeof module !== undefined) module.exports = polyline;

},{}],3:[function(require,module,exports){
(function (global){
(function() {
	'use strict';

	var L = (typeof window !== "undefined" ? window['L'] : typeof global !== "undefined" ? global['L'] : null);
	var corslite = require('corslite');
	var polyline = require('polyline');

	L.Routing = L.Routing || {};

	L.Routing.Mapbox = L.Class.extend({
		options: {
			serviceUrl: 'https://api.tiles.mapbox.com/v4/directions/',
			timeout: 30 * 1000,
			profile: 'mapbox.driving'
		},

		initialize: function(accessToken, options) {
			L.Util.setOptions(this, options);
			this._accessToken = accessToken;
		},

		route: function(waypoints, callback, context, options) {
			var timedOut = false,
				wps = [],
				url,
				timer,
				wp,
				i;

			options = options || {};
			url = this.buildRouteUrl(waypoints, options);

			timer = setTimeout(function() {
								timedOut = true;
								callback.call(context || callback, {
									status: -1,
									message: 'OSRM request timed out.'
								});
							}, this.options.timeout);

			// Create a copy of the waypoints, since they
			// might otherwise be asynchronously modified while
			// the request is being processed.
			for (i = 0; i < waypoints.length; i++) {
				wp = waypoints[i];
				wps.push({
					latLng: wp.latLng,
					name: wp.name,
					options: wp.options
				});
			}

			corslite(url, L.bind(function(err, resp) {
				var data;

				clearTimeout(timer);
				if (!timedOut) {
					data = resp && resp.responseText ? JSON.parse(resp.responseText) : {};
					if (!err && !data.hasOwnProperty('error')) {
						this._routeDone(data, wps, callback, context);
					} else {
						callback.call(context || callback, {
							status: -1,
							message: 'HTTP request failed: ' + (err || data.error)
						});
					}
				}
			}, this), true);

			return this;
		},

		_routeDone: function(response, inputWaypoints, callback, context) {
			var alts = [],
				route,
				coordinates,
			    actualWaypoints,
			    indices,
			    i;

			context = context || callback;

			actualWaypoints = this._toWaypoints(inputWaypoints,
				[response.origin].concat(response.waypoints).concat([response.destination]));

			for (i = 0; i < response.routes.length; i++) {
				route = response.routes[i];
				coordinates = polyline.decode(route.geometry, 6);
				indices = this._mapWaypointIndices(actualWaypoints, route.steps, coordinates);
				alts.push({
					name: route.summary,
					coordinates: coordinates,
					instructions: this._convertInstructions(route.steps, indices.stepIndices),
					summary: this._convertSummary(route),
					inputWaypoints: inputWaypoints,
					waypoints: actualWaypoints,
					waypointIndices: indices.waypointIndices
				});
			}

			callback.call(context, undefined, alts);
		},

		_toWaypoints: function(inputWaypoints, vias) {
			var wps = [],
			    i,
			    c;
			for (i = 0; i < vias.length; i++) {
				c = vias[i].geometry.coordinates;
				wps.push({
					latLng: L.latLng(c[1], c[0]),
					name: vias[i].properties.name,
					options: inputWaypoints[i].options
				});
			}

			return wps;
		},

		buildRouteUrl: function(waypoints, options) {
			var locs = [],
			    computeInstructions,
			    computeAlternative,
			    locationKey;

			for (var i = 0; i < waypoints.length; i++) {
				locationKey = this._locationKey(waypoints[i].latLng);
				locs.push((i ? ';' : '') + locationKey);
			}

			computeAlternative = computeInstructions =
				!(options && options.geometryOnly);

			return this.options.serviceUrl + this.options.profile + '/' + locs + '.json?' +
				'instructions=' + computeInstructions + '&' +
				'alternatives=' + computeAlternative + '&' +
				'geometry=polyline&access_token=' + this._accessToken;
		},

		_locationKey: function(location) {
			return location.lng + ',' + location.lat;
		},

		_convertSummary: function(route) {
			return {
				totalDistance: route.distance,
				totalTime: route.duration
			};
		},

		_convertInstructions: function(steps, stepIndices) {
			var result = [],
			    i,
			    step,
			    type;

			for (i = 0; i < steps.length; i++) {
				step = steps[i];
				type = this._drivingDirectionType(step.maneuver);
				if (type) {
					result.push({
						type: type,
						distance: step.distance || 0,
						time: step.duration || 0,
						road: step.way_name,
						direction: step.direction,
						index: stepIndices[i]
					});
				}
			}

			return result;
		},

		_drivingDirectionType: function(maneuver) {
			switch (maneuver.type) {
			case 'continue':
				return 'Straight';
			case 'bear right':
				return 'SlightRight';
			case 'turn right':
				return 'Right';
			case 'sharp right':
				return 'SharpRight';
			case 'u-turn':
				return 'TurnAround';
			case 'sharp left':
				return 'SharpLeft';
			case 'turn left':
				return 'Left';
			case 'bear left':
				return 'SlightLeft';
			case 'waypoint':
				return 'WaypointReached';
			case 'depart':
				return 'Straight';
			case 'enter roundabout':
				return 'Roundabout';
			case 'arrive':
				return 'DestinationReached';
			default:
				return null;
			}
		},

		_mapWaypointIndices: function(waypoints, instructions, coordinates) {
			var wpIndices = [],
				stepIndices = [],
				wpIndex = 0,
				stepIndex = 0,
				wp = waypoints[wpIndex],
				stepCoord = instructions[stepIndex].maneuver.location.coordinates,
			    i,
			    c;

			for (i = 0; i < coordinates.length; i++) {
				c = coordinates[i];
				if (Math.abs(c[0] - wp.latLng.lat) < 1e-5 &&
					Math.abs(c[1] - wp.latLng.lng) < 1e-5) {
					wpIndices.push(i);
					wp = waypoints[++wpIndex];
				}
				if (stepCoord && Math.abs(c[0] - stepCoord[1]) < 1e-5 &&
					Math.abs(c[1] - stepCoord[0]) < 1e-5) {
					stepIndices.push(i);
					stepIndex++;
					stepCoord = instructions[stepIndex] && instructions[stepIndex].maneuver.location.coordinates;
				}
			}

			// For some reason, Mapbox Directions sometimes doesn't return a coordinate
			// which is exactly the last waypoint; it looks like they might accidentally truncate
			// the last oordinate or similar; this is a workaround: if we're mising the last
			// waypoint, just add the last coordinate as a probable match.
			if (wpIndices.length < waypoints.length && wpIndex === waypoints.length - 1) {
				wpIndices.push(coordinates.length - 1);
			}

			if (wpIndices.length !== waypoints.length) {
				console.warn('Could not find all waypoints in route\'s coordinates. :(');
			}

			return {
				waypointIndices: wpIndices,
				stepIndices: stepIndices
			};
		}
	});

	L.Routing.mapbox = function(accessToken, options) {
		return new L.Routing.Mapbox(accessToken, options);
	};

	module.exports = L.Routing.Mapbox;
})();

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})
},{"corslite":1,"polyline":2}]},{},[3]);
