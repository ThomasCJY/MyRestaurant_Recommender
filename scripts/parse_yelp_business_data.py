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
	restaurants = [entry for entry in entries if 'Restaurants' in entry['categories']]
	f.close()

	# TODO will "open" ever be false? seems to be true always. But if it just
	# changes over time we don't care about this field.

	conn = sqlite3.connect(const.DB_FILENAME)
	c = conn.cursor()

	## weekdays
	for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
				'Friday', 'Saturday', 'Sunday']:
		c.execute('INSERT INTO weekdays (name) values (?)', [day])

	## restaurant_categories
	restaurant_categories = ([category for x in restaurants
							  for category in x['categories']])


	### DUMMY PART!!
	# HACK: just one metro per state in this dataset, hard-coding
	metro_areas_by_state = {
		'NV': 'Las Vegas', 'AZ': 'Phoenix', 'WI': 'Madison',
		'IL': 'Urbana-Champaign', 'NC': 'Charlotte', 'PA': 'Pittsburgh',
		'QC': 'Montreal', 'ON': 'Waterloo', 'BW': 'Karlsruhe',
		'EDH': 'Edinburgh'
	}

	# states
	c.executemany('INSERT INTO states (name) VALUES (?)',
			      [[x] for x in metro_areas_by_state.keys()])
	state_entries = c.execute('SELECT id, name FROM states').fetchall()
	states_ids = {x[1]: x[0] for x in state_entries}

	# metro_areas
	c.executemany('INSERT INTO metro_areas (name, state_id) VALUES (?,?)',
			      [(metro_areas_by_state[state], states_ids[state])
			       for state in metro_areas_by_state])

	# zip_codes_metro_areas
	zip_codes_entries = []
	zip_codes_metro_areas_entries = []
	# (HACK)
	metro_names_to_id = {x[1]: x[0] for x in
						 c.execute('SELECT id, name FROM metro_areas').fetchall()}
	for state_id, state in state_entries:
		# TODO(HACK) need a better way to get zip code. Canada and Germany have
		# other characters in their zip codes, including spaces. Some restaurants
		# haven't listed their zip at all, just state...
		# As it is below we don't store any zip codes for Canada/Germany!
		zip_codes = [x['full_address'][-5:] for x in restaurants
				     if len(x['full_address']) >= 5
				     and x['state'] == state
				     and x['full_address'][-5:].isdigit()]
		for zip_code in set(zip_codes):
			zip_codes_entries.append((zip_code, state_id))
			# (HACK)
			zip_codes_metro_areas_entries.append((
				zip_code, state_id,
				metro_names_to_id[metro_areas_by_state[state]]
			))

	c.executemany('INSERT INTO zip_codes (zip_code, state_id) VALUES (?,?)',
				  zip_codes_entries)

	c.executemany('INSERT INTO metro_areas_zip_codes(zip_code, state_id, ' +
				  'metro_id) VALUES (?,?,?)', zip_codes_metro_areas_entries)

	### END OF DUMMY PART

	for r in restaurants:
		restaurant_id = r['business_id']

		## restaurants
		data = [
			restaurant_id,
			r['full_address'],
			r['city'],
			r['review_count'],
			r['name'],
			r['longitude'],
			r['latitude'],
			get_id_of_name(c, 'states', r['state']),
			r['stars'],
		]
		c.execute(
			'INSERT INTO restaurants (id, full_address, city, review_count, ' +
			'name, longitude, latitude, state_id, stars) VALUES ' +
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
			category_id = get_id_of_name(c, 'restaurant_categories', category)
			if category_id is None:
				print ("ERROR: Couldn't find category %s for restaurant %s" %
					   (category, restaurant_id))
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
			attribute_id = get_id_of_name(c, 'restaurant_attributes', attribute)
			if attribute_id is None:
				print ("ERROR: Failed to insert attribute \"%s\" of " +
					   "restaurant \"%s\"" % (attribute, restaurant_id))
				continue
			has = 1 if r['attributes'][attribute] else 0

			# restaurants_attributes
			c.execute('INSERT INTO restaurants_attributes (restaurant_id, ' +
				' attribute_id, has) VALUES (?,?,?)',
				(restaurant_id, attribute_id, has))

	### DUMMY PART 2
	# restaurants_scores
	category_ids = get_unique_values(c, 'restaurant_categories', 'id')
	scores_by_zip_metro = []
	for zip_code, state_id, metro_id in zip_codes_metro_areas_entries:
		for category_id in category_ids:
			# TODO is category_id an integer already?
			scores_by_zip_metro.append((
				int(category_id), zip_code, state_id, metro_id, randint(0,100)
			))

	c.executemany(
		'INSERT INTO restaurants_scores (restaurant_category_id, zip_code, ' +
		'state_id, metro_id, score) VALUES (?,?,?,?,?)', scores_by_zip_metro
	)

	### END OF DUMMY PART 2

	conn.commit()
	c.close()

def get_id_of_name(c, table, name, id_field='id', name_field='name'):
	return dao.get_id_of_name(c, table, name, id_field=id_field, name_field=name_field)

def get_unique_values(c, table, field):
	return dao.get_unique_values(c, table, field)

if __name__ == "__main__":
	import_yelp_data()