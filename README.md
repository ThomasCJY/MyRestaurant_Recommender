# CSE6242 project
## Data:
* https://www.census.gov/acs/www/data/data-tables-and-tools/data-profiles/
* http://www.restaurantowner.com/public/How-to-Create-a-Winning-Restaurant-Business-Plan-2.cfm
* http://www.city-data.com/city/Pittsburgh-Pennsylvania.html
* http://www.zillow.com/howto/api/APIOverview.htm
* www.mapbox.com

## Building the DB
1. Extract the yelp dataset somewhere
2. Create your dataset_dirs.py file (see dataset_dirs_example.py)
3. Run json_to_sqlite3.py

## REST API
### `/metro_areas`

Returns a list of all metro area names in database:

 `{'metro_areas': [metro area names]}`
  
### `/scores/<metro_area_name>`

Returns the top ten scores in the given metro area:

`{'scores': [{'category': ..., 'score': ..., 'zip_code': ...}]}`
