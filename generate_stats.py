#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generate historical statistics

This script fetches the daily counts of venues by category from the
Ohsome API and saves them as the file data/stat.json.

Currently runs weekly and is supported by half-hourly updates via refresh.py
"""

import json
import urllib3

HTTP = urllib3.PoolManager()

FILTERS = {
    "n_vegan_only": "diet:vegan=only",
    "n_vegetarian_only": "diet:vegan=yes and diet:vegetarian=only",
    "n_vegan_friendly": "diet:vegan=yes and diet:vegetarian!=only",
    "n_vegan_limited": "diet:vegan=limited",
    "n_vegetarian_friendly": "diet:vegetarian in (only,yes) and not diet:vegan in (only,yes,limited)",
}

OHSOME_URL = "https://api.ohsome.org/v1/elements/count"

stat_data = {}
for key, filter_expression in FILTERS.items():
    print("Fetching", key, filter_expression)
    request = HTTP.request(
        "GET",
        OHSOME_URL,
        fields={
            "filter": filter_expression,
            "showMetadata": "true",
            "bboxes": "-180,-90,180,90",
            "time": "2011-02-01//P1D",
        },
    )
    response = json.loads(request.data.decode("utf-8"))

    if response.get("result") is not None:
        for datapoint in response.get("result"):
            date = datapoint.get("timestamp").split("T")[0]
            stat_data.setdefault(date, {"date": date})[key] = int(
                datapoint.get("value")
            )

    else:
        print("No data received, skipping")

if len(stat_data) > 0:
    with open("data/stat.json", "wt") as stat_file:
        json.dump(
            {"stat": sorted(stat_data.values(), key=lambda x: x.get("date"))},
            stat_file,
            indent=1,
            sort_keys=True,
        )
    print("Done writing stat file!")
else:
    print("No data received! Not writing stat file")
