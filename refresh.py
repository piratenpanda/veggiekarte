#!/usr/bin/python
import cgi
import urllib3
import os
import time
import json
import sys
import datetime	# for the timestamp
import html

assert sys.version_info >= (3,0)

# variables for the overpass request
servers = ["http://overpass-api.de/api/interpreter","http://api.openstreetmap.fr/api/interpreter","http://dev.overpass-api.de/api_drolbr/interpreter"]
http = urllib3.PoolManager()

# variables for the output files
timestamp = datetime.datetime.now()				# the actual date and time
scriptdir = os.path.dirname(os.path.abspath(__file__))		# get the path of the directory of this script
veggiemap_tempfile = scriptdir + '/js/veggiemap-data-temp.js'	# the temp file to store the data from the overpass request
veggiemap_file = scriptdir + '/js/veggiemap-data.js'		# the data file which will be used for the map
veggiemap_oldfile = scriptdir + '/js/veggiemap-data_old.js'	# previous version of the data file (helpful to examine changes)

# icon mapping
icon_mapping = {
'amenity:bar': 'food_bar',
'amenity:bbq': 'tourist_picnic',
'amenity:cafe': 'food_cafe',
'amenity:cinema': 'tourist_cinema',
'amenity:college': 'education_university',
'amenity:fast_food': 'food_fastfood',
'amenity:fuel': 'transport_fuel',
'amenity:hospital': 'health_hospital',
'amenity:kindergarten': 'education_nursery3',
'amenity:library': 'amenity_library',
'amenity:marketplace': 'shopping_marketplace',
'amenity:nightclub': 'food_bar',
'amenity:pharmacy': 'health_pharmacy',
'amenity:place_of_worship': 'place_of_worship_unknown',
'amenity:pub': 'food_pub',
'amenity:restaurant': 'food_restaurant',
'amenity:school': 'education_school',
'amenity:shelter': 'accommodation_shelter2',
'amenity:swimming_pool': 'sport_swimming_outdoor',
'amenity:theatre': 'tourist_theatre',
'amenity:university': 'education_university',
'amenity:vending_machine': 'shopping_vending_machine',
'historic:memorial': 'tourist_memorial',
'leisure:golf_course': 'sport_golf',
'leisure:pitch': 'sport_leisure_centre',
'leisure:recreation_ground': 'sport_leisure_centre',
'leisure:sports_centre': 'sport_leisure_centre',
'leisure:stadium': 'sport_stadium',
'leisure:track': 'sport_leisure_centre',
'shop:alcohol': 'shopping_alcohol',
'shop:bakery': 'shopping_bakery',
'shop:bicycle': 'shopping_bicycle',
'shop:books': 'shopping_book',
'shop:butcher': 'shopping_butcher',
'shop:clothes': 'shopping_clothes',
'shop:confectionery': 'shopping_confectionery',
'shop:convenience': 'shopping_convenience',
'shop:department_store': 'shopping_department_store',
'shop:doityourself': 'shopping_diy',
'shop:fishmonger': 'shopping_fish',
'shop:garden_centre': 'shopping_garden_centre',
'shop:gift': 'shopping_gift',
'shop:greengrocer': 'shopping_greengrocer',
'shop:hairdresser': 'shopping_hairdresser',
'shop:kiosk': 'shopping_kiosk',
'shop:laundry': 'shopping_laundrette',
'shop:music': 'shopping_music',
'shop:supermarket': 'shopping_supermarket'
}

# Determine icon for the marker
def determine_icon(tags):
	icon = 'vegan'

	for kv in icon_mapping:
		k,v = kv.split(':')
		t = tags.get(k)

		if not t:
			continue

		t = t.split(';')[0]

		if t == v:
			icon = icon_mapping[kv]
			break

	icon = icon.replace('-', '_')
	return icon

server = 0

# Getting osm data
def get_data_osm():
	global server

	# Preparing the string for the Overpass request
	overpass_server =		servers[server]
	overpass_data_out =		'?data=[out:json];('
	overpass_vegan_objects =	'node["diet:vegan"~"yes|only"];way["diet:vegan"~"yes|only"];'
	overpass_veggie_objects =	'node["diet:vegetarian"~"yes|only"];way["diet:vegetarian"~"yes|only"];'
	overpass_out =			');out+center;'

	# Overpass request
	r = http.request('GET', overpass_server + overpass_data_out + overpass_vegan_objects + overpass_veggie_objects + overpass_out)

	if r.status == 200:
		return json.loads(r.data.decode('utf-8'))

	elif(r.status == 429):
		time.sleep(60)
		server = (server+1)%len(servers)
		return get_data_osm()

	elif (r.status == 504):
		time.sleep(600)
		server = (server+1)%len(servers)
		return get_data_osm()

	elif (r.status == 400):
		print("HTTP error code", r.status, ": Bad Request")
		time.sleep(5)
		server = (server+1)%len(servers)
		return get_data_osm()

	else:
		print("Unknown HTTP error code", r.status)
		return None

