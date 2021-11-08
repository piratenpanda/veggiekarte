// The "use strict" directive helps to write cleaner code.
"use strict";


/* Definition (polyfill) for the function replaceAll
   for older browser versions (before 2020)
   Can be removed after some years. */
if (!String.prototype.replaceAll) {
  String.prototype.replaceAll = function(old_str, new_str) {
    return this.replace(new RegExp(old_str, 'g'), new_str);
  };
}

// Define marker groups
let parentGroup = L.markerClusterGroup({ showCoverageOnHover: false, maxClusterRadius: 20 });
let vegan_only = L.featureGroup.subGroup(parentGroup, {});
let vegetarian_only = L.featureGroup.subGroup(parentGroup, {});
let vegan_friendly = L.featureGroup.subGroup(parentGroup, {});
let vegan_limited = L.featureGroup.subGroup(parentGroup, {});
let vegetarian_friendly = L.featureGroup.subGroup(parentGroup, {});
let subgroups = { vegan_only, vegetarian_only, vegan_friendly, vegan_limited, vegetarian_friendly };

let map;
let locate_control;
let fullscreenControl;
let layerControl;
let languageControl;


function veggiemap() {

  // TileLayer
  let tileOSM = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap contributors</a>",
    maxZoom: 18
  });

  // Map
  map = L.map("map", {
    layers: [tileOSM],
    center: [20, 17],
    zoom: 3,
    worldCopyJump: true,
    zoomControl: false
  });

  // Add zoom control
  L.control.zoom({ position: 'topright' }).addTo(map);

  // Define overlays (each marker group gets a layer) + add legend to the description
  let overlays = {
    "<div class='legendRow'><div class='firstCell vegan_only'></div><div class='secondCell'></div><div class='thirdCell' id='n_vegan_only'></div></div>": vegan_only,
    "<div class='legendRow'><div class='firstCell vegetarian_only'></div><div class='secondCell'></div><div class='thirdCell' id='n_vegetarian_only'></div></div>": vegetarian_only,
    "<div class='legendRow'><div class='firstCell vegan_friendly'></div><div class='secondCell'></div><div class='thirdCell' id='n_vegan_friendly'></div></div>": vegan_friendly,
    "<div class='legendRow'><div class='firstCell vegan_limited'></div><div class='secondCell'></div><div class='thirdCell' id='n_vegan_limited'></div></div>": vegan_limited,
    "<div class='legendRow'><div class='firstCell vegetarian_friendly'></div><div class='secondCell'></div><div class='thirdCell' id='n_vegetarian_friendly'></div></div>": vegetarian_friendly
  };

  veggiemap_populate(parentGroup);

  // Enable the on-demand popup and tooltip calculation
  parentGroup.bindPopup(calculatePopup);
  parentGroup.bindTooltip(calculateTooltip);

  // Close the tooltip when opening the popup
  parentGroup.on("click", function(e) {
    if (parentGroup.isPopupOpen()) {
      parentGroup.closeTooltip();
    }
  })

  // Add hash to the url
  let hash = new L.Hash(map);

  // Add fullscreen control button
  fullscreenControl = new L.Control.Fullscreen({
    position: 'topright',
  });
  fullscreenControl.addTo(map);

  // Add info button
  let infoButton = L.easyButton(
    '<div class="info-button"></div>',
    function(btn, map) { toggleInfo() }
  ).addTo(map);
  infoButton.setPosition('topright');

  // Add button for search places
  L.Control.geocoder().addTo(map);

  // Add button to search own position
  locateControl = L.control.locate({
    icon: 'locate_icon',
    iconLoading: 'loading_icon',
    showCompass: true,
    locateOptions: { maxZoom: 16 },
    position: 'topright'
  }).addTo(map);

  // Add language control button
  languageControl = L.languageSelector({
    languages: [
      L.langObject('de', 'de - Deutsch',   './third-party/leaflet.languageselector/images/de.svg'),
      L.langObject('en', 'en - English',   './third-party/leaflet.languageselector/images/en.svg'),
      L.langObject('eo', 'eo - Esperanto', './third-party/leaflet.languageselector/images/eo.svg'),
      L.langObject('fi', 'fi - suomi',     './third-party/leaflet.languageselector/images/fi.svg'),
      L.langObject('fr', 'fr - Français',  './third-party/leaflet.languageselector/images/fr.svg')
    ],
    callback: changeLanguage,
    vertical: false,
    button: true
  });
  languageControl.addTo(map);

  // Add layer control button
  layerControl = L.control.layers(null, overlays);
  layerControl.addTo(map);

  // Add scale control
  L.control.scale().addTo(map);
}


/**
 * Add or replace the language parameter of the URL and reload the page.
 * @param String id of the language
 */
function changeLanguage(selectedLanguage) {
  window.location.href = updateURLParameter(window.location.href, 'lang', selectedLanguage);
}

/**
 * Add or replace a parameter (with value) in the given URL.
 * @param String url the URL
 * @param String param the parameter
 * @param String paramVal the value of the parameter
 * @return String the changed URL
 */
