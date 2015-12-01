import sqlite3
import constants as const
from sklearn.ensemble import RandomForestClassifier


def get_matching_top3(c, constraints, count=3):
	data = c.execute( "SELECT id,attribute_id,has,zip FROM restaurants_attributes join (SELECT * FROM (SELECT id,zip_codes.zip_code as zip,metro_id FROM restaurants join zip_codes where restaurants.zip_code=zip_codes.zip_code) where metro_id = %d) where restaurant_id = id" % constraints['metro_id']).fetchall();  
	rid = [];
	Y = [];
	X= [];
	x = [0]*37;
	rid.append(data[0][0]);
	print rid
	for every in data:
		if every[0] in rid:
			x[every[1]] = every[2];
		else:
			x = x[1:27];
			rid.append(every[0]);
			X.append(x);
			Y.append(every[3]);
			x = [0]*37;
	x = x[1:27];
	X.append(x);
	Y.append(every[3]);
	# X = [[0, 0], [1, 1]]
	# Y = [0, 1]
	clf = RandomForestClassifier(n_estimators = 100);
	clf = clf.fit(X, Y)
	a = clf.predict(constraints['feature']).tolist();
	print a;
	print Y[1]
	print Y[2]
	return [a, [Y[1]], [Y[2]]]
	#print clf.predict_proba(X)
	#r = clf.score(feature_test , target_test)
	# print clf