var x = document.getElementById("location-map");
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    }
    else { x.innerHTML = "Geolocation is not supported by this browser."; }
}

function showPosition(position) {
    var lat = position.coords.latitude;
    var lon = position.coords.longitude;
    var latlon = new google.maps.LatLng(lat, lon)
    var mapholder = document.getElementById('mapholder')
    mapholder.style.height = '100%';
    mapholder.style.width = '100%';

    var myOptions = {
        center: latlon, zoom: 14,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        mapTypeControl: false,
        navigationControlOptions: { style: google.maps.NavigationControlStyle.SMALL }
    };
    var map = new google.maps.Map(document.getElementById("mapholder"), myOptions);
    var marker = new google.maps.Marker({ position: latlon, map: map, title: "You are here!" });
}

function showError(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            x.innerHTML = "User denied the request for Geolocation."
            break;
        case error.POSITION_UNAVAILABLE:
            x.innerHTML = "Location information is unavailable."
            break;
        case error.TIMEOUT:
            x.innerHTML = "The request to get user location timed out."
            break;
        case error.UNKNOWN_ERROR:
            x.innerHTML = "An unknown error occurred."
            break;
    }
}


// the following code has been adapted from ChatGPT on Febuary 28th

function generateInitMap() {
    var map_options = {
        center: { lat: 45.6225, lng: -61.9934 },
        maxZoom: 100,
        zoom: 6,
        styles: [
            {
                featureType: 'poi',
                stylers: [{ visibility: 'off' }]
            },
            {
                featureType: 'transit',
                elementType: 'labels.icon',
                stylers: [{ visibility: 'off' }]
            }
        ]
    }
    const map = new google.maps.Map(document.getElementById("mapholder"), map_options);


    // // Get user's location and center the map on it
    // if (navigator.geolocation) {
    //     navigator.geolocation.getCurrentPosition(function (position) {
    //         const userLocation = {
    //             lat: position.coords.latitude,
    //             lng: position.coords.longitude
    //         };
    //         map.setCenter(userLocation);
    //     }, function () {
    //         console.log("Geolocation failed.");
    //     });
    // } else {
    //     console.log("Geolocation is not supported by this browser.");
    // }


    // var start_img_path = "{% static '/images/start_marker.png' %}";
    // var end_img_path = "{% static '/images/end_marker.png' %}";

    // Define custom icons for the start and end markers
    // var startIcon = {
    //     url: start_img_path, // path to your start icon image
    //     scaledSize: new google.maps.Size(50, 50), // size of the image
    //     origin: new google.maps.Point(0, 0), // position of the top-left corner of the image relative to the origin
    //     anchor: new google.maps.Point(25, 50) // position of the anchor point on the image relative to the origin
    // };

    // var endIcon = {
    //     url: end_img_path, // path to your end icon image
    //     scaledSize: new google.maps.Size(50, 50), // size of the image
    //     origin: new google.maps.Point(0, 0), // position of the top-left corner of the image relative to the origin
    //     anchor: new google.maps.Point(25, 50) // position of the anchor point on the image relative to the origin
    // };


    var directionsService = new google.maps.DirectionsService();
    function renderDirections(result) {
        var directionsRenderer = new google.maps.DirectionsRenderer();
        directionsRenderer.setMap(map);

        // Define a color palette
        var colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#FFA500', '#FFC0CB', '#800080', '#00FF7F', '#ADD8E6', '#FFFFE0', '#FA8072', '#8B0000', '#1E90FF', '#9400D3', '#FF69B4', '#FF4500', '#4B0082', '#DC143C', '#7CFC00', '#7B68EE', '#FF1493', '#00CED1', '#20B2AA', '#FF6347', '#BA55D3', '#7FFF00', '#9932CC', '#00BFFF', '#8B008B', '#FF8C00', '#FFD700', '#00FA9A', '#00FFFF', '#FFE4E1', '#FF00FF', '#FFB6C1', '#E6E6FA', '#FFFF00', '#FFA07A', '#FFC0CB', '#9400D3', '#6A5ACD', '#ADFF2F', '#FF69B4', '#FF6347', '#DA70D6', '#DB7093', '#F0E68C', '#FFA500'];


        // Pick a random color from the palette for the route
        var routeColor = colors[Math.floor(Math.random() * colors.length)];

        directionsRenderer.setDirections(result);

        // Set the start and end location markers
        var startMarker = new google.maps.Marker({
            position: result.routes[0].legs[0].start_location,
            map: map,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                fillColor: routeColor,
                fillOpacity: 1,
                strokeWeight: 0,
                scale: 8
            }
        });

        var endMarker = new google.maps.Marker({
            position: result.routes[0].legs[0].end_location,
            map: map,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                fillColor: routeColor,
                fillOpacity: 1,
                strokeWeight: 0,
                scale: 8
            }
        });

        // Set the route color
        var routeOptions = {
            polylineOptions: {
                strokeColor: routeColor
            }
        };
        directionsRenderer.setOptions(routeOptions);
    }


    function requestDirections(start, end) {
        directionsService.route({
            origin: start,
            destination: end,
            travelMode: google.maps.DirectionsTravelMode.DRIVING
        }, function (result) {
            renderDirections(result);
        });
    }

    const geocoder = new google.maps.Geocoder();
    // const bounds = new google.maps.LatLngBounds();

    // Define an array to hold all the waypoints for each trip
    const all_starting = [];
    const all_destination = [];

    // Create an array of geocode promises
    const geocodePromises = [];
    for (let i = 0; i < json_trip_list.length; i++) {

        // if there isn't already a gecoder latlng 
        const starting_address = json_trip_list[i]["starting_address"];
        const destination_address = json_trip_list[i]["destination_address"];

        // Geocode the starting address
        const geocodeStarting = new Promise((resolve, reject) => {
            geocoder.geocode({ address: starting_address }, (results, status) => {
                if (status === "OK") {
                    const starting_location = results[0].geometry.location;
                    // Add starting location to waypoints array
                    all_starting.push(starting_location);
                    resolve(starting_location);
                } else {
                    console.error("Geocode was not successful for the following reason: " + status);
                    reject(status);
                }
            });
        });

        // Geocode the destination address
        const geocodeDestination = new Promise((resolve, reject) => {
            geocoder.geocode({ address: destination_address }, (results, status) => {
                if (status === "OK") {
                    const destination_location = results[0].geometry.location;
                    // Add destination location to endpoint array
                    all_destination.push(destination_location);
                    resolve(destination_location);
                } else {
                    console.error("Geocode was not successful for the following reason: " + status);
                    reject(status);
                }
            });
        });

        // Push the geocode promises to the array
        geocodePromises.push(geocodeStarting, geocodeDestination);
    }

    // Wait for all the geocode promises to be resolved
    Promise.all(geocodePromises).then(() => {
        for (let i = 0; i < all_starting.length; i++) {
            console.log("all_starting[i]:", all_starting[i]);
            console.log("all_destination[i]:", all_destination[i]);
            requestDirections(all_starting[i], all_destination[i]);
        }
    }).catch((error) => {
        console.error(error);
    });

}


