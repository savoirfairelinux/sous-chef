// Javascript of the delivery application
// ****************************************

var control;  // global bind

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
    $('.leaflet-routing-geocoder').each(function (i, elem) {
        routes.push({
            client_order: $(elem).find('> .geocoder-handle').text(),
            client_name: $(elem).find('> input').val()
        });
    });
    var waypoints = control.getWaypoints();
    $.each(waypoints, function (i, waypoint) {
        routes[i].client_address = waypoint.options.address;
    });
    $('.leaflet-marker-pane > div').each(function (i, elem) {
        var position = $(elem).position();
        routes[i].marker_html = elem.outerHTML;
    });

    var directions = $('.leaflet-routing-alt:not(.leaflet-routing-alt-minimized)');

    var template_vars = {
        map_height: $('#main').height(),
        map_width: $('#main').width(),
        pane_left: pane_position.left,
        pane_top: pane_position.top,
        map_imgs: map_imgs,
        map_route_svg: $('svg.leaflet-zoom-animated')[0].outerHTML,
        routes: routes,
        distance_and_time: directions.find('> h3').text()
    };

    var w = window.open('');
    w.document.open();
    w.document.write(Mustache.render($("#print-template").html(), template_vars));
    w.document.close();
}

function getRouteWaypoints(routeId) {
    var waypoints = [];
    // Reset current waypoints
    control.setWaypoints(waypoints);

    // Ajax call to get waypoint according route
    $.get( "../getDailyOrders/?route="+routeId+"&mode=euclidean&if_exist_then_retrieve=true", function(data ) {
        var deliveryPoints = L.Routing.Waypoint.extend({ member:"", address:""});
        // create an array of waypoint from ajax call
        for(var i in data.waypoints)
        {
             waypoints.push(new deliveryPoints(L.latLng(data.waypoints[i].latitude, data.waypoints[i].longitude)) );
             waypoints[i].options.address = data.waypoints[i].address;
             waypoints[i].options.member = data.waypoints[i].member;
             waypoints[i].options.id = data.waypoints[i].id;
             waypoints[i].name = data.waypoints[i].member ;
        }

        //add first waypoint for santropol
        var santro = new deliveryPoints(L.latLng(45.516564,  -73.575145));
        santro.santro = true;
        santro.name = "Santropol Roulant";
        santro.options.address = "111 rue Roy Est";
        waypoints.splice(0, 0, santro);

        // add return waypoint to go back to santropol
        var santro = new deliveryPoints(L.latLng(45.516564,  -73.575145));
        santro.santro = true;
        santro.hideMarker = true;
        santro.name = "Santropol Roulant";
        santro.options.address = "111 rue Roy Est";
        waypoints.push(santro);

        // Set waypoints on the map
        control.setWaypoints(waypoints);
      }
    );
}

