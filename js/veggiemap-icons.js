/* Variables for the icon color */
var vegan_icon_color      = "-white.svg";
var veggie_icon_color     = "-white.svg";
var others_icon_color     = "-black.svg";
var nocategory_icon_color = "-black.svg";

/* Function to get the icon depending from the symbol and the category */
function getIcon(symbol, category) {
  if (category == "vegan") {
    var icon_color = vegan_icon_color;
  } else if (category == "vegan_limited") {
    var icon_color = others_icon_color;
  } else if (category == "veggie") {
    var icon_color = veggie_icon_color;
  } else {
    var icon_color = nocategory_icon_color;
    /*  To find the entries without category. */
    console.log("nocategory category");
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
