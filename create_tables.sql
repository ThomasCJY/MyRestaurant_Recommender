CREATE TABLE states(
	id INTEGER PRIMARY KEY AUTOINCREMENT, 
	name TEXT NOT NULL UNIQUE
);

CREATE TABLE metro_areas (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	state_id INTEGER NOT NULL REFERENCES states(id)
);

-- Composite key since same zip-code could exist in different countries
CREATE TABLE zip_codes (
		zip_code TEXT NOT NULL,
		state_id INTEGER NOT NULL REFERENCES states(id),
		PRIMARY KEY(zip_code, state_id)
);

CREATE TABLE metro_areas_zip_codes(
	metro_id INTEGER REFERENCES metro_areas(id),
	zip_code TEXT NOT NULL,
	state_id INTEGER NOT NULL,
	PRIMARY KEY(metro_id, zip_code),
	FOREIGN KEY(zip_code, state_id) REFERENCES zip_codes(zip_code, state_id)
);

CREATE TABLE restaurants (
	id TEXT PRIMARY KEY,
	full_address TEXT,
	city TEXT NOT NULL,
	review_count INTEGER NOT NULL,
	name TEXT NOT NULL,
	longitude REAL,
	latitude REAL,
	state_id TEXT NOT NULL REFERENCES states(id),
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
	name TEXT UNIQUE NOT NULL
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
	zip_code TEXT NOT NULL,
	state_id INTEGER NOT NULL,
	metro_id INTEGER NOT NULL,
	score INTEGER NOT NULL,
	PRIMARY KEY(restaurant_category_id, zip_code, metro_id),
	FOREIGN KEY(zip_code, state_id, metro_id) REFERENCES
	zip_codes(zip_code, state_id, metro_id)
);

CREATE TABLE price_levels(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL
);

CREATE TABLE zip_codes_income_levels(
	state_id INTEGER NOT NULL,
	zip_code TEXT NOT NULL,
	level INTEGER NOT NULL REFERENCES price_levels(id),
	percentage REAL NOT NULL,
	PRIMARY KEY(state_id, zip_code, level),
	FOREIGN KEY(zip_code, state_id) REFERENCES zip_codes(zip_code, state_id)
);
