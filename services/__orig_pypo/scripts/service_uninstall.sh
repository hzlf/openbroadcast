#!/bin/sh
echo "----------------------------------"
echo "uninstalling pypo for daemon-tools"
echo "----------------------------------"

svc -d /etc/service/pypo*
rm /etc/service/pypo*
echo "ls -l /etc/service/"
ls -l /etc/service/