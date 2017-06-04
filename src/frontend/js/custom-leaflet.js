// Javascript of the delivery application
// ****************************************

function printMapAndItinerary() {
    var pane_position = $('.leaflet-map-pane').position();
    var map_imgs = [];
    $('img.leaflet-tile.leaflet-tile-loaded').each(function (i, elem) {
        var position = $(elem).position();
        map_imgs.push({
            top: position.top,
            left: position.left,
            src: elem.src
        });
    });

    var routes = [];
    $('#clients-on-delivery-history tr').each(function (i, tr) {
        routes.push({
            client_order: $(tr).find('[data-property="delivery_sequence"]').text(),
            client_name: $(tr).find('[data-property="name"]').text(),
            client_address: $(tr).find('[data-property="address"]').text()
        });
    });
    var markers = [];
    $('.leaflet-marker-pane > div').each(function (i, elem) {
        var position = $(elem).position();
        markers.push({
            html: elem.outerHTML
        });
    });

    var routeResult = $("#delivery_history_edit_map").data("routeResult");
    var template_vars = {
        map_height: $('#delivery_history_edit_map').height(),
        map_width: $('#delivery_history_edit_map').width(),
        pane_left: pane_position.left,
        pane_top: pane_position.top,
        map_imgs: map_imgs,
        map_route_svg: $('svg.leaflet-zoom-animated')[0].outerHTML,
        routes: routes,
        markers: markers,
        distance: (routeResult.summary.totalDistance / 1000).toFixed(2),
        time: (routeResult.summary.totalTime / 60).toFixed(1),
        vehicle: $('#id_vehicle option:selected').text()
    };

    var w = window.open('');
    w.document.open();
    w.document.write(Mustache.render($("#print-template").html(), template_vars));
    w.document.close();
}

function groupWaypoints(waypoints) {

  // Parse waypoints. If they are within 5 decimal places of tolerance with another waypoint
  // on the list, we can safely assume they are at the same address.
  // In this case, we show one special marker with the number of the coexisting waypoints on it.

  var groupedWaypoints = waypoints.reduce(function(rv, x) {
    var lat = x.latLng.lat.toString().split('.');
    lat[1] = lat[1].slice(0, 5);
    lat = lat.join('.');

    var lng = x.latLng.lng.toString().split('.');
    lng[1] = lng[1].slice(0, 5);
    lng = lng.join('.');

    var val = lat + ', ' + lng;

    (rv[val] = rv[val] || []).push(x);
    return rv;
  }, {});

  return groupedWaypoints;

}

function sous_chef_leaflet_map_init (map, options, settings) {

    // Create a new tile layer with bike path (http://thunderforest.com/maps/opencyclemap/)
    var tileUrl = 'https://{s}.tile.thunderforest.com/cycle/{z}/{x}/{y}.png',
    layer = new L.TileLayer(tileUrl, {maxZoom: 18});
    map.addLayer(layer);

    // Center on santropol
    map.setView(new L.LatLng(45.516564, -73.575145), 13);

    // Create router
    var router = L.Routing.mapbox('pk.eyJ1IjoicmphY3F1ZW1pbiIsImEiOiJjaXAxaWpxdGkwMm5ydGhtNG84eGdjbGthIn0.TdwCw6vhAJdgxzH0JBp6iA');
    var defaultVehicle = settings.vehicle || 'cycling';
    router.options.profile = 'mapbox/' + defaultVehicle;

    if (settings.addListenerOnVehicleChange) {
        settings.addListenerOnVehicleChange(function (vehicle) {
            // vehicle is one of: cycling, driving, or walking
            control.getRouter().options.profile = "mapbox/" + vehicle;
            // refresh route display
            control.route();
        });
    }

    // Create route plan
    var plan = new L.Routing.Plan(
        // Empty waypoints
        [], {
            // Default geocoder
            geocoder: L.Control.Geocoder.nominatim({ geocodingQueryParams: { countrycodes: 'ca'}}),

            // Create routes while dragging markers
            routeWhileDragging: false,

            createMarker: function(i, wp) {
                if (wp.ignore_marker) return false;  // Don't create marker in this case.

                var marker = L.marker(wp.latLng, {
                    icon: wp.settings.icon,
                    draggable: false,
                    opacity: 1
                });
                marker.bindPopup(wp.settings.popup_html).openPopup();
                return marker;
            }
        }
    );

    // Create route control
    var control = new L.Routing.Control({
        router: router,
        language: 'fr',
        showAlternatives: true,
        lineOptions: {
            styles: [
                {color: 'black', opacity: 0.3, weight: 11, lineCap: 'round'},
                {color: 'white', opacity: 0.9, weight: 9},
                {color: 'red', opacity: 1, weight: 3}
            ]
        },
        altLineOptions: {
            styles: [
                {color: 'black', opacity: 0.1, weight: 11},
                {color: 'white', opacity: 0.25, weight: 9},
                {color: 'blue', opacity: 0.25, weight: 3}
            ]
        },
        plan: plan
    });
    var routeBlock = control.onAdd(map);

    var _setWaypoints = function (waypoints) {
        var L_waypoints = [];
        for (var i = 0; i < waypoints.length; i++) {
            var waypoint_obj = new L.Routing.Waypoint(L.latLng(waypoints[i][0], waypoints[i][1]));
            waypoint_obj.settings = waypoints[i][2] || {};
            L_waypoints.push(waypoint_obj);
        }

        var grouped_waypoints = groupWaypoints(L_waypoints);
        for (var geoid in grouped_waypoints) {
            if (grouped_waypoints.hasOwnProperty(geoid)) {
                // We can add attributes directly on these Waypoint objects
                // because they are stored as references in JavaScript.
                wps = grouped_waypoints[geoid];
                for (var i = 1; i < wps.length; i++) {
                    wps[i].ignore_marker = true;
                    if (wps[i].settings.popup_html) {
                        wps[0].settings.popup_html = (wps[0].settings.popup_html || '') + wps[i].settings.popup_html;
                    }

                }
                if (wps.length > 1) {
                    // Tweak icon content and text size when there are multiple clients
                    var MAGNIFY_FACTOR = 1.5
                    if ((wps[0].settings.icon || {}).options.glyph) {
                        wps[0].settings.icon.options.glyph += '*';
                        var text_size = wps[0].settings.icon.options.glyphSize;  // e.g.: 11px
                        var number = parseInt(text_size);  // 11
                        var unit = text_size.slice(number.toString().length); // px
                        var new_number = Math.round(number * MAGNIFY_FACTOR);
                        var new_text_size = new_number.toString() + unit;
                        wps[0].settings.icon.options.glyphSize = new_text_size;
                    }
                }
            }
        }
        control.setWaypoints(L_waypoints);
    }

    if (settings.waypoints) {
        // initial waypoints
        _setWaypoints(settings.waypoints);
    }
    if (settings.addListenerOnWaypointsUpdate) {
        settings.addListenerOnWaypointsUpdate(_setWaypoints);
    }

    if (settings.onRoutesfound) {
        control.on('routesfound', settings.onRoutesfound);
    }
}

    //:::  This routine calculates the distance between two points (given the     :::
    //:::  latitude/longitude of those points).                                   :::
    //:::  Passed to function:                                                    :::
    //:::    lat1, lon1 = Latitude and Longitude of point 1 (in decimal degrees)  :::
    //:::    lat2, lon2 = Latitude and Longitude of point 2 (in decimal degrees)  :::
    //:::    unit = the unit you desire for results                               :::
    //:::           where: 'M' is statute miles (default)                         :::
    //:::                  'K' is kilometers                                      :::
    //:::                  'N' is nautical miles                                  :::
    function distance(lat1, lon1, lat2, lon2, unit) {
        var radlat1 = Math.PI * lat1/180;
        var radlat2 = Math.PI * lat2/180;
        var theta = lon1-lon2;
        var radtheta = Math.PI * theta/180;
        var dist = Math.sin(radlat1) * Math.sin(radlat2) + Math.cos(radlat1) * Math.cos(radlat2) * Math.cos(radtheta);
        dist = Math.acos(dist);
        dist = dist * 180/Math.PI;
        dist = dist * 60 * 1.1515;
        if (unit=="K") { dist = dist * 1.609344; }
        if (unit=="N") { dist = dist * 0.8684; }
        return dist;
    }


