import sys, requests, os
from time import sleep
import digital_ocean
import all_process
import subprocess
import traceback
import json
import socket
import time
import delegator
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
import requests
from Crypto.PublicKey import RSA
from os import chmod
from sshtunnel import SSHTunnelForwarder
import requests
import signal
from cryptography.hazmat.primitives import serialization
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
import credentials
import MySQLdb
import config
import urllib2
import ssl

if digital_ocean.digital_ocean_token:
    key = RSA.generate(2048)
    with open("/tmp/private.key", 'wb') as content_file:
        chmod("/tmp/private.key", 0600)
        content_file.write(key.exportKey('PEM'))
    pubkey = key.publickey()
    with open("/tmp/public.key", 'wb') as content_file:
        content_file.write(pubkey.exportKey('OpenSSH'))

    f_pb_key = open("/tmp/public.key", "r")
    public_key = f_pb_key.read()
    f_pb_key.close()

input_file = sys.argv[1]
domain_main = sys.argv[2]



input_file_open = open(input_file, 'r')

if digital_ocean.digital_ocean_token:
    id_droplet_gb = ""
    #you have to get the image_id of your snapshot already configured to work as a proxy
    create_ssh_key = "curl -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer "+digital_ocean.digital_ocean_token+"' -d '{\"name\":\"icukey\",\"public_key\":\""+str(public_key)+"\"}' \"https://api.digitalocean.com/v2/account/keys\""
    result_creation_keys = subprocess.Popen(create_ssh_key, shell=True, stdout=subprocess.PIPE).stdout
    key = result_creation_keys.read()

    key_dict = json.loads(key)
    key_gb = str(key_dict["ssh_key"]["id"])

domains = input_file_open.readlines()

def generate_image_from_snapshot(key_gb):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+digital_ocean.digital_ocean_token,
    }

    data = '{"name":"icudomain","region":"nyc1","size":"s-1vcpu-1gb","image":"ubuntu-16-04-x64","ssh_keys":['+key_gb+'],"backups":false,"ipv6":true,"user_data":null,"private_networking":null,"volumes": null,"tags":["web"]}'
    response = requests.post('https://api.digitalocean.com/v2/droplets', headers=headers, data=data)
    status = response.status_code
    while status != 202:
        response = requests.post('https://api.digitalocean.com/v2/droplets', headers=headers, data=data)
        status = response.status_code
        time.sleep(2)
    return response.content


def get_droplet(id_droplet):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+digital_ocean.digital_ocean_token,
    }

    response = requests.get('https://api.digitalocean.com/v2/droplets/'+str(id_droplet), headers=headers)
    status = response.status_code
    while status != 200:
        response = requests.get('https://api.digitalocean.com/v2/droplets/' + str(id_droplet), headers=headers)
        status = response.status_code
        time.sleep(2)
    return response.content


def del_droplet(id_droplet):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+digital_ocean.digital_ocean_token,
    }
    response = requests.delete('https://api.digitalocean.com/v2/droplets/' + str(id_droplet), headers=headers)
    status = response.status_code
    while status != 204:
        response = requests.delete('https://api.digitalocean.com/v2/droplets/'+str(id_droplet), headers=headers)
        status = response.status_code
        time.sleep(2)

def del_ssh(id_key):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+digital_ocean.digital_ocean_token,
    }

    response = requests.delete('https://api.digitalocean.com/v2/account/keys/'+str(id_key), headers=headers)
    status = response.status_code
    while status != 204:
        response = requests.delete('https://api.digitalocean.com/v2/account/keys/'+str(id_key), headers=headers)
        status = response.status_code
        time.sleep(2)


def status_response(droplet):
    dict = json.loads(droplet)
    status = dict["droplet"]["status"]
    if 'active' in status:
        return True
    else:
        return False

def ip_response(droplet):
    dict = json.loads(droplet)
    ip = dict["droplet"]["networks"]["v4"][0]["ip_address"]
    return ip

def id_response(droplet):
    dict = json.loads(droplet)
    id = dict["droplet"]["id"]
    return id

