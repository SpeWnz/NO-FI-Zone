import ZHOR_Modules.nicePrints as np
import sqlite3
import pandas as pd
import sys
import argparse

parser = argparse.ArgumentParser(description='CSV to sqlite DB - Generic implementation')
REQUIRED_ARGUMENTS = parser.add_argument_group("Required arguments")
OPTIONAL_ARGUMENTS = parser.add_argument_group("Optional arguments")


# === Argomenti necessari ===
REQUIRED_ARGUMENTS.add_argument('-i', metavar='\"INPUT CSV\"',type=str, required=True, help='Input csv file to feed into the database (or txt list ontaining csv files)')
REQUIRED_ARGUMENTS.add_argument('-t', metavar='\"TABLE\"',type=str, required=True, help='Table to feed the data into.')
REQUIRED_ARGUMENTS.add_argument('-d', metavar='\"DATABASE\"',type=str, required=True, help='Database to feed the data into.')
REQUIRED_ARGUMENTS.add_argument('-s', metavar='\"SEP\"',type=str, required=True, help='Separator character (for example , or ;)')

# === Argomenti opzionali ===
#OPTIONAL_ARGUMENTS.add_argument('--ow', action='store_true', help='Overwrite the specified db. WARNING! This will delete the db and create a new one.')
OPTIONAL_ARGUMENTS.add_argument('--debug', action='store_true', help='Debug mode')

args = parser.parse_args()

# =========================================================================================================================================================

np.DEBUG = ('--debug' in sys.argv)


# Load the CSV into a pandas DataFrame
csv_file_path = args.i
TABLE = args.t
df = pd.read_csv(csv_file_path,sep=args.s)

# strip
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Create SQLite database and connect to it
db_file_path = args.d  # SQLite database file
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Create the table based on CSV columns and types
columns = df.columns.tolist()
column_defs = []

def get_sqlite_type(series):
    if pd.api.types.is_integer_dtype(series):
        return 'INTEGER'
    elif pd.api.types.is_float_dtype(series):
        return 'REAL'
    else:
        return 'TEXT'

# insert access points information
for col in columns:
    column_type = get_sqlite_type(df[col])
    column_defs.append(f"{col} {column_type}")

create_table_query = "CREATE TABLE IF NOT EXISTS {} ({});".format(TABLE,', '.join(column_defs))
cursor.execute(create_table_query)

# Insert data into the table
for row in df.itertuples(index=False, name=None):
    com = "INSERT INTO {} ({}) VALUES ({})".format(
        TABLE,
        ', '.join(columns),
        ', '.join(['?'] * len(row))
    )
    cursor.execute(com, row)





# Commit and close
conn.commit()
conn.close()

print(f"CSV data has been successfully imported into {db_file_path}")
