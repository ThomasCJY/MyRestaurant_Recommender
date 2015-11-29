import csv
import os
import dataset_dirs
import lib.dao as dao
import lib.util as util
import sqlite3
import lib.constants as const

def import_rent_per_sqft_by_zip():
    filename = dataset_dirs.ZIP_INCOME_DIR + "Zip_ZriPerSqft_AllHomes.csv"
    rows = util.csv_to_dict_list(filename)
    if rows is None:
        # Something went wrong
        return

    conn = sqlite3.connect(const.DB_FILENAME)
    c = conn.cursor()

    rents = []
    level_mappings = util.get_level_mappings(c)
    for row in rows:
        state = row['State']
        if state not in const.metro_areas_by_state:
            # Ignore states we don't have Yelp data for
            continue
        state_id = dao.get_id_of_name(c, 'states', state)
        zip_code = int(row['RegionName'])
        metro_id = dao.get_id_of_name(c, 'metro_areas',
                                      const.metro_areas_by_state[state],
                                      state_id=state_id)

        if not dao.get_matching(c, 'zip_codes', ['zip_code'],
                                {'zip_code': zip_code,
                                 'state_id': state_id,
                                 'metro_id': metro_id}):
            # Zip code we don't have Yelp data for, so we don't care.
            continue

        # ZRI - Zillow Rent Index
        # More info at http://www.zillow.com/research/data/#rental-data
        rent = row['2015-10']
        rents.append([zip_code, state_id, metro_id, rent])

    c.executemany(
        'INSERT INTO zip_codes_rent(zip_code, state_id, metro_id, rent) VALUES ' +
        '(?,?,?,?)', rents
    )

    conn.commit()
    c.close()

if __name__ == "__main__":
    import_rent_per_sqft_by_zip()
