#!/usr/bin/python
import cgi
import urllib
import urllib2
import simplejson
import os

icon_mapping = {
'aeroway:aerodrome': 'transport_airport',
'aeroway:gate': 'transport_airport_gate',
'aeroway:helipad': 'transport_helicopter_pad',
'aeroway:terminal': 'transport_airport_terminal',
'amenity:atm': 'money_atm',
'amenity:bank': 'money_bank2',
'amenity:bar': 'food_bar',
'amenity:bbq': 'tourist_picnic',
'amenity:bench': 'amenity_bench',
'amenity:bicycle_parking': 'transport_parking_bicycle',
'amenity:bicycle_rental': 'transport_rental_bicycle',
'amenity:bus_station': 'transport_bus_station',
'amenity:cafe': 'food_cafe',
'amenity:car_rental': 'transport_rental_car',
'amenity:cinema': 'tourist_cinema',
'amenity:college': 'education_university',
'amenity:drinking_water': 'food_drinkingtap',
'amenity:fast_food': 'food_fastfood',
'amenity:ferry_terminal': 'transport_port',
'amenity:fire_station': 'amenity_firestation2',
'amenity:fountain': 'amenity_fountain2',
'amenity:fuel': 'transport_fuel',
'amenity:grave_yard': 'place_of_worship_unknown3',
'amenity:hospital': 'health_hospital',
'amenity:hunting_stand': 'sport_shooting',
'amenity:kindergarten': 'education_nursery3',
'amenity:library': 'amenity_library',
'amenity:marketplace': 'shopping_marketplace',
'amenity:nightclub': 'food_bar',
'amenity:parking': 'transport_parking_car',
'amenity:pharmacy': 'health_pharmacy',
'amenity:place_of_worship': 'place_of_worship_unknown',
'amenity:police': 'amenity_police2',
'amenity:post_box': 'amenity_post_box',
'amenity:post_office': 'amenity_post_office',
'amenity:pub': 'food_pub',
'amenity:recycling': 'amenity_recycling',
'amenity:restaurant': 'food_restaurant',
'amenity:school': 'education_school',
'amenity:shelter': 'accommodation_shelter2',
'amenity:swimming_pool': 'sport_swimming_outdoor',
'amenity:taxi': 'transport_taxi_rank',
'amenity:telephone': 'amenity_telephone',
'amenity:theatre': 'tourist_theatre',
'amenity:toilets': 'amenity_toilets',
'amenity:townhall': 'amenity_town_hall',
'amenity:university': 'education_university',
'amenity:vending_machine': 'shopping_vending_machine',
'amenity:veterinary': 'health_veterinary',
'amenity:waste_basket': 'amenity_waste_bin',
'barrier:block': 'barrier_blocks',
'barrier:bollard': 'barrier_bollard',
'barrier:cattle_grid': 'barrier_cattle_grid',
'barrier:cycle_barrier': 'barrier_cycle_barrier',
'barrier:gate': 'barrier_gate',
'barrier:kissing_gate': 'barrier_kissing_gate',
'barrier:lift_gate': 'barrier_lift_gate',
'barrier:stile': 'barrier_stile',
'barrier:toll_booth': 'barrier_toll_booth',
'boundary:administrative': 'poi_boundary_administrative',
'highway:bus_stop': 'transport_bus_stop2',
'highway:crossing': 'transport_zebra_crossing',
'highway:mini_roundabout': 'transport_miniroundabout_anticlockwise',
'highway:turning_circle': 'transport_turning_circle',
'historic:archaeological_site': 'tourist_archaeological',
'historic:battlefield': 'tourist_battlefield',
'historic:castle': 'tourist_castle',
'historic:memorial': 'tourist_memorial',
'historic:monument': 'tourist_monument',
'historic:ruins': 'tourist_ruin',
'landuse:cemetery': 'place_of_worship_unknown3',
'landuse:farmland': 'landuse_grass',
'landuse:farm': 'landuse_grass',
'landuse:farmyard': 'landuse_grass',
'landuse:forest': 'landuse_coniferous',
'landuse:meadow': 'landuse_grass',
'landuse:military': 'poi_military_bunker',
'landuse:orchard': 'landuse_grass',
'landuse:quarry': 'poi_mine',
'landuse:vineyard': 'landuse_grass',
'leisure:golf_course': 'sport_golf',
'leisure:marina': 'transport_marina',
'leisure:pitch': 'sport_leisure_centre',
'leisure:playground': 'amenity_playground',
'leisure:recreation_ground': 'sport_leisure_centre',
'leisure:slipway': 'transport_slipway',
'leisure:sports_centre': 'sport_leisure_centre',
'leisure:stadium': 'sport_stadium',
'leisure:track': 'sport_leisure_centre',
'natural:wood': 'landuse_coniferous',
'place:city': 'poi_place_city',
'place:hamlet': 'poi_place_hamlet',
'place:neighbourhood': 'poi_place_suburb',
'place:suburb': 'poi_place_suburb',
'place:town': 'poi_place_town',
'place:village': 'poi_place_village',
'power:pole': 'power_tower_low',
'power:station': 'power_substation',
'power:sub_station': 'power_transformer',
'power:tower': 'power_tower_high2',
'railway:station': 'transport_train_station',
'railway:tram_stop': 'transport_tram_stop',
'shop:alcohol': 'shopping_alcohol',
'shop:bakery': 'shopping_bakery',
'shop:bicycle': 'shopping_bicycle',
'shop:books': 'shopping_book',
'shop:butcher': 'shopping_butcher',
'shop:car_repair': 'shopping_car_repair',
'shop:car': 'shopping_car',
'shop:clothes': 'shopping_clothes',
'shop:confectionery': 'shopping_confectionery',
'shop:convenience': 'shopping_convenience',
'shop:department_store': 'shopping_department_store',
'shop:doityourself': 'shopping_diy',
'shop:fishmonger': 'shopping_fish',
'shop:florist': 'shopping_florist',
'shop:garden_centre': 'shopping_garden_centre',
'shop:gift': 'shopping_gift',
'shop:greengrocer': 'shopping_greengrocer',
'shop:hairdresser': 'shopping_hairdresser',
'shop:hifi': 'shopping_hifi',
'shop:jewelry': 'shopping_jewelry',
'shop:kiosk': 'shopping_kiosk',
'shop:laundry': 'shopping_laundrette',
'shop:motorcycle': 'shopping_motorcycle',
'shop:music': 'shopping_music',
'shop:supermarket': 'shopping_supermarket',
'shop:supermarket': 'shopping_supermarket',
'shop:toys': 'shopping_toys',
'tourism:alpine_hut': 'accommodation_alpinehut',
'tourism:artwork': 'tourist_art_gallery2',
'tourism:attraction': 'tourist_attraction',
'tourism:camp_site': 'accommodation_camping',
'tourism:caravan_site': 'accommodation_caravan_park',
'tourism:chalet': 'accommodation_chalet',
'tourism:guest_house': 'accommodation_bed_and_breakfast',
'tourism:hostel': 'accommodation_youth_hostel',
'tourism:hotel': 'accommodation_hotel',
'tourism:motel': 'accommodation_motel',
'tourism:museum': 'tourist_museum',
'tourism:picnic_site': 'tourist_picnic',
'tourism:theme_park': 'tourist_theme_park',
'tourism:viewpoint': 'tourist_view_point',
'tourism:zoo': 'tourist_zoo',
'traffic_calming:yes': 'transport_speedbump',
}

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

