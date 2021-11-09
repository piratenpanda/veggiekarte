# Leaflet.LanguageSelector

A language selector for Leaflet based maps

Feel free to flattr me if you like it: [![alttext](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=Kranich&url=https%3A%2F%2Fgithub.com%2Fbuche%2Fleaflet-languageselector)

## Description
[Leaflet](http://leafletjs.com/) is an open-source JavaScript library for online maps. Leaflet-languageselector is an extension for Leaflet based maps to add a language selector to the map. Languages can be represented by text or image. The words or images can be aligned horizontally or vertically. When a language is clicked a callback function is called. Doing the language change is then up to the caller.

## Demo
A demo page with different configurations you can find at [/demo/demo.html](/demo/demo.html).

Maps using this library (and others) can be seen here:
- https://ahorn.lima-city.de/owm/ [(GitHub)](https://github.com/buche/leaflet-openweathermap)
- https://www.veggiekarte.de [(GitHub)](https://github.com/piratenpanda/veggiekarte)

## License

This code is licensed under [CC0](http://creativecommons.org/publicdomain/zero/1.0/ "Creative Commons Zero - Public Domain").

## Using Leaflet.LanguageSelector

First, you have to define the languages. Second, you have to initialise the language selector. Third, you have to provide a callback function which reacts according to the changed language. Don't forget to include leaflet-languageselector.js and leaflet-languageselector.css in your website.

## Simple Example 

Here are the most important lines:

```html
<head>
  <script type="text/javascript" src="leaflet.js"></script>
  <link rel="stylesheet" type="text/css" href="leaflet-languageselector.css" />
  <script src="leaflet-languageselector.js"></script>
</head>
```

```js
// callback function for language change
function changeLanguage(selectedLanguage) {
  var url = updateLangParameter(window.location.href, selectedLanguage);
  // Note updateLangParameter() is not shown here. It adds or replaces the language parameter of the document URL.
  // Look at the demo page for an implementation if you need one.
  window.location.href = url; // make it easy, just reload the page using the changed parameter
}

// initialize the map
var osm = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 18, attribution: '[insert correct attribution here!]' });
var map = L.map('map', { center: new L.LatLng(51.5, 10), zoom: 10, layers: [osm] });
var baseMaps = { "OSM Standard": osm };
L.control.layers(baseMaps).addTo(map);

// Now the interesting stuff, the new languageselector:
map.addControl(L.languageSelector({
  languages: new Array(
    L.langObject('en', 'English', 'en.svg'),
    L.langObject('eo', 'Esperanto', 'eo.svg'),
    L.langObject('de', 'Deutsch', 'de.svg'),
    L.langObject('fr', 'Français', 'fr.svg'),
    L.langObject('ru', 'Русский', 'ru.svg')
  ),
  callback: changeLanguage
}));
```

## Options
Some *options* are available to configure the behaviour of the language selector. Only two options are mandatory: **languages** - the array of languages we will use and **callback** - the callback function which will be called when the user selects a language. Here are all options, the **default value** is bold:

* *languages*: Array ( **new Array()** ) array of at least one Object with language information. See below for details.
* *callback*: Function ( **null** ) callback function with one string parameter, the id of the language
* *title*: String ( **null** ) optional: Title of the control
* *vertical*: Boolean ( **false** ) optional: If *true* renders the languages vertically instead of horizontally
* *hideSelected*: Boolean ( **false** ) optional: If *true* hides the language currently used
* *initialLanguage*: String ( **null** ) optional: Indicate the initial language of your page. It will be marked (when *hideSelected=true*) or hidden (when *hideSelected=true*) at the start.
* *position*: String ( **'topright'** ) optional: Position of this control. Available are standard positions of Leaflet controls ('topright', 'topleft', 'bottomright', 'bottomleft').

## How to define languages and how to define what will be displayed

Languages are added as an array of language objects. Please create them using the function 'L.langObject(id,name,image)' as you see in the "Simple Example" code above. Only the first parameter is mandatory, it is the language id which will be passed as the only parameter of the callback function.

If you provide an image, the image will be displayed as a symbol for the language. The name or id is the tooltip of the image. If you don't provide an image but a name, the name will be used. If you provide neither an image nor a name the id will be used.

* *L.langObject('en','English','en.svg')* - using image en.svg with tooltip 'English'
* *L.langObject('en',null,'en.svg')* - using image en.svg with tooltip 'en'
* *L.langObject('en','English')* - using text 'English'
* *L.langObject('en')* - using text 'en'

## Stylesheet
*leaflet-languageselector.css* is used to style the components of the control. Adapt it as you like.

## Language images
Only some images are provided here - look at [Image info](/images/image_info.md). If you need more, there are a lot of free ones out there in the universe. For example https://openclipart.org/, http://commons.wikimedia.org/ or http://famfamfam.com/lab/icons/flags/ ("These flag icons are available for free use for any purpose with no requirement for attribution").

## Best practice for presenting languages
Consider these clues about [Best practice for presenting languages](http://www.flagsarenotlanguages.com/blog/best-practice-for-presenting-languages/).

