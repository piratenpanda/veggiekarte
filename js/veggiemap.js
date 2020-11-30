// The "use strict" directive helps to write cleaner code.
"use strict";

// Define marker groups
let parentGroup = L.markerClusterGroup({showCoverageOnHover: false, maxClusterRadius: 20});
let vegan_only = L.featureGroup.subGroup(parentGroup, {});
let vegetarian_only = L.featureGroup.subGroup(parentGroup, {});
let vegan_friendly = L.featureGroup.subGroup(parentGroup, {});
let vegan_limited = L.featureGroup.subGroup(parentGroup, {});
let vegetarian_friendly = L.featureGroup.subGroup(parentGroup, {});
let subgroups = { vegan_only, vegetarian_only, vegan_friendly, vegan_limited, vegetarian_friendly };
let map;


function veggiemap() {

  // TileLayer
  let tileOSM = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; <a href='https://openstreetmap.org'>OpenStreetMap</a> contributors, <a href='https://creativecommons.org/licenses/by-sa/2.0/'>CC-BY-SA</a>",
    maxZoom: 18
  });

  // Map
  map = L.map("map", {
    layers: [tileOSM],
    center: [51.43, 17.58],
    zoom: 4,
    worldCopyJump: true
  });

  // Define overlays (each marker group gets a layer) + add legend to the description
  let overlays = {
    "<div class='legendRow' title='Place which offers only vegan food.'><div class='firstCell vegan_only'></div><div class='secondCell'>vegan only</div><div class='thirdCell' id='n_vegan_only'></div></div>" : vegan_only,
    "<div class='legendRow' title='Place which offers only vegetarian and vegan food.'><div class='firstCell vegetarian_only'></div><div class='secondCell'>vegetarian only + vegan</div><div class='thirdCell' id='n_vegetarian_only'></div></div>" : vegetarian_only,
    "<div class='legendRow' title='Place which offers also vegan food.'><div class='firstCell vegan_friendly'></div><div class='secondCell'>vegan friendly</div><div class='thirdCell' id='n_vegan_friendly'></div></div>" : vegan_friendly,
    "<div class='legendRow' title='Place with limited vegan offer (usualy that means, you have to ask for it).'><div class='firstCell vegan_limited'></div><div class='secondCell'>vegan limited</div><div class='thirdCell' id='n_vegan_limited'></div></div>" : vegan_limited,
    "<div class='legendRow' title='Place which offers also vegetarian food, but no vegan.'><div class='firstCell vegetarian_friendly'></div><div class='secondCell'>vegetarian friendly</div><div class='thirdCell' id='n_vegetarian_friendly'></div></div><br /><br /><div id='date'></div>" : vegetarian_friendly
  };

  // Add marker groups to the map
  vegan_only.addTo(map);
  vegetarian_only.addTo(map);
  vegan_friendly.addTo(map);
  vegan_limited.addTo(map);
  vegetarian_friendly.addTo(map);

  veggiemap_populate(parentGroup);

  // Add the parent marker group to the map
  parentGroup.addTo(map);

  // Enable the on-demand popup and tooltip calculation
  parentGroup.bindPopup(calculatePopup);
  parentGroup.bindTooltip(calculateTooltip);

  // Add hash to the url
  let hash = new L.Hash(map);

  // Add info button
  L.easyButton('fa-info', function(btn, map){
    toggleInfo();
  }, 'Information').addTo(map);

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

// Function to toogle the visibility of the Info box.
function toggleInfo() {
  let element = document.getElementById('information');    // get the element of the information window
  let computedStyle = window.getComputedStyle(element);    // get the actual style information
    if (computedStyle.display != "block") {
      element.style.display = "block";
    }
    else {
      element.style.display = "none";
    }
}

// Function to put the numbers of markers into the legend.
//   The numbers are calculated using the refresh.py script and stored in the places.json file.
function stat_populate() {

    const url = "data/stat.json";

    fetch(url)
    .then(response => response.json())
    .then(data => onEachFeatureStat(data))
    .catch(error  => {console.log('Request failed', error);});
}

function onEachFeatureStat(data) {

  for (let x in data.stat[data.stat.length -1]){
    document.getElementById(x).innerHTML = data.stat[data.stat.length -1][x];
  }
}

