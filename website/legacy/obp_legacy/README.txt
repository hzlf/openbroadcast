# mount (needs vpn connection)

sshfs root@172.20.10.84:/var/www/obp/data ~/sshfs/obp_legacy/


# on server (vz host)
cd ~/vpn/
openvpn --config config.conf
sshfs root@172.20.10.84:/var/www/obp/data ~/obp_legacy/ -o IdentityFile=/home/ohrstrom/.ssh/id_rsa -o allow_other
# 
mount -n -t simfs /root/pmount/ /vm/nodes/root/106/root/pmount/ -o /root/pmount/