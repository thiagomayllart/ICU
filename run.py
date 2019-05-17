#!/usr/bin/python
try:
	import sys, os, MySQLdb, datetime, credentials, config

	sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/tools/")
	import all_process
	#if there is a scan running exit
	if all_process.is_scan_running():
		print "[+] Scan is still Running, Gonna Try Next time"
		print "[+] If you want it to stop, kill the process"
		sys.exit()
	else:
		connection = MySQLdb.connect (host = credentials.database_server, user = credentials.database_username, passwd = credentials.database_password, db = credentials.database_name)
		cursor = connection.cursor ()

		cursor.execute ("insert into scans (StartDate) values (CURRENT_TIMESTAMP)")
		connection.commit()
		scanId = cursor.lastrowid
		#checks if it can increase scanID value, otherwise, keep same value
		if os.path.exists(config.path_store):
			scanId -= 1
		cursor.execute ("select Domain,scan_Id from domains where TopDomainID is NULL order by Domain")
		data = cursor.fetchall ()
		connection.close()

		for row in data:
			scanId_temp = int(scanId)
			if row[1] == None or int(row[1]) != 0:
				scanId = 1
				domain = str(row[0])
				connection = MySQLdb.connect(host=credentials.database_server, user=credentials.database_username,
											 passwd=credentials.database_password, db=credentials.database_name)
				cursor = connection.cursor()
				cursor.execute("update domains set scan_Id = 0 where Domain = %s", (domain,))
				connection.commit()
				connection.close()
			print "Starting subdomain scans on " + row[0]
			print "Scan ID: " +str(scanId)
			os.system("python " + os.path.dirname(os.path.abspath(__file__))  + "/database/additional_tools/domains_db.py " + row[0] + " " + str(scanId))
			scanId = scanId_temp

		connection = MySQLdb.connect (host = credentials.database_server, user = credentials.database_username, passwd = credentials.database_password, db = credentials.database_name)
		cursor = connection.cursor ()
		cursor.execute ("update scans set EndDate = CURRENT_TIMESTAMP where ScanID = %s", (scanId))
		os.remove(config.path_store)
		connection.commit()
		connection.close()
		#remove backup file
		os.system("python " + os.path.dirname(os.path.abspath(__file__))  + "/telegram/notify.py " + str(scanId))
except Exception, e:
	print "error: " + str(e)

	if not os.path.exists(os.path.dirname(os.path.abspath(__file__))  + "/logs"):
                os.makedirs(os.path.dirname(os.path.abspath(__file__))  + "/logs")

	with open(os.path.dirname(os.path.abspath(__file__))  + '/logs/run_logs.txt', 'w+') as the_file:
		the_file.write(str(e) + "\n")
