domain=$(dig +short $2 | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" | head -1)
proxychains nmap -Pn -PS -n -sT -p80,443,8080,8443 $ports $domain | tee $3/$1/$2/nmap-ports.txt
