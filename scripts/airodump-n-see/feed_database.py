import ZHOR_Modules.listUtils as lu
import ZHOR_Modules.nicePrints as np
import ZHOR_Modules.osUtils as osu
import ZHOR_Modules.fileManager as fm
import argparse
import os
import sqlite3
import pandas as pd
import sys

import _common

AP_CSV_HEADER = 'BSSID, First time seen, Last time seen, channel, Speed, Privacy, Cipher, Authentication, Power, # beacons, # IV, LAN IP, ID-length, ESSID, Key'
STA_CSV_HEADER = 'Station MAC, First time seen, Last time seen, Power, # packets, BSSID, Probed ESSIDs'

DATABASE        = None
TEMP_AP_CSV     = '__temp-ap.csv'
TEMP_STA_CSV    = '__temp-sta.csv'


def get_sqlite_type(series):
    if pd.api.types.is_integer_dtype(series):
        return 'INTEGER'
    elif pd.api.types.is_float_dtype(series):
        return 'REAL'
    else:
        return 'TEXT'

def mac2OUI(mac: str):
    return mac.strip()[0:8].replace(':','')

# make the normalized and fixed stations csv file to feed into the db
def makeSTAsCSV(csvLines: list):
    np.debugPrint("Extracting and normalizing STAs data ...")
    fixedLines = ["Station_MAC, First_time_seen, Last_time_seen, Power, num_of_packets, BSSID, Probed_ESSIDs, ap_OUI, sta_OUI"]
    
    # gli ap stanno tra l'index <dove sta la scritta degli STA -1> e la "fine -1 ""
    STA_linesIndex = 0
    for line in csvLines:
        if STA_CSV_HEADER in line:
            break # trovato
        else:
            STA_linesIndex += 1

    # qui è gia senza csv header
    STA_lines = csvLines[STA_linesIndex + 1:-1]

    for l in STA_lines:
        
        # probe requests are from index 6 on
        values = l.split(',')
        probes = values[6:]

        staMac = values[0]
        apMac = values[5]

        staOUI = mac2OUI(staMac)

        # is it a case where we have a "not associated" client?
        if ':' in apMac:
            apOUI = mac2OUI(apMac)
        else:
            apOUI = ""

        #print(probes)

        for p in probes:
            fixedLine = lu.concatenate_elements(values[0:6],',') + f',"{p}",{apOUI},{staOUI}'
            #print(fixedLine)
            fixedLines.append(fixedLine)

    fm.listToFile(fixedLines,TEMP_STA_CSV)

# make the fixed csv file to feed into the db  
def makeAPsCSV(csvLines: list):
    np.debugPrint("Extracting APs data ...")

    # gli ap stanno tra l'index 2 e <dove sta la scritta degli STA -2>
    AP_linesIndex = 0
    for line in csvLines:
        if STA_CSV_HEADER in line:
            break
        else:
            AP_linesIndex += 1

    AP_lines = csvLines[2:AP_linesIndex - 1]

    fixedLines = ["BSSID, First_time_seen, Last_time_seen, channel, Speed, Privacy, Cipher, Authentication, Power, num_beacons, num_IV, LAN_IP, ID_length, ESSID, Key, ap_OUI"]
    for l in AP_lines:
        
        values = l.split(',')
        staMac = values[0]
        staOUI = mac2OUI(staMac)

        fixedLine = f'{l},{staOUI}'
        fixedLines.append(fixedLine)

    fm.listToFile(fixedLines,TEMP_AP_CSV) 


# creates the database to store airodump information
def createDatabase(database: str):
    np.debugPrint(f"Database {database} does not exist. Creating it.")
    db = sqlite3.connect(database)
    cursor = db.cursor() 

    # create ap table
    np.debugPrint("Creating ap table ...")
    with open('sql-scripts/create_ap.sql', 'r') as sql_file:
        sql_script = sql_file.read()
    cursor.execute(sql_script)

    # create sta table
    np.debugPrint("Creating sta table ...")
    with open('sql-scripts/create_sta.sql', 'r') as sql_file:
        sql_script = sql_file.read()
    cursor.execute(sql_script)

    # create scope table
    np.debugPrint("Creating scope table ...")
    with open('sql-scripts/create_scope.sql', 'r') as sql_file:
        sql_script = sql_file.read()
    cursor.execute(sql_script)

    db.commit()
    db.close()

# used to feed either the APs or the STAs table
def feedData(inputCsv: str, dbTable: str):
    global DATABASE
    
    np.debugPrint(f"Feeding {inputCsv} into table {dbTable} ...")
    df = pd.read_csv(inputCsv)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Create SQLite database and connect to it
    db_file_path = DATABASE  # SQLite database file
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Create the table based on CSV columns and types
    columns = df.columns.tolist()
    column_defs = []

    # insert access points information
    for col in columns:
        column_type = get_sqlite_type(df[col])
        column_defs.append(f"{col} {column_type}")


    # Insert data into the table
    for row in df.itertuples(index=False, name=None):
        com = "INSERT INTO {} ({}) VALUES ({})".format(
            dbTable,
            ', '.join(columns),
            ', '.join(['?'] * len(row))
        )
        cursor.execute(com, row)

    # Commit and close
    conn.commit()
    conn.close()

# remove temporary files
def cleanup():
    np.debugPrint("Cleaning up temporary files...")
    os.remove(TEMP_AP_CSV)
    os.remove(TEMP_STA_CSV)

# =========================================================================================================================================================

parser = argparse.ArgumentParser(description='Airodump-n-see | database feeder ' + _common.VERSION)
REQUIRED_ARGUMENTS = parser.add_argument_group("Required arguments")
OPTIONAL_ARGUMENTS = parser.add_argument_group("Optional arguments")


# === Argomenti necessari ===
REQUIRED_ARGUMENTS.add_argument('-i', metavar='\"INPUT CSV(s)\"',type=str, required=True, help='Input csv file to feed into the database (or txt list ontaining csv files)')
REQUIRED_ARGUMENTS.add_argument('-o', metavar='\"DATABASE\"',type=str, required=True, help='Database to feed the data into.')

# === Argomenti opzionali ===
OPTIONAL_ARGUMENTS.add_argument('--ow', action='store_true', help='Overwrite the specified db. WARNING! This will delete the db and create a new one.')
OPTIONAL_ARGUMENTS.add_argument('--debug', action='store_true', help='Debug mode')

args = parser.parse_args()

# =========================================================================================================================================================

np.DEBUG = ('--debug' in sys.argv)

if __name__ == '__main__':
    
    DATABASE = args.o

    if('--ow' in sys.argv):
        os.remove(args.o)

    # create the database if it doesn't exist
    if not os.path.isfile(DATABASE):
        createDatabase(DATABASE)

    inputFiles = []
    inputFile = args.i

    if '.txt' in inputFile[-4:]:
        inputFiles = fm.fileToSimpleList(inputFile)
    elif '.csv' in inputFile[-4:]:
        inputFiles = [inputFile]
    else:
        np.errorPrint("The provided input file is not valid. It's neither a csv or a txt.")
        exit()


    for item in inputFiles:
        np.infoPrint(f"Feeding {item} data into {DATABASE}")
        csvLines = fm.fileToSimpleList(item)
        
        makeAPsCSV(csvLines)
        makeSTAsCSV(csvLines)

        feedData(TEMP_AP_CSV,'access_points')
        feedData(TEMP_STA_CSV,'stations')

    cleanup()