def write_data(osm_data):

	with open(veggiemap_tempfile, 'w') as f:
		f.write('// Created: %s\n' % (timestamp))
		f.write('function veggiemap_populate(markers) {\n')

		for e in osm_data['elements']:
			ide = e['id']
			typ = e['type']
			tags = e.get('tags', {})

			for k in tags.keys():
				tags[k] = cgi.escape(tags[k]).replace('"', '\\"')

			if typ == 'node':
				lat = e.get('lat', None)
				lon = e.get('lon', None)
				if tags.get('diet:vegan') != 'yes' and tags.get('diet:vegan') != 'only' and tags.get('diet:vegetarian') != 'only' and tags.get('diet:vegetarian') != 'yes':
					continue

			if typ == 'way':
				centerCoordinates = e.get('center', None) # get the coordinates from the center of the object
				lat = centerCoordinates.get('lat', None)
				lon = centerCoordinates.get('lon', None)

			if not lat or not lon:
				continue

			if 'name' in tags:
				name = html.unescape(tags['name'])
				# html.unescape() to convert HTML entities to proper characters (issue #25)
			else:
				name = '%s %s' % (typ, ide)

			icon = determine_icon(tags)

			if (tags.get('diet:vegetarian', '') != '' and tags.get('diet:vegan', '') == '') or tags.get('diet:vegan', '') == 'no':
				icon += "_veggie"
			else:
				icon += "_vegan"

			# Building the textbox of the Marker
			popup = '<b>%s</b> <a href=\\"http://openstreetmap.org/browse/%s/%s\\" target=\\"_blank\\">*</a><hr/>' % (name, typ, ide)

			if 'cuisine' in tags:
			#	cuisine = tags['cuisine']
				popup += 'cuisine: %s <br/>' % (tags['cuisine'])

			if 'addr:street' in tags:
				popup += '%s %s<br/>' % (tags.get('addr:street', ''), tags.get('addr:housenumber', ''))

			if 'addr:city' in tags:
				popup += '%s %s<br/>' % (tags.get('addr:postcode', ''), tags.get('addr:city', ''))

			if 'addr:country' in tags:
				popup += '%s<br/>' % (tags.get('addr:country', ''))
				popup += '<hr/>'

			if 'contact:website' in tags:
				popup += 'website: <a href=\\"%s\\" target=\\"_blank\\">%s</a><br/>' % (tags['contact:website'], tags['contact:website'])

			elif 'website' in tags:
				popup += 'website: <a href=\\"%s\\" target=\\"_blank\\">%s</a><br/>' % (tags['website'], tags['website'])

			if 'contact:email' in tags:
				popup += 'email: <a href=\\"mailto:%s\\" target=\\"_blank\\">%s</a><br/>' % (tags['contact:email'], tags['contact:email'])

			elif 'email' in tags:
				popup += 'email: <a href=\\"mailto:%s\\" target=\\"_blank\\">%s</a><br/>' % (tags['email'], tags['email'])

			if 'contact:phone' in tags:
				popup += 'phone: %s<br/>' % (tags['contact:phone'])

			elif 'phone' in tags:
				popup += 'phone: %s<br/>' % (tags['phone'])

			f.write('L.marker([%s, %s], {"title": "%s", icon: icon_%s}).bindPopup("%s").addTo(markers);\n' % (lat, lon, name, icon, popup))
		f.write('}\n')

osm_data = get_data_osm()

while(osm_data == False or osm_data == None or osm_data == ""):
	osm_data = get_data_osm()

write_data(osm_data)

if os.path.isfile(veggiemap_tempfile):				# check if the temp file exists
	if os.path.getsize(veggiemap_tempfile) > 100:		# check if the temp file isn't to small (see issue #21)
		print("rename " + veggiemap_tempfile + " to " + veggiemap_file)
		os.rename(veggiemap_file, veggiemap_oldfile)	# rename old file
		os.rename(veggiemap_tempfile, veggiemap_file)	# rename temp file to new file
	else:
		print("temp file is to small!")
		print(os.path.getsize(veggiemap_tempfile))
else:
    print("temp file don't exists!")
