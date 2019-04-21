// To close the infomation window per click on the x.
function closeinfo() {
  close = document.getElementsByClassName("information");
  close[0].style.display = "none";
}

function getURLParameter(name) {
  return decodeURI((RegExp(name + "=" + "(.+?)(&|$)").exec(location.search)||[,])[1]);
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

  var regionParameter = getURLParameter("region");
  var region = (regionParameter === "undefined") ? "" : regionParameter;

  // add info button
  L.control.info().addTo(map);        

  function onLocationFound(e){
    var radius = e.accuracy / 2;
    L.marker(e.latlng).addTo(map)
    var circle = L.circle(e.latlng, 800, {
      color: "blue",
      stroke: false,
      //fillColor: '#f03',
      fillOpacity: 0.1
    }).addTo(map);
  }

  var markers = new L.MarkerClusterGroup({showCoverageOnHover: false, maxClusterRadius: 32});

  veggiemap_populate(markers);

  map.addLayer(markers);

  // add hash to the url
  var hash = new L.Hash(map);

  // add search field
  L.Control.geocoder({
	placeholder: 'Nach Ortsnamen suchen...',
	errorMessage: 'Nichts gefunden'
  }).addTo(map);

  // add position search field
  L.control.locate({
    strings: {
      title: "Standort ermitteln",
      metersUnit: "Meter",
      popup: "Du befindest dich maximal {distance} {unit} entfernt von diesem Punkt."
    },
  }).addTo(map);
}
