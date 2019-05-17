#!/usr/bin/python

import sys, datetime, MySQLdb, telegram, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
import credentials

if credentials.telegram_bot_token == "" or credentials.telegram_chat_id == "":
	print "[+] No telegram bot token and/or telegram chat id set in credentials.py"
	sys.exit()

bot = telegram.Bot(credentials.telegram_bot_token)
scanId = sys.argv[1]
message = "*" + str(datetime.datetime.now().replace(microsecond=0)) + "*"

connection = MySQLdb.connect (host = credentials.database_server, user = credentials.database_username, passwd = credentials.database_password, db = credentials.database_name)
cursor = connection.cursor()

cursor.execute ("select urls from domains where count_new_domain > 0 and Active order by TopDomainID")
newSubDomains = cursor.fetchall()

#get domains by counter, only the ones with counter bigger than 0

#get domains_services by the other counter, only the ones with counter bigger than 0

cursor.execute ("select * from errors where scan_Id = %s order by ErrorDate", (scanId))
errors = cursor.fetchall()

connection.close()

display_all = False

try:
	if sys.argv[2] == "true":
		display_all = True
except:
	print "Not called from bot"

message += "\n_Scan " + str(scanId) + "_"

message += "\n"

if len(errors) > 1:
        message += "\n(" + str(len(errors)) + "  Errors)"
elif len(errors) == 1:
        message += "\n(" + str(len(errors)) + "  Error)"

if len(errors) > 0:
	message += "\n--------------"

if (len(newSubDomains) < 15 and display_all == False) or (len(newSubDomains) < 100 and display_all == True):
	message += "\n\[+] " + str(len(newSubDomains)) + " New subdomains:"
	for domain in newSubDomains:
		message += "\n" + str(domain[0])
else:
	message += "\n\[+] " + str(len(newSubDomains)) + " New subdomains"

message += ""

try:
    if len(message) <= 4000:
        bot.send_message(chat_id=credentials.telegram_chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        parts = []
        while len(message) > 0:
            if len(message) > 4000:
                part = message[:4000]
                first_lnbr = part.rfind('\n')
                if first_lnbr != -1:
                    parts.append(part[:first_lnbr])
                    message = message[(first_lnbr + 1):]
                else:
                    parts.append(part)
                    message = message[4000:]
            else:
                parts.append(message)
                break

        msg = None
        for part in parts:
            msg = bot.send_message(chat_id=credentials.telegram_chat_id, text=part, parse_mode=telegram.ParseMode.MARKDOWN)

except Exception as msg:
    print msg
