let autocomplete;
function initAutocomplete() {
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('autocomplete'),
        {
            types: ['street_address'],
            componentRestrictions: { country: 'ca' }
        });

    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('autocomplete1'),
        {
            types: ['street_address'],
            componentRestrictions: { country: 'ca' }
        });

    autocomplete.addListener('place_changed', fillInAddress);
}

function fillInAddress() {
    var place = autocomplete.getPlace();
    if (!place.geometry) {

        document.getElementById('autocomplete').innerHTML = '';
    }
    else {
        document.getElementById('autocomplete').innerHTML = place.name;
    }
}