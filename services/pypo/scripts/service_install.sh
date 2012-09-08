#!/bin/sh
echo "--------------------------------"
echo "installing pypo for daemon-tools"
echo "--------------------------------"

svc -d /etc/service/pypo*
rm /etc/service/pypo*
ln -s /var/svc.d/pypo* /etc/service/
svc -u /etc/service/pypo*
svstat /etc/service/pypo*