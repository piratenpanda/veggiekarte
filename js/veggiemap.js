// To close the infomation window per click on the x.
function closeinfo() {
  close = document.getElementsByClassName("information");
  close[0].style.display = "none";
}

// Define marker groups
var parentGroup = L.markerClusterGroup({showCoverageOnHover: false, maxClusterRadius: 35});
var vegan = L.featureGroup.subGroup(parentGroup, {});
var veggie = L.featureGroup.subGroup(parentGroup, {});

function veggiemap() {

  // TileLayer
  var tileOSM = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; <a href='https://openstreetmap.org'>OpenStreetMap</a> contributors, <a href='https://creativecommons.org/licenses/by-sa/2.0/'>CC-BY-SA</a>",
    maxZoom: 18
  });

  // Map
  var map = L.map("map", {
    layers: [tileOSM],
    center: [51.43,17.58],
    zoom: 4,
    worldCopyJump: true
  });

  // Define overlays (each marker group gets a layer) + add legend to the description
  var overlays = {
    "<div class='legendRow' title='Place which offers vegan food.'><div class='firstCell vegan'></div><div class='secondCell'>vegan</div></div>" : vegan,
    "<div class='legendRow' title='Place which offers vegetarian but no vegan food.'><div class='firstCell veggie'></div><div class='secondCell'>veggie</div></div>"  : veggie
  };

  // Add marker groups to the map
  vegan.addTo(map);
  veggie.addTo(map);

  veggiemap_populate(parentGroup);

  // Add the parent marker group to the map
  parentGroup.addTo(map);

  // Add hash to the url
  var hash = new L.Hash(map);

  // Add info button
  L.control.info().addTo(map);

  // Add button for search places
  L.Control.geocoder({
    placeholder: 'Nach Ortsnamen suchen...',
    errorMessage: 'Nichts gefunden.'
  }).addTo(map);

  // Add button to search own position
  L.control.locate({
    strings: {
      title: "Standort ermitteln",
      metersUnit: "Meter",
      popup: "Du befindest dich maximal {distance} {unit} entfernt von diesem Punkt."
    },
    locateOptions: {maxZoom: 16}
  }).addTo(map);

  // Add layer control button
  L.control.layers(null, overlays).addTo(map);
}
