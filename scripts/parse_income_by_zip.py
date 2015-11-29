import csv     # imports the csv module
import os
import dataset_dirs
import lib.dao as dao
import lib.util as util
import sqlite3
import lib.constants as const

def import_income_by_zip():
    filename = dataset_dirs.ZIP_INCOME_DIR + "13zpallagi.csv"
    rows = util.csv_to_dict_list(filename)
    if rows is None:
        # Something went wrong
        return

    conn = sqlite3.connect(const.DB_FILENAME)
    c = conn.cursor()

    counts = {}
    level_mappings = util.get_level_mappings(c)
    for row in rows:
        state = row['STATE']
        if state not in const.metro_areas_by_state:
            # Ignore states we don't have Yelp data for
            continue
        state_id = dao.get_id_of_name(c, 'states', state)
        zip_code = int(row['zipcode'])
        metro_id = dao.get_id_of_name(c, 'metro_areas',
                                      const.metro_areas_by_state[state],
                                      state_id=state_id)
        
        if not dao.get_matching(c, 'zip_codes', ['zip_code'],
                                {'zip_code': zip_code,
                                 'state_id': state_id,
                                 'metro_id': metro_id}):
            # Zip code we don't have Yelp data for, so we don't care. This dataset
            # contains zip codes that don't exist, too, for some reason...
            continue
        
        if zip_code not in counts:
            counts[zip_code] = {}
        level_raw = int(row['agi_stub'])
        level = level_mappings[level_raw]
        count = int(float(row['N1']))
        if level in counts[zip_code]:
            counts[zip_code][level] += count
        else:
            counts[zip_code][level] = count

    values = []
    total_population_values = []
    for i, zip_code in enumerate(counts):
        total_count = sum([counts[zip_code][level] for level in counts[zip_code]])
        total_population_values.append([zip_code, total_count])
        for level in counts[zip_code]:
            percentage = (0.0 if total_count == 0 else
                          (100*counts[zip_code][level] / float(total_count)))
            values.append([zip_code, level, percentage])

    c.executemany(
        'INSERT INTO zip_codes_income_levels (zip_code, level, percentage) VALUES ' +
        '(?,?,?)', values
    )

    c.executemany(
        'INSERT INTO zip_codes_population (zip_code, population) VALUES ' +
        '(?,?)', total_population_values
    )

    conn.commit()
    c.close()

if __name__ == "__main__":
    import_income_by_zip()
