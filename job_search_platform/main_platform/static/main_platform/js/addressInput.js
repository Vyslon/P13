// This sample uses the Places Autocomplete widget to:
// 1. Help the user select a place
// 2. Retrieve the address components associated with that place
// 3. Populate the form fields with those address components.
// This sample requires the Places library, Maps JavaScript API.
// Include the libraries=places parameter when you first load the API.
// For example: <script
// src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places">
let autocomplete;
let addressField;
let latitudeField;
let longitudeField;

function initAutocomplete() {
  addressField = document.querySelector("#addressInput");
  latitudeField = document.querySelector("#latitude");
  longitudeField = document.querySelector("#longitude");
  // Create the autocomplete object, restricting the search predictions to
  // addresses in the FR.
  autocomplete = new google.maps.places.Autocomplete(addressField, {
    componentRestrictions: { country: ["fr"] },
    fields: ["address_components", "geometry"],
    types: ["address"],
  });
  addressField.focus();
  // When the user selects an address from the drop-down, populate the
  // address fields in the form.
  autocomplete.addListener("place_changed", fillInAddress);
}

function fillInAddress() {
  // Get the place details from the autocomplete object.
  const place = autocomplete.getPlace();
  let latitude = "";
  let longitude = "";
  let address = "";

  // Get each component of the address from the place details,
  // and then fill-in the corresponding field on the form.
  // place.address_components are google.maps.GeocoderAddressComponent objects
  // which are documented at http://goo.gle/3l5i5Mr
  document.getElementById('latitude').value = place.geometry.location.lat();
  document.getElementById('longitude').value = place.geometry.location.lng();

  for (const component of place.address_components) {
    const componentType = component.types[0];

    switch (componentType) {
      case "street_number": {
        address = `${component.long_name} ${address}`;
        break;
      }

      case "route": {
        address += component.short_name;
        break;
      }

        addressField.value = address;
    }
  }
}