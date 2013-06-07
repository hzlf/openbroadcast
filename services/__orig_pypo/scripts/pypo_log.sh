#!/bin/sh

clear
echo
echo "##############################"
echo "# STARTING PYPO MULTI-LOG    #"
echo "##############################"
sleep 1
clear

# split
multitail -M 10000 -s 2 \
        -t "scheduler push log" -mb 999990 \
        -l "tail -n 100 -F /var/svc.d/scheduler_push/log/main/current | tai64nlocal" \
\
        -t "scheduler fetch log" -mb 99999 \
        -l "tail -n 100 -F /var/svc.d/scheduler_fetch/log/main/current | tai64nlocal" \
\
        -t "pypo debug log" -mb 999990 \
        -l "tail -n 100 -F /var/log/obp/pypo/debug.log | grep -v DEBUG" \
\
        -t "daypart push log" -mb 999990 \
        -l "tail -n 100 -F /var/svc.d/daypart_push/log/main/current | tai64nlocal" \
\
        -t "daypart fetch log" -mb 99999 \
        -l "tail -n 100 -F /var/svc.d/daypart_fetch/log/main/current | tai64nlocal" \
\
        -t "pypo liquidsoap log" -mb 99999 \
        -l "tail -n 100 -F /var/svc.d/liquidsoap/log/main/current | tai64nlocal"
echo
