#!/usr/bin/python
"""
With this module we get the POIs with the tags vegan = * and
vegetarian = * from OpenStreetMap and fill them in a file.
"""

import os         # for handling files
import time       # for sleep
import json       # read and write json
import sys        # to check the python version
import datetime   # for the timestamp
import urllib3    # for the HTTP GET request

assert sys.version_info >= (3, 0)

# constants for the overpass request

## server list (from: https://wiki.openstreetmap.org/wiki/Overpass_API)
SERVERS = [
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "http://api.openstreetmap.fr/api/interpreter",
    "http://dev.overpass-api.de/api_drolbr/interpreter",
    "http://overpass-api.de/api/interpreter",
    "http://overpass.openstreetmap.fr/api/interpreter"
]
HTTP = urllib3.PoolManager()

## constants for the output files
TIMESTAMP = str(datetime.datetime.now())                   # the actual date and time
DATE = datetime.datetime.now().strftime("%Y-%m-%d")          # the actual date
DATADIR = os.path.dirname(os.path.abspath(__file__))       # get the path of the directory of this script
VEGGIEPLACES_TEMPFILE = DATADIR + "/data/places_temp.json" # the temp file to store the data from the overpass request
VEGGIEPLACES_FILE = DATADIR + "/data/places.json"          # the data file which will be used for the map
VEGGIESTAT_FILE = DATADIR + "/data/stat.json"              # the data file which will be used for the map
VEGGIEPLACES_OLDFILE = DATADIR + "/data/places_old.json"   # previous version of the data file (helpful to examine changes)

# variables to handle the json data
places_data = {}
stat_data = {}

# icon mapping
# (the first element of the array is for the icon in the marker, the second is an emoji and it is used in the title)
ICON_MAPPING = {
    # Intentionally not alphabetical order
    "cuisine:pizza": ["maki_restaurant-pizza", "🍕"],
    # Alphabetical order
    "amenity:bar": ["bar", "🍸"],
    "amenity:bbq": ["bbq", "🍴"],
    "amenity:cafe": ["cafe", "☕"],
    "amenity:cinema": ["cinema", "🎦"],
    "amenity:college": ["maki_college", "🎓"],
    "amenity:fast_food": ["fast_food", "🍔"],
    "amenity:food_court": ["restaurant", "🍽️"],
    "amenity:fuel": ["fuel", "⛽"],
    "amenity:hospital": ["hospital", "🏥"],
    "amenity:ice_cream": ["ice_cream", "🍨"],
    "amenity:kindergarten": ["playground", "🧒"],
    "amenity:pharmacy": ["pharmacy", "💊"],
    "amenity:place_of_worship": ["place_of_worship", "🛐"],
    "amenity:pub": ["pub", "🍻"],
    "amenity:restaurant": ["restaurant", "🍽️"],
    "amenity:school": ["maki_school", "🏫"],
    "amenity:shelter": ["shelter", "☂️"],
    "amenity:swimming_pool": ["maki_swimming", "🏊‍♀️"],
    "amenity:theatre": ["theatre", "🎭"],
    "amenity:university": ["maki_college", "🎓"],
    "amenity:vending_machine": ["maki_shop", "🛒"],
    "historic:memorial": ["monument", "🗿"],
    "leisure:golf_course": ["golf", "🏌️"],
    "leisure:pitch": ["maki_pitch", "🏃"],
    "leisure:sports_centre": ["sports", "🤼"],
    "leisure:stadium": ["maki_stadium", "🏟️"],
    "shop:alcohol": ["alcohol", "🍷"],
    "shop:bakery": ["bakery", "🥯"],
    "shop:beauty": ["beauty", "💇"],
    "shop:bicycle": ["bicycle", "🚲"],
    "shop:books": ["library", "📚"],
    "shop:butcher": ["butcher", "🔪"],
    "shop:clothes": ["clothes", "👚"],
    "shop:confectionery": ["confectionery", "🍬"],
    "shop:convenience": ["convenience", "🏪"],
    "shop:department_store": ["department_store", "🏬"],
    "shop:doityourself": ["diy", "🛠️"],
    "shop:fishmonger": ["maki_shop", "🐟"],
    "shop:garden_centre": ["garden-centre", "🏡"],
    "shop:general": ["maki_shop", "🛒"],
    "shop:gift": ["gift", "🎁"],
    "shop:greengrocer": ["greengrocer", "🍏"],
    "shop:hairdresser": ["hairdresser", "💇"],
    "shop:kiosk": ["maki_shop", "🛒"],
    "shop:music": ["music", "🎶"],
    "shop:supermarket": ["supermarket", "🏪"],
    "shop:wine": ["alcohol", "🍷"],
    "tourism:guest_house": ["guest_house", "🏠"],
    "tourism:museum": ["museum", "🖼️"],
}


