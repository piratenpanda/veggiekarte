// To close the infomation window per click on the x.
function closeinfo() {
	close = document.getElementsByClassName("information");
	close[0].style.display = "none";
}

function getURLParameter(name) {
	return decodeURI((RegExp(name + '=' + '(.+?)(&|$)').exec(location.search)||[,])[1]);
}

function veggiemap() {

  var tileOSM = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a> - <a href="impressum.html">Impressum</a>',
    maxZoom: 18
  });

  var map = new L.map('map', { layers: [tileOSM], zoomControl: false, worldCopyJump: true });

  map.setView([51.43,17.58], 4);

  var zoomControl = L.control.zoom({
                    position: 'topleft'
                });

  map.addControl(zoomControl);

  var regionParameter = getURLParameter('region');
  var region = (regionParameter === 'undefined') ? '' : regionParameter;

  //new L.Control.GeoSearch({provider: new L.GeoSearch.Provider.OpenStreetMap({region: region})}).addTo(map);
  L.Control.geocoder().addTo(map);
  L.control.info().addTo(map);

  function onLocationFound(e){
  	var radius = e.accuracy / 2;
  	L.marker(e.latlng).addTo(map)
  	var circle = L.circle(e.latlng, 800, {
  		color: 'blue',
  		stroke: false,
  		//fillColor: '#f03',
  		fillOpacity: 0.1
  	}).addTo(map);

  }

  L.control.locate({
	position: 'topleft', // set the location of the control
	drawCircle: true, // controls whether a circle is drawn that shows the uncertainty about the location
	follow: false, // follow the user's location
	setView: true, // automatically sets the map view to the user's location, enabled if `follow` is true
	keepCurrentZoomLevel: false, // keep the current map zoom level when displaying the user's location. (if `false`, use maxZoom)
	stopFollowingOnDrag: false, // stop following when the map is dragged if `follow` is true (deprecated, see below)
	remainActive: false, // if true locate control remains active on click even if the user's location is in view.
	markerClass: L.circleMarker, // L.circleMarker or L.marker
	circleStyle: {
                color: '#136AEC',
                fillColor: '#136AEC',
                fillOpacity: 0.15,
                weight: 2,
                opacity: 0.5
        },
        // inner marker
        markerStyle: {
                color: '#136AEC',
                fillColor: '#2A93EE',
                fillOpacity: 0.7,
                weight: 2,
                opacity: 0.9,
                radius: 5
        },
	//followCircleStyle: {}, // set difference for the style of the circle around the user's location while following
	//followMarkerStyle: {},
	icon: 'fa fa-map-marker', // class for icon, fa-location-arrow or fa-map-marker
	iconLoading: 'fa fa-spinner fa-spin', // class for loading icon
	circlePadding: [0, 0], // padding around accuracy circle, value is passed to setBounds
	//metric: true, // use metric or imperial units
	onLocationError: function(err) {alert(err.message)}, // define an error callback function
	onLocationOutsideMapBounds: function(context) { // called when outside map boundaries
	alert(context.options.strings.outsideMapBoundsMsg);
	},
	showPopup: false, // display a popup when the user click on the inner marker
	strings: {
	title: "Standort ermitteln", // title of the locate control
	},
	locateOptions: {maxZoom: 16} // define location options e.g enableHighAccuracy: true or maxZoom: 10
  }).addTo(map);

  var markers = new L.MarkerClusterGroup({showCoverageOnHover: false, maxClusterRadius: 32});

  veggiemap_populate(markers);

  map.addLayer(markers);

  var hash = new L.Hash(map);

}
