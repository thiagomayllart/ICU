#!/bin/bash
echo $3
echo $2
echo $1
domain=$(dig +noedns +short $2 | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" | head -1)
sudo masscan $domain | head -1) -p1-65535 --rate 300 --wait 3 2> /dev/null | grep -o -P '(?<=port ).*(?=/)' | tee $3/$1/$2/nmap-ports.txt
