#!/usr/bin/python
import os, sys, MySQLdb, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")
import credentials
import config
from datetime import datetime


def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def enum_sub():
    # if there is a backup_file do not do recon
	os.system(os.path.dirname(os.path.abspath(
		__file__)) + "/../../tools/dependencies/sublister/sublist3r.py -o " + config.path_store + "/" + domain + "/domains-all.txt -d " + domain)
	time.sleep(2)

	# Subfinder
	os.system(
		"subfinder -d " + domain + " -v -o " + config.path_store + "/" + domain + "/domains-subfinder.txt --timeout 6")
	time.sleep(2)

	# Amass
	os.system("amass enum -o " + config.path_store + "/" + domain + "/domains-amass.txt -d " + domain)
	time.sleep(2)

	os.system("$SUDOMY/sudomy --no-probe -d " + domain " > sudomy_results.txt")
	f = open(config.path_store + "/" + domain + "/domains-massdns.txt", "r")
	f2 = open(config.path_store + "/" + domain + "/domains-massdns2.txt", "w+")
	for x in f:
		line = x.split(". A")
		f2.write(line[0] + "\n")
	f.close()
	f2.close()
	time.sleep(2)
	
	# MassDNS
	#os.system(
	#	"python $MASSDNS/scripts/subbrute.py $MASSDNS/lists/names.txt " + domain + " | $MASSDNS/bin/massdns -r $MASSDNS/lists/resolvers.txt -t A -o S -w " + config.path_store + "/" + domain + "/domains-massdns.txt")
	#time.sleep(2)

	#f = open(config.path_store + "/" + domain + "/domains-massdns.txt", "r")
	#f2 = open(config.path_store + "/" + domain + "/domains-massdns2.txt", "w+")
	#for x in f:
	#	line = x.split(". A")
	#	f2.write(line[0] + "\n")
	#f.close()
	#f2.close()

