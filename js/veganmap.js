function getURLParameter(name) {

	return decodeURI((RegExp(name + '=' + '(.+?)(&|$)').exec(location.search)||[,])[1]);
}

function veganmap() {

  var tileOSM = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a> - <a href="impressum.html">Impressum</a>',
    maxZoom: 18
  });

  var tileCloudMade = L.tileLayer('http://{s}.tile.cloudmade.com/9fc04dd0af2241b38e5aeea5d93c2655/997/256/{z}/{x}/{y}.png', {
    attribution: '&copy; 2013 <a href="http://cloudmade.com">CloudMade</a> &#8211; Map data <a href="http://www.openstreetmap.org/copyright">ODbL</a> 2013 <a href="http://www.openstreetmap.org/">OpenStreetMap.org</a> contributors &#8211; <a href="http://cloudmade.com/website-terms-conditions">Terms of Use</a> - <a href="impressum.html">Impressum</a>',
    maxZoom: 18
  });

  var map = new L.map('map', { layers: [tileOSM], zoomControl: false, worldCopyJump: true });

  map.setView([51.43,17.58], 4);

  var layers = {
    "OpenStreetMap": tileOSM,
  };

  var layerControl = L.control.layers(layers, null, {position: 'bottomright'});
  
  //layerControl.addTo(map);

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
