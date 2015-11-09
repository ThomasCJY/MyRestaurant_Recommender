from flask import Flask
from flask import jsonify
from flask import render_template
import sqlite3
import dao
import constants
from flask import g

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
    	db = g._database = sqlite3.connect(constants.DB_FILENAME)
    return db

app = Flask(__name__)

@app.route('/')
def start_page():
    return render_template('index.html')

@app.route('/metro_areas')
def metro_areas():
	c = get_db().cursor()
	unique_values = dao.get_unique_values(c, 'metro_areas', 'name')
	result = {'metro_areas': unique_values}
	response = jsonify(result)
	response.status_code = 200
	return response

@app.route('/scores/<metro_name>')
def score_by_zip_code(metro_name):
	# return 'Request for scores in metro %s' % metro_name
	try:
		c = get_db().cursor()
		result = {'scores': dao.get_n_top_scores(c, metro_name)}
		response = jsonify(result)
		response.status_code = 200
	except Exception as e:
		print e
	return response

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
	app.debug = True
	app.run()