def determine_icon(tags):
    """Determine an icon for the marker."""
    icon = ["maki_star-stroked", ""]   # Use this icon if there is no matching per ICON_MAPPING.
    for kv in ICON_MAPPING:
        k, v = kv.split(":")
        t = tags.get(k)

        if not t:
            continue

        t = t.split(";")[0]

        if t == v:
            icon = ICON_MAPPING[kv]
            break
    return icon


def get_data_osm():
    """Get the data from OSM."""
    # Initialize variables
    server = 0
    result = None

    # Preparing the string for the Overpass request
    overpass_data_out = '?data=[out:json];('
    overpass_vegan_objects = 'node["diet:vegan"~"yes|only|limited"];way["diet:vegan"~"yes|only|limited"];'
    overpass_vegetarian_objects = 'node["diet:vegetarian"~"yes|only"];way["diet:vegetarian"~"yes|only"];'
    overpass_out = ');out+center;'

    # Sending a request to one server after another until one gives a valid answer or the end of the server list is reached.
    while (server < len(SERVERS)) and (result is None):
        # Get a server from the server list
        overpass_server = SERVERS[server]

        # Overpass request
        print("Send query to server: ", overpass_server)
        r = HTTP.request("GET", overpass_server + overpass_data_out + overpass_vegan_objects + overpass_vegetarian_objects + overpass_out)

        # Check the status of the request
        if r.status == 200:
            print("Received answer successfully.")
            result = json.loads(r.data.decode("utf-8"))
        elif r.status == 400:
            print("HTTP error code ", r.status, ": Bad Request")
            time.sleep(5)
        elif r.status == 429:
            print("HTTP error code ", r.status, ": Too Many Requests")
            time.sleep(60)
        elif r.status == 504:
            print("HTTP error code ", r.status, ": Gateway Timeout")
            time.sleep(600)
        else:
            print("Unknown HTTP error code: ", r.status)

        # Increase to get another server for the next pass of the loop.
        server += 1

    return result


