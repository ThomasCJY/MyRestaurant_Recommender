import os
import sys
import json
import sqlite3

def get_n_top_scores(c, metro_area, n=10):
	metro_id = get_metro_id(c, metro_area)
	if metro_id is None:
		return {}
	results_raw = c.execute(
		"""
		SELECT cat.name, sc.zip_code, sc.score FROM
		restaurants_scores sc JOIN restaurant_categories cat
		ON sc.restaurant_category_id == cat.id
		WHERE sc.metro_id=?
		ORDER BY score DESC
		LIMIT ?
		""",
		[metro_id, n]
	).fetchall()
	results = [{'category': r[0], 'zip_code': r[1], 'score': r[2]}
			   for r in results_raw]
	return results

def get_metro_id(c, metro_name):
	# Could use get_id_of_name as well but then we'd create stuff in db...
	matches = c.execute('SELECT id FROM metro_areas WHERE name=?',
				    [metro_name]).fetchall()
	if not matches:
		return None
	else:
		# TODO(HACK): This relies on that metro area names are unique.
		# Should require sending state too!
		return matches[0][0]

def get_unique_values(c, table, field):
	query_res = c.execute(
		'SELECT DISTINCT %s FROM %s' % (field, table)
	).fetchall()
	return [x[0] for x in query_res]

# If the given combo of zip_code and state_id doesn't exist, store it.
def check_add_zip_code(c, zip_code, state_id):
	results = c.execute(
		'SELECT zip_code from zip_codes WHERE zip_code=? and state_id=?',
		[zip_code, state_id]
	).fetchall()

	if len(results) != 1 or len(results[0]) != 1:
		c.execute('INSERT INTO zip_codes (zip_code, state_id) VALUES (?, ?)',
				  [zip_code, state_id])

def get_id_of_name(c, table, name, id_field='id', name_field='name'):
	results = c.execute('SELECT %s from %s WHERE %s=?' %
					    (id_field, table, name_field), [name]).fetchall()

	if len(results) != 1 or len(results[0]) != 1:
		c.execute('INSERT INTO %s (%s) VALUES (?)' % (table, name_field),
				  [name])
		results = c.execute('SELECT %s from %s WHERE %s=?' %
						    (id_field, table, name_field), [name]).fetchall()
		if len(results) != 1 or len(results[0]) != 1:
			return None

	return results[0][0]

def get_level_ids(c):
    level_ids = []
    for level in ['low', 'mid', 'high']:
        level_ids.append(get_id_of_name(c, 'price_levels', level))
    return level_ids