/* Variables for the icon color */
const white_icon_color = "-white.svg";
const black_icon_color = "-black.svg";

/* Function to get the icon depending from the symbol and the category */
function getIcon(symbol, category) {
  if (category == "vegan_only") {
    var icon_color = white_icon_color;
  } else if (category == "vegetarian_only") {
    var icon_color = white_icon_color;
  } else if (category == "vegan_friendly") {
    var icon_color = black_icon_color;
  } else if (category == "vegan_limited") {
    var icon_color = black_icon_color;
  } else if (category == "vegetarian_friendly") {
    var icon_color = black_icon_color;
  }

  /* Check if it's a maki or osm-carto icon */
  if (symbol.startsWith("maki_")) {
    var icon_path = "third-party/icons/maki/";
    symbol = symbol.replace('maki_','');
  } else {
    var icon_path = "third-party/icons/openstreetmap-carto/";
  }

  return L.icon({
    iconUrl:     icon_path+symbol+icon_color,
    iconSize:    [18, 18],
    iconAnchor:  [11, 18],
    popupAnchor: [0, -18],
    className:   "marker " + category
  });
}
