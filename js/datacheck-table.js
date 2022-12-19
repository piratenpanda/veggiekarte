const url = "../data/check_results.json";
fetch(url)
  .then((response) => response.json())
  .then((geojson) => {
    const markerGroups = geojson.features;
    const date = geojson._timestamp.split(" ")[0];
    const output = document.getElementById("output");
    const head = document.createElement("h1");
    head.innerText = `Datacheck ${date}`;

    const issuesDiv = document.createElement("div");
    issuesDiv.innerText += `Places with issues: ${geojson.features.length}`;

    const table = document.createElement("table");
    const tableHead = document.createElement("tr");
    tableHead.innerHTML += "<th>index</th>";
    tableHead.innerHTML += "<th>osm</th>";
    tableHead.innerHTML += "<th>name</th>";
    tableHead.innerHTML += "<th>issue count</th>";
    tableHead.innerHTML += "<th>undefined</th>";
    tableHead.innerHTML += "<th>other issues</th>";
    table.appendChild(tableHead);

    markerGroups.forEach((element, index) => {
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

    output.appendChild(head);
    output.appendChild(issuesDiv);
    output.appendChild(table);
  })
  .catch((error) => {
    console.log("Request failed", error);
  });
