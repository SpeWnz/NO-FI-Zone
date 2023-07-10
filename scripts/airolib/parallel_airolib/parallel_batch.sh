#!/bin/sh

# path dei file 
SSIDs_PATH=$1



# import degli ssid sequenziale
printf "Importing SSIDs: \n"
printf "Importing on DB1 ...\n"
airolib-ng $PWD/DB1.db --import essid $SSIDs_PATH

printf "Importing on DB2 ...\n"
airolib-ng $PWD/DB2.db --import essid $SSIDs_PATH

printf "Importing on DB3 ...\n"
airolib-ng $PWD/DB3.db --import essid $SSIDs_PATH

printf "Importing on DB4 ...\n"
airolib-ng $PWD/DB4.db --import essid $SSIDs_PATH

# batch parallelo
printf "Batching parallely. Launching airolib instances...\n"

xterm -T "Airolib Istance #1" -e "airolib-ng \"$PWD/DB1.db\" --batch; read" &
xterm -T "Airolib Istance #2" -e "airolib-ng \"$PWD/DB2.db\" --batch; read" &
xterm -T "Airolib Istance #3" -e "airolib-ng \"$PWD/DB3.db\" --batch; read" &
xterm -T "Airolib Istance #4" -e "airolib-ng \"$PWD/DB4.db\" --batch; read" &