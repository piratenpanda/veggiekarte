// To close the infomation window per click on the x.
function closeinfo() {
  close = document.getElementsByClassName("information");
  close[0].style.display = "none";
}

// Define marker groups
var parentGroup = L.markerClusterGroup({showCoverageOnHover: false, maxClusterRadius: 20});
var vegan_only = L.featureGroup.subGroup(parentGroup, {});
var vegetarian_only = L.featureGroup.subGroup(parentGroup, {});
var vegan_friendly = L.featureGroup.subGroup(parentGroup, {});
var vegan_limited = L.featureGroup.subGroup(parentGroup, {});
var vegetarian_friendly = L.featureGroup.subGroup(parentGroup, {});

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
    "<div class='legendRow' title='Place which offers only vegan food.'><div class='firstCell vegan_only'></div><div class='secondCell'>vegan only</div></div>" : vegan_only,
    "<div class='legendRow' title='Place which offers only vegetarian and vegan food.'><div class='firstCell vegetarian_only'></div><div class='secondCell'>vegetarian only + vegan</div></div>"  : vegetarian_only,
    "<div class='legendRow' title='Place which offers also vegan food.'><div class='firstCell vegan_friendly'></div><div class='secondCell'>vegan friendly</div></div>" : vegan_friendly,
    "<div class='legendRow' title='Place with limited vegan offer (usualy that means, you have to ask for it).'><div class='firstCell vegan_limited'></div><div class='secondCell'>vegan limited</div></div>"  : vegan_limited,
    "<div class='legendRow' title='Place which offers also vegetarian food, but no vegan.'><div class='firstCell vegetarian_friendly'></div><div class='secondCell'>vegetarian friendly</div></div>" : vegetarian_friendly
  };

  // Add marker groups to the map
  vegan_only.addTo(map);
  vegetarian_only.addTo(map);
  vegan_friendly.addTo(map);
  vegetarian_friendly.addTo(map);
  vegan_limited.addTo(map);

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
