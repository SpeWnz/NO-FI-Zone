#!/bin/sh

INTERFACE=$1

ifconfig $INTERFACE down

iwconfig $INTERFACE mode monitor
airmon-ng check kill

ifconfig $INTERFACE up