def write_data(data):
    """Write the data in a temp file."""
    # Initialize variables to count the markers
    n_vegan_only = 0
    n_vegetarian_only = 0
    n_vegan_friendly = 0
    n_vegan_limited = 0
    n_vegetarian_friendly = 0

    # Adding timestamp
    places_data["_timestamp"] = TIMESTAMP

    places_data["type"] = "FeatureCollection"

    # Adding list object which will contain all place objects
    places_data["features"] = []

    # Go through every osm element and put the information into a new places element.
    for e in data["elements"]:

        elementId = e["id"]
        elementType = e["type"]
        tags = e.get("tags", {})

        placeObj = {}
        placeObj["type"] = "Feature"

        placeObj["properties"] = {}

        placeObj["properties"]["_id"] = elementId
        placeObj["properties"]["_type"] = elementType


        if elementType == "node":
            lat = e.get("lat", None)
            lon = e.get("lon", None)

        if elementType == "way":
            center_coordinates = e.get("center", None) # get the coordinates from the center of the object
            lat = center_coordinates.get("lat", None)
            lon = center_coordinates.get("lon", None)

        if not lat or not lon:
            continue


        placeObj["geometry"] = {}
        placeObj["geometry"]["type"] = "Point"
        placeObj["geometry"]["coordinates"] = [lon,lat]

        icon = determine_icon(tags)
        placeObj["properties"]["icon"] = icon[0]
        placeObj["properties"]["symbol"] = icon[1]



        if "name" in tags:
            name = tags["name"]
            ## Double quoutes could escape code, so we have to replace them:
            name = name.replace('"', '”')
        else:
            ## If there is no name given from osm, we build one.
            name = "%s %s" % (elementType, elementId)
        placeObj["properties"]["name"] = name

        # Give the object a category
        if tags.get("diet:vegan", "") == "only":
            category = "vegan_only"
            placeObj["properties"]["category"] = "vegan_only"
            n_vegan_only += 1
        elif (tags.get("diet:vegetarian", "") == "only"
              and tags.get("diet:vegan", "") == "yes"):
            category = "vegetarian_only"
            placeObj["properties"]["category"] = "vegetarian_only"
            n_vegetarian_only += 1
        elif tags.get("diet:vegan", "") == "yes":
            category = "vegan_friendly"
            placeObj["properties"]["category"] = "vegan_friendly"
            n_vegan_friendly += 1
        elif tags.get("diet:vegan", "") == "limited":
            category = "vegan_limited"
            placeObj["properties"]["category"] = "vegan_limited"
            n_vegan_limited += 1
        else:
            category = "vegetarian_friendly"
            placeObj["properties"]["category"] = "vegetarian_friendly"
            n_vegetarian_friendly += 1

        if "cuisine" in tags:
            placeObj["properties"]["cuisine"] = tags["cuisine"]
        if "addr:street" in tags:
            placeObj["properties"]["addr_street"] = tags.get("addr:street", "")
            if "addr:housenumber" in tags:
                placeObj["properties"]["addr_street"] += " " + tags.get("addr:housenumber", "")
        if "addr:city" in tags:
            placeObj["properties"]["addr_city"] = tags.get("addr:city", "")
        if "addr:postcode" in tags:
            placeObj["properties"]["addr_postcode"] = tags.get("addr:postcode", "")
        if "addr:country" in tags:
            placeObj["properties"]["addr_country"] = tags.get("addr:country", "")
        if "contact:website" in tags:
            placeObj["properties"]["contact_website"] = tags.get("contact:website", "")
        elif "website" in tags:
            placeObj["properties"]["contact_website"] = tags.get("website", "")
        if "contact:email" in tags:
            placeObj["properties"]["contact_email"] = tags.get("contact:email", "")
        elif "email" in tags:
            placeObj["properties"]["contact_email"] = tags.get("email", "")
        if "contact:phone" in tags:
            placeObj["properties"]["contact_phone"] = tags.get("contact:phone", "")
        elif "phone" in tags:
            placeObj["properties"]["contact_phone"] = tags.get("phone", "")
        if "opening_hours" in tags:
            # Replacing line breaks with spaces (Usually there should be no line breaks,
            # but if they do appear, they break the structure of the veggiemap-data.js).
            opening_hours = tags["opening_hours"].replace("\n", " ").replace("\r", "")
            # Diverting entries with break (that looks better in the popup box)
            opening_hours = opening_hours.replace("; ", "<br/>")
            placeObj["properties"]["opening_hours"] = opening_hours

        places_data["features"].append(placeObj)

    # Collect the statistic data in an object and add it to the places object
    statObj = {}
    statObj["date"] = DATE
    statObj["n_vegan_only"] = n_vegan_only
    statObj["n_vegetarian_only"] = n_vegetarian_only
    statObj["n_vegan_friendly"] = n_vegan_friendly
    statObj["n_vegan_limited"] = n_vegan_limited
    statObj["n_vegetarian_friendly"] = n_vegetarian_friendly


    # Open statistic data file
    with open(VEGGIESTAT_FILE) as json_file:
    
        # Get previous statistic data
        previous_stat_data = json.load(json_file)
        stat_data["stat"] = previous_stat_data["stat"]
        
        # Get date from the last entry
        LAST_DATE = stat_data["stat"][-1]["date"]

        # Ensure that there is only one entry each day
        if DATE == LAST_DATE:
           stat_data["stat"].pop(-1)

        # Append the new data
        stat_data["stat"].append(statObj)

def check_data():
    """Check the temp file and replace the old VEGGIEPLACES_FILE if it is ok."""

    if os.path.isfile(VEGGIEPLACES_TEMPFILE):                   # check if the temp file exists
        if os.path.getsize(VEGGIEPLACES_TEMPFILE) > 500:        # check if the temp file isn't to small (see issue #21)
            print("rename " + VEGGIEPLACES_TEMPFILE + " to " + VEGGIEPLACES_FILE)
            os.rename(VEGGIEPLACES_FILE, VEGGIEPLACES_OLDFILE)  # rename old file
            os.rename(VEGGIEPLACES_TEMPFILE, VEGGIEPLACES_FILE) # rename temp file to new file

            # Write the new statistic file
            outfilestat = open(VEGGIESTAT_FILE, "w")
            outfilestat.write(json.dumps(stat_data, indent=1, sort_keys=True))
            outfilestat.close()

        else:
            print("temp file is to small!")
            print(os.path.getsize(VEGGIEPLACES_TEMPFILE))
    else:
        print("temp file don't exists!")


def main():
    """Call the functions to get and write the osm data."""
    # Get data
    osm_data = get_data_osm()

    # Write data
    if osm_data is not None:
        write_data(osm_data)
        outfile = open(VEGGIEPLACES_TEMPFILE, "w")
        outfile.write(json.dumps(places_data, indent=1, sort_keys=True))
        outfile.close()

        check_data()
    else:
        print("A problem has occurred. The old VEGGIE_MAP was not replaced!")


main()
