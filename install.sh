#!/usr/bin/env bash
sudo apt-get update && sudo apt-get -y upgrade
sudo apt install proxychains
sudo apt install snapd
sudo service snapd restart

echo "[+] Installing python-pip"
apt-get install python-pip

echo "[+] Installing sublist3r"
git clone https://github.com/aboul3la/Sublist3r.git tools/dependencies/sublister

echo "----------------------------------------------------------------"

echo "[?] Do you want to pip install the requirements.txt?"
echo "[Y/n]"

chmod 777 -R ../NightVision
echo "[+] Installing MySQL Server"
apt install mysql-server
mysql_secure_installation

echo "[+] Installing Nmap and Masscan"
apt-get install nmap
apt-get install masscan

echo "[+] Downloading wordlists"
wget https://gist.githubusercontent.com/jhaddix/86a06c5dc309d08580a018c66354a056/raw/96f4e51d96b2203f19f6381c8c545b278eaa0837/all.txt
wget https://raw.githubusercontent.com/janmasarik/resolvers/master/resolvers.txt
wget https://raw.githubusercontent.com/assetnote/commonspeak2-wordlists/master/subdomains/subdomains.txt
cat all.txt >> subdomains.txt
sort subdomains.txt | uniq > all2.txt

echo "[+] Installing GO"
wget -c https://storage.googleapis.com/golang/go1.7.3.linux-amd64.tar.gz
sudo tar -C /usr/local -xvzf go1.7.3.linux-amd64.tar.gz
mkdir -p ~/go_projects/{bin,src,pkg}
export PATH=$PATH:/usr/local/go/bin
export GOPATH="$HOME/go_projects"
export GOBIN="$GOPATH/bin"
export PATH=$PATH:$GOBIN

echo "[+] Installing Amass"
apt-get install snap
export PATH=$PATH:/snap/bin
snap install docker
docker pull caffix/amass

echo "[+] Installing subfinder"
wget https://github.com/projectdiscovery/subfinder/releases/download/v2.2.4/subfinder-linux-amd64.tar
tar -xzvf subfinder-linux-amd64.tar
mv subfinder-linux-amd64 /usr/bin/subfinder


pip install requests
pip install dnspython
pip install -v python-telegram-bot==10.0.1
pip install psutil
pip install delegator
pip install sshtunnel
pip install pycrypto
pip install logging

echo "[+] Installing Python3"
apt install python3
apt-get install python3-pip
pip3 install requests
pip3 install feedparser
pip3 install dnspython

echo "[+] Installing crt.sh"
wget https://raw.githubusercontent.com/Inf0Junki3/pentesty_goodness/master/ct_scan/ct_scan.py -o tools/dependencies/crt.py
chmod +x tools/dependencies/crt.py

echo "[+] Installing Sudomy"
apt install npm
apt-get install jq nmap phantomjs npm parallel
npm i -g wappalyzer wscat
git clone --recursive https://github.com/screetsec/Sudomy.git
cd Sudomy
pip install -r requirements.txt
apt-get install jq nmap phantomjs golang
go get -u github.com/tomnomnom/httprobe
go get -u github.com/OJ/gobuster
cd ..
export SUDOMY=$(pwd)/Sudomy

echo "[+] Installing Assetfinder"
go get -u github.com/tomnomnom/assetfinder

echo "[+] Installing Findomain"
wget https://github.com/Edu4rdSHL/findomain/releases/download/2.1.1/findomain-linux
chmod +x findomain-linux

echo "[+] Installing massdns"
git clone https://github.com/blechschmidt/massdns
apt-get install make
make --directory $(pwd)/massdns/
export MASSDNS=$(pwd)/massdns

go get -u github.com/subfinder/subfinder

echo "[+] Installing AltDns"
pip install py-altdns

echo "[+] Installing ShuffleDns"
GO111MODULE=on go get -u -v github.com/projectdiscovery/shuffledns/cmd/shuffledns

read choice_pip_requirements

if [ "$choice_pip_requirements" == "Y" ] || [ "$choice_pip_requirements" == "y" ] || [ -z "$choice_pip_requirements" ]; then
        pip install -r requirements.txt
	sudo apt-get install python-mysqldb
else
	echo "[!] Make sure you have the right modules installed. You can check which modules are used in requirements.txt"
fi

echo "----------------------------------------------------------------"

echo "[?] What is the database username?"
read database_username

echo "[?] What is the database password?"
read database_password

echo "[?] What is the database server? e.g. localhost (most common), if it runs on the same server."
read database_server

echo "
database_username = \"$database_username\"
database_password = \"$database_password\"
database_server = \"$database_server\"
database_name = \"recon\"

telegram_bot_token = \"\"
telegram_chat_id = \"\"
digital_ocean_token = \"\"
" > "credentials.py"

echo "[+] Creating database 'recon' with tables 'domains', scans and 'errors'"
python database/init_db.py

echo "[+] Checking if the database was created successfully"
python database/db_test.py

echo "----------------------------------------------------------------"

echo "[+] Adding a cron task to run 'run.py' every 24 hours. You can edit this with the command 'crontab -e'"
echo "[?] Adding the path to crontab. If this isn't the right path to the file, please edit this with the command 'crontab -e'"
#write out current crontab
crontab -l > mycron
#echo new cron into cron file
echo "0 */96 * * * python $(pwd)/run.py" >> mycron
#install new cron file
crontab mycron
rm mycron
echo "[+] Crontab task created!"

echo "----------------------------------------------------------------"

echo "[?] Do you want to create ICU.php? A simple web interface for the domains."
echo "[Y/n]"
read choice_web

if [ "$choice_web" == "Y" ] || [ "$choice_web" == "y" ] || [ -z "$choice_web" ]; then
        ./web/setup.sh "$database_username" "$database_password" "$database_server"
	echo "[+] ICU.php was added."
fi

echo "----------------------------------------------------------------"

echo "[!] All set!"

echo "----------------------------------------------------------------"

echo "[+] If you want to use the telegram options, please add your telegram bot token in credentials.py."
echo "[?] Do you want to run main.py? This script lets you manage your domains."
echo "[Y/n]"
read choice_main

if [ $choice_main = "Y" ] || [ $choice_main = "y" ] || [ -z $choice_main ]; then
	python main.py
fi
