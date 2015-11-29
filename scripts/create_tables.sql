CREATE TABLE states(
	id INTEGER PRIMARY KEY AUTOINCREMENT, 
	name TEXT NOT NULL UNIQUE
);

CREATE TABLE metro_areas (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL UNIQUE,
	state_id INTEGER NOT NULL REFERENCES states(id)
);

-- Composite key since same zip-code could exist in different countries
CREATE TABLE zip_codes (
		zip_code INTEGER NOT NULL PRIMARY KEY,
		state_id INTEGER NOT NULL REFERENCES states(id),
		metro_id INTEGER NOT NULL REFERENCES metro_areas(id)
);

CREATE TABLE restaurants (
	id TEXT PRIMARY KEY,
	full_address TEXT,
	city TEXT NOT NULL,
	review_count INTEGER NOT NULL,
	name TEXT NOT NULL,
	longitude REAL,
	latitude REAL,
	zip_code INTEGER NOT NULL REFERENCES zip_codes(zip_code),
	stars REAL
);

CREATE TABLE weekdays(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL
);

CREATE TABLE restaurants_hours(
	restaurant_id NOT NULL REFERENCES restaurants(id),
	day INTEGER NOT NULL REFERENCES weekdays(id),
	open TEXT,
	close TEXT
);

CREATE TABLE restaurant_categories(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL
);

CREATE TABLE restaurants_categories(
	restaurant_id NOT NULL REFERENCES restaurants(id),
	category_id INTEGER NOT NULL REFERENCES restaurant_categories
);

CREATE TABLE restaurant_neighborhoods(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL UNIQUE
);

CREATE TABLE restaurants_neighborhoods(
	restaurant_id TEXT NOT NULL REFERENCES restaurants(id),
	neighborhood_id INTEGER NOT NULL REFERENCES restaurant_neighborhoods(id)
);

CREATE TABLE restaurant_attributes(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL
);

CREATE TABLE restaurants_attributes(
	restaurant_id TEXT NOT NULL REFERENCES restaurants(id),
	attribute_id INTEGER NOT NULL REFERENCES restaurant_attributes(id),
	has INTEGER NOT NULL
);

CREATE TABLE restaurants_scores(
	restaurant_category_id INTEGER NOT NULL REFERENCES restaurant_categories(id),
	zip_code INTEGER NOT NULL REFERENCES zip_codes(zip_code),
	metro_id INTEGER NOT NULL REFERENCES zip_codes(metro_id),
	state_id INTEGER NOT NULL REFERENCES states(id),
	score INTEGER NOT NULL,
	PRIMARY KEY(restaurant_category_id, zip_code, metro_id)
);

CREATE TABLE price_levels(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL
);

CREATE TABLE zip_codes_income_levels(
	zip_code INTEGER NOT NULL REFERENCES zip_codes(zip_code),
	level INTEGER NOT NULL REFERENCES price_levels(id),
	percentage REAL NOT NULL,
	PRIMARY KEY(zip_code, level)
);

CREATE TABLE zip_codes_population(
	zip_code INTEGER NOT NULL PRIMARY KEY REFERENCES zip_codes(zip_code),
	population INTEGER NOT NULL
);

CREATE TABLE zip_codes_rent(
	zip_code INTEGER NOT NULL PRIMARY KEY REFERENCES zip_codes(zip_code),
	state_id INTEGER NOT NULL REFERENCES states(id),
	metro_id INTEGER NOT NULL REFERENCES zip_codes(metro_id),
	rent REAL NOT NULL
);