try:
	domain = sys.argv[1].strip()
	scanId = sys.argv[2]

	if not os.path.exists(config.path_store):
		os.makedirs(config.path_store)

	if not os.path.exists(config.path_store+"/"+domain+"/"):
		os.makedirs(config.path_store+"/"+domain+"/")

	#Add new subdomain scanners here. Make sure to let them save the output to /tmp/ICU/{domain}/doains-all.txt

	try:
		if os.path.exists(config.path_store+"/"+domain+"/backup.txt"):
			backup_file = open(config.path_store+"/"+domain+"/backup.txt", "r")
			backup_file_content = backup_file.read()
			backup_file.close()
			if backup_file_content.strip() != "":
				"[+] Restoring Backup!!"
			else:
				enum_sub()
		else:
			enum_sub()


	except Exception as e:
		print "An error occured; You probably dont have either subfinder or amass installed. Check the README.md to see you how to install them. Error: "
		print str(e)


	connection = MySQLdb.connect (host = credentials.database_server, user = credentials.database_username, passwd = credentials.database_password, db = credentials.database_name)
	cursor = connection.cursor()

	#Retrieve all info from a top domain and its subdomains, so we can use this data instead of opening new db connections later on
	cursor.execute("select Domain, TopDomainID, Active, Program, DomainID, scan_Id from domains where TopDomainID = (select DomainID from domains where Domain = %s) or Domain = %s", (domain, domain))
	database_data = cursor.fetchall()
	database_domains = [d[0] for d in database_data]

        non_active_subdomains = [x[0] for x in database_data if ord(x[2]) == False]
        program = [x[3] for x in database_data if x[0] == domain][0]
        topDomainID = [x[4] for x in database_data if x[0] == domain][0]

	#All the domains from the subdomain scanners
	domains_all = open(config.path_store+"/"+domain+"/domains-all.txt",'r').read().split('\n')


	try:
		#Domains from subfinder
		domains_subfinder = open(config.path_store+"/"+domain+"/domains-subfinder.txt",'r').read().split('\n')
		
	        #Domains from amass
        	domains_amass = open(config.path_store+"/"+domain+"/domains-amass.txt",'r').read().split('\n')
		
        	domains_sudomys = open(config.path_store+"/"+domain+"/domains-amass.txt",'r').read().split('\n')
		
		domains_amass = open(config.path_store+"/"+domain+"/domains-amass.txt",'r').read().split('\n')
		sudomy = os.getenv("SUDOMY")
		domains_sudomy = open(sudomy+"/"+datetime.today().strftime('%m-%d-%Y')+domain+"/subdomain.txt",'r').read().split('\n')
		#Domains from censys
		#domains_censys = open("/tmp/ICU/"+domain+"/domains-censys.txt",'r').read().split('\n')

		#Domains from subfind3r
		#domains_sublist3r = open("/tmp/ICU/"+domain+"/domains-sublist3r.txt",'r').read().split('\n')

		#DOmains from Crt
		#domains_crt = open("/tmp/ICU/"+domain+"/domains-crt.txt",'r').read().split('\n')

		#Domains from massdns
		#domains_massdns = open(config.path_store+"/"+domain+"/domains-massdns2.txt",'r').read().split('\n')

		#Add the massdns domains
                #domains_all.extend(x for x in domains_massdns if x not in domains_all)

                #domains_all = list(set(domains_all))

		#Add the sublist3r domains
                #domains_all.extend(x for x in domains_crt if x not in domains_all)

                #domains_all = list(set(domains_all))


		#Add the sublist3r domains
                #domains_all.extend(x for x in domains_sublist3r if x not in domains_all)

		domains_all = list(set(domains_all))


	        #Add the subfinder domains
        	domains_all.extend(x for x in domains_subfinder if x not in domains_all)

		domains_all = list(set(domains_all))

		#Add the censys domains
		#domains_all.extend(x for x in domains_censys if x not in domains_all)

		#unique
		domains_all = list(set(domains_all))

	        #Add the amass domains
        	domains_all.extend(x for x in domains_amass if x not in domains_all)

        	#unique
        	domains_all = list(set(domains_all))
        except Exception as e:
                print "An error occured; You probably dont have either subfinder or amass installed. Check the README.md to see you how to install them. Error: "
                print str(e)

	#Add all the database subdomain to it
	domains_all.extend(x for x in database_domains if x not in domains_all)

	#unique -- Unique each time after adding a new list, to limit ram usage
	domains_all = list(set(domains_all))

	print domains_all
	domain_all_write = open(config.path_store+"/"+domain+"/domains-all.txt",'w')
	for d in domains_all:
		domain_all_write.write(d+"\n")

	domain_all_write.close()

	#Put all the online domains in a domains-online.txt
	os.system("sudo python "+os.path.dirname(os.path.abspath(__file__)) + "/../../tools/nmap_masscan.py "+config.path_store+"/"+domain+"/domains-all.txt "+domain)
	#Convert online domains to array

	while ("" in domains_all):
		domains_all.remove("")

	while ("\n" in domains_all):
		domains_all.remove("\n")


	#Loop through every subdomain
	for sub_domain in domains_all:
		sub_domain.replace("\n", "")
		try:
			if sub_domain:
				urls_file = open(config.path_store+"/" + domain + "/"+sub_domain+"/domains-online.txt", 'r')
				urls = urls_file.read()
				urls_file.close()
				active = False
				if urls == "" or urls == None:
					active = False
				else:
					active = True
				#Get the scanID to insert. If the domains was already in the db and isnt changed, then keep the old scanID. otherwise use the scanID of the current scan
				insertScanId = scanId

				if int(scanId) == 1: #first run
					counter = 0

					#Insert the new values, or update them if they already existed
					if active == True:

						nmap_file_f = open(config.path_store+"/" + domain + "/" + sub_domain + "/nmap-ports.txt", "r")
						nmap_file = nmap_file_f.read()
						nmap_result = find_between(nmap_file, "\n\n", "\n\n")
						cursor.execute("INSERT INTO domains (Program, TopDomainID, Active, InScope, Domain, scan_Id, count_new_domain, urls, Nmap_Result) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (program, topDomainID, active, 1, sub_domain, insertScanId, counter, urls, nmap_result))
						connection.commit()
						nmap_file_f.close()

						#
					else:
						cursor.execute(
							"INSERT INTO domains (Program, TopDomainID, Active, InScope, Domain, scan_Id, count_new_domain) VALUES (%s, %s, %s, %s, %s, %s, %s) ",
							(program, topDomainID, active, 1, sub_domain, insertScanId, counter))
						connection.commit()
						#

				else:
					counter = 0

					#select domain_name, if exists, check if is active: counter decays, if becomes active, counter becomes 14
					#count = heuristics

					#select domain name, if exists, get nmap results, compare old and new results, update nmap results and add the new result to newresult column, update counter
					if active == True:
						nmap_file_f = open(config.path_store+"/" + domain + "/" + sub_domain + "/nmap-ports.txt", "r")
						nmap_file = nmap_file_f.read()
						nmap_result = find_between(nmap_file, "\n\n", "\n\n")
						cursor.execute("select Domain from domains where Domain = %s and Active", [sub_domain])
						domain_was_active = cursor.fetchall()
						nmap_file_f.close()
						if len(domain_was_active) == 1:

							cursor.execute(
								"INSERT INTO domains (Program, TopDomainID, Active, InScope, Domain, scan_Id, urls, Nmap_Result) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE Active = %s, LastModified = now(), scan_Id = %s, count_new_domain = IF(count_new_domain > 0, count_new_domain - 1, count_new_domain), urls = %s, Nmap_Result=%s",
								(program, topDomainID, active, 1, sub_domain, insertScanId, urls, nmap_result, active, insertScanId, urls, nmap_result))
							connection.commit()

						#
						else:
							cursor.execute(
								"INSERT INTO domains (Program, TopDomainID, Active, InScope, Domain, scan_Id, count_new_domain, urls, Nmap_Result) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE Active = %s, LastModified = now(), scan_Id = %s,count_new_domain = %s, urls = %s, Nmap_Result=%s",
								(program, topDomainID, active, 1, sub_domain, insertScanId, 14, urls, nmap_result, active,
								 insertScanId,14, urls, nmap_result))
							connection.commit()
							#


					else:
						cursor.execute(
							"INSERT INTO domains (Program, TopDomainID, Active, InScope, Domain, scan_Id, count_new_domain) VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE Active = %s, LastModified = now(), scan_Id = %s, urls = null",
							(program, topDomainID, active, 1, sub_domain, insertScanId, counter, active, insertScanId))
						connection.commit()
		except Exception as e:
			print e


	cursor.close ()
	connection.close ()
except Exception as e:
	#Handle the errors, and save them to the database
	print "error in domains_db.py with main domain; " + domain
	print e
	if scanId == "NULL":
		scanId = None
	cursor.execute("INSERT INTO errors (Domain, ErrorDescription, Error, Script, scan_Id) VALUES (%s, %s, %s, %s, %s) ", (domain, "error in domains_db.py with main domain; "+domain, e, "sublister_to_db.py", scanId))
	connection.commit()
	cursor.close()
	connection.close()
	print e
sys.exit()
