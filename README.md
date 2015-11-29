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
3. Run parse_yelp_business_data.py

## REST API
### `/metro_areas`

Returns a list of all metro area names in database:

 `{'metro_areas': [metro area names]}`
  
### `/scores/<metro_area_name>`

Returns the top ten scores in the given metro area:

`{'scores': [{'category': ..., 'score': ..., 'zip_code': ...}]}`

### `/scores/top_zip_codes/<metro_area>/<category>`

Returns the top 3 zip codes for the given category within the given metro area.
Format is subject to some degree of change but can be found in app.py.
However, it will be similar to the below format:
```
{
  "category": "Indian", 
  "metro_area": "Charlotte", 
  "top3": [
    {
      "restaurants": [
        {
          "city": "Charlotte", 
          "full_address": "8432 Old Statesville\nSte 300\nCharlotte, NC 28269", 
          "id": "XiUxS327vVkwWtR2TgpxLw", 
          "latitude": 35.33806, 
          "longitude": -80.8240579, 
          "name": "Rudino's Pizza & Grinders", 
          "review_count": 6, 
          "stars": 2.5, 
          "zip_code": 28269
        },
        ...
    },
    ...
}
```
