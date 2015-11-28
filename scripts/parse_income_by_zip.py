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
    total_population_values = []
    for i, key in enumerate(counts):
        total_count = sum([counts[key][level] for level in counts[key]])
        total_population_values.append([key[0], key[1], total_count])
        for level in counts[key]:
            percentage = 0.0 if total_count == 0 else (100*counts[key][level] / float(total_count))
            values.append([key[0], key[1], level, percentage])

    c.executemany(
        'INSERT INTO zip_codes_income_levels (state_id, zip_code, ' +
        'level, percentage) VALUES (?,?,?,?)', values
    )

    c.executemany(
        'INSERT INTO zip_codes_population (state_id, zip_code, ' +
        'population) VALUES (?,?,?)', total_population_values
    )

    conn.commit()
    c.close()

if __name__ == "__main__":
    import_income_by_zip()
