/* eslint-disable no-return-assign */
/* global L */

// Define marker groups
const parentGroup = L.markerClusterGroup({
  showCoverageOnHover: false,
  maxClusterRadius: 20
});
const issueCount1 = L.featureGroup.subGroup(parentGroup, {});
const issueCount2 = L.featureGroup.subGroup(parentGroup, {});
const issueCount3 = L.featureGroup.subGroup(parentGroup, {});
const issueCount4 = L.featureGroup.subGroup(parentGroup, {});
const issueCount5 = L.featureGroup.subGroup(parentGroup, {});
const issueCount6 = L.featureGroup.subGroup(parentGroup, {});
const issueCountMany = L.featureGroup.subGroup(parentGroup, {});
const subgroups = {
  issue_count_1: issueCount1,
  issue_count_2: issueCount2,
  issue_count_3: issueCount3,
  issue_count_4: issueCount4,
  issue_count_5: issueCount5,
  issue_count_6: issueCount6,
  issue_count_many: issueCountMany
};

let map;

function veggiemap() {
  // TileLayer
  const tileOSM = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap contributors</a>",
    maxZoom: 18
  });

  // Map
  map = L.map("map", {
    layers: [tileOSM],
    center: [51.42, 12.0],
    zoom: 11,
    worldCopyJump: true,
    zoomControl: false
  });

  // Add zoom control
  L.control.zoom({ position: "topright" }).addTo(map);

  // Define overlays (each marker group gets a layer) + add legend to the description
  const overlays = {
    "<div class='legend-row'><div class='second-cell'>1 issue</div><div class='third-cell' id='issue_count_1'></div></div>": issueCount1,
    "<div class='legend-row'><div class='second-cell'>2 issues</div><div class='third-cell' id='issue_count_2'></div></div>": issueCount2,
    "<div class='legend-row'><div class='second-cell'>3 issues</div><div class='third-cell' id='issue_count_3'></div></div>": issueCount3,
    "<div class='legend-row'><div class='second-cell'>4 issues</div><div class='third-cell' id='issue_count_4'></div></div>": issueCount4,
    "<div class='legend-row'><div class='second-cell'>5 issues</div><div class='third-cell' id='issue_count_5'></div></div>": issueCount5,
    "<div class='legend-row'><div class='second-cell'>6 issues</div><div class='third-cell' id='issue_count_6'></div></div>": issueCount6,
    "<div class='legend-row'><div class='second-cell'>more than 6</div><div class='third-cell' id='issue_count_many'></div></div>": issueCountMany
  };

  veggiemapPopulate(parentGroup);

  // Close the tooltip when opening the popup
  parentGroup.on("click", () => {
    if (parentGroup.isPopupOpen()) {
      parentGroup.closeTooltip();
    }
  });

  // Add hash to the url
  // eslint-disable-next-line no-unused-vars
  const hash = new L.Hash(map);

  // Add info button
  const infoButton = L.easyButton('<div class="info-button"></div>', () => {
    toggleInfo();
  }).addTo(map);
  infoButton.setPosition("topright");

  // Add button for search places
  L.Control.geocoder().addTo(map);

  // Add button to search own position
  L.control
    .locate({
      showCompass: true,
      locateOptions: { maxZoom: 16 },
      position: "topright"
    })
    .addTo(map);

  // Add layer control button
  L.control.layers(null, overlays).addTo(map);
}

// Function to toogle the visibility of the Info box.
function toggleInfo() {
  const element = document.getElementById("information"); // get the element of the information window
  const computedStyle = window.getComputedStyle(element); // get the actual style information
  if (computedStyle.display !== "block") {
    element.style.display = "block";
  } else {
    element.style.display = "none";
  }
}

// Function to hide the spinner.
function hideSpinner() {
  const element = document.getElementById("spinner");
  element.style.display = "none";
}

/**
 * Function to detect the number of markers for each category and
 * add them to the Layer Control.
 *
 * @param {object} markerGroups The marker groups.
 * @param {string} date The date when the data was queried.
 */
