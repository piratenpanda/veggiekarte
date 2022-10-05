/* global L */

/* Variables for the icon color */
const whiteIconColor = "-white.svg";
const blackIconColor = "-black.svg";

/* Function to get the icon depending from the symbol and the category */
export function getIcon(symbol, category) {
  let iconColor;
  if (category === "vegan_only") {
    iconColor = whiteIconColor;
  } else if (category === "vegetarian_only") {
    iconColor = whiteIconColor;
  } else if (category === "vegan_friendly") {
    iconColor = blackIconColor;
  } else if (category === "vegan_limited") {
    iconColor = blackIconColor;
  } else if (category === "vegetarian_friendly") {
    iconColor = blackIconColor;
  }

  /* Check if it's a maki or osm-carto icon */
  let iconPath;
  if (symbol.startsWith("maki_")) {
    iconPath = "third-party/icons/maki/";
    // eslint-disable-next-line no-param-reassign
    symbol = symbol.replace("maki_", "");
  } else {
    iconPath = "third-party/icons/openstreetmap-carto/";
  }

  return L.icon({
    iconUrl: iconPath + symbol + iconColor,
    iconSize: [18, 18],
    iconAnchor: [11, 18],
    popupAnchor: [0, -18],
    className: `marker ${category}`
  });
}
