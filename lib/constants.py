DB_FILENAME = "flask.db"

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