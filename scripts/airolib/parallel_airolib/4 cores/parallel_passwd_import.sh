#!/bin/sh

# path dei file 
WORDLIST_PATH=$1
TEMP_WORDLIST="__temp_wordlist.txt"
TEMP_DB="__temp_db.db"


# filtro con grep
printf "Filtering out passwords with grep ... \n"
cat $WORDLIST_PATH | grep -x '.\{8,63\}' > $TEMP_WORDLIST

# temp db per filtrare le password non valide
printf "Filtering out more passwords with a temp db ... \n"
airolib-ng $PWD/$TEMP_DB --import passwd $TEMP_WORDLIST
sqlite3 -batch -csv $PWD/$TEMP_DB "select passwd from passwd;" > $TEMP_WORDLIST


#split della wordlist (in 4 parti)
split $TEMP_WORDLIST -n 4

# import degli ssid sequenziale
printf "Importing passwords: \n"
printf "Importing on DB1 ...\n"
airolib-ng $PWD/DB1.db --import passwd xaa

printf "Importing on DB2 ...\n"
airolib-ng $PWD/DB2.db --import passwd xab

printf "Importing on DB3 ...\n"
airolib-ng $PWD/DB3.db --import passwd xac

printf "Importing on DB4 ...\n"
airolib-ng $PWD/DB4.db --import passwd xad

# rimuovo file temporanei
rm xaa
rm xab
rm xac
rm xad
rm $TEMP_DB
rm $TEMP_WORDLIST