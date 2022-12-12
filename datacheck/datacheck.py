#!/usr/bin/python
"""
With this module we check the OpenStreetMap data.
"""

import datetime  # for the timestamp
import json  # read and write json
from urllib.parse import urlparse
import phonenumbers  # to check phone numbers
import requests  # to check if websites are reachable
from email_validator import EmailNotValidError, validate_email

# ### constants ###
# the actual date and time
TIMESTAMP = str(datetime.datetime.now())
# the actual date
DATE = str(datetime.date.today())
# the raw overpass output file (useful for later use)
OVERPASS_FILE = "../data/overpass.json"
VEGGIEPLACES_CHECK_RESULT_FILE = "../data/check_results.json"  # check results
# results of previous url checks
URL_DATA_FILE = "../data/urldata.json"

# don't check more than 100 url's (because it takes to much time)
MAX_URL_CHECKS = 100

# don't check URLs that have already been tested within the last x days
MIN_URL_CHECK_AGE = 50

# headers for the htttp request
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
}


# Get the OSM data.
def get_osm_data():
    """
    Open overpass data file.
    """
    with open(OVERPASS_FILE, encoding="utf-8") as overpass_json_file:
        # Get overpass data
        overpass_data = json.load(overpass_json_file)
    return overpass_data


def is_url_format_valid(url):
    """
    Check if the URL has a valid format by trying to parse it.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def is_url_ok(url):
    """
    Check if the URL is okay by the following steps.
     1. Check if the URL has checked recently.
     2. If not, check if the URL has a valid format.
     3. If so, check if the URL is reachable.
    """

    result = {"date": DATE}

    if url in proc.url_data:
        # URL has recently checked, so we save time to check again and take the last result.
        result["isOk"] = proc.url_data[url]["isOk"]
        result["text"] = proc.url_data[url]["text"]
    else:
        # URL not recently checked
        if is_url_format_valid(url):
            if proc.counter < MAX_URL_CHECKS:
                try:
                    # Try to reach the URL
                    response = requests.get(url, headers=headers, timeout=5)
                except Exception as error:
                    # Catch all exception if the URL isn't reachable
                    result["isOk"] = False
                    result["text"] = f"Exception: {str(error.__class__.__name__)}"
                    print(url, " ", result["text"])
                else:
                    # URL is reachable
                    if response.status_code < 400:
                        # All status_codes below 400 should be fine
                        result["isOk"] = True
                        result["text"] = "OK"
                    elif response.status_code == 403:
                        # We get that status from a lot of websites which are available with a browser
                        result["isOk"] = True
                        result["text"] = "Can't do full check: HTTP response: Forbidden"
                    elif response.status_code == 429:
                        # We get that status from a lot of websites which are available with a browser (especially from instagram)
                        result["isOk"] = True
                        result[
                            "text"
                        ] = "Can't do full check: HTTP response: Too Many Requests"
                    else:
                        result["isOk"] = False
                        result["text"] = "HTTP response error"
                        print(url, " ", response.status_code)
                    result["text"] = f"{result['text']} - {response.status_code}"
                    proc.counter += 1
            else:
                result["isOk"] = True
                result["text"] = "Not checked"
        else:
            result["isOk"] = False
            result["text"] = "No valid URL format"
        if result["text"] != "Not checked":
            proc.url_data[url] = result
    return result


def check_data(data):

    places_data_checks = {
        "_timestamp": TIMESTAMP,
        "type": "FeatureCollection",
        "features": [],
    }

    # Variables to print progress in the console
    osm_elements_number = len(data["elements"])

    # Go through every osm element and put the information into a new places element.
    for osm_element in data["elements"]:

        osm_element_index = data["elements"].index(osm_element) + 1

        print(osm_element_index, " / ", osm_elements_number, "\t")
        element_id = osm_element["id"]
        element_type = osm_element["type"]
        tags = osm_element.get("tags", {})

        place_check_obj = {"type": "Feature", "properties": {}}
        place_check_obj["properties"]["_id"] = element_id
        place_check_obj["properties"]["_type"] = element_type
        place_check_obj["properties"]["undefined"] = []
        place_check_obj["properties"]["issues"] = []

        if element_type == "node":
            lat = osm_element.get("lat", None)
            lon = osm_element.get("lon", None)
        elif element_type == "way" or element_type == "relation":
            # get the coordinates from the center of the object
            center_coordinates = osm_element.get("center", None)
            lat = center_coordinates.get("lat", None)
            lon = center_coordinates.get("lon", None)

        place_check_obj["geometry"] = {}
        place_check_obj["geometry"]["type"] = "Point"
        place_check_obj["geometry"]["coordinates"] = [lon, lat]

        # Name
        if "name" in tags:
            name = tags["name"]
            place_check_obj["properties"]["name"] = name
        else:
            # If there is no name, take the english if exists
            if "name:en" in tags:
                name = tags["name:en"]
            # If it is a vending machine, name it "vending machine"
            elif tags.get("amenity", "") == "vending_machine":
                name = "vending machine"
            else:
                # If there is no name given from osm, we build one
                name = f"{element_type} {element_id}"
                # Log this
                place_check_obj["properties"]["undefined"].append("name")
        # Double quotes could escape code, so we have to replace them:
        name = name.replace('"', "”")
        place_check_obj["properties"]["name"] = name

        # Diet tags
        if "diet:vegan" in tags:
            diet_vegan = tags.get("diet:vegan", "")
            place_check_obj["properties"]["diet_vegan"] = diet_vegan
            # Check if "diet:vegan" has unusual values
            if (
                diet_vegan != "only"
                and diet_vegan != "yes"
                and diet_vegan != "limited"
                and diet_vegan != "no"
            ):
                place_check_obj["properties"]["issues"].append(
                    "'diet:vegan' has an unusual value: " + diet_vegan
                )
            # If "diet:vegan" is "only", "diet:vegetarian" should not have another value.
            elif "diet:vegetarian" in tags and diet_vegan == "only":
                diet_vegetarian = tags.get("diet:vegetarian", "")
                if diet_vegetarian != "only":
                    place_check_obj["properties"]["issues"].append(
                        "'diet:vegan' is 'only', then 'diet:vegetarian' should be too."
                    )
        else:
            place_check_obj["properties"]["undefined"].append("diet:vegan")

        if tags.get("diet:vegan", "") != "no":
            # Cuisine
            if "cuisine" not in tags and "shop" not in tags:
                # Everything except cafeś and shops should have a cuisine tag
                if (
                    tags.get("amenity", "") != "cafe"
                    and tags.get("amenity", "") != "ice_cream"
                    and tags.get("amenity", "") != "bar"
                ):
                    place_check_obj["properties"]["undefined"].append("cuisine")

            if "cuisine" in tags:
                # The old values "vegan" and "vegetarian" should no longer be used
                cuisine = tags["cuisine"]
                if "vegan" in cuisine:
                    place_check_obj["properties"]["issues"].append(
                        "There is 'vegan' in the cuisine tag. Remove it and create a 'diet:vegan' tag if there is none."
                    )
                if "vegetarian" in cuisine:
                    place_check_obj["properties"]["issues"].append(
                        "There is 'vegetarian' in the cuisine tag. Remove it and create a 'diet:vegetarian' tag if there is none."
                    )

            # Address
            if "addr:housename" not in tags:
                if "addr:street" not in tags:
                    place_check_obj["properties"]["undefined"].append("addr:street")
                if "addr:housenumber" not in tags:
                    place_check_obj["properties"]["undefined"].append(
                        "addr:housenumber"
                    )
            if "addr:city" not in tags:
                if "addr:suburb" not in tags:
                    place_check_obj["properties"]["undefined"].append(
                        "addr:city/suburb"
                    )
            if "addr:postcode" not in tags:
                place_check_obj["properties"]["undefined"].append("addr:postcode")

            # Website
            website = "undefined"
            if "contact:website" in tags:
                website = tags.get("contact:website", "")
                check = is_url_ok(website)
                if check["isOk"] is False:
                    place_check_obj["properties"]["issues"].append(
                        f"'contact:website' {check['text']}"
                    )
            if "website" in tags:
                website = tags.get("website", "")
                check = is_url_ok(website)
                if check is False:
                    place_check_obj["properties"]["issues"].append(
                        f"'website' {check['text']}"
                    )
            if "facebook" in website:
                place_check_obj["properties"]["issues"].append(
                    "'facebook' URI as website -> change to 'contact:facebook'"
                )
            if "instagram" in website:
                place_check_obj["properties"]["issues"].append(
                    "'instagram' URI as website -> change to 'contact:instagram'"
                )
            if "contact:website" in tags and "website" in tags:
                place_check_obj["properties"]["issues"].append(
                    "'website' and 'contact:website' defined -> remove one"
                )

            # Facebook
            if "contact:facebook" in tags:
                contact_facebook = tags.get("contact:facebook", "")
                if contact_facebook.startswith("http://"):
                    place_check_obj["properties"]["issues"].append(
                        "'contact:facebook' starts with 'http' instead of 'https'"
                    )
                elif contact_facebook.startswith("https://"):
                    if contact_facebook.startswith(
                        "https://www.facebook.com/"
                    ) or contact_facebook.startswith("https://facebook.com/"):
                        check = is_url_ok(contact_facebook)
                        if check["isOk"] is False:
                            place_check_obj["properties"]["issues"].append(
                                f"'contact:facebook' {check['text']}"
                            )
                    else:
                        place_check_obj["properties"]["issues"].append(
                            "'contact:facebook' should start with 'https://www.facebook.com/'"
                        )
                else:
                    contact_facebook = f"https://www.facebook.com/{contact_facebook}"
                    check = is_url_ok(contact_facebook)
                    if check["isOk"] is False:
                        place_check_obj["properties"]["issues"].append(
                            f"'contact:facebook' {check['text']}"
                        )
            if "facebook" in tags:
                place_check_obj["properties"]["issues"].append(
                    "old tag: 'facebook' -> change to 'contact:facebook'"
                )

            # Instagram
            if "contact:instagram" in tags:
                contact_instagram = tags.get("contact:instagram", "")
                if contact_instagram.startswith("http://"):
                    place_check_obj["properties"]["issues"].append(
                        "'contact:instagram' starts with 'http' instead of 'https'"
                    )
                elif contact_instagram.startswith("https://"):
                    if contact_instagram.startswith(
                        "https://www.instagram.com/"
                    ) or contact_instagram.startswith("https://instagram.com/"):
                        check = is_url_ok(contact_instagram)
                        if check["isOk"] is False:
                            place_check_obj["properties"]["issues"].append(
                                f"'contact:instagram' {check['text']}"
                            )
                    else:
                        place_check_obj["properties"]["issues"].append(
                            "'contact:instagram' should start with 'https://www.instagram.com/'"
                        )
                else:
                    contact_instagram = f"https://www.instagram.com/{contact_instagram}"
                    check = is_url_ok(contact_instagram)
                    if check["isOk"] is False:
                        place_check_obj["properties"]["issues"].append(
                            f"'contact:instagram' {check['text']}"
                        )
            if "instagram" in tags:
                place_check_obj["properties"]["issues"].append(
                    "old tag 'instagram' -> change to 'contact:instagram'"
                )

            # E-Mail
            if "contact:email" in tags:
                email = tags.get("contact:email", "")
            elif "email" in tags:
                email = tags.get("email", "")
            if "contact:email" in tags or "email" in tags:
                email = email.split(";")[0]  # Use only the first email address
                try:
                    validate_email(email)
                except EmailNotValidError as error:
                    place_check_obj["properties"]["issues"].append(
                        "E-Mail is not valid: " + str(error)
                    )
            if "contact:email" in tags and "email" in tags:
                place_check_obj["properties"]["issues"].append(
                    "'email' and 'contact:email' defined -> remove one"
                )

            # Phone
            if "contact:phone" in tags:
                tag_name = "contact:phone"
                check_phone_number(place_check_obj, tag_name, tags)
            if "contact:mobile" in tags:
                tag_name = "contact:mobile"
                check_phone_number(place_check_obj, tag_name, tags)
            if "phone" in tags:
                tag_name = "phone"
                check_phone_number(place_check_obj, tag_name, tags)
            if "contact:phone" in tags and "phone" in tags:
                place_check_obj["properties"]["issues"].append(
                    "'phone' and 'contact:phone' defined -> remove one"
                )

            # Opening hours
            opening_hours = "undefined"
            if (
                "opening_hours:covid19" in tags
                and tags["opening_hours:covid19"] != "same"
                and tags["opening_hours:covid19"] != "restricted"
            ):
                opening_hours = tags["opening_hours:covid19"]
            elif "opening_hours" in tags:
                opening_hours = tags["opening_hours"]
            else:
                place_check_obj["properties"]["undefined"].append("opening_hours")
            if "\n" in opening_hours or "\r" in opening_hours:
                place_check_obj["properties"]["issues"].append(
                    "There is a line break in 'opening_hours' -> remove"
                )

            # Disused
            if "disused" in "".join(tags):
                place_check_obj["properties"]["issues"].append(
                    "There is a 'disused' tag: Check whether this tag is correct. If so please remove the diet tags."
                )

            # fixme
            if "fixme" in tags:
                place_check_obj["properties"]["issues"].append(
                    f'fixme: {tags["fixme"]}'
                )

            # Count issues
            place_check_obj["properties"]["issue_count"] = len(
                place_check_obj["properties"]["issues"]
            ) + len(place_check_obj["properties"]["undefined"])

            if len(place_check_obj["properties"]["issues"]) == 0:
                del place_check_obj["properties"]["issues"]
            if len(place_check_obj["properties"]["undefined"]) == 0:
                del place_check_obj["properties"]["undefined"]

            # Only use elements with issues
            if place_check_obj["properties"]["issue_count"] > 0:
                places_data_checks["features"].append(place_check_obj)
    print(osm_elements_number, " elements.")

    # Sort list by issue count
    places_data_checks["features"] = sorted(
        places_data_checks["features"],
        key=lambda x: x["properties"]["issue_count"],
        reverse=True,
    )
    return places_data_checks


def check_phone_number(place_check_obj, tag_name, tags):
    """Validate phone numbers.

    Args:
        place_check_obj (object): Object to collect the results.
        tag_name (string): Name of the tag that contains the phone number.
        tags (object): All tags of a place.
    """

    # TODO: Also use parsing and formatting in refresh script.
    phone_number = tags.get(tag_name, "")
    phone_number = phone_number.split(";")[0]  # Use only the first phone number
    try:
        parsed_number = phonenumbers.parse(phone_number, None)
        if phonenumbers.is_valid_number(parsed_number):
            phone_number_itute123_pattern = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
            phone_number_rfc3966_pattern = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.RFC3966
            )
            phone_number_rfc3966_pattern = phone_number_rfc3966_pattern.replace(
                "tel:", ""
            )
            if (phone_number_itute123_pattern != phone_number) and (
                phone_number_rfc3966_pattern != phone_number
            ):
                if phone_number.startswith("+1"):
                    place_check_obj["properties"]["issues"].append(
                        f"'{tag_name}' does not conform to the RFC 3966 pattern. It's '{phone_number}' but it should be '{phone_number_rfc3966_pattern}'."
                    )
                else:
                    place_check_obj["properties"]["issues"].append(
                        f"'{tag_name}' does not conform to the ITU-T E.123 pattern. It's '{phone_number}' but it should be '{phone_number_itute123_pattern}'."
                    )
        else:
            place_check_obj["properties"]["issues"].append(
                f"'{tag_name}': Validation of number '{phone_number}' failed. Is this number correct?."
            )
    except Exception as error:
        place_check_obj["properties"]["issues"].append(
            f"'{tag_name}' corresponds neither to the ITU-T E.123 pattern (like '+44 99 123456789') nor to the RFC 3966 pattern (like '+1-710-555-2333') - Error message: "
            + "".join(error.args)
        )


def main():
    # Open url data file
    with open(URL_DATA_FILE, encoding="utf-8") as url_json_file:

        # Get previous url data
        proc.url_data = json.load(url_json_file)

        key_list = list(proc.url_data.keys())

        for element in key_list:
            today = datetime.datetime.strptime(DATE, "%Y-%m-%d")
            url_data_date = datetime.datetime.strptime(
                proc.url_data[element]["date"], "%Y-%m-%d"
            )
            delta = today - url_data_date
            if delta.days > MIN_URL_CHECK_AGE:
                del proc.url_data[element]

    # Call the functions to get and write the osm data.
    osm_data = get_osm_data()

    # Write data
    if osm_data is not None:
        check_result = check_data(osm_data)

        # Write check result file in pretty format
        outfile = open(VEGGIEPLACES_CHECK_RESULT_FILE, "w", encoding="utf-8")
        outfile.write(json.dumps(check_result, indent=1, sort_keys=True))
        outfile.close()
    else:
        print("A problem has occurred. osm_data is None")

    # Write data
    if proc.url_data is not None:
        # print(url_data)
        url_outfile = open(URL_DATA_FILE, "w", encoding="utf-8")
        url_outfile.write(json.dumps(proc.url_data, indent=1, sort_keys=True))
        url_outfile.close()
    else:
        print("A problem has occurred. url_data is None")


class Processor:
    """Class container for processing stuff."""

    counter = 0
    url_data = {}


if __name__ == "__main__":
    proc = Processor()
    main()