function updateURLParameter(url, param, paramVal) {
  let theAnchor = null;
  let newAdditionalURL = "";
  let tempArray = url.split("?");
  let baseURL = tempArray[0];
  let additionalURL = tempArray[1];
  let temp = "";

  if (additionalURL) {
    let tmpAnchor = additionalURL.split("#");
    let theParams = tmpAnchor[0];
    theAnchor = tmpAnchor[1];
    if (theAnchor) {
      additionalURL = theParams;
    }

    tempArray = additionalURL.split("&");

    for (let i = 0; i < tempArray.length; i++) {
      if (tempArray[i].split('=')[0] != param) {
        newAdditionalURL += temp + tempArray[i];
        temp = "&";
      }
    }
  } else {
    let tmpAnchor = baseURL.split("#");
    let theParams = tmpAnchor[0];
    theAnchor = tmpAnchor[1];

    if (theParams) {
      baseURL = theParams;
    }
  }
  let rows_txt = temp + "" + param + "=" + paramVal;
  return baseURL + "?" + newAdditionalURL + rows_txt;
}



// Function to toogle the visibility of the Info box.
function toggleInfo() {
  let element = document.getElementById('information'); // get the element of the information window
  let computedStyle = window.getComputedStyle(element); // get the actual style information
  if (computedStyle.display != "block") {
    element.style.display = "block";
  } else {
    element.style.display = "none";
  }
}


// Function to hide the spinner.
function hideSpinner() {
  let element = document.getElementById('spinner');
  element.style.display = "none";
}


/**
 * Function to detect the number of markers for each category and
 * add them to the Layer Control.
 *
 * @param {object} markerGroups The marker groups.
 * @param {string} date The date when the data was queried.
 */
function stat_populate(markerGroups, date) {
  // Get all categories
  let markerGroupCategories = Object.keys(markerGroups);
  // Go through the list of categories
  for (let i = 0; i < markerGroupCategories.length; i++) {
    // Get the name
    let categoryName = markerGroupCategories[i];
    // Get the number of the markers
    let markerNumber = markerGroups[categoryName].length;
    // Add the number to the category entry in the Layer Control
    document.getElementById("n_" + categoryName).innerHTML = "(" + markerNumber + ")";
  }
  // Add the date to the Layer Control
  let lastEntry = document.getElementById("n_vegetarian_friendly").parentNode.parentNode;
  lastEntry.innerHTML += "<br /><div>(" + date + ")</div>";
}


// Function to get the information from the places json file.
function veggiemap_populate(parentGroup) {
  const url = "data/places.min.json";
  fetch(url)
    .then(response => response.json())
    .then(geojson => geojsonToMarkerGroups(geojson))
    .then(markerGroupsAndDate => {
      let markerGroups = markerGroupsAndDate[0];
      let date = markerGroupsAndDate[1];
      Object.entries(subgroups).forEach(([key, subgroup]) => {
        // Bulk add all the markers from a markerGroup to a subgroup in one go
        // Source: https://github.com/ghybs/Leaflet.FeatureGroup.SubGroup/issues/5
        subgroup.addLayer(L.layerGroup(markerGroups[key]));
        map.addLayer(subgroup);
      });

      // Reveal all the markers and clusters on the map in one go
      map.addLayer(parentGroup);

      // Call the function to put the numbers into the legend
      stat_populate(markerGroups, date);

      // Hide spinner
      hideSpinner();

      // Update translations
      updateContent();
    })
    .catch(error => { console.error('Request failed', error); });
}

// Process the places GeoJSON into the groups of markers
function geojsonToMarkerGroups(geojson) {
  let date = geojson._timestamp.split(" ")[0];
  let groups = {};
  geojson.features.forEach(feature => {
    let eCat = feature.properties.category;
    if (!groups[eCat]) groups[eCat] = [];
    groups[eCat].push(getMarker(feature));
  });
  return [groups, date];
}


