#!/usr/bin/python
"""
With this module we get the POIs with the tags vegan = * and
vegetarian = * from OpenStreetMap and fill them in a file.
"""

import os         # for handling files
import time       # for sleep
import json       # read and write json
import gzip       # for compressing the json file
import sys        # to check the python version
import datetime   # for the timestamp
import urllib3    # for the HTTP GET request

assert sys.version_info >= (3, 0)

# constants for the overpass request

# # server list (from: https://wiki.openstreetmap.org/wiki/Overpass_API)
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

# # constants for the output files
TIMESTAMP = str(datetime.datetime.now())                             # the actual date and time
DATE = datetime.datetime.now().strftime("%Y-%m-%d")                  # the actual date
DATA_DIR = os.path.dirname(os.path.abspath(__file__))                # get the path of the directory of this script
VEGGIEPLACES_TEMPFILE = DATA_DIR + "/data/places_temp.json"          # the temp file to store the data
VEGGIEPLACES_TEMPFILE_MIN = DATA_DIR + "/data/places_temp.min.json"  # the minimized temp file
VEGGIEPLACES_TEMPFILE_GZIP = DATA_DIR + "/data/places_temp.min.json.gz"  # the gzipped temp file
VEGGIEPLACES_FILE = DATA_DIR + "/data/places.json"                   # the data file which will be used for the map
VEGGIEPLACES_FILE_MIN = DATA_DIR + "/data/places.min.json"           # the minimized data file which will be used for the map
VEGGIEPLACES_FILE_GZIP = DATA_DIR + "/data/places.min.json.gz"       # the gzipped data file which will be used for the map
VEGGIESTAT_FILE = DATA_DIR + "/data/stat.json"                       # the statistics data file which will be used for the map
VEGGIEPLACES_OLDFILE = DATA_DIR + "/data/places_old.json"            # previous version of the data file (helpful to examine changes)
OVERPASS_FILE = DATA_DIR + "/data/overpass.json"                     # the raw overpass output file (useful for later use)

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
    for key_value in ICON_MAPPING:
        key, value = key_value.split(":")
        tag = tags.get(key)

        if not tag:
            continue

        tag = tag.split(";")[0]

        if tag == value:
            icon = ICON_MAPPING[key_value]
            break
    return icon


