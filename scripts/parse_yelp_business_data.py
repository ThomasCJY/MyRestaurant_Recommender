import os
import json
import sqlite3
from random import randint
import lib.constants as const
import dataset_dirs
import lib.dao as dao

def import_yelp_data():
	BUSINESS_JSON_FILE = "%syelp_academic_dataset_business.json" % dataset_dirs.YELP_DATASET_DIR
	
	if not os.path.exists(BUSINESS_JSON_FILE):
		print "Parse Yelp business data: Couldn't find json file \"%s\"" % BUSINESS_JSON_FILE
		return
	f = open(BUSINESS_JSON_FILE)	
	lines = f.read().split('\n')[:-1]
	entries = [json.loads(line) for line in lines]
	restaurants = [
		entry for entry in entries if [cat for cat in entry['categories'] 
									   if cat in const.RESTAURANT_CATEGORIES]
	]
	f.close()
	conn = sqlite3.connect(const.DB_FILENAME)
	c = conn.cursor()

	## weekdays
	for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
				'Friday', 'Saturday', 'Sunday']:
		c.execute('INSERT INTO weekdays (name) values (?)', [day])

	## restaurant_categories
	c.executemany('INSERT INTO restaurant_categories (name) VALUES(?)',
				  [[x] for x in const.RESTAURANT_CATEGORIES])

	# There's very few restaurants that don't list their zip code, and something around
	# half are food trucks and thus don't have one set location. We disregard these
	# since there are only about 30 out of tens of thousands of restaurants in the dataset.
	restaurants = [r for r in restaurants if r['state'] in const.metro_areas_by_state.keys()
			       if len(r['full_address'])>=5 and r['full_address'][-5:].isdigit()]

	for r in restaurants:
		r['zip_code'] = int(r['full_address'][-5:])

	# states
	c.executemany('INSERT INTO states (name) VALUES (?)',
			      [[x] for x in const.metro_areas_by_state.keys()])
	state_entries = c.execute('SELECT id, name FROM states').fetchall()
	states_ids = {x[1]: x[0] for x in state_entries}

	# metro_areas
	c.executemany('INSERT INTO metro_areas (name, state_id) VALUES (?,?)',
			      [(const.metro_areas_by_state[state], states_ids[state])
			       for state in const.metro_areas_by_state])

	# zip_codes_metro_areas
	zip_codes_entries = []
	metro_names_to_id = {x[1]: x[0] for x in
						 c.execute('SELECT id, name FROM metro_areas').fetchall()}
	for state_id, state in state_entries:
		# TODO(HACK) need a better way to get zip code. Canada and Germany have
		# other characters in their zip codes, including spaces. Some restaurants
		# haven't listed their zip at all, just state...
		# As it is below we don't store any zip codes for Canada/Germany!
		zip_codes = [r['zip_code'] for r in restaurants
				     if r['state'] == state]
		for zip_code in set(zip_codes):
			zip_codes_entries.append((
				zip_code, state_id,
				# (HACK)
				metro_names_to_id[const.metro_areas_by_state[state]]
			))

	c.executemany('INSERT INTO zip_codes (zip_code, state_id, metro_id) VALUES (?,?,?)',
				  zip_codes_entries)

	for r in restaurants:
		restaurant_id = r['business_id']

		## restaurants

		# We disregard the 'open' field since it seems to be just a way for yelp to find
		# restaurants that are open at the current time and thus serve that info to users.
		# They would just update it in the database whenever a restaurant opens or closes,
		# to amortize the cost of looking this up when users search for restaurants 'Open Now'.

		data = [
			restaurant_id,
			r['full_address'],
			r['city'],
			r['review_count'],
			r['name'],
			r['longitude'],
			r['latitude'],
			r['zip_code'],
			r['stars'],
		]
		c.execute(
			'INSERT INTO restaurants (id, full_address, city, review_count, ' +
			'name, longitude, latitude, zip_code, stars) VALUES ' +
			'(?, ?, ?, ?, ?, ?, ?, ?, ?)', data
		)

		## restaurants_hours
		for day in r['hours']:
			day_id = get_id_of_name(c, 'weekdays', day)
			if day_id is None:
				print ("ERROR: Couldn't find day \"%s\" for restaurant %s" %
					   (day, restaurant_id))
				continue
			open_time = r['hours'][day]['open']
			close_time = r['hours'][day]['close']
			c.execute('INSERT INTO restaurants_hours (restaurant_id, day, ' +
					  'open, close) VALUES (?, ?, ?, ?)',
					  [restaurant_id, day_id, open_time, close_time])

		for category in [cat for cat in r['categories']
						 if cat != 'Restaurants']:
			category_id = get_id_of_name(c, 'restaurant_categories', category,
										 add_nonexisting=False)
			if category_id is None:
				continue

			c.execute(
				'INSERT INTO restaurants_categories ' +
				'(restaurant_id, category_id) VALUES (?,?)',
				[restaurant_id, category_id])

		for neighborhood in r['neighborhoods']:
			# restaurant_neighborhoods
			neighborhood_id = get_id_of_name(c, 'restaurant_neighborhoods',
										      neighborhood)
			if neighborhood_id is None:
				print ("ERROR: Failed to insert neighborhood \"%s\" of " +
					   "restaurant \"%s\"" % (neighborhood, restaurant_id))
				continue

			# restaurants_neighborhoods
			c.execute(
				'INSERT INTO restaurants_neighborhoods ' +
				'(restaurant_id, neighborhood_id) VALUES (?,?)',
				[restaurant_id, neighborhood_id]
			)

		# restaurant_attributes
		for attribute in r['attributes']:
			if attribute=='Ambience' or attribute=='Good For' or attribute=='Parking':
				for attr in r['attributes'][attribute]:
					insert_attributs(c, attr, restaurant_id,r['attributes'][attribute])
			elif attribute=='Outdoor Seating' or attribute=='Waiter Service' or attribute=='Accepts Credit Cards' or attribute=='Take-out' or attribute=='Takes Reservations' or attribute=='Delivery'or attribute=='Price Range':
				insert_attributs(c, attribute, restaurant_id, r['attributes'])
			else:
				continue
			# attribute_id = get_id_of_name(c, 'restaurant_attributes', attribute,
			# 							  add_nonexisting=True)
			# if attribute_id is None:
			# 	print (("ERROR: Failed to insert attribute \"%s\" of " +
			# 		   "restaurant \"%s\"") % (attribute, restaurant_id))
			# 	continue
			# has = 1 if r['attributes'][attribute] else 0

			# # restaurants_attributes
			# c.execute('INSERT INTO restaurants_attributes (restaurant_id, ' +
			# 	' attribute_id, has) VALUES (?,?,?)',
			# 	(restaurant_id, attribute_id, has))

	### DUMMY SCORES
	# restaurants_scores
	category_ids = get_unique_values(c, 'restaurant_categories', 'id')
	scores_by_zip_metro = []
	for zip_code, state_id, metro_id in zip_codes_entries:
		for category_id in category_ids:
			# TODO is category_id an integer already?
			scores_by_zip_metro.append((
				int(category_id), zip_code, state_id, metro_id, randint(0,100)
			))

	c.executemany(
		'INSERT INTO restaurants_scores (restaurant_category_id, zip_code, ' +
		'state_id, metro_id, score) VALUES (?,?,?,?,?)', scores_by_zip_metro
	)

	conn.commit()
	c.close()

def insert_attributs(c, attribute, restaurant_id, l):
	if(attribute == 'valet'):
		return 
	attribute_id = get_id_of_name(c, 'restaurant_attributes', attribute,
								  add_nonexisting=True)
	if attribute_id is None:
		print (("ERROR: Failed to insert attribute \"%s\" of " +
			   "restaurant \"%s\"") % (attribute, restaurant_id))
		return 
	if l[attribute] == 'True':
		has = 1
	elif l[attribute]=='False':
		has = 0
	elif l[attribute]=={}:
		return
	else:
		has = int(l[attribute])

	# restaurants_attributes
	c.execute('INSERT INTO restaurants_attributes (restaurant_id, ' +
		' attribute_id, has) VALUES (?,?,?)',
		(restaurant_id, attribute_id, has))
	return 

def get_id_of_name(c, table, name, id_field='id', name_field='name', add_nonexisting=True):
	return dao.get_id_of_name(c, table, name, id_field=id_field, name_field=name_field,
							  add_nonexisting=add_nonexisting)

def get_unique_values(c, table, field):
	return dao.get_unique_values(c, table, field)

if __name__ == "__main__":
	import_yelp_data()