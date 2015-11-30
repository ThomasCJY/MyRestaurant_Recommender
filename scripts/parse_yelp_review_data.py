import os
import json
import sqlite3
from random import randint
import lib.constants as const
import dataset_dirs
import lib.dao as dao

def import_yelp_data():
	if not os.path.exists(const.YELP_RESTAURANT_STARS_FILE):
		print (("Didn't find the ready file %s, regenerating this file from " +
			   "the Yelp dataset... NOTE: THIS IS SLOW!!! You shouldn't have " +
			   "to do this, the txt file should be in the repo!") %
			   const.YELP_RESTAURANT_STARS_FILE)
		create_txt()
	import_from_txt()

def create_txt():
	REVIEWS_JSON_FILE = ("%syelp_academic_dataset_review.json" %
						 dataset_dirs.YELP_DATASET_DIR)

	if not os.path.exists(REVIEWS_JSON_FILE):
		print ("Parse Yelp review data: Couldn't find json file \"%s\"" %
			   REVIEWS_JSON_FILE)
		return
	f = open(REVIEWS_JSON_FILE)
	lines = f.read().split('\n')[:-1]
	f.close()
	entries = [json.loads(line) for line in lines]
	conn = sqlite3.connect(const.DB_FILENAME)
	c = conn.cursor()
	restaurant_ids = dao.get_unique_values(c, 'restaurants', 'id')
	conn.commit()
	c.close()

	all_reviews = [[entry['business_id'], entry['stars']]
					for entry in entries if entry['business_id']
					in restaurant_ids]
	f = open(const.YELP_RESTAURANT_STARS_FILE, 'w')

	for r_id in restaurant_ids:
		reviews = [review[1] for review in all_reviews
				   if review[0]==r_id]
		avg = 0.0 if not reviews else (sum(reviews) / float(len(reviews)))
		f.write("%s,%s\n" % (avg, r_id))

	f.close()

def import_from_txt():
	conn = sqlite3.connect(const.DB_FILENAME)
	c = conn.cursor()
	f = open(const.YELP_RESTAURANT_STARS_FILE)
	entries = [[float(line.split(',')[0]), line.split(',')[1]]
			   for line in f.read().split('\n')[:-1]]
	f.close()
	c.executemany('UPDATE restaurants SET stars=? WHERE id=?', entries)

	conn.commit()
	c.close()

if __name__ == "__main__":
	import_yelp_data()