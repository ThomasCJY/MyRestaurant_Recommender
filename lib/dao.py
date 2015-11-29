import os
import sys
import json
import sqlite3
import lib.constants as const

def get_top_scores_in_metro(c, metro_area, count=10):
	if count < 1:
		return {}
	metro_id = get_id_of_name(c, 'metro_areas', metro_area, add_nonexisting=False)
	if metro_id is None:
		return None
	results_raw = get_top_scoring(c, fields=['restaurant_category_id', 'zip_code', 'score'],
							      constraints={'metro_id': metro_id}, count=count)
	results = [{'category': get_name_from_id(c, 'restaurant_categories', r[0]),
	 			'zip_code': r[1], 'score': r[2]} for r in results_raw]
	return results

def get_top_scoring(c, fields=[], constraints={}, count=3):
	return get_matching(c,
					    'restaurants_scores',
					    fields,
					    constraints,
					    tail="ORDER BY score DESC LIMIT %d" % count)

def list_restaurants_in_zip(c, zip_code, fields=None):
	if fields is None:
		fields = const.RESTAURANTS_FIELDS
	# Might wanna check for SQL injection
	fields_str = ', '.join(fields)
	return c.execute('SELECT %s FROM restaurants WHERE zip_code=?' % fields_str,
					 [zip_code]).fetchall()

def get_matching(c, table, fields, constraints, tail=None):
	# Might wanna check for SQL injection
	result = []
	fields_str = ', '.join(fields)
	constraint_vars = constraints.keys()
	constraints_str = ' AND '.join(["%s=?" % (var) for var in constraint_vars])
	query = ("SELECT %s FROM %s WHERE %s" %
			 (fields_str, table, constraints_str))
	if tail:
		query = "%s %s" % (query, tail)
	# Generate parameters to c.execute(query, <values for ?'s>)
	return c.execute(query, [constraints[var] for var in constraint_vars]).fetchall()	

def get_unique_values(c, table, field):
	query_res = c.execute(
		'SELECT DISTINCT %s FROM %s' % (field, table)
	).fetchall()
	return [x[0] for x in query_res]

def get_id_of_name(c, table, name, id_field='id', name_field='name', add_nonexisting=True, **kwargs):
	return get_unique_val(c, table, [name], [name_field], id_field, add_nonexisting, **kwargs)

def get_name_from_id(c, table, id_val, id_field='id', name_field='name', **kwargs):
	return get_unique_val(c, table, [id_val], [id_field], name_field, False, **kwargs)

def get_unique_val(c, table, given_vals, given_fields, desired_field, add_nonexisting, **kwargs):
	if len(given_vals) != len(given_vals):
		print "len mismatch between given vals and fields!"
		return None
	constraints_str = ' AND '.join(["%s=?" % field for field in given_fields])
	query = ('SELECT %s FROM %s WHERE %s' %
			(desired_field, table, constraints_str))
	results = c.execute(query, given_vals).fetchall()

	if (len(results) != 1 or len(results[0]) != 1):
		if not add_nonexisting:
			print ("not add nonexisting for %s of %s %s in table %s" %
				   (desired_field, given_fields, given_vals, table))
			return None
		insert_tables = ', '.join(given_fields + kwargs.keys())
		given_vals = given_vals + kwargs.values()
		c.execute('INSERT INTO %s (%s) VALUES (%s)' %
				  (table, insert_tables, ','.join(['?' for _ in given_vals])),
				  given_vals)
		results = c.execute(query, given_vals).fetchall()
		if len(results) != 1 or len(results[0]) != 1:
			print "not 1 result for %s of %s %s" % (desired_field, given_fields, given_vals)
			return None

	return results[0][0]

def get_level_ids(c):
    level_ids = []
    for level in ['low', 'mid', 'high']:
        level_ids.append(get_id_of_name(c, 'price_levels', level))
    return level_ids