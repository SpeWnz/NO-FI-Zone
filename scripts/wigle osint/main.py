import ZHOR_Modules.fileManager as fm
import ZHOR_Modules.requestUtils as requ
import ZHOR_Modules.nicePrints as np
import ZHOR_Modules.fileManager as fm
import ZHOR_Modules.csvUtils as csvUtils
import sys
import requests
import argparse
import urllib
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

parser = argparse.ArgumentParser(description="Wigle Osint")
REQUIRED_ARGUMENTS = parser.add_argument_group("Necessary arguments")
OPTIONAL_ARGUMENTS = parser.add_argument_group("Optional arguments")

# Argomenti necessari
REQUIRED_ARGUMENTS.add_argument('--latFrom',metavar='"Latitude From"',type=str,required=True,help='Starting latitude coordinate')
REQUIRED_ARGUMENTS.add_argument('--latTo',metavar='"Latitude To"',type=str,required=True,help='Ending latitude coordinate')
REQUIRED_ARGUMENTS.add_argument('--lonFrom',metavar='"Longitude From"',type=str,required=True,help='Starting longitude coordinate')
REQUIRED_ARGUMENTS.add_argument('--lonTo',metavar='"Longitude To"',type=str,required=True,help='Ending longitude coordinate')
REQUIRED_ARGUMENTS.add_argument('-q',metavar='"SSID Query"',type=str,required=True,help='SSID to look for in the Wigle Database. Examples of queries are: something, something%%, %%something, %%something%%')


# Argomenti opzionali
OPTIONAL_ARGUMENTS.add_argument('--debug',action="store_true",help="Debug mode")

args = parser.parse_args()

np.DEBUG = ("--debug" in sys.argv)

API_TOKENS = fm.fileToSimpleList('api-tokens.txt')

outputFileName = args.q.replace("%%","_") + ".csv"

searchAfter = None
firstRequest = True

for token in API_TOKENS:
    np.infoPrint("An api token was selected from the list.")
    np.debugPrint("Token: " + token)
    tokenExausted = False

    HEADERS = {'Authorization':'Basic ' + token}

    while not tokenExausted:
        URL =  "https://api.wigle.net/api/v2/network/search?"
        URL += "latrange1={}".format(args.latFrom)
        URL += "&latrange2={}".format(args.latTo)
        URL += "&longrange1={}".format(args.lonFrom)
        URL += "&longrange2={}".format(args.lonTo)
        URL += "&resultsPerPage=1000"
        URL += "&variance=0.200&minQoS=0&encryption=&netid=&ssid="
        URL += "&ssidlike={}".format(urllib.parse.quote(args.q))
        URL += "&Query=Query"

        if (searchAfter != None):
            URL += "&searchAfter={}".format(searchAfter)
        
        np.debugPrint(URL)
        r = requests.get(url=URL,headers=HEADERS,verify=False)

        if(r.status_code == 429):
            np.infoPrint("Queries exausted for the current token. Selecting new one...")
            tokenExausted = True
        else:

            jsonObj = json.loads(r.text)
            if ('searchAfter' in jsonObj):
                searchAfter = jsonObj['searchAfter']
            else:
                np.debugPrint("no searchAfter parameter")

            if(np.DEBUG):
                print(r.status_code)
                if(r.status_code != 200):
                    print(r.content)

            np.debugPrint("writing to csv...")
            csvUtils.lod2CSV_v2(lod=jsonObj['results'],csvPath=outputFileName,mode='a',insertHeader=firstRequest)

            firstRequest = False