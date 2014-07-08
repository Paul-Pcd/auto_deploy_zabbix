#! /bin/bash

serverip=192.168.100.125
hostname=$(hostname)
 
resfile=/etc/resolv.conf
logfile=/var/log/auto_install_zabbix_agent.log
 
mod_config() {
    sed -i.bak 's/^Server=.*$/Server='"$serverip"'/;
                s/^ServerActive=.*$/ServerActive='"$serverip"'/;
                s/^Hostname=.*$/Hostname='"$hostname"'/ ' /etc/zabbix/zabbix_agentd.conf
    service zabbix-agent restart
}
 
log() {
    echo "[$(date +%H:%M:%S)] $1" >> $logfile
}
 
if dpkg -l | grep zabbix-agent > /dev/null ;then
    log "Zabbix-agent has installed, Just mod the config files"
    mod_config
else
    if ping -c 1 www.baidu.com 2>&1 | grep 'unknow' >/dev/null ;then
        log "Dns resolved failed, try to fix it"
 
        log "Backup $resfile to $resfile.bak"
        log "Use 8.8.8.8 as default dns server"
        cp /etc/resolv.conf $resfile.bak
        echo "nameserver 8.8.8.8" > $resfile
    fi
    # install zabbix-agent
    log "Begin install zabbix-agent"
    apt-get install zabbix-agent -y
 
    log "Mod zabbix-agent config"
    mod_config
fi
 
log  "Install & Config finished"
exit 0
