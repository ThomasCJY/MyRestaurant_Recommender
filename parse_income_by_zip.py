import csv     # imports the csv module
import dataset_dirs
import dao
import sqlite3
import constants

def import_income_by_zip():
    filename = dataset_dirs.ZIP_INCOME_DIR + "13zpallagi.csv"
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

    conn = sqlite3.connect(constants.DB_FILENAME)
    c = conn.cursor()

    if len_mismatches:
        print "There were %d cases where the #fields didn't match with the header!" % len_mismatches

    counts = {}
    level_mappings = get_level_mappings(c)
    for row in rows:
        state = row['STATE']
        state_id = dao.get_id_of_name(c, 'states', state)
        zip_code = row['zipcode']
        dao.check_add_zip_code(c, zip_code, state_id)
        key = (state_id, zip_code)
        if key not in counts:
            counts[key] = {}
        level_raw = int(row['agi_stub'])
        level = level_mappings[level_raw]
        count = int(float(row['N1']))
        if level in counts[key]:
            counts[key][level] += count
        else:
            counts[key][level] = count

    values = []
    for key in counts:
        total_count = sum([counts[key][level] for level in counts[key]])
        for level in counts[key]:
            percentage = 0.0 if total_count == 0 else (100*counts[key][level] / float(total_count))
            values.append([key[0], key[1], level, percentage])

    c.executemany(
        'INSERT INTO zip_codes_income_levels (state_id, zip_code, ' +
        'level, percentage) VALUES (?,?,?,?)', values
    )

    conn.commit()
    c.close()

def get_level_mappings(c):
    low, mid, high = dao.get_level_ids(c)
    return {1: low, 2: low, 3: mid, 4: mid, 5: high, 6: high}

if __name__ == "__main__":
    import_income_by_zip()