function __client_address_map_init (map, options) {
    var marker;  // keeps the reference to the map marker once created.

    function setMarker(latitude, longitude) {
        // Add or update marker for the found address
        if (typeof(marker) === 'undefined') {
            // If the marker has not been created.
            marker = L.marker([latitude, longitude], {draggable: true});
            marker.addTo(map);
            // Adjust latitude / longitude if user drag the marker
            marker.on("dragend",function(ev){
                var chagedPos = ev.target.getLatLng();
                $('.field > .latitude').val(chagedPos.lat);
                $('.field > .longitude').val(chagedPos.lng);
                var newdist = distance(45.516564,-73.575145, chagedPos.lat,chagedPos.lng,"K")
                $('.field > .distance').val(newdist);
            });
        }

        marker.setLatLng([latitude, longitude]);
        map.setView([latitude, longitude], 17);
    }

    $('#geocodeBtn').click(function(e) {

        // Display a loading indicator
        $('form').addClass('loading');
        var notFoundMsg = $(this).data('notFoundMsg');

        var geocoder = new L.Control.Geocoder.nominatim({ geocodingQueryParams: { countrycodes: 'ca'}});
        // var yourQuery = "4846 rue cartier, Montreal, Qc";
        var apt='',street  ='' , city ='', zipcode ='';

        if ($('.field > .street.name').val() ) {
            street = $('.field > .street.name').val()+ "&";
        }
        if ($('.field > .city').val()) {
            city =  $('.field > .city').val()+ "&"; ;
        }

        var yourQuery = apt +  street + city + zipcode;

        geocoder.geocode(yourQuery, function(results) {
            if (results.length > 0) {
                var data = { address: results[0].name,
                             lat: results[0].center.lat,
                             long: results[0].center.lng };

                // calculate distance between santropol and the place found
                var dist = distance(45.516564,-73.575145, results[0].center.lat, results[0].center.lng,"K");

                // update text field withe info
                $('.field > .latitude').val(data.lat);
                $('.field > .longitude').val(data.long);
                $('.field .distance').val(dist);

                setMarker(data.lat, data.long);
            }
            else {
                alert(notFoundMsg);
            }

            // Remove the loading indicator
            $('form').removeClass('loading');
        });
    });

    var initial_lat = $('.field > .latitude').val();
    var initial_long = $('.field > .longitude').val();
    if (initial_lat && initial_long && (initial_lat !== '0') && (initial_long !== '0')) {
        setMarker(initial_lat, initial_long);
    } else {
        map.setView([45.516564,-73.575145], 12);  // Santropol
    }
}
