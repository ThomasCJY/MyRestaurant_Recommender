from flask import Flask
from flask import jsonify
from flask import render_template
from flask import g
from flask import request
from flask import abort

import json
import sqlite3

import lib.constants as const
import lib.dao as dao

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
    	db = g._database = sqlite3.connect(const.DB_FILENAME)
    return db

app = Flask(__name__)

# @app.route('/form_action', methods=['POST'])
# def form_action():
# 	name = request.form['name']
# 	email = request.form['email']
# 	msg = request.form['msg']
# 	team_members = {'members': ['Jiayu', 'Chiyao', 'Dong', 'Hao', 'Gustav']}
# 	json_response = json.dumps(team_members)
# 	return render_template('form_action.html', name=name, email=email,
# 						   json_response=json_response)

# @app.route('/wp-admin')
# def wpadmin():
# 	return render_template('no.html')

@app.route('/')
def start_page():
    return render_template('index.html')

@app.route('/metro_areas')
def metro_areas():
	try:
		c = get_db().cursor()
		try:
			unique_values = dao.get_unique_values(c, 'metro_areas', 'name')
			result = {'metro_areas': unique_values}
			response = jsonify(result)
			response.status_code = 200
			return response
		finally:
			c.close()
	except Exception as e:
		print e
		abort(500)

@app.route('/<metro_area>/<category>',methods=['GET', 'POST'])
def top_zip_codes(metro_area, category):
	# Get features from POST or URL
	# name = request.form['name']

	# Get into the Algorithm
	# Get top 3 zipcode from the algorithm return

	# According to the city, category, zipcode, get all the restaurant information we need

	# TEST
	try:
		c = get_db().cursor()
		try:
			category_id = dao.get_id_of_name(c, 'restaurant_categories', category,
											 add_nonexisting=False)
			metro_id = dao.get_id_of_name(c, 'metro_areas', metro_area,
										  add_nonexisting=False)
			if category_id is None:
				print "Category \"%s\" not found in DB!" % category
				abort(500)
			if metro_id is None:
				print "Metro area \"%s\" not found in DB!" % metro_area
				abort(500)

			fields = ['zip_code', 'score']
			constraints = {'metro_id': metro_id, 'restaurant_category_id': category_id}
			top3 = [{'zip_code': t[0], 'score': t[1]} for t in
					 dao.get_top_scoring(c, fields=fields, constraints=constraints,
					 			         count=3)]
			for t in top3:
				restaurants = [
					{field: r[i] for i, field in enumerate(const.RESTAURANTS_FIELDS)}
					for r in dao.list_restaurants_in_zip(c, t['zip_code'])
				]

				# Add other variables of interest
				# for r in restaurants:
					# TODO

				t['restaurants'] = restaurants

			result = {
				'metro_area': metro_area,
				'category': category,
				'top3': top3
			}
			information = json.dumps(result)

		finally:
			c.close()
	except Exception as e:
		print e
		abort(500)

	return render_template('mapview.html', information=information)


@app.route('/scores/<metro_name>',methods=['GET', 'POST'])
def top10(metro_name):
	# return 'Request for scores in metro %s' % metro_name
	try:
		c = get_db().cursor()
		try:
			result_list = dao.get_top_scores_in_metro(c, metro_name, count=10)
			if result_list is None:
				abort(404)
			result_dict = {'metro_area': metro_name, 'top_scores': result_list}
			response = jsonify(result_dict)
			response.status_code = 200
			return response
		finally:
			c.close()
	except Exception as e:
		print e
		abort(500)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
	app.debug = True
	app.run()
