import sqlite3
import scripts.parse_yelp_business_data as yelp_business
import scripts.parse_income_by_zip as income
import lib.dao as dao
import lib.constants as const

def parse_datasets():
    # Create tables
    conn = sqlite3.connect(const.DB_FILENAME)
    c = conn.cursor()
    create_tables_script = open('scripts/create_tables.sql')
    c.executescript(create_tables_script.read())
    create_tables_script.close()
    conn.commit()
    c.close()

    # Parse Yelp business dataset
    yelp_business.import_yelp_data()

    # Parse income data by zip, synthesize population data
    income.import_income_by_zip()

if __name__ == "__main__":
    parse_datasets()