function main_map_init (map, options) {

    // create a new tile layer wiyh bike path (http://thunderforest.com/maps/opencyclemap/)
    var tileUrl = 'https://{s}.tile.thunderforest.com/cycle/{z}/{x}/{y}.png',
    layer = new L.TileLayer(tileUrl, {maxZoom: 18});

    // add the layer to the map
    map.addLayer(layer);

    // center on santropol
    map.setView(new L.LatLng(45.516564, -73.575145), 13);

    // Create bike router using mapbox
    var bikerouter = L.Routing.mapbox('pk.eyJ1IjoicmphY3F1ZW1pbiIsImEiOiJjaXAxaWpxdGkwMm5ydGhtNG84eGdjbGthIn0.TdwCw6vhAJdgxzH0JBp6iA');
    var defaultVehicle = $('#route_map').data('selected-vehicle');
    bikerouter.options.profile = 'mapbox/' + defaultVehicle;

    // Extend Routing Plan to add more buttons
    var routingPlan = L.Routing.Plan.extend({
        createGeocoders: function () {
            // Helper function
            function create_button(innerHTML, container) {
                var btn = L.DomUtil.create('button', '', container);
                btn.setAttribute('type', 'button');
                btn.className = 'ui button';
                btn.innerHTML = innerHTML;
                return btn;
            }

            var container = L.Routing.Plan.prototype.createGeocoders.call(this);

            // Create a button group for different route vehicles
            var div = L.DomUtil.create('div', '', container);
            div.style.padding = '0';
            div.className = 'small ui basic buttons';
            var vehicleButtons = {};
            var vehicles = $('#route_map').data('vehicles');  // already JSON
            $.each(vehicles, function (idx, tuple) {
                var code = tuple[0];
                var displayName = tuple[1];
                var button = L.DomUtil.create('button', '', div);
                button.setAttribute('type', 'button');
                button.className = 'ui button';
                button.innerText = displayName;
                button.style.float = 'left';
                var can_save = $('#route_map').data('can-save');
                if (can_save === 'no') {
                    button.setAttribute('disabled', 'disabled');
                }
                vehicleButtons[code] = button;
            });
            $.each(vehicleButtons, function (vehicle, btn) {
                L.DomEvent.on(btn, 'click', function () {
                    vehicleButtons[vehicle].classList.add('loading');
                    save_vehicle(vehicle, function () {
                        // success callback
                        vehicleButtons[vehicle].classList.remove('loading');

                        // vehicle is one of: cycling, driving, or walking
                        control.getRouter().options.profile = "mapbox/" + vehicle;
                        // refresh route display
                        control.route();

                        $.each(vehicleButtons, function (v, b) {
                            b.classList.remove('active');
                        });
                        vehicleButtons[vehicle].classList.add('active');
                    });

                });
            });

            vehicleButtons[defaultVehicle].classList.add('active');  // set default active button
            return container;
        }
    });

    var plan = new routingPlan(
        // Empty waypoints
        [], {
            // Default geocoder
            geocoder: L.Control.Geocoder.nominatim({ geocodingQueryParams: { countrycodes: 'ca'}}),

            // Create routes while dragging markers
            routeWhileDragging: true,

            // Add a button for reversing waypoints
            reverseWaypoints: true,

            createGeocoder: function(i, total_waypoints, plan) {
                var geocoder = L.Routing.GeocoderElement.prototype.options.createGeocoder.call(plan, i, total_waypoints, plan),
                    handle = L.DomUtil.create('div', 'geocoder-handle'),
                    geolocateBtn = L.DomUtil.create('span', 'geocoder-geolocate-btn', geocoder.container);

                handle.innerHTML = String.fromCharCode(65 + i);
                geocoder.container.insertBefore(handle, geocoder.container.firstChild);
                return geocoder;
            },

            createMarker: function(i, wp) {
                var marker;

                // adjust marker according waypoints
                if (wp.santro && !wp.hideMarker) {
                    // add awesome marker for santropol
                    marker =  L.marker([45.516564, -73.575145], {
                        draggable: false,
                        opacity: 1,
                        icon: L.AwesomeMarkers.icon({icon: 'cutlery', prefix: 'fa', markerColor: 'red', iconColor: '#f28f82'})
                    });

                    var info = "<div class='ui list'>"
                        +"<div class='item'><i class='user icon'></i> Santro </div>"
                        +"</div>"

                    marker.bindPopup(info).openPopup();

                    return marker;
                }
                else if (wp.santro) {
                  return;
                }
                else {
                    marker =  L.marker(wp.latLng, {
                        icon: L.icon.glyph({
                            prefix: '',
                            glyph: String.fromCharCode(65 + i)
                        }),
                        draggable: true
                    });

                    var info = "<div class='ui list'>"
                        +"<div class='item'><i class='user icon'></i>" + wp.options.member + "</div>"
                        +"<div class='item'><i class='home icon'></i>" + wp.options.address + "</div>"
                        +"</div>"

                    marker.bindPopup(info).openPopup();
                    return marker;
                }
            }
        }
    );

    // Extend Routing Control to build sortable geocoder
    var routingContol = L.Routing.Control.extend({
        initialize: function(map, initialWaypoints) {
            L.Routing.Control.prototype.initialize.call(this, {
                router: bikerouter,
                language: 'fr',
                showAlternatives: true,
                lineOptions: {
                    styles: [
                        {color: 'black', opacity: 0.3, weight: 11},
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
                plan: plan,
                show: false
            });
        },
    });

    // Bind control outside of the map
    control = new routingContol()
    var routeBlock = control.onAdd(map);
    $(".controls").append(routeBlock);

    var routeId = $('#route_map').attr('data-route');
    getRouteWaypoints(routeId);

    // Add sortable on the route controler
    Sortable.create(document.querySelector('.leaflet-routing-geocoders'), {
        handle: '.geocoder-handle',
        draggable: '.leaflet-routing-geocoder',
        onUpdate: function(e) {
           var oldI = e.oldIndex,
               newI = e.newIndex,
               wps = control.getWaypoints(),
               wp = wps[oldI];

           if (oldI === newI || newI === undefined) {
               return;
           }

           wps.splice(oldI, 1);
           wps.splice(newI, 0, wp);
           control.setWaypoints(wps);

           // Save the route
           save_route(control);
        }
    });
}

function save_route(control) {
    var wp = control.getWaypoints();
    var data = { route: [], members: [] };
    var routeId = $('#route_map').data('route');
    var save_url = $('#route_map').data('save-url');
    var can_save = $('#route_map').data('can-save');
    if (can_save == 'no') { return; }
    data.route.push({"id" : routeId});
    // simplify waypoint into a list of member id in the map order
    $.each(wp, function(key,value) {
        if (typeof value.options.id !== "undefined") {
            data.members.push({
                "id" : value.options.id
            });
        }
    });
    // Post simple list of members to server
    $.ajax(save_url, {
      data : JSON.stringify(data),
      contentType : 'application/json; charset=utf-8',
      type : 'POST',
      dataType: "json",
      success: function(result) {
      }
   });
}
function save_vehicle(vehicle, success_callback, error_callback) {
    var data = { route: [], vehicle: '' };
    var routeId = $('#route_map').data('route');
    var save_vehicle_url = $('#route_map').data('save-vehicle-url');
    var can_save = $('#route_map').data('can-save');
    if (can_save == 'no') { return; }
    data.route.push({"id" : routeId});
    data.vehicle = vehicle;
    // Post simple list of members to server
    $.ajax(save_vehicle_url, {
      data : JSON.stringify(data),
      contentType : 'application/json; charset=utf-8',
      type : 'POST',
      dataType: "json",
      success: success_callback,
      error: error_callback
   });
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

$(function() {
    // Add map
    if ($('#mapid').length > 0) {
        var mymap = new L.map('mapid').setView([45.516564,-73.575145], 18);
        var tileUrl = 'https://{s}.tile.thunderforest.com/cycle/{z}/{x}/{y}.png',
        layer = new L.TileLayer(tileUrl, {maxZoom: 18});
        mymap.addLayer(layer);
        // Add marker for the address
        var marker;
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
            if (results.length > 0 ) {;
                  var data = { address: results[0].name,
                               lat: results[0].center.lat,
                               long: results[0].center.lng };

                  // calculate distance between santropol and the place found
                  var dist = distance(45.516564,-73.575145, results[0].center.lat, results[0].center.lng,"K");

                  // update text field withe info
                  $('.field > .latitude').val(data.lat);
                  $('.field > .longitude').val(data.long);
                  $('.field .distance').val(dist);

                 // Add or update marker for the found address
                 if (typeof(marker)==='undefined') {
                   marker =   L.marker([ data.lat, data.long], {draggable:true});
                   marker.addTo(mymap);
                   mymap.setView([data.lat, data.long], 17);
                 }
                 else {
                    marker.setLatLng([data.lat,data.long]);
                    mymap.setView([data.lat, data.long], 17);
                 }

                  // Adjust latitude / longitude if user drag the marker
                  marker.on("dragend",function(ev){
                      var chagedPos = ev.target.getLatLng();
                      $('.field > .latitude').val(chagedPos.lat);
                      $('.field > .longitude').val(chagedPos.lng);
                      var newdist = distance(45.516564,-73.575145, chagedPos.lat,chagedPos.lng,"K")
                      $('.field > .distance').val(newdist);
                  });
            }
            else {
                alert(notFoundMsg);
            }

            // Remove the loading indicator
            $('form').removeClass('loading');
        });
    });
});
