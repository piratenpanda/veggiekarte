#!/usr/bin/python
import urllib3
import os
import time
import json
import sys
import datetime	# for the timestamp
import html

assert sys.version_info >= (3,0)

# variables for the overpass request

# server list from: https://wiki.openstreetmap.org/wiki/Overpass_API
servers = [	"https://lz4.overpass-api.de/api/interpreter",
		"https://overpass.kumi.systems/api/interpreter",
		"https://z.overpass-api.de/api/interpreter",
		"http://api.openstreetmap.fr/api/interpreter",
		"http://dev.overpass-api.de/api_drolbr/interpreter",
		"http://overpass-api.de/api/interpreter",
		"http://overpass.openstreetmap.fr/api/interpreter",
		"http://overpass.osm.ch/api/interpreter"
		]
http = urllib3.PoolManager()

# variables for the output files
timestamp = datetime.datetime.now()				# the actual date and time
scriptdir = os.path.dirname(os.path.abspath(__file__))		# get the path of the directory of this script
veggiemap_tempfile = scriptdir + '/js/veggiemap-data-temp.js'	# the temp file to store the data from the overpass request
veggiemap_file = scriptdir + '/js/veggiemap-data.js'		# the data file which will be used for the map
veggiemap_oldfile = scriptdir + '/js/veggiemap-data_old.js'	# previous version of the data file (helpful to examine changes)

# icon mapping
icon_mapping = {
'amenity:bar': 'bar',
'amenity:bbq': 'bbq',
'amenity:cafe': 'cafe',
'amenity:cinema': 'cinema',
'amenity:college': 'maki_college',
'amenity:fast_food': 'fast_food',
'amenity:food_court': 'restaurant',
'amenity:fuel': 'fuel',
'amenity:hospital': 'hospital',
'amenity:ice_cream': 'ice_cream',
'amenity:kindergarten': 'playground',
'amenity:pharmacy': 'pharmacy',
'amenity:place_of_worship': 'place_of_worship',
'amenity:pub': 'pub',
'amenity:restaurant': 'restaurant',
'amenity:school': 'maki_school',
'amenity:shelter': 'shelter',
'amenity:swimming_pool': 'maki_swimming',
'amenity:theatre': 'theatre',
'amenity:university': 'maki_college',
'amenity:vending_machine': 'maki_shop',
'historic:memorial': 'monument',
'leisure:golf_course': 'golf',
'leisure:pitch': 'maki_pitch',
'leisure:sports_centre': 'sports',
'leisure:stadium': 'maki_stadium',
'shop:alcohol': 'alcohol',
'shop:bakery': 'bakery',
'shop:beauty': 'beauty',
'shop:bicycle': 'bicycle',
'shop:books': 'library',
'shop:butcher': 'butcher',
'shop:clothes': 'clothes',
'shop:confectionery': 'confectionery',
'shop:convenience': 'convenience',
'shop:department_store': 'department_store',
'shop:doityourself': 'diy',
'shop:fishmonger': 'maki_shop',
'shop:garden_centre': 'garden-centre',
'shop:general': 'maki_shop',
'shop:gift': 'gift',
'shop:greengrocer': 'greengrocer',
'shop:hairdresser': 'hairdresser',
'shop:kiosk': 'maki_shop',
'shop:music': 'music',
'shop:supermarket': 'supermarket',
'shop:wine': 'alcohol',
'tourism:guest_house': 'guest_house',
'tourism:museum': 'museum'
}

# Determine icon for the marker
def determine_icon(tags):
	icon = 'maki_star-stroked'	# Use this icon if there is no matching per icon_mapping.
	for kv in icon_mapping:
		k,v = kv.split(':')
		t = tags.get(k)

		if not t:
			continue

		t = t.split(';')[0]

		if t == v:
			icon = icon_mapping[kv]
			break
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
	print("Send query to server: ", overpass_server)
	r = http.request('GET', overpass_server + overpass_data_out + overpass_vegan_objects + overpass_veggie_objects + overpass_out)

	if r.status == 200:
		print("Received answer successfully.")
		return json.loads(r.data.decode('utf-8'))
	elif (r.status == 400):
		print("HTTP error code ", r.status, ": Bad Request")
		time.sleep(5)
		server = (server+1)%len(servers)
		return get_data_osm()
	elif(r.status == 429):
		print("HTTP error code ", r.status, ": Too Many Requests")
		time.sleep(60)
		server = (server+1)%len(servers)
		return get_data_osm()
	elif (r.status == 504):
		print("HTTP error code ", r.status, ": Gateway Timeout")
		time.sleep(600)
		server = (server+1)%len(servers)
		return get_data_osm()
	else:
		print("Unknown HTTP error code: ", r.status)
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
				# Convert characters into html entities
				# (to prevent escape any code)
				tags[k] = html.escape(tags[k])

			if typ == 'node':
				lat = e.get('lat', None)
				lon = e.get('lon', None)

			if typ == 'way':
				centerCoordinates = e.get('center', None) # get the coordinates from the center of the object
				lat = centerCoordinates.get('lat', None)
				lon = centerCoordinates.get('lon', None)

			if not lat or not lon:
				continue

			if 'name' in tags:
				# The name will be shown in the popup box
				# (where the browser converts html entities).
				name = tags['name']

				# The title of a marker will be shown on mouse hover
				# (where the browser DON'T converts html entities (issue #25)).
				# So we reconvert the html entities into the proper characters:
				title = html.unescape(name)
				## But double quoutes could escape code, so we have to replace them:
				title = title.replace('"', '”')
			else:
				name = '%s %s' % (typ, ide)
				title = name

			icon = determine_icon(tags)

			# Give the object a category
			if (tags.get('diet:vegetarian', '') != '' and tags.get('diet:vegan', '') == '') or tags.get('diet:vegan', '') == 'no':
				category = "veggie"
			elif (tags.get('diet:vegan', '') == 'yes' or tags.get('diet:vegan', '') == 'only'):
				category = "vegan"
			elif tags.get('diet:vegan', '') == 'limited':
				category = "vegan_limited"
			else:
				category = "no_category"
				print("Object without category!")

			# Building the textbox of the Marker
			popup = '<b>%s</b> <a href=\\"https://openstreetmap.org/%s/%s\\" target=\\"_blank\\">*</a><hr/>' % (name, typ, ide)

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

			f.write('L.marker([%s, %s], {title: "%s", icon: getIcon("%s", "%s")}).bindPopup("%s").addTo(%s);\n' % (lat, lon, title, icon, category, popup, category))
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
