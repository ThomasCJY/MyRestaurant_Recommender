DB_FILENAME = "flask.db"

YELP_RESTAURANT_STARS_FILE = "yelp_restaurant_stars.txt"

RESTAURANTS_SCORES_FIELDS = ['restaurant_category_id', 'zip_code',
							 'metro_id', 'state_id', 'score']

# HACK: just one metro per state in this dataset, hard-coding
metro_areas_by_state = {
	'NV': 'Las Vegas', 'AZ': 'Phoenix', 'WI': 'Madison',
	'IL': 'Urbana-Champaign', 'NC': 'Charlotte', 'PA': 'Pittsburgh'
}
# metro_areas_by_state = {
# 	'NV': 'Las Vegas', 'AZ': 'Phoenix', 'WI': 'Madison',
# 	'IL': 'Urbana-Champaign', 'NC': 'Charlotte', 'PA': 'Pittsburgh',
# 	'QC': 'Montreal', 'ON': 'Waterloo', 'BW': 'Karlsruhe',
# 	'EDH': 'Edinburgh'
# }

RESTAURANTS_FIELDS = ['id', 'full_address', 'city', 'review_count', 'name',
					  'longitude', 'latitude', 'zip_code', 'stars']

RESTAURANT_CATEGORIES = [
	"Nightlife",
	"Bars",
	"Sandwiches",
	"Chinese",
	"Mexican",
	"American (New)",
	"Pizza",
	"Breakfast & Brunch",
	"Japanese",
	"Cafes",
	"Coffee & Tea",
	"American (Traditional)",
	"Fast Food",
	"Italian",
	"Burgers",
	"Seafood",
	"Sushi Bars",
	"Vietnamese",
	"Thai",
	"Asian Fusion",
	"Indian",
	"French",
	"Korean"
]

FEATURES = {'Ambience':['divey','classy','tourisity','hipster','trendy','intimate','casual','romantic','upscale'],
			'Good_for':['breakfast','lunch','dinner','latenight','brunch','dessert'],
			'Parking':['lot','street','garage','validated'],
			'Outdoor_Seating':[],
			'Price_Range':[],
			'Reservations':[],
			'Take_out':[],
			'Waiter_Service':[]}