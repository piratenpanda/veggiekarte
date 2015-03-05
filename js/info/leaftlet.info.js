/*!
Copyright (c) 2015 Benjamin Grimm-Lebsanft

*/
(function (factory) {
	// Packaging/modules magic dance
	var L;
	if (typeof define === 'function' && define.amd) {
		// AMD
		define(['leaflet'], factory);
	} else if (typeof module !== 'undefined') {
		// Node/CommonJS
		L = require('leaflet');
		module.exports = factory(L);
	} else {
		// Browser globals
		if (typeof window.L === 'undefined')
			throw 'Leaflet must be loaded first';
		factory(window.L);
	}
} (function (L) {
    'use strict';
    L.Control.Info = L.Control.extend({
        options: {
            position: 'topleft',
            icon: 'fa fa-info'           
        },

        initialize: function (options) {
		L.Util.setOptions(this, options);			
	},

        onAdd: function (map) {
            	var container = L.DomUtil.create('div','leaflet-control-info leaflet-bar leaflet-control');
		this._link = L.DomUtil.create('a', 'leaflet-bar-part leaflet-bar-part-single', container);
                this._link.href = '#';
		this._icon = L.DomUtil.create('span', this.options.icon, this._link);
		this._map = map;
		this._container = container;

		L.DomEvent
                .on(this._link, 'click', function() {
                    this.div = document.getElementsByClassName("information");
		    if (this.div[0].style.display == "none") {
			this.div[0].style.display = "block";
		    }
	            else {
			this.div[0].style.display = "none";
	            }
		    
                }, this)
		.on(this._link, 'dblclick', L.DomEvent.stopPropagation);

		return container;
        }
    });

    L.control.info = function (options) {
        return new L.Control.Info(options);
    };

    return L.Control.Info;
}));
