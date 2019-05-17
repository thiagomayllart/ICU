#!/bin/bash
ports=$(cat $3/$1/$2/masscan-ports.txt | paste -sd "," -)
domain=$(dig +short $2 | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" | head -1)
nmap --proxies socks4://127.0.0.1:9050 -Pn -n -sT -p $ports $domain | tee $3/$1/$2/nmap-ports.txt