def get_data_osm():
    """Get the data from OSM."""
    # Initialize variables
    server = 0
    result = None

    # Preparing the string for the Overpass request
    # Define export format
    overpass_query = '?data=[out:json];('
    # # Collect the vegan nodes, ways and relations
    overpass_query += 'nwr["diet:vegan"~"yes|only|limited"];'
    # # Collect the vegetarian nodes, ways and relations
    overpass_query += 'nwr["diet:vegetarian"~"yes|only"];'
    # # End of the query and use "out center" to reduce the geometry of ways and relations to a single coordinate
    overpass_query += ');out+center;'

    # Sending a request to one server after another until one gives a valid answer or
    # the end of the server list is reached.
    while (server < len(SERVERS)) and (result is None):
        # Get a server from the server list
        overpass_server = SERVERS[server]

        # Overpass request
        print("Send query to server: ", overpass_server)
        osm_request = HTTP.request("GET", overpass_server + overpass_query)

        # Check the status of the request
        if osm_request.status == 200:
            print("Received answer successfully.")

            # Store the raw output in a file (for any later use)
            with open(OVERPASS_FILE, "wb") as overpass_file:
                overpass_file.write(osm_request.data)

            result = json.loads(osm_request.data.decode("utf-8"))
        elif osm_request.status == 400:
            print("HTTP error code ", osm_request.status, ": Bad Request")
            time.sleep(5)
        elif osm_request.status == 429:
            print("HTTP error code ", osm_request.status, ": Too Many Requests")
            time.sleep(60)
        elif osm_request.status == 504:
            print("HTTP error code ", osm_request.status, ": Gateway Timeout")
            time.sleep(600)
        else:
            print("Unknown HTTP error code: ", osm_request.status)

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
    for osm_element in data["elements"]:

        element_id = osm_element["id"]
        element_type = osm_element["type"]
        tags = osm_element.get("tags", {})

        place_obj = {}
        place_obj["type"] = "Feature"
        place_obj["properties"] = {}
        place_obj["properties"]["_id"] = element_id
        place_obj["properties"]["_type"] = element_type

        if element_type == "node":
            lat = osm_element.get("lat", None)
            lon = osm_element.get("lon", None)

        elif element_type == "way" or element_type == "relation":
            center_coordinates = osm_element.get("center", None)  # get the coordinates from the center of the object
            lat = center_coordinates.get("lat", None)
            lon = center_coordinates.get("lon", None)

        else:
            continue

        place_obj["geometry"] = {}
        place_obj["geometry"]["type"] = "Point"
        place_obj["geometry"]["coordinates"] = [lon, lat]

        icon = determine_icon(tags)
        place_obj["properties"]["icon"] = icon[0]
        place_obj["properties"]["symbol"] = icon[1]

        # Get a name
        if "name" in tags:
            name = tags["name"]
        else:
            # If there is no name, take the english if exists
            if "name:en" in tags:
                name = tags["name:en"]
            else:
                # If there is no name given from osm, we build one
                name = "%s %s" % (element_type, element_id)
        # Double quotes could escape code, so we have to replace them:
        name = name.replace('"', '”')
        place_obj["properties"]["name"] = name

        # Give the object a category
        if tags.get("diet:vegan", "") == "only":
            place_obj["properties"]["category"] = "vegan_only"
            n_vegan_only += 1
        elif (tags.get("diet:vegetarian", "") == "only"
              and tags.get("diet:vegan", "") == "yes"):
            place_obj["properties"]["category"] = "vegetarian_only"
            n_vegetarian_only += 1
        elif tags.get("diet:vegan", "") == "yes":
            place_obj["properties"]["category"] = "vegan_friendly"
            n_vegan_friendly += 1
        elif tags.get("diet:vegan", "") == "limited":
            place_obj["properties"]["category"] = "vegan_limited"
            n_vegan_limited += 1
        else:
            place_obj["properties"]["category"] = "vegetarian_friendly"
            n_vegetarian_friendly += 1

        if "cuisine" in tags:
            place_obj["properties"]["cuisine"] = tags["cuisine"]
        if "addr:street" in tags:
            place_obj["properties"]["addr_street"] = tags.get("addr:street", "")
            if "addr:housenumber" in tags:
                place_obj["properties"]["addr_street"] += " " + tags.get("addr:housenumber", "")
        if "addr:city" in tags:
            place_obj["properties"]["addr_city"] = tags.get("addr:city", "")
        else:
            if "addr:suburb" in tags:
                # In some regions (e.g. in USA and Australia) they often tag suburbs instead of city
                place_obj["properties"]["addr_city"] = tags.get("addr:suburb", "")
        if "addr:postcode" in tags:
            place_obj["properties"]["addr_postcode"] = tags.get("addr:postcode", "")
        if "addr:country" in tags:
            place_obj["properties"]["addr_country"] = tags.get("addr:country", "")
        if "contact:website" in tags:
            place_obj["properties"]["contact_website"] = tags.get("contact:website", "").rstrip("/")
        elif "website" in tags:
            place_obj["properties"]["contact_website"] = tags.get("website", "").rstrip("/")
        if "contact:facebook" in tags:
            place_obj["properties"]["contact_facebook"] = tags.get("contact:facebook", "").rstrip("/")
        elif "facebook" in tags:
            place_obj["properties"]["contact_facebook"] = tags.get("facebook", "").rstrip("/")
        if "contact:instagram" in tags:
            place_obj["properties"]["contact_instagram"] = tags.get("contact:instagram", "").rstrip("/")
        if "contact:email" in tags:
            place_obj["properties"]["contact_email"] = tags.get("contact:email", "")
        elif "email" in tags:
            place_obj["properties"]["contact_email"] = tags.get("email", "")
        if "contact:phone" in tags:
            place_obj["properties"]["contact_phone"] = tags.get("contact:phone", "")
        elif "phone" in tags:
            place_obj["properties"]["contact_phone"] = tags.get("phone", "")
        if "opening_hours:covid19" in tags and tags["opening_hours:covid19"] != "same" and tags["opening_hours:covid19"] != "restricted":
            # Replacing line breaks with spaces (Usually there should be no line breaks,
            # but if they do appear, they break the structure of the places.json).
            opening_hours = tags["opening_hours:covid19"].replace("\n", "").replace("\r", "")
            place_obj["properties"]["opening_hours"] = opening_hours
        elif "opening_hours" in tags:
            # Replacing line breaks with spaces (Usually there should be no line breaks,
            # but if they do appear, they break the structure of the places.json).
            opening_hours = tags["opening_hours"].replace("\n", "").replace("\r", "")
            place_obj["properties"]["opening_hours"] = opening_hours
        if "shop" in tags:
            place_obj["properties"]["shop"] = tags["shop"]

        places_data["features"].append(place_obj)

    # Collect the statistic data in an object and add it to the places object
    stat_obj = {"date": DATE,
                "n_vegan_only": n_vegan_only,
                "n_vegetarian_only": n_vegetarian_only,
                "n_vegan_friendly": n_vegan_friendly,
                "n_vegan_limited": n_vegan_limited,
                "n_vegetarian_friendly": n_vegetarian_friendly}

    # Open statistic data file
    with open(VEGGIESTAT_FILE) as json_file:

        # Get previous statistic data
        previous_stat_data = json.load(json_file)
        stat_data["stat"] = previous_stat_data["stat"]

        # Get date from the last entry
        last_date = stat_data["stat"][-1]["date"]

        # Ensure that there is only one entry each day
        if DATE == last_date:
            stat_data["stat"].pop(-1)

        # Append the new data
        stat_data["stat"].append(stat_obj)


