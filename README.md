## 📌 Fork Description
This fork implements new functionalities to the original project of Random003 (https://github.com/003random/ICU) and is currently maintained by Thiago Mayllart.

New Functionalities:

[+] **New tools** added to subdomain enumeration: Subfinder and Massdns  
[+] **Port Scan**: each domain is scanned by Masscan and NMAP to find services and HTTP/HTTPS servers.  
[+] Domains are active based on existance of services in the results of **Masscan and NMAP**.  
[+] **Proxy Scan**: The tool uses proxies to scan each subdomain identified.  
[+] **Proxy Creation and Destroy**: the tool is capable of creating droplets for each scanning action executed by the program. The proxy is automatically created and destroyed by the tool. All the process of setting up the proxy and the communications to the proxy is automatically made by the program.  
[+] **API communications**: The tool uses the Digital Ocean's API to create and destroy the proxies.  
[+] **New Telegram Functionalities**: URL's Button -> retrieve all urls (HTTP/HTTPS) identified using the port scan (not restricted to default ports 80/443). NMAP Button -> retrieve the NMAP result for a specifc domain scan.  
[+] **Bug Fix**: No more message length limit retrieving results using the telegram bot.  
[+] **New Methodology to point new domains**: discovered domains are no longer considered "new" after 14 scans.  
[+] Domains inserted in the database are only scanned (Nmap and Masscan) again after a "validity" period: 14 scans.  

## 📌 Description 
NightVision is a tool to constantly keep an updated database of domains and subdomains, by regularly scanning domains for subdomains with the most common subdomain scanners.  
  
NightVision works by creating a database with domains and a crontask to launch the subdomain scanners script. You can launch this script manually as well. You can also keep control of your domains and subdomains with the main.py script or with the telegram bot. There is also a simple web application that is meant for a quick view of your domains. This web application is not meant yet for a large number of domains.  

This new fork intends to add more tools and procedures commonly and repeatedly executed in the phase of Recon. It currently executes masscan and nmap to find active services and new HTTP/HTTPS endpoints identified (not restricted to ports 80/443).

All the scans are executed behind proxies and all the proxies are automatically created and destroyed by the tool. There is no need to worry about droplet creation or stablishing SOCKS communications with these proxies. 
  
    
# Install 

This tool **MUST BE RUN AS ROOT** in order to work. Install on **Ubuntu 18.04**.
```
mdkir /home/ubuntu/
cd /home/ubuntu/
git clone https://github.com/thiagomayllart/NightVision 
cd NightVision
source install.sh 
```  
The installation script asks for various things, including your MySQL database username and password. These will be saved in credentials.py. You can always change these credentials later on. 

## Optional (recommended)
NightVision also uses [Subfinder]("https://github.com/Ice3man543/subfinder") and [Amass]("https://github.com/caffix/amass/"). 
You need to install those as well. You need to have GO for those tools. [Here]("https://www.digitalocean.com/community/tutorials/how-to-install-go-on-debian-8") you can find how to install GO. 
After you've installed GO; Execute the following commands to install Amass and Subfinder: 
```
go get github.com/caffix/amass
go get github.com/Ice3man543/subfinder
```
 
 ## Setting up the MySQL server

```

$sudo mysql_secure_installation

Would you like to setup VALIDATE PASSWORD plugin?

Press y|Y for Yes, any other key for No: n

Remove anonymous users? (Press y|Y for Yes, any other key for No) : y

Success.

Disallow root login remotely? (Press y|Y for Yes, any other key for No) : y

Success.

Remove test database and access to it? (Press y|Y for Yes, any other key for No) : y

 - Dropping test database...

Success.

 - Removing privileges on test database...

Success.

Reload privilege tables now? (Press y|Y for Yes, any other key for No) : y

Success.

All done!

```

 ## Setting up the DigitalOcean API
 
 This procedure is required in order to allow the creation and destruction of droplets, consequently, the execution of port scans and discovery of web services.
 
Just add the digital API key to the file **digital_ocean.py** in the **tools** directory.
 
Easy dizzy.

```
digital_ocean_token = "{ADD_YOUR_KEY_HERE}"

```
  
 ## Setting up the Proxy Configuration
 
 All the proxy communications are done by using the default port of the proxychains file. Please, keep the default line of the **proxychains.conf** file:

 ```
socks4 127.0.0.1 9050
 ```
 
 
## WARNING:

In case of failure, check your Digital Ocean Account to check if there are no remaining Droplets (to avoid extra charges).

## BACKUP Functionality:

In case of failure, the tool is able to return to the same point of execution. Just kill the process and run the scan again (Telegram bot or terminal interface).


## 📌 TO DO's

[+] Directory Fuzzing behind proxies: to avoid IP blocks.
[+] Add directory fuzzing results to the database
[+] Telegram Buttons to retrieve directory fuzzing results.
[+] Change privileges of execution
  
# Telegram 
NightVision also includes a telegram bot and notifications part. If you want to use this, you will have to include your telegram bot token in credentials.py. You can get a telegram bot token [here]("https://core.telegram.org/bots#3-how-do-i-create-a-bot"). Next off, you need to run setup.py in /telegram, and then send /start to the bot. This will save your chat_id to credentials.py so it can be used for authentication with the bot, and to send the notifications to.  
   
# Modules 
The following modules are used: MySQLdb, telegram, random, sys, os, datetime, logging, time. 
 
The install script offers an option to install the modules from requirements.txt. This requires pip to be installed. If, for some reason, some modules are still missing. Then install these modules. The most important one is MySQLdb. [here]("https://stackoverflow.com/questions/25865270/how-to-install-python-mysqldb-module-using-pip") you can read how to install MySQLdb.  

# Extra
To get NightVision up and running, requires some simple skills. If you need serious help, you can contact me via twitter.  
 
# Credits 
Credits to:  
[Subfinder]("https://github.com/Ice3man543/subfinder"), [Amass]("https://github.com/caffix/amass/"), [Sublist3r]("https://github.com/aboul3la/Sublist3r")!

# Images  
![main.py](https://poc-server.com/github/ICU/main.py.png)
  ___  
![Telegram Bot](https://poc-server.com/github/ICU/telegrambot.png)

 
*Created by [003random](http://hackerone.com/003random) - [@003random](https://twitter.com/rub003) - [003random.com](https://poc-server.com/blog/)* - [tmayllart](https://twitter.com/tmayllart) 



