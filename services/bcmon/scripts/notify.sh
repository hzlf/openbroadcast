#!/bin/sh
############################################
# just a wrapper to call the notifyer      #
# needed here to keep dirs/configs clean   #
# and maybe to set user-rights             #
############################################
cd ../
./bcmon_notify.py "$1" "$2" "$3" &
