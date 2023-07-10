import ZHOR_Modules.nicePrints as np
import ZHOR_Modules.fileManager as fm
import ZHOR_Modules.listUtils as lu
import sys
import os


if (len(sys.argv) != 2):
    np.errorPrint("Usage python3 main.py <hccapx file path>")
    exit()


filePath = str(sys.argv[1])

fileLines = fm.fileToSimpleList(filePath)




def getMac(rawMacAddr: str):
    rawMacAddr = rawMacAddr.upper()
    group = 2
    char = ":"
    rawMacAddr = str(rawMacAddr)
    return char.join(rawMacAddr[i:i+group] for i in range(0, len(rawMacAddr), group))

index = 1
for line in fileLines:
    values = line.split('*')

    np.infoPrint("Result #" + str(index))

    

    macAP = getMac(values[3])
    macSTA = getMac(values[4])
    ssid = bytes.fromhex(values[5]).decode('utf-8')

    print("SSID:\r\t\t",ssid)
    print("MAC AP:\r\t\t", macAP)
    print("MAC STA:\r\t\t",macSTA)
    
    #pmkid / mic (eapol)
    if values[1] == '01':
        print("PMKID:\r\t\t",values[2])
    
    if values[1] == '02':
        print("MIC:\r\t\t",values[2])
        print("ANONCE:\r\t\t",values[6])
        print("SNONCE:\r\t\t",values[7])
    
    

    print("\n")
    index += 1