function showModal(Div){

    // Get the modal
    var modal = document.getElementById(Div)
    // Get the <span> element that closes the modal
    var close = "close" + Div
    var span = document.getElementById(close);
    
    modal.style.display = "block"



    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = "none";
    }
  
    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}

function previewProfileImage( uploader ) {   
    //ensure a file was selected 
    if (uploader.files && uploader.files[0]) {
            //set the image data as source
            $('#profile-picture').attr('src', window.URL.createObjectURL(uploader.files[0]));
        }    
    }

$("#file-input").change(function(){
    previewProfileImage( this );
});

function previewProfileImage1( uploader ) {   
    //ensure a file was selected 
    if (uploader.files && uploader.files[0]) {
            //set the image data as source
            $('#profile-picture1').attr('src', window.URL.createObjectURL(uploader.files[0]));
        }    
    }

$("#file-input1").change(function(){
    previewProfileImage1( this );
});




// function displayRouteOnMap(waypoints) {
//     // Define a DirectionsService object to get the route between all the waypoints
//     const directionsService = new google.maps.DirectionsService();

//     // Define a DirectionsRenderer object to display the route on the map
//     const directionsRenderer = new google.maps.DirectionsRenderer({ map: map });

//     // Define a request object to pass to the DirectionsService
//     const request = {
//         origin: waypoints[0].location,
//         destination: waypoints[waypoints.length - 1].location,
//         waypoints: waypoints.slice(1, waypoints.length - 1),
//         optimizeWaypoints: true,
//         travelMode: google.maps.TravelMode.DRIVING,
//     };

//     // Call the DirectionsService to get the route
//     directionsService.route(request, (result, status) => {
//         if (status === "OK") {
//             // Display the route on the map
//             directionsRenderer.setDirections(result);
//         } else {
//             console.error("Directions request failed due to " + status);
//         }
//     });
// }




// const map = new google.maps.Map(document.getElementById("mapholder"), {
//     center: { lat: 45.6225, lng: -61.9934 },
//     maxZoon: 100,
//     zoom: 10,
// });

// let marker = null;


// function addMarker(latlng) {
//     // if there is already a marker, remove it
//     if (marker) {
//         marker.setMap(null);
//     }

//     // create a marker and set its position
//     marker = new google.maps.Marker({
//         position: latlng,
//         map: map,
//         title: "Ride location",
//     });

//     // set center of the map to the marker position
//     map.setCenter(latlng);
// }

// function removeMarker() {
//     // If the marker exists, remove it from the map
//     if (marker) {
//         marker.setMap(null);
//     }
// }

// var geocoder = new google.maps.Geocoder();
// var bounds = new google.maps.LatLngBounds();
// var directionsService = new google.maps.DirectionsService();
// var directionsRenderer = new google.maps.DirectionsRenderer({ map: map });

// for (var i = 0; i < addresses.length - 1; i += 2) {
//     var start = addresses[i];
//     var end = addresses[i + 1];
//     var request = {
//         origin: start,
//         destination: end,
//         travelMode: google.maps.TravelMode.DRIVING
//     };
//     directionsService.route(request, function (result, status) {
//         if (status == "OK") {
//             setTimeout(function () {
//                 // code to execute after delay
//                 directionsRenderer.setDirections(result);
//                 bounds.union(result.routes[0].bounds);
//                 map.fitBounds(bounds);
//             }, 3000); // 3000 milliseconds = 3 seconds
//         } else {
//             console.log("Directions request failed due to " + status);
//         }
//     });
// }

// function handleLocationError(browserHasGeolocation, pos) {
//     const infoWindow = new google.maps.InfoWindow();
//     infoWindow.setPosition(pos);
//     infoWindow.setContent(
//         browserHasGeolocation
//             ? "Error: The Geolocation service failed."
//             : "Error: Your browser doesn't support geolocation."
//     );
//     infoWindow.open(map);
// }

// if (navigator.geolocation) {
//     navigator.geolocation.getCurrentPosition(
//         (position) => {
//             const pos = {
//                 lat: position.coords.latitude,
//                 lng: position.coords.longitude,
//             };
//             addMarker(pos);
//         },
//         () => {
//             handleLocationError(true, map.getCenter());
//         }
//     );
// } else {
//     handleLocationError(false, map.getCenter());
// }



console.log(json_trip_list);


