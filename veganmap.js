function getURLParameter(name) {

	return decodeURI((RegExp(name + '=' + '(.+?)(&|$)').exec(location.search)||[,])[1]);
}

function veganmap() {

  var tileOSM = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
    maxZoom: 18
  });

  var tileToner = L.tileLayer('http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.png', {
    subdomains: 'abcd',
    attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.',
    minZoom: 0,
    maxZoom: 18
  });

  var tileMapQuest = L.tileLayer('http://otile{s}.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.jpeg', {
    subdomains: '1234',
    attribution: 'Tiles Courtesy of <a href="http://www.mapquest.com/">MapQuest</a> &mdash; Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
    maxZoom: 18
  });

  var tileCloudMade = L.tileLayer('http://{s}.tile.cloudmade.com/9fc04dd0af2241b38e5aeea5d93c2655/997/256/{z}/{x}/{y}.png', {
    attribution: '&copy; 2013 <a href="http://cloudmade.com">CloudMade</a> &#8211; Map data <a href="http://www.openstreetmap.org/copyright">ODbL</a> 2013 <a href="http://www.openstreetmap.org/">OpenStreetMap.org</a> contributors &#8211; <a href="http://cloudmade.com/website-terms-conditions">Terms of Use</a>&#8221;',
    maxZoom: 18
  });

  var map = new L.map('map', { center: [0, 0], zoom: 3, layers: [tileCloudMade], zoomControl: false, worldCopyJump: true });

  var layers = {
    "OpenStreetMap": tileOSM,
    "MapQuestOpen": tileMapQuest,
    "Toner": tileToner,
    "CloudMade": tileCloudMade,
  };

  var layerControl = L.control.layers(layers, null, {position: 'bottomright'});
  
  layerControl.addTo(map);

  var zoomControl = L.control.zoom({
                    position: 'bottomright'
                });

  map.addControl(zoomControl);

  var regionParameter = getURLParameter('region');
  var region = (regionParameter === 'undefined') ? '' : regionParameter;

  new L.Control.GeoSearch({
          provider: new L.GeoSearch.Provider.OpenStreetMap({
            	region: region
            })
        }).addTo(map);

  var markers = new L.MarkerClusterGroup({showCoverageOnHover: false, maxClusterRadius: 32});

  veganmap_populate(markers);

  map.addLayer(markers);

  var hash = new L.Hash(map);

}
