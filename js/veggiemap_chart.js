'use strict';


// Load statisctics data and call funtion to handle the data
function getStatistics() {
  const url = "data/stat.json";
  fetch(url)
  .then(response => response.json())
  .then(data => handleData(data.stat))
  .catch(error  => {console.log('Request failed', error);});
}


function handleData(data) {
  // Call function to put the values from each day in arrays
  (data).forEach(getValues);
  
  // Get config
  let config = buildConfig();
  
  // Publish chart
  publishChart(config);
}


function getValues(element) {
  let currentElementDate = new Date(element.date);
  let diffTime = Math.abs(currentElementDate - lastElementDate);
  let diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  let minimumElementDayDifference = 6;

  if (diffDays >= minimumElementDayDifference) {
    dateArray.push(element.date);
    dataVeganOnly.push(element.n_vegan_only);
    dataVegetarianOnly.push(element.n_vegetarian_only);
    dataVeganFriendly.push(element.n_vegan_friendly);
    dataVeganLimited.push(element.n_vegan_limited);
    dataVegetarianFriendly.push(element.n_vegetarian_friendly);
    lastElementDate = currentElementDate;
  }
} 


function buildConfig() {

    let config = {
      type: 'line',
      data: {
        labels: dateArray,
        datasets: [{
          label: 'vegan only',
          borderColor: 'DarkGreen',
          backgroundColor: 'DarkGreen',
          data: dataVeganOnly,
          fill: false
        }, {
          label: 'vegetarian only',
          borderColor: 'SpringGreen',
          backgroundColor: 'SpringGreen',
          data: dataVegetarianOnly,
          fill: false
        }, {
          label: 'vegan friendly',
          borderColor: 'SkyBlue  ',
          backgroundColor: 'SkyBlue  ',
          data: dataVeganFriendly,
          fill: false
        }, {
          label: 'vegan limited',
          borderColor: 'Orange',
          backgroundColor: 'Orange',
          data: dataVeganLimited,
          fill: false
        }, {
          label: 'vegetarian friendly',
          borderColor: 'lightgrey',
          backgroundColor: 'lightgrey',
          data: dataVegetarianFriendly,
          fill: false
        }]
      }
    };
  
  return config;
}


function publishChart(config) {
  let ctx = document.getElementById('canvas').getContext('2d');
  window.myLine = new Chart(ctx, config);
}


// Global variables for the config
let dateArray = [];
let dataVeganFriendly = [];
let dataVeganLimited = [];
let dataVeganOnly = [];
let dataVegetarianFriendly = [];
let dataVegetarianOnly = [];
let lastElementDate = new Date();


getStatistics();
