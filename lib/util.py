import lib.dao as dao
import os
import csv

def get_level_mappings(c):
    low, mid, high = dao.get_level_ids(c)
    return {1: low, 2: low, 3: mid, 4: mid, 5: high, 6: high}

def csv_to_dict_list(filename):
	if not os.path.exists(filename):
		print "Parse income by zip: Couldn't find file \"%s\"" % filename
		return
	f = open(filename, 'rb') # opens the csv file
	header = None
	rows = []
	len_mismatches = 0
	try:
		reader = csv.reader(f)  # creates the reader object
		header = reader.next()
		for row_list in reader:   # iterates the rows of the file in orders
			row = {}
			if len(header) != len(row_list):
				len_mismatches += 1
			for i in xrange(len(header)):
				row[header[i]] = row_list[i]
			rows.append(row)
	finally:
		f.close()      # closing

	if len_mismatches:
		print ("There were %d cases where the #fields didn't match with the header!"
			   % len_mismatches)

	return rows