def check_data():
    """Check the temp file and replace the old VEGGIEPLACES_FILE if it is ok."""
    if os.path.isfile(VEGGIEPLACES_TEMPFILE_GZIP):                        # check if the temp file exists
        if os.path.getsize(VEGGIEPLACES_TEMPFILE_GZIP) > 500:             # check if the temp file isn't to small (see issue #21)
            print("rename " + VEGGIEPLACES_TEMPFILE + " to " + VEGGIEPLACES_FILE)
            os.rename(VEGGIEPLACES_FILE, VEGGIEPLACES_OLDFILE)           # rename old file
            os.rename(VEGGIEPLACES_TEMPFILE, VEGGIEPLACES_FILE)          # rename temp file to new file
            print("rename " + VEGGIEPLACES_TEMPFILE_MIN + " to " + VEGGIEPLACES_FILE_MIN)
            os.rename(VEGGIEPLACES_TEMPFILE_MIN, VEGGIEPLACES_FILE_MIN)  # rename minimized temp file to new file
            print("rename " + VEGGIEPLACES_TEMPFILE_GZIP + " to " + VEGGIEPLACES_FILE_GZIP)
            os.rename(VEGGIEPLACES_TEMPFILE_GZIP, VEGGIEPLACES_FILE_GZIP)  # rename minimized temp file to new file

            # Write the new statistic file
            outfilestat = open(VEGGIESTAT_FILE, "w")
            outfilestat.write(json.dumps(stat_data, indent=1, sort_keys=True))
            outfilestat.close()

        else:
            print("New gzip temp file is to small!")
            print(os.path.getsize(VEGGIEPLACES_TEMPFILE_GZIP))
    else:
        print("temp file don't exists!")


def main():
    """Call the functions to get and write the osm data."""
    # Get data
    if len(sys.argv) < 2:
        osm_data = get_data_osm()
    else:
        # For testing without new osm requests
        osm_data = json.load(open(sys.argv[1]))

    # Write data
    if osm_data is not None:
        write_data(osm_data)

        # Write file in pretty format
        outfile = open(VEGGIEPLACES_TEMPFILE, "w")
        outfile.write(json.dumps(places_data, indent=1, sort_keys=True))
        outfile.close()

        # Write file in minimized format
        outfile_min = open(VEGGIEPLACES_TEMPFILE_MIN, "w")
        outfile_min.write(json.dumps(places_data, indent=None, sort_keys=True, separators=(',', ':')))
        outfile_min.close()

        # Write file in gzipped format
        with gzip.open(VEGGIEPLACES_TEMPFILE_GZIP, "wt", encoding="UTF-8") as outfile_gzip:
            outfile_gzip.write(json.dumps(places_data, indent=None, sort_keys=True, separators=(',', ':')))

        check_data()
    else:
        print("A problem has occurred. The old VEGGIE_MAP was not replaced!")


main()
