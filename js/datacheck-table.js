function veggiemapPopulate() {
  const url = "../data/check_results.json";
  fetch(url)
    .then((response) => response.json())
    .then((geojson) => geojsonToMarkerGroups(geojson))
    .then((markerGroupsAndDate) => {
      const markerGroups = markerGroupsAndDate[0];
      // const date = markerGroupsAndDate[1];

      Object.keys(markerGroups);
      console.log(markerGroups);

      /*
        let markerGroupCategories = Object.keys(markerGroupsAndDate[0]);
        // Go through the list of categories
        for (let i = 0; i < markerGroupCategories.length; i++) {
          // Get the name
          let categoryName = markerGroupCategories[i];
          // Get the number of the markers
          let markerNumber = markerGroups[categoryName].length;
          // Add the number to the category entry
          document.getElementById(categoryName).innerHTML = "(" + markerNumber + ")";
        }
      */

      // convert object to key's array
      const keys = Object.keys(markerGroups);

      // print all keys
      console.log(keys);
      // [ 'java', 'javascript', 'nodejs', 'php' ]

      // iterate over object
      keys.forEach((key) => {
        const DIV = document.createElement("DIV");

        const heading = document.createElement("h2");
        heading.innerText = key;
        heading.innerText += ` (${markerGroups[key].length})`;
        DIV.appendChild(heading);
        const table = document.createElement("table");
        const tableHead = document.createElement("tr");
        tableHead.innerHTML += "<th>index</th>";
        tableHead.innerHTML += "<th>osm</th>";
        tableHead.innerHTML += "<th>name</th>";
        tableHead.innerHTML += "<th>issue count</th>";
        tableHead.innerHTML += "<th>undefined</th>";
        tableHead.innerHTML += "<th>other issues</th>";
        table.appendChild(tableHead);

        markerGroups[key].forEach((element, index) => {
          const row = document.createElement("tr");
          // eslint-disable-next-line no-param-reassign
          index += 1;

          let undef = element.properties.undefined;
          if (undef === undefined) {
            undef = "-";
          } else {
            undef = undef.toString();
            undef = undef.replaceAll(",", "<br>");
          }

          let issues = element.properties.issues;
          if (issues === undefined) {
            issues = "-";
          } else {
            issues = issues.toString();
            issues = issues.replaceAll(",", "<br>");
          }

          console.log(element);
          row.innerHTML += `<td>${index}</td>`;
          row.innerHTML += `<td><a href="https://www.openstreetmap.org/${element.properties._type}/${element.properties._id}" target="_blank">show</a><br><a href="https://www.openstreetmap.org/edit?${element.properties._type}=${element.properties._id}" target="_blank">edit</a></td>`;
          row.innerHTML += `<td>${element.properties.name}</td>`;
          row.innerHTML += `<td>${element.properties.issue_count}</td>`;
          row.innerHTML += `<td>${undef}</td>`;
          row.innerHTML += `<td>${issues}</td>`;
          table.appendChild(row);
        });

        DIV.appendChild(table);

        const output = document.getElementById("output");

        output.appendChild(DIV);
      });
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
    // console.log(feature.properties.diet_vegan);

    const eCat = feature.properties.diet_vegan;

    if (!groups[eCat]) groups[eCat] = [];
    groups[eCat].push(feature);
  });
  return [groups, date];
}

/*
function json2Table(json) {
  const cols = Object.keys(json[0]);

  // Map over columns, make headers,join into string
  const headerRow = cols.map((col) => `<th>${col}</th>`).join("");

  // map over array of json objs, for each row(obj) map over column values,
  // and return a td with the value of that object for its column
  // take that array of tds and join them
  // then return a row of the tds
  // finally join all the rows together
  const rows = json
    .map((row) => {
      const tds = cols.map((col) => `<td>${row[col]}</td>`).join("");
      return `<tr>${tds}</tr>`;
    })
    .join("");

  // build the table
  const table = `
	<table>
		<thead>
			<tr>${headerRow}</tr>
		<thead>
		<tbody>
			${rows}
		<tbody>
	<table>`;

  output = document.getElementById("output");
  output.innerHTML = json2Table(data);
}
*/

veggiemapPopulate();
