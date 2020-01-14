#!/usr/bin/python

import sys, datetime, MySQLdb, telegram, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
import credentials

def disjoint(e,f):
    c = list(e) # [:] works also, but I think this is clearer
    d = list(f)
    for i in e: # no need for index. just walk each items in the array
        for j in f:
            if i == j: # if there is a match, remove the match.
                c.remove(i)
                d.remove(j)
    print c + d
    return c + d

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

newSubDomains2 = []

for i in newSubDomains:
    urls_same_dom = i[0].split('\n')
    for h in urls_same_dom:
        if h:
            newSubDomains2.append(h)

newSubDomains = newSubDomains2[:]
#get domains by counter, only the ones with counter bigger than 0

#get domains_services by the other counter, only the ones with counter bigger than 0

cursor.execute ("select * from errors where scan_Id = %s order by ErrorDate", (scanId,))
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

old_domains = []

try:
    fa = open('alllastdomains.txt')
    all_old_domains = fa.readlines()
    fa.close()
except Exception as e:
    fa2 = open('alllastdomains.txt','w')
    fa2.close()

try:
    f = open('lastdomains.txt')
    old_domains = f.readlines()
    f.close()
except Exception as e:
    f2 = open('lastdomains.txt','w')
    f2.close()


new_domains = disjoint(all_old_domains,newSubDomains)
f2 = open('lastdomains.txt','w')
for i in new_domains:
    f2.write(i + '\n')
f2.close()

fa2 = open('alllastdomains.txt','w')
for i in newSubDomains:
    fa2.write(i + '\n')
fa2.close()

message += "\n\[+] " + str(len(new_domains)) + " New subdomains:"
for domain in new_domains:
    domain = domain.strip()
    message += "\n" + str(domain)

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
