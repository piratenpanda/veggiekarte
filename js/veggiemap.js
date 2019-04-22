// To close the infomation window per click on the x.
function closeinfo() {
  close = document.getElementsByClassName("information");
  close[0].style.display = "none";
}

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

  // add info button
  L.control.info().addTo(map);        

  var markers = new L.MarkerClusterGroup({showCoverageOnHover: false, maxClusterRadius: 32});

  veggiemap_populate(markers);

  map.addLayer(markers);

  // add hash to the url
  var hash = new L.Hash(map);

  // add button for search places
  L.Control.geocoder({
	placeholder: 'Nach Ortsnamen suchen...',
	errorMessage: 'Nichts gefunden'
  }).addTo(map);

  // add button to search own position
  L.control.locate({
    strings: {
      title: "Standort ermitteln",
      metersUnit: "Meter",
      popup: "Du befindest dich maximal {distance} {unit} entfernt von diesem Punkt."
    },
    locateOptions: {maxZoom: 16}
  }).addTo(map);
}