// Function to get the information from the places json file.
function veggiemap_populate(parentGroup) {
    const url = "data/places.json";

    fetch(url)
    .then(response => response.json())
    .then(data => geojsonToMarkerGroups(data))
    .then(markerGroups => {
        map.removeLayer(parentGroup);
        Object.entries(subgroups).forEach(([key, subgroup]) => {
            map.removeLayer(subgroup);
            subgroup.clearLayers();
            // Bulk add all the markers from a markerGroup to a subgroup in one go
            // Source: https://github.com/ghybs/Leaflet.FeatureGroup.SubGroup/issues/5
            subgroup.addLayer(L.layerGroup(markerGroups[key]));
            map.addLayer(subgroup);
        });
        // Reveal all the markers and clusters on the map in one go
        map.addLayer(parentGroup);
    })
    .catch(error  => {console.log('Request failed', error);});
}

// Process the places GeoJSON into the groups of markers
function geojsonToMarkerGroups(data) {
    const groups = {};
    data.features.forEach(feature => {
        const eCat = feature.properties.category;
        if (!groups[eCat]) groups[eCat] = [];
        groups[eCat].push(onEachFeature(feature));
    });
    return groups;
}

// Function to handle the places data.
function onEachFeature(feature) {
    let eLatLon = [feature.geometry.coordinates[1],feature.geometry.coordinates[0]];
    let eSym = feature.properties.symbol;
    let eNam = feature.properties.name;
    let eIco = feature.properties.icon;
    let eCat = feature.properties.category;

    let marker = L.marker(eLatLon, { icon: getIcon(eIco, eCat) });
    marker.feature = feature;
    return marker;
}

// Calculate tooltip content for a given marker layer
function calculateTooltip(layer) {
    let feature = layer.feature;
    let eSym = feature.properties.symbol;
    let eNam = feature.properties.name;
    return eSym + " " + eNam;
}

// Calculate popup content for a given marker layer
function calculatePopup(layer) {
    // Get the Information
    let feature = layer.feature;
    let eId  = feature.properties._id;
    let eLatLon = [feature.geometry.coordinates[1],feature.geometry.coordinates[0]];
    let eNam = feature.properties.name;
    let eTyp = feature.properties._type;
    let eCit = feature.properties.addr_city;
    let eCou = feature.properties.addr_country;
    let ePos = feature.properties.addr_postcode;
    let eStr = feature.properties.addr_street;
    let eCat = feature.properties.category;
    let eEma = feature.properties.contact_email;
    let ePho = feature.properties.contact_phone;
    let eWeb = feature.properties.contact_website;
    let eCui = feature.properties.cuisine;
    let eIco = feature.properties.icon;
    let eInf = feature.properties.more_info;
    let eOpe = feature.properties.opening_hours;
    let eSym = feature.properties.symbol;

    /*** Building the popup content ***/
    let popupContent = "<b>" + eSym + " " + eNam + "</b> "; // Symbol and name
    popupContent += "<a href=\"https://openstreetmap.org/"+eTyp+"/"+eId+"\" target=\"_blank\">*</a><hr/>"; // OSM link

    // Adding cuisine information to popup
    if(eCui!=undefined){popupContent += "<div class='popupflex-container'><div>👩‍🍳</div><div>" + eCui +"</div></div>"}

    // Address
    let eAddr = ""
    // Collecting address information
    if(eStr!=undefined){eAddr += eStr +"<br/>"} // Street
    if(ePos!=undefined){eAddr += ePos +" "}     // Postcode
    if(eCit!=undefined){eAddr += eCit +" "}     // City
    // if(eCou!=undefined){eAddr += eCou}       // Country

    // Adding address information to popup
    if(eAddr!=""){popupContent += "<div class='popupflex-container'><div>📍</div><div>" + eAddr +"</div></div>"}

    // Adding addidtional information to popup
    if(eOpe!=undefined){popupContent += "<div class='popupflex-container'><div>🕖</div><div>" + eOpe +"</div></div>"}
    if(ePho!=undefined){popupContent += "<div class='popupflex-container'><div>☎️</div><div><a href=\"tel:" + ePho + "\" target=\"_blank\">" + ePho + "</a></div></div>"}
    if(eEma!=undefined){popupContent += "<div class='popupflex-container'><div>📧</div><div><a href=\"mailto:" + eEma + "\" target=\"_blank\">" + eEma + "</a></div></div>"}
    if(eWeb!=undefined){popupContent += "<div class='popupflex-container'><div>🌐</div><div><a href=\"" + eWeb + "\" target=\"_blank\">" + eWeb + "</a></div></div>"}
    if(eInf){popupContent += "<hr/><div class='popupflex-container'><div>ℹ️</div><div><a href=\"https://www.vegan-in-halle.de/wp/leben/vegane-stadtkarte/#"+eTyp+eId+"\" target=\"_top\">Mehr Infos</a></div>"}

    return popupContent;
}

// Main function to put the markers to the map
veggiemap();

// Call the function to put the numbers into the legend
stat_populate();
