# zabbix-curl-ping
Zabbix ping remote hosts via curl

# Installation
```bash
cd /opt/
rm -rf zabbix-curl-ping
apt-get install -y curl python
git clone https://github.com/Slach/zabbix-curl-ping.git
cp -fv /opt/zabbix-curl-ping/UserParams.conf /etc/zabbix/zabbix_agentd.conf.d/zabbix_curl_ping.conf
chmod +x /opt/zabbix-curl-ping/zabbix_curl.py
# check discovery working
sudo -H -u zabbix /opt/zabbix-curl-ping/zabbix_curl.py --discovery=True --curl-params="https://google.com"
sudo -H -u zabbix /opt/zabbix-curl-ping/zabbix_curl.py --curl-params="https://google.com" --verbose=True
```

# Tuning for /etc/zabbix/zabbix_agentd.conf
```
Timeout=30
ServerActive=<your_zabbix_server>
StartAgents=10
```
# Tuning for /etc/zabbix/zabbix_server.conf
```
Timeout=30
```

## Install Templates

Open Zabbix Menu:
Configuration -> Templates -> Import

Choose Template_Zabbix_MTR_Example.xml

## Modify Items, Triggers and Graphs for your latency and destination hosts requirements
