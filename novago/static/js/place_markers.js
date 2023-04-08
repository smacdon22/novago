function place_markets(triplist) {
    const map = new google.maps.Map(document.getElementById("mapholder"), {
        center: { lat: 45.6225, lng: -61.9934 },
        maxZoon: 100,
        zoom: 10,
    });

    for (let i = 0; i < triplist.length; i++) {
        var destinationAddress = triplist[i].destination_address;

        // Use the Geocoding API to convert the address to a latitude and longitude
        var geocoder = new google.maps.Geocoder();
        geocoder.geocode({ 'address': destinationAddress }, function (results, status) {
            if (status === 'OK') {
                // Create a new marker for this destination address and add it to the map
                var marker = new google.maps.Marker({
                    position: results[0].geometry.location,
                    map: map,
                    title: destinationAddress
                });
            } else {
                console.log('Geocode was not successful for the following reason: ' + status);
            }
        })
    }
};