def try_port(domain,port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = False
    try:
        ip_thing = socket.gethostbyname(domain)
        result = sock.connect_ex((ip_thing,port))
        if result == 0:
            print "Port is open"
            return True
        else:
            print "Port is not open"
            return False
    except Exception as e:
        print("Port is in use")
        return False

def available(domain):
    try:
        response = requests.get(domain, verify=False)
        return True
    except urllib2.HTTPError, e:
        code = e.code
        print(code)
        try:
            int(code)
            return True
        except ValueError:
            return False
    except Exception as e:
        print e
        return False

def masscan_ports(domain):
        try:

            print "Running Masscan"
            #os.system("/home/th3w4y/PycharmProjects/ICU/ICU/tools/masscan.sh "+domain)
            process = os.system("bash "+str(os.path.dirname(os.path.abspath(__file__)))+"/masscan.sh "+domain+" "+domain_main+" "+config.path_store)
            print "Finished running masscan"
                # and you can block util the cmd execute finish
        except Exception as msg:
            print msg

while("" in domains) :
    domains.remove("")

while("\n" in domains) :
    domains.remove("\n")

for domain in domains:
    domain = domain.replace("\n", "")
    domain = domain.strip()

if os.path.exists(config.path_store+"/"+domain_main+"/backup.txt"):
    backup_file = open(config.path_store+"/"+domain_main+"/backup.txt", "r")
    backup_file_content = backup_file.read()
    backup_file.close()
else:
    backup_file_content = ""


if backup_file_content.strip() == "":
    pass

else:
    print "[+] Backup found"
    print backup_file_content
    for domain in domains[:]:
        backup_file_content = backup_file_content.strip()
        backup_file_content = backup_file_content.replace("\n", "")
        if backup_file_content in domain:
            break
        else:
            print "[+] Recovering State"
        print "[+] Removing" + domain
        domains.remove(domain)


#if there is a backup file:
#remove all the entries until find the entry in the backup file
while("" in domains) :
    domains.remove("")

while("\n" in domains) :
    domains.remove("\n")

print "[+] Domains Remaining: "
print domains

for domain in domains:
    domain = domain.replace("\n", "")
    domain = domain.strip()
    backup_file = open(config.path_store +"/"+domain_main+"/backup.txt", "w+")
    backup_file.write(domain)
    backup_file.close()
    connection = MySQLdb.connect(host=credentials.database_server, user=credentials.database_username,
                                 passwd=credentials.database_password, db=credentials.database_name)
    cursor = connection.cursor()
    cursor.execute("select validity from domains where Domain = %s", (domain,))
    data = cursor.fetchall()
    is_14 = False
    try:
        val = int(data[0])
        if val == 14:
            is_14 = True
        else:
            is_14 = False
    except Exception as e:
        is_14 = True
    cursor.execute("update domains set validity = IF(validity > 0, validity - 1, 14) where domain = %s",
                  (domain,))
    connection.commit()
    connection.close()
    if is_14 is False:
        "Domain State is still Valid!"
        "Skipping Scan"
        if not os.path.exists(config.path_store+"/" + domain_main + "/" + domain):
            os.mkdir(config.path_store+"/" + domain_main + "/" + domain)
        if not os.path.exists(config.path_store+"/" + domain_main + "/" + domain + "/domains-online.txt"):
            output_file = config.path_store+"/" + domain_main + "/" + domain + "/domains-online.txt"
            output_file_open = open(output_file, "a")
            output_file_open.close()
        if not os.path.exists(config.path_store+"/" + domain_main + "/" + domain + "/masscan-ports.txt"):
            temp_file = open(config.path_store+"/" + domain_main + "/" + domain + "/masscan-ports.txt", "a")
            temp_file.close()
        if not os.path.exists(config.path_store+"/" + domain_main + "/" + domain + "/http_https_ssl.txt"):
            temp_file = open(config.path_store+"/" + domain_main + "/" + domain + "/http_https_ssl.txt", "a")
            temp_file.close()
        if not os.path.exists(config.path_store+"/" + domain_main + "/" + domain + "/nmap-ports.txt"):
            nmap_write = open(config.path_store+"/" + domain_main + "/" + domain + "/nmap-ports.txt", "a")
            nmap_write.close()
    else:
        urls = []
        print "Doing Scan"
        #check if domain exist and value is > 0
        # if it is bigger, do the scan
        #else: pass on and update to 14 again
        id_droplet = ""
        try:
            ipadd = socket.gethostbyname(domain)
            print "Domain exist: "+domain
            print "IP: "+ipadd


            if not os.path.exists(config.path_store+"/"+domain_main+"/"+domain):
                os.mkdir(config.path_store+"/"+domain_main+"/"+domain)

            print domain
            print("\n-- Writing masscan and nmap results in " + input_file +" --\n")



#            masscan_ports(domain)
 #           #verify if too many services identified, do manual validation
  #          if not os.path.exists(config.path_store+"/"+domain_main+"/"+domain+"/masscan-ports.txt"):
   #             temp_file = open(config.path_store+"/"+domain_main+"/"+domain+"/masscan-ports.txt","w+")
    #            temp_file.close()
     #       masscan_file = open(config.path_store+"/"+domain_main+"/"+domain+"/masscan-ports.txt","r")
      #      lines = masscan_file.read()
       #     masscan_file.close()
        #    arr_lines = lines.split("\n")
         #   line_count = 0
          #  for x in arr_lines:
           #     try:
            #        int(x)
             #       line_count += 1
              #  except ValueError:
               #     pass
            if True:
                os.system("bash "+str(os.path.dirname(os.path.abspath(__file__)))+"/masscan.sh "+domain_main+" "+domain+" "+config.path_store)
                ports_nmap = ""
                #save nmap only http/https/ssl
                os.system("bash "+str(os.path.dirname(os.path.abspath(__file__)))+"/save_http_https.sh "+domain_main+" "+domain+" "+config.path_store)
                if not os.path.exists(config.path_store+"/"+domain_main+"/"+domain+"/http_https_ssl.txt"):
                    temp_file = open(config.path_store+"/"+domain_main+"/"+domain+"/http_https_ssl.txt", "w+")
                    temp_file.close()
                with open(config.path_store+"/"+domain_main+"/"+domain+"/nmap-ports.txt", "r") as f:
                    ports_nmap = f.readlines()

                prot = ["http", "https"]
                urls = []
                print "[+] Ports in Nmap: "
                print ports_nmap
                len_ports = len(ports_nmap)
                for p in ports_nmap:
                    p = p.replace("\n","")
                    if p == "80" or p == "443":
                        port = ""
                    else:
                        port = ":"+p
                    try:
                        print requests.get("http://"+domain+port,timeout=10).status_code
                        urls.append("http://"+domain+port)
                    except Exception as e:
                        pass
                    try:
                        print requests.get("https://"+domain+port,timeout=10).status_code
                        urls.append("https://"+domain+port)
                    except Exception as e:
                        pass
                if len_ports > 0:
                    with open(config.path_store + "/" + domain_main + "/" + domain + "/domains-online.txt", 'w'): pass

                    for u in urls:
                        output_file = config.path_store + "/" + domain_main + "/" + domain + "/domains-online.txt"
                        output_file_open = open(output_file, "a")
                        output_file_open.write(u + "\n")
                        output_file_open.close()
                if len_ports < 1 and digital_ocean.digital_ocean_token:
                    print "Nothing Found, Doing Secondary Scan"
                    result_creation = generate_image_from_snapshot(key_gb)
                    id_droplet = id_response(result_creation)
                    id_droplet_gb = id_droplet

                    get_status = False
                    while get_status == False:
                        time.sleep(6)
                        result_creation = get_droplet(id_droplet)
                        get_status = status_response(result_creation)
                    print "[+] Trying to create droplet"

                    droplet_IP = ip_response(result_creation)

                    remote_user = 'root'
                    remote_host = droplet_IP
                    remote_port = 22
                    local_host = '127.0.0.1'
                    local_port = 9050
                    ssh_private_key = "/tmp/private.key"
                    result = 1
                    while result != 0:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        result = sock.connect_ex((remote_host, remote_port))
                        time.sleep(4)
                    print "[+] Trying to connect to droplet!"
                    ssh_connect = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -D " + str(
                            local_port) + " -Nf -i " + ssh_private_key + " " + remote_user + "@" + str(remote_host)
                    proc1 = subprocess.Popen(ssh_connect, shell=True)
                    out, err = proc1.communicate()
                    if out == None:
                        out = ""
                    if err == None:
                        err = ""

                    while "Connection refused" in out or "Connection refused" in err or "Connect reset" in out or "Connection reset" in err:
                        ssh_connect = "ssh -o 'GatewayPorts yes' -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -D " + str(
                            local_port) + " -Nf -i " + ssh_private_key + " " + remote_user + "@" + str(remote_host)
                        proc1 = subprocess.Popen(ssh_connect, shell=True)
                        out, err = proc1.communicate()
                        time.sleep(2)
                        if out == None:
                            out = ""
                        if err == None:
                            err = ""
                    print 'SSH Port Forward started, PID:', proc1.pid

                    os.system("bash " + str(os.path.dirname(
                        os.path.abspath(__file__))) + "/masscan2.sh " + domain_main + " " + domain + " " + config.path_store)
                    print "Deleting Droplet"
                    del_droplet(id_droplet)
                    print "Droplet Deleted"
                    all_process.kill_process_like(ssh_connect)

                        # save nmap only http/https/ssl
                    os.system("bash " + str(os.path.dirname(os.path.abspath(
                        __file__))) + "/save_http_https.sh " + domain_main + " " + domain + " " + config.path_store)
                    if not os.path.exists(config.path_store + "/" + domain_main + "/" + domain + "/http_https_ssl.txt"):
                        temp_file = open(config.path_store + "/" + domain_main + "/" + domain + "/http_https_ssl.txt", "w+")
                        temp_file.close()

                    with open(config.path_store + "/" + domain_main + "/" + domain + "/nmap-ports.txt", "r") as f:
                        ports_nmap = f.readlines()
                        prot = ["http", "https"]
                        urls = []
                        print "[+] Ports in Nmap: "
                        print ports_nmap
                        for p in ports_nmap:
                            p = p.replace("\n", "")
                            if p == "80":
                                urls.append("http://" + domain)
                            else:
                                if p == "443":
                                    urls.append("https://" + domain)
                                else:
                                    if "80" in p:
                                        urls.append("http://" + domain + ":" + p)
                                    else:
                                        if "443" in p:
                                            urls.append("https://" + domain + ":" + p)
                                        else:
                                            urls.append("http://" + domain + ":" + p)
                                            urls.append("https://" + domain + ":" + p)
                    len_nmap = len(ports_nmap)
                    if len_nmap > 0:
                        with open(config.path_store + "/" + domain_main + "/" + domain + "/domains-online.txt", 'w'): pass

                        for u in urls:
                            output_file = config.path_store + "/" + domain_main + "/" + domain + "/domains-online.txt"
                            output_file_open = open(output_file, "a")
                            output_file_open.write(u + "\n")
                            output_file_open.close()
                    id_droplet = ""
                    with open(config.path_store + "/" + domain_main + "/" + domain + "/domains-online.txt", 'w'): pass
        except Exception as e:
            print e
            traceback.print_exc()
            if id_droplet != "":
                if digital_ocean.digital_ocean_token:
                    del_droplet(id_droplet)
                id_droplet = ""
            if not os.path.exists(config.path_store+"/" + domain_main + "/" + domain):
                os.mkdir(config.path_store+"/" + domain_main + "/" + domain)
            if not os.path.exists(config.path_store+"/" + domain_main + "/" + domain + "/domains-online.txt"):
                output_file = config.path_store+"/" + domain_main + "/" + domain + "/domains-online.txt"
                output_file_open = open(output_file, "w+")
                output_file_open.close()
            if not os.path.exists(config.path_store+"/"+domain_main+"/"+domain+"/masscan-ports.txt"):
                temp_file = open(config.path_store+"/"+domain_main+"/"+domain+"/masscan-ports.txt","a")
                temp_file.close()
            if not os.path.exists(config.path_store+"/" + domain_main + "/" + domain + "/http_https_ssl.txt"):
                temp_file = open(config.path_store+"/" + domain_main + "/" + domain + "/http_https_ssl.txt", "a")
                temp_file.close()
            if not os.path.exists(config.path_store+"/" + domain_main + "/" + domain + "/nmap-ports.txt"):
                nmap_write = open(config.path_store+"/" + domain_main + "/" + domain + "/nmap-ports.txt", "a")
                nmap_write.close()

if digital_ocean.digital_ocean_token:
    del_ssh_command = del_ssh(key_gb)
input_file_open.close()
print("\n-- Done Scanning SubDomains of: "+domain)
