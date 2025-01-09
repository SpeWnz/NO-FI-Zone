import argparse
import sqlite3
import pandas as pd
import sys
import ZHOR_Modules.nicePrints as np
import ZHOR_Modules.jsonUtils as jsu
import ZHOR_Modules.fileManager as fm
import ZHOR_Modules.timestampsUtils as tsu
import _common


# global variables 
DATABASE = None
CURSOR = None
_config = jsu.loadConfig()

TOC_LINES = ["<h1>Table of contents</h1><ol>"]
BODY_LINES = ["<hr>"]
QUERY_ID_INDEX = 0


# https://stackoverflow.com/questions/54289555/how-do-i-execute-an-sqlite-script-from-within-python
def query(queryTitle: str,scriptPath: str):
    global DATABASE
    global CURSOR
    global TOC_LINES
    global BODY_LINES
    global QUERY_ID_INDEX

    np.debugPrint(f"Reading query file {scriptPath}")
    with open(scriptPath, 'r') as sql_file:
        sql_script = sql_file.read()

    #print(sql_script)

    #db = sqlite3.connect(database)
    #cursor = DATABASE.cursor()
    np.debugPrint("Executing query")
    CURSOR.execute(sql_script)


    # Fetch the column names from the cursor description
    columns = [description[0] for description in CURSOR.description]
    #print(columns)
    
    # Fetch all rows of query result
    np.debugPrint("Fetching results")
    rows = CURSOR.fetchall()

    

    np.debugPrint("Composing html with results")
    href = f'<li><a href=#QUERY{QUERY_ID_INDEX}>{queryTitle}</a></li>'
    TOC_LINES.append(href)
    
    # Start the HTML table
    html = f'<h2 id="QUERY{QUERY_ID_INDEX}">Query #{QUERY_ID_INDEX+1} | {queryTitle}</h2>'
    html += f'<p><b>SQL Script:</b> {scriptPath}</p>'
    html += f'<p><b>Results:</b> {len(rows)}</p>'
   
   # are there actually results to display?
    if len(rows) > 0:
        html += '<table border="1" cellpadding="5" cellspacing="0">'    
        # Add the table header
        html += '<tr>'
        for column in columns:
            html += f'<th>{column}</th>'
        html += '</tr>'
        
        # Add the table rows
        for row in rows:
            html += '<tr>'
            for cell in row:
                html += f'<td>{cell}</td>'
            html += '</tr>'
        
        # Close the table 
        html += '</table>'
    
    html += "<hr>"

    BODY_LINES.append(html)
    QUERY_ID_INDEX += 1

def attachOUIdb(ouiDB: str):
    global CURSOR    
    np.debugPrint("Attaching database")

    q = f"ATTACH DATABASE '{ouiDB}' as oui;"
    CURSOR.execute(q)

def detatchOUIdb():
    global CURSOR    
    np.debugPrint("Detaching database")

    q = f"DETACH DATABASE oui;"
    CURSOR.execute(q)

def styleLines():
    lines = ["<style>"]
    lines += fm.fileToSimpleList(_config['report-style-file'])
    lines += ["</style>"]
    return lines

def titleLines(title: str):
    lines = ["<title>"]
    lines += [title]
    lines += ["</title>"]
    return lines


def writeReport(reportPath: str,db: str):
    global DATABASE
    global CURSOR
    global TOC_LINES
    global BODY_LINES
    global QUERY_ID_INDEX

    # terminate the ordered list
    TOC_LINES.append("</ol>")

    # compose the html and write it
    np.debugPrint("Writing lines to html file")

    reportLines = []
    reportLines.append("<!DOCTYPE html><html><head>")
    reportLines += titleLines(db)
    reportLines += styleLines()
    reportLines.append("</head><body>")
    reportLines += TOC_LINES
    reportLines += BODY_LINES
    reportLines.append("</body></html>")


    fm.listToFile(reportLines,reportPath)

# =========================================================================================================================================================

parser = argparse.ArgumentParser(description='Airodump-n-see | report generator ' + _common.VERSION)
REQUIRED_ARGUMENTS = parser.add_argument_group("Required arguments")
OPTIONAL_ARGUMENTS = parser.add_argument_group("Optional arguments")


# === Argomenti necessari ===
REQUIRED_ARGUMENTS.add_argument('-d', metavar='\"INPUT DB\"',type=str, required=True, help='Input database (already populated db)')
REQUIRED_ARGUMENTS.add_argument('-o', metavar='\"OUTPUT\"',type=str, required=True, help='Output html report path')

# === Argomenti opzionali ===
OPTIONAL_ARGUMENTS.add_argument('--debug', action='store_true', help='Debug mode')

args = parser.parse_args()

# =========================================================================================================================================================

np.DEBUG = ('--debug' in sys.argv)


if __name__ == '__main__':

    timestamp = tsu.getTimeStamp_iso8601()
    
    queries_jsonObj = jsu.jsonFile2dict(_config['queries-json-path'])

    DATABASE = sqlite3.connect(args.d)
    CURSOR = DATABASE.cursor()    

    attachOUIdb(_config['oui-db-abs-path'])

    index = 1
    for item in queries_jsonObj:
        title = item['title']
        queryScript = item['query']
        np.infoPrint(f"Executing query #{index} - {title}")
        query(title,queryScript)
        index += 1

    detatchOUIdb()
    DATABASE.commit()
    DATABASE.close()

    
    reportName = args.o.replace(".html","") + ".html"
    writeReport(reportName,args.d)