// Function to get the marker.
function getMarker(feature) {
  let eLatLon = [feature.geometry.coordinates[1], feature.geometry.coordinates[0]];
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


/**
 * Check if there is an entry for a place (feature) on https://lib.reviews/.
 * @param  {Object} feature
 */
function addLibReview(feature) {
  const url = 'https://lib.reviews/api/thing?url=https://www.openstreetmap.org/' + feature.properties._type + '/' + feature.properties._id;
  fetch(url)
    .then(response => response.json())
    .then(data => document.getElementById('libreviews').innerHTML = '<div class="popupflex-container"><div>📓</div><div><a href="https://lib.reviews/' + data.thing.urlID + '" target="_blank" rel="noopener noreferrer">' + i18next.t('words.review') + '</a></div>')
    .catch(error => {
      console.info("There is no review of this place or lib.reviews isn't available.");
    });
}


// Calculate popup content for a given marker layer
function calculatePopup(layer) {
  // Get the information
  let feature = layer.feature;
  let eId  = feature.properties._id;
  let eLatLon = [feature.geometry.coordinates[1], feature.geometry.coordinates[0]];
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
  let eFac = feature.properties.contact_facebook;
  let eIns = feature.properties.contact_instagram;
  let eCui = feature.properties.cuisine;
  let eIco = feature.properties.icon;
  let eOpe = feature.properties.opening_hours;
  let eSym = feature.properties.symbol;

  /*** Building the popup content ***/
  let popupContent = "<div class='mapPopupTitle'>" + eSym + " " + eNam; // Symbol and name
  let osmUrl = "https://openstreetmap.org/" + eTyp + "/" + eId;
  popupContent += "<a href='" + osmUrl + "' target='_blank' rel='noopener noreferrer'> *</a></div><hr/>"; // OSM link

  // Adding cuisine information to popup
  if (eCui != undefined) { popupContent += "<div class='popupflex-container'><div>👩‍🍳</div><div>" + eCui.replaceAll(";", ", ").replaceAll("_", " ") + "</div></div>" }

  // Address
  let eAddr = "";
  // Collecting address information
  if (eStr != undefined) { eAddr += eStr + "<br/>" } // Street
  if (ePos != undefined) { eAddr += ePos + " " }     // Postcode
  if (eCit != undefined) { eAddr += eCit + " " }     // City
  if (eCou != undefined) { eAddr += "<br/>" + eCou } // Country

  // Adding address information to popup
  if (eAddr != "") { popupContent += "<div class='popupflex-container'><div>📍</div><div>" + eAddr + "</div></div>" }

  // Adding opening hours to popup
  if (eOpe != undefined) {
    // Country: Germany
    let country_code = 'de';
    // State: Sachsen-Anhalt
    let state = 'Sachsen-Anhalt';
    // Get browser language for the warnings and the prettifier
    let locale = userLanguage; // userLanguage is defined in i18n.js

    //Create opening_hours object
    let oh = new opening_hours(eOpe, {
      'address': { 'country_code': country_code, 'state': state }
    }, { 'locale': locale });
    let prettified_value = oh.prettifyValue({ conf: { 'locale': locale, 'rule_sep_string': '<br />', 'print_semicolon': false, 'sep_one_day_between': ', ' } });
    prettified_value = prettified_value.replaceAll(',', ', ').replaceAll('PH', i18next.t('words.public_holiday')).replaceAll('SH', i18next.t('words.school_holidays'));
    // Find out the open state
    let open_state = '';
    let open_state_emoji = '';
    if (oh.getState()) {
      open_state = i18next.t('words.open');
      open_state_emoji = 'open';
      if (!oh.getFutureState()) {
        open_state += i18next.t('texts.will close soon');
        open_state_emoji = 'closes_soon';
      }
    } else {
      open_state = i18next.t('words.closed');
      open_state_emoji = 'closed';
      if (oh.getFutureState()) {
        open_state += i18next.t('texts.will open soon');
        open_state_emoji = 'opens_soon';
      }
    }
    // Append opening hours to the popup
    popupContent += "<div class='popupflex-container'><div>🕖</div><div><span class='open_state_circle " + open_state_emoji + "'></span>" + open_state + "<br />" + prettified_value + "</div></div>";
  }

  // Adding addidtional information to popup
  if (ePho != undefined) {
    // Split the value for the case that there are more then one phone number
    ePho = ePho.split(";");
    popupContent += "<div class='popupflex-container'><div>☎️</div><div><a href='tel:" + ePho[0] + "' target='_blank' rel='noopener noreferrer'>" + ePho[0] + "</a></div></div>";
    if (ePho[1] != undefined) {
      popupContent += "<div class='popupflex-container'><div></div><div><a href='tel:" + ePho[1] + "' target='_blank' rel='noopener noreferrer'>" + ePho[1] + "</a></div></div>";
    }
  }
  if (eEma != undefined) { popupContent += "<div class='popupflex-container'><div>📧</div><div><a href='mailto:" + eEma + "' target='_blank' rel='noopener noreferrer'>" + eEma + "</a></div></div>" }
  if (eWeb != undefined) { popupContent += "<div class='popupflex-container'><div>🌐</div><div><a href='" + eWeb + "' target='_blank' rel='noopener noreferrer'>" + eWeb.replace("https://", "") + "</a></div></div>" }
  if (eFac != undefined) { popupContent += "<div class='popupflex-container'><div>🇫</div><div><a href='" + eFac + "' target='_blank' rel='noopener noreferrer'>" + decodeURI(eFac).replace("https://", "") + "</a></div></div>" }
  if (eIns != undefined) { popupContent += "<div class='popupflex-container'><div>📸</div><div><a href='" + eIns + "' target='_blank' rel='noopener noreferrer'>" + eIns.replace("https://", "") + "</a></div></div>" }

  // Add review entry from lib.reviews if exists
  popupContent += "<div id='libreviews'></div>";
  addLibReview(feature);

  return popupContent;
}


// Adding function for opening_hours objects to check if place will be open after n minutes (60 minutes as default)
if (!opening_hours.prototype.getFutureState) {
  opening_hours.prototype.getFutureState = function(minutes = 60) {
    let nowPlusHours = new Date();
    nowPlusHours.setUTCMinutes(nowPlusHours.getUTCMinutes() + minutes);
    return this.getState(nowPlusHours);
  };
}


// Main function
veggiemap();