function statPopulate(markerGroups, date) {
  // Get all categories
  const markerGroupCategories = Object.keys(markerGroups);
  // Go through the list of categories
  for (let i = 0; i < markerGroupCategories.length; i += 1) {
    // Get the name
    const categoryName = markerGroupCategories[i];
    // Get the number of the markers
    const markerNumber = markerGroups[categoryName].length;
    // Add the number to the category entry
    document.getElementById(categoryName).innerHTML = `(${markerNumber})`;
  }
  // Add the date to the Layer Control
  const lastEntry = document.getElementById("issue_count_many").parentNode.parentNode;
  lastEntry.innerHTML += `<br /><div>(${date})</div>`;
}

// Function to get the information from the places json file.
function veggiemapPopulate(parentGroupVar) {
  const url = "../data/check_results.json";
  fetch(url)
    .then((response) => response.json())
    .then((geojson) => geojsonToMarkerGroups(geojson))
    .then((markerGroupsAndDate) => {
      const markerGroups = markerGroupsAndDate[0];
      const date = markerGroupsAndDate[1];

      Object.entries(subgroups).forEach(([key, subgroup]) => {
        // Bulk add all the markers from a markerGroup to a subgroup in one go
        // Source: https://github.com/ghybs/Leaflet.FeatureGroup.SubGroup/issues/5
        subgroup.addLayer(L.layerGroup(markerGroups[key]));
        map.addLayer(subgroup);
      });

      // Reveal all the markers and clusters on the map in one go
      map.addLayer(parentGroupVar);

      // Call the function to put the numbers into the legend
      statPopulate(markerGroups, date);

      // Enable the on-demand popup and tooltip calculation
      parentGroup.eachLayer((layer) => {
        layer.bindPopup(calculatePopup);
        layer.bindTooltip(calculateTooltip);
      });

      // Hide spinner
      hideSpinner();
    })
    .catch((error) => {
      console.log("Request failed", error);
    });
}

// Process the places GeoJSON into the groups of markers
function geojsonToMarkerGroups(geojson) {
  const date = geojson._timestamp.split(" ")[0];
  const groups = {};
  geojson.features.forEach((feature) => {
    let eCat = "issue_count_";
    if (feature.properties.issue_count > 6) {
      eCat += "many";
    } else {
      eCat += feature.properties.issue_count;
    }
    if (!groups[eCat]) groups[eCat] = [];
    groups[eCat].push(getMarker(feature));
  });
  return [groups, date];
}

// Function to get the marker.
function getMarker(feature) {
  const eLatLon = [feature.geometry.coordinates[1], feature.geometry.coordinates[0]];
  const marker = L.marker(eLatLon);
  marker.feature = feature;
  return marker;
}

// Calculate tooltip content for a given marker layer
function calculateTooltip(layer) {
  const feature = layer.feature;
  const eNam = feature.properties.name;
  return eNam;
}

// Calculate popup content for a given marker layer
function calculatePopup(layer) {
  // Get the information
  const feature = layer.feature;
  const eId = feature.properties._id;
  const eNam = feature.properties.name;
  const eTyp = feature.properties._type;

  /** * Building the popup content ** */

  // Popup title
  let popupContent = `<div class='map-popup-title'>${eNam}</div><hr/>`;

  // Add undefined keys
  if (feature.properties.undefined !== undefined) {
    feature.properties.undefined.forEach((key) => (popupContent += `<div class='popup-issue'>'${key}' is undefined</div>`));
  }

  // Add issues
  if (feature.properties.issues !== undefined) {
    feature.properties.issues.forEach((issue) => (popupContent += `<div class='popup-issue'>${issue}</div>`));
  }

  // OSM link to edit
  const osmShowUrl = `https://openstreetmap.org/${eTyp}/${eId}`;
  const osmEditUrl = `https://www.openstreetmap.org/edit?${eTyp}=${eId}`;
  popupContent += `<hr/><div class='map-editor-link'><a href='${osmShowUrl}' target='_blank' rel='noopener noreferrer'>Show on OpenStreetMap</a><br>
  <a href='${osmEditUrl}' target='_blank' rel='noopener noreferrer'>Edit on OpenStreetMap</a></div>`;

  return popupContent;
}

// Main function
veggiemap();
