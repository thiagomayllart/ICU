domain=$(dig +short $2 | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" | head -1)
proxychains nmap -Pn --open -PS -n -sT -p80,443,8080,8443 $domain | awk '!/Starting/' | awk '!/Nmap scan/' | awk '!/Host is up/' | awk '!/Proxychains/' | tee $3/$1/$2/nmap-ports.txt
