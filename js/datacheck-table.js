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

          row.innerHTML += `<td>${index}</td>`;
          row.innerHTML += `<td><a href="https://www.openstreetmap.org/${element.properties._type}/${element.properties._id}"
            target="_blank">show</a><br><a href="https://www.openstreetmap.org/edit?${element.properties._type}=${element.properties._id}" target="_blank">edit</a></td>`;
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

veggiemapPopulate();