scriptdir = os.path.dirname(os.path.abspath(__file__))

f = urllib2.urlopen('http://overpass-api.de/api/interpreter?data=[out:json];(node["diet:vegan"~"yes|only"];way["diet:vegan"~"yes|only"];>;);out;')
json = simplejson.load(f)
f.close()

nodes = {}
cnt = 0

with open(scriptdir + 'js/veganmap-data.js', 'w') as f:
  f.write('function veganmap_populate(markers) {\n')
  for e in json['elements']:
    lat = e.get('lat', None)
    lon = e.get('lon', None)
    typ = e['type']
    tags = e.get('tags', {})
    for k in tags.keys():
        tags[k] = cgi.escape(tags[k]).replace('"', '\\"')
    ide = e['id']

    if typ == 'node':
      nodes[ide] = (lat,lon)
      if tags.get('diet:vegan') != 'yes' and tags.get('diet:vegan') != 'only':
        continue
      #if tags.get('diet:vegetarian') != 'yes' and tags.get('diet:vegetarian') != 'only':
	#continue

    if typ == 'way':
      lat, lon = nodes[e['nodes'][0]] # extract coordinate of first node

    if not lat or not lon:
      continue

    cnt += 1

    if 'name' in tags:
      name = tags['name']
    else:
      name = '%s %s' % (typ, ide)

    icon = determine_icon(tags)
    popup = '<b>%s</b> <a href=\\"http://openstreetmap.org/browse/%s/%s\\" target=\\"_blank\\">*</a><hr/>' % (name, typ, ide)
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
    f.write('  L.marker([%s, %s], {"title": "%s", icon: icon_%s}).bindPopup("%s").addTo(markers);\n' % (lat, lon, name.encode('utf-8'), icon, popup.encode('utf-8')))
#  f.write('  document.getElementById("count").innerHTML = "<b>%d</b>";\n' % cnt);
  f.write('}\n')
