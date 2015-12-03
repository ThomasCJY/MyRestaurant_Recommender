import sqlite3
import constants as const
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals.joblib import Parallel, delayed

def get_matching_top3(c, constraints, count=3):
	data = c.execute( "SELECT id,attribute_id,has,zip FROM restaurants_attributes join (\
		SELECT * FROM (\
			SELECT id,zip_codes.zip_code as zip,metro_id FROM restaurants join zip_codes where restaurants.zip_code=zip_codes.zip_code)\
	where metro_id = %d) where restaurant_id = id" % constraints['metro_id']).fetchall();

	rid = [];
	Y = [];
	X = [];
	x = [0]*26;
	rid.append(data[0][0]);
	for every in data:
		if every[0] in rid:
			x[every[1]-1] = every[2];
		else:
			cate = c.execute( "SELECT category_id from restaurants_categories WHERE restaurant_id = '%s'" %rid[-1]).fetchall();
			rid.append(every[0]);
			for cc in cate:
				import copy; xx = copy.deepcopy(x)
				xx.append(int(cc[0]));
				X.append(xx);
				Y.append(every[3]);
			x = [0]*26;
	cate = c.execute( "SELECT category_id from restaurants_categories WHERE restaurant_id = '%s'" %rid[-1]).fetchall();
	for cc in cate:
		import copy; xx = copy.deepcopy(x)
		xx.append(int(cc[0]));
		X.append(xx);
		Y.append(every[3]);
	# X = [[0, 0], [1, 1]]
	# Y = [0, 1]
	clf = RandomForestClassifier(n_estimators = 100);
	feature_train, feature_test, target_train, target_test = train_test_split(X, Y, test_size=0.1, random_state=42)
	clf = clf.fit(feature_train, target_train)
	r = clf.score(feature_test , target_test)
	print r
	y = constraints['feature']
	a = clf.predict(y).tolist();
	return [a, [Y[1]], [Y[2]]]
	#print clf.predict_proba(X)

