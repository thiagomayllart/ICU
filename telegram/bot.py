#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, datetime, MySQLdb, os, telegram, sys
from telegram import (InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton)
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from random import randint
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../tools/")
import all_process
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
import credentials
import time

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

telegram_bot_token = credentials.telegram_bot_token

logger = logging.getLogger(__name__)

BUTTON, CUSTOM_SCAN_ID_INPUT, ADD_DOMAIN, EDIT_DOMAIN, GET_DOMAINS, CONTAINS, GET_DOMAIN_URLS, GET_NMAP, GET_ALL_URLS, GET_SERVICE_DOMAIN = range(10)

def send_update(update, message):
    try:
        if len(message) <= 4000:
            return update.message.reply_text(message)

        parts = []
        while len(message) > 0:
            if len(message) > 4000:
                part = message[:4000]
                first_lnbr = part.rfind('\n')
                if first_lnbr != -1:
                    parts.append(part[:first_lnbr])
                    message = message[(first_lnbr+1):]
                else:
                    parts.append(part)
                    message = message[4000:]
            else:
                parts.append(message)
                break

        msg = None
        for part in parts:
            msg = update.message.reply_text(part)

    except Exception as msg:
        print msg


def send_message(bot, chat_id, message):
    try:
        if len(message) <= 4000:
            return bot.send_message(chat_id=credentials.telegram_chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

        parts = []
        while len(message) > 0:
            if len(message) > 4000:
                part = message[:4000]
                first_lnbr = part.rfind('\n')
                if first_lnbr != -1:
                    parts.append(part[:first_lnbr])
                    message = message[(first_lnbr+1):]
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

def start(bot, update):
    print "---------- Start -----------"
    if str(update.message.chat_id) != str(credentials.telegram_chat_id):
        update.message.reply_text(
            "Not authorized! If you think this is a mistake, please check if your chat_id is in credentials.py. You can also run setup.py in /telegram to setup the right credentials for your telegram.")
        return

    user = update.message.from_user
    hour = datetime.datetime.now().hour
    greeting = "Good morning " + str(user['first_name']) if 5 <= hour < 12 else "Good afternoon " + str(
        user['first_name']) if hour < 18 else "Good evening " + str(user['first_name'])

    keyboard = [[InlineKeyboardButton("Data", callback_data='data-' + str(randint(0, 999))),
                 InlineKeyboardButton("Scans", callback_data='scan-' + str(randint(0, 999)))],
                [InlineKeyboardButton("✘  Close", callback_data='close-' + str(randint(0, 999)))]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(greeting, reply_markup=reply_markup)
    print "button before"
    return BUTTON


def button(bot, update):
    global choice
    global limit
    choice = ""
    limit = ""
    query = update.callback_query
    # each callback_data attr has a random int after the '-' to make the button unique each time so the spinning loading circle goes away after returning to an excisting button
    choice = query.data.split('-')[0]
    r = str(randint(0, 99))

    header_1 = "Category:"
    keyboard_1 = [[InlineKeyboardButton("Data", callback_data='data-' + r),
                   InlineKeyboardButton("Scans", callback_data='scan-' + r)],
                  [InlineKeyboardButton("✘  Close", callback_data='close-' + r)]]

    header_2 = "Action:"
    keyboard_2 = [[InlineKeyboardButton("Latest", callback_data='latest-' + r),
                   InlineKeyboardButton("Custom", callback_data='custom-' + r),
                   InlineKeyboardButton("Run", callback_data='run-' + r)],
                  [InlineKeyboardButton("« Back to catagories", callback_data='back-' + r)]]

    header_3 = "Action:"
    keyboard_3 = [[InlineKeyboardButton("Add", callback_data='add-' + r),
                   InlineKeyboardButton("Edit", callback_data='edit-' + r),
                   InlineKeyboardButton("Get", callback_data='get-' + r)],
                  [InlineKeyboardButton("« Back to catagories", callback_data='back-' + r)]]

    header_4 = "It looks like a scan is already running. Want to start a new one?"
    keyboard_4 = [[InlineKeyboardButton("Yes", callback_data='yes_scan-' + r),
                   InlineKeyboardButton("No", callback_data='no_scan-' + r)],
                  [InlineKeyboardButton("« Back to scans", callback_data='back_scan-' + r)]]

    header_5 = "Action:"
    keyboard_5 = [[InlineKeyboardButton("(top)Domains", callback_data='topdomains-' + r),
                   InlineKeyboardButton("Subdomains", callback_data='subdomains-' + r), InlineKeyboardButton("URLs", callback_data='urls-' + r), InlineKeyboardButton("Nmap", callback_data='nmap-' + r),
                   InlineKeyboardButton("Contains", callback_data='contains-' + r)],
                  [InlineKeyboardButton("« Back to data", callback_data='back_data-' + r)]]

    header_6 = "Which type of domains?"
    keyboard_6 = [[InlineKeyboardButton("Active", callback_data='active-' + r),
                   InlineKeyboardButton("All", callback_data='all-' + r)],
                  [InlineKeyboardButton("« Back to actions", callback_data='back_get-' + r)]]

    header_7 = "How many domains?"
    keyboard_7 = [[InlineKeyboardButton("Top 20", callback_data='limit-' + r),
                   InlineKeyboardButton("All", callback_data='nolimit-' + r)],
                  [InlineKeyboardButton("« Back to actions", callback_data='back_data-' + r)]]

    header_8 = "All URL's or Domain Specific?"
    keyboard_8 = [[InlineKeyboardButton("All", callback_data='all_urls-' + r),
                   InlineKeyboardButton("Specific", callback_data='domain_specific-' + r), InlineKeyboardButton("All (Txt)", callback_data='all_urls_txt-' + r)],
                  [InlineKeyboardButton("« Back to actions", callback_data='back_data-' + r)]]

    header_9 = "Find Service or Nmap Result for Domain?"
    keyboard_9 = [[InlineKeyboardButton("Find Service", callback_data='f_service-' + r),
                   InlineKeyboardButton("Nmap Result", callback_data='nmap_res-' + r)],
                  [InlineKeyboardButton("« Back to actions", callback_data='back_data-' + r)]]



    # ToDO: Transform into a swtich
    if choice == "back":
        bot.edit_message_text(header_1, reply_markup=InlineKeyboardMarkup(keyboard_1), chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return BUTTON
    elif choice == "close":
        bot.edit_message_text("/start", chat_id=query.message.chat_id, message_id=query.message.message_id)
        return ConversationHandler.END
    elif choice == "scan":
        bot.edit_message_text(header_2, reply_markup=InlineKeyboardMarkup(keyboard_2), chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return BUTTON
    elif choice == "data":
        bot.edit_message_text(header_3, reply_markup=InlineKeyboardMarkup(keyboard_3), chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return BUTTON

    connection = MySQLdb.connect(host=credentials.database_server, user=credentials.database_username,
                                 passwd=credentials.database_password, db=credentials.database_name)
    cursor = connection.cursor()

    if choice == "latest":
        get_latest_scan(bot, update, cursor)
        cursor.close()
        connection.close()
    elif choice == "custom":
        get_custom_scan(bot, update, cursor)
        cursor.close()
        connection.close()
        return CUSTOM_SCAN_ID_INPUT
    elif choice == "run":
        global choice
        choice = ""
        run_scan(bot, update, cursor)
        cursor.close()
        connection.close()
        time.sleep(6)
        print "button before"
        return BUTTON
    if choice == "add":
        cursor.close()
        connection.close()
        bot.send_message(text="Coming soon, pr's are welcome...", chat_id=query.message.chat_id,
                         parse_mode=telegram.ParseMode.MARKDOWN)
        return BUTTON
    # return ADD_DOMAIN
    elif choice == "edit":
        cursor.close()
        connection.close()
        bot.send_message(text="Coming soon...", chat_id=query.message.chat_id, parse_mode=telegram.ParseMode.MARKDOWN)
        return BUTTON
    # return EDIT_DOMAIN
    elif choice == "get":
        cursor.close()
        connection.close()
        bot.edit_message_text(header_5, reply_markup=InlineKeyboardMarkup(keyboard_5), chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return BUTTON

    if choice == "topdomains":
        bot.edit_message_text(header_7, reply_markup=InlineKeyboardMarkup(keyboard_7), chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        global subdomains
        subdomains = False
        print "choice = topdomains"
        return BUTTON
    elif choice == "subdomains":
        bot.edit_message_text(header_6, reply_markup=InlineKeyboardMarkup(keyboard_6), chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        global subdomains
        subdomains = True
        return BUTTON
    elif choice == "urls":
        bot.edit_message_text(header_8, reply_markup=InlineKeyboardMarkup(keyboard_8), chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return BUTTON
    elif choice == "nmap":
        bot.edit_message_text(header_9, reply_markup=InlineKeyboardMarkup(keyboard_9), chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return BUTTON
    elif choice == "contains":
        bot.send_message(text="Coming soon...", chat_id=query.message.chat_id, parse_mode=telegram.ParseMode.MARKDOWN)
        return BUTTON
    # return CONTAINS
    elif choice == "back_data":
        bot.edit_message_text(header_3, reply_markup=InlineKeyboardMarkup(keyboard_3), chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return BUTTON
    elif choice == "back_get":
        bot.edit_message_text(header_5, reply_markup=InlineKeyboardMarkup(keyboard_5), chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return BUTTON

    if choice == "active":
        global active
        active = True
        bot.edit_message_text(header_7, reply_markup=InlineKeyboardMarkup(keyboard_7), chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return BUTTON
    elif choice == "all":
        global active
        active = False
        bot.edit_message_text(header_7, reply_markup=InlineKeyboardMarkup(keyboard_7), chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return BUTTON

    if choice == "nolimit":
        print "Nolimit"
        global subdomains
        if subdomains:
            global limit
            limit = False
            bot.send_message(text="What is the (top)domain?", chat_id=query.message.chat_id,
                             parse_mode=telegram.ParseMode.MARKDOWN)
            return GET_DOMAINS
        else:
            print "topdomain"
            global limit
            limit = False
            get_topdomains(bot, update)

    elif choice == "limit":
        global subdomains
        print "Limit"
        if subdomains:
            global limit
            limit = True
            bot.send_message(text="What is the (top)domain?", chat_id=query.message.chat_id,
                             parse_mode=telegram.ParseMode.MARKDOWN)
            return GET_DOMAINS
        else:
            print "Topdomain"
            global limit
            limit = True
            get_topdomains(bot, update)

    if choice == "yes_scan":
        bot.send_message(text="Cleaning all Running Process. Starting a new scan...", chat_id=query.message.chat_id,
                         parse_mode=telegram.ParseMode.MARKDOWN)
        os.system("sudo pkill -f run.py")
        os.system("python " + os.path.dirname(os.path.abspath(__file__))  + "/../run.py &")
        keyboard = [[InlineKeyboardButton("Data", callback_data='data-' + str(randint(0, 999))),
                     InlineKeyboardButton("Scans", callback_data='scan-' + str(randint(0, 999)))],
                    [InlineKeyboardButton("✘ Close", callback_data='close-' + str(randint(0, 999)))]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=credentials.telegram_chat_id, text="Hi again!", reply_markup=reply_markup)
        return BUTTON
    elif choice == "back_scan" or choice == "no_scan":
        bot.edit_message_text(header_2, reply_markup=InlineKeyboardMarkup(keyboard_2), chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return BUTTON


    if choice == "all_urls_txt":
        try:
            return get_all_urls_txt(bot, update)
        except Exception as e:
            print e

    if choice == "all_urls":
        try:
            return get_all_urls(bot, update)
        except Exception as e:
            print e
    # os.system("python " + os.path.dirname(os.path.abspath(__file__))  + "/../run.py")
    elif choice == "domain_specific":
        bot.send_message(text="What is the subdomain?", chat_id=query.message.chat_id,
                             parse_mode=telegram.ParseMode.MARKDOWN)
        return GET_DOMAIN_URLS

    if choice == "f_service":
        bot.send_message(text="What is the Service/Port ?", chat_id=query.message.chat_id,
                             parse_mode=telegram.ParseMode.MARKDOWN)
        return GET_SERVICE_DOMAIN
    # os.system("python " + os.path.dirname(os.path.abspath(__file__))  + "/../run.py")
    elif choice == "domain_specific":
        bot.send_message(text="What is the subdomain?", chat_id=query.message.chat_id,
                             parse_mode=telegram.ParseMode.MARKDOWN)
        return GET_NMAP


def get_service(bot, update):
    global active
    global limit
    global choice
    choice = ""
    print "domain: " + update.message.text

    connection = MySQLdb.connect(host=credentials.database_server, user=credentials.database_username,
                                 passwd=credentials.database_password, db=credentials.database_name)
    cursor = connection.cursor()

    cursor.execute(
        "select Domain,Nmap_Result from domains where Nmap_Result like %s", ('%' + update.message.text + '%',))

    data = cursor.fetchall()
    cursor.close()
    connection.close()

    subdomains_message = ""
    try:
        if not data:
            subdomains_message = "No URL Results found for " + str(update.message.text)
        else:
            for row in data:
                subdomains_message += "\n Domain: " + str(row[0])
                subdomains_message += "\n Nmap: " + str(row[1])
        send_message(bot, credentials.telegram_chat_id, subdomains_message)
        keyboard = [[InlineKeyboardButton("Data", callback_data='data-' + str(randint(0, 999))),
                     InlineKeyboardButton("Scans", callback_data='scan-' + str(randint(0, 999)))],
                    [InlineKeyboardButton("✘ Close", callback_data='close-' + str(randint(0, 999)))]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=credentials.telegram_chat_id, text="Hi again!", reply_markup=reply_markup)
        return BUTTON
    except Exception as e:
        send_message(bot, credentials.telegram_chat_id, str(e))
        keyboard = [[InlineKeyboardButton("Data", callback_data='data-' + str(randint(0, 999))),
                     InlineKeyboardButton("Scans", callback_data='scan-' + str(randint(0, 999)))],
                    [InlineKeyboardButton("✘ Close", callback_data='close-' + str(randint(0, 999)))]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=credentials.telegram_chat_id, text="Hi again!", reply_markup=reply_markup)
        return BUTTON

def get_latest_scan(bot, update, cursor):
    cursor.execute("select max(ScanID) from scans where EndDate is not null")
    data = cursor.fetchall()
    if data:
        os.system("python " + os.path.dirname(os.path.abspath(__file__)) + "/notify.py " + str(data[0][0]) + " true")
    else:
        bot.send_message(text="No completed scans found!", chat_id=query.message.chat_id,
                         parse_mode=telegram.ParseMode.MARKDOWN)


def get_custom_scan(bot, update, cursor):
    global choice
    choice = ""
    query = update.callback_query

    cursor.execute("SELECT ScanID FROM scans where EndDate is not null ORDER BY ScanID DESC LIMIT 10")
    data = cursor.fetchall()
    if data:
        latestScanIds = sorted([str(x[0]) for x in data])
        firstRow = latestScanIds[:len(latestScanIds) / 2]
        secondRow = latestScanIds[len(latestScanIds) / 2:]
        custom_keyboard = [firstRow, secondRow]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

        if data:
            bot.send_message(chat_id=query.message.chat_id,
                             text="Which scan ID? \n/cancel to cancel",
                             reply_markup=reply_markup, ForceReply=True)
        else:
            bot.send_message(chat_id=query.message.chat_id,
                             text="Which scan ID? \n/cancel to cancel")


def run_scan(bot, update, cursor):
    global active
    global limit
    global choice
    active = ""
    choice = ""
    limit = ""
    query = update.callback_query
    cursor.execute("SELECT * FROM scans ORDER BY ScanID DESC LIMIT 1")
    data = cursor.fetchall()
    try:
        if all_process.is_scan_running() != True:
            bot.send_message(text="Starting a new scan...", chat_id=query.message.chat_id,
                             parse_mode=telegram.ParseMode.MARKDOWN)
            os.system("python " + os.path.dirname(os.path.abspath(__file__)) + "/../run.py &")
            print "Scanning"
        else:
            r = str(randint(0, 99))
            header_4 = "It looks like a scan is already running. Want to start a new one?"
            keyboard_4 = [[InlineKeyboardButton("Yes", callback_data='yes_scan-' + r),
                           InlineKeyboardButton("No", callback_data='no_scan-' + r)],
                          [InlineKeyboardButton("« Back to scans", callback_data='back_scan-' + r)]]
            bot.edit_message_text(header_4, reply_markup=InlineKeyboardMarkup(keyboard_4),
                                  chat_id=query.message.chat_id, message_id=query.message.message_id)
    except Exception, e:
        print "error: " + str(e)
        bot.send_message(text="Error Ocurred", chat_id=query.message.chat_id,
                         parse_mode=telegram.ParseMode.MARKDOWN)
        keyboard = [[InlineKeyboardButton("Data", callback_data='data-' + str(randint(0, 999))),
                     InlineKeyboardButton("Scans", callback_data='scan-' + str(randint(0, 999)))],
                    [InlineKeyboardButton("✘ Close", callback_data='close-' + str(randint(0, 999)))]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=credentials.telegram_chat_id, text="Hi again!", reply_markup=reply_markup)
        return BUTTON


def custom_scan_id_input(bot, update):
    print "inside input method with data: " + update.message.text
    customId = update.message.text
    try:
        int(customId)
    except ValueError:
        print "invalid number"
        update.message.reply_text("Not a valid number")
    else:
        print "valid number"
        connection = MySQLdb.connect(host=credentials.database_server, user=credentials.database_username,
                                     passwd=credentials.database_password, db=credentials.database_name)
        cursor = connection.cursor()
        cursor.execute("SELECT EndDate FROM scans where scanID = %s", (customId))
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        if data:
            print "scan ID was found in the db"
            print "data[0][0] is: " + str(data[0][0])
            if data[0][0] == None:
                print "EndDate of scan is empty"
                update.message.reply_text("This scan hasn't finished yet")
            else:
                print "Valid scan found"
                reply_markup = telegram.ReplyKeyboardRemove()
                update.message.reply_text("Showing scan from scan " + str(customId), reply_markup=reply_markup)
                os.system(
                    "python " + os.path.dirname(os.path.abspath(__file__)) + "/notify.py " + str(customId) + " true")
                return ConversationHandler.END
        else:
            print "Scan ID not found in db"
            update.message.reply_text("This scan ID doesn't exist")


def add_domain(bot, update):
    print update.message.text
    return BUTTON


def edit_domain(bot, update):
    print update.message.text
    return BUTTON


def get_topdomains(bot, update):
    global limit
    global choice
    choice = ""
    limit = ""

    print "Inside get_topdomains"

    connection = MySQLdb.connect(host=credentials.database_server, user=credentials.database_username,
                                 passwd=credentials.database_password, db=credentials.database_name)
    cursor = connection.cursor()

    if limit == True:
        cursor.execute("select Domain from domains where TopDomainID is NULL order by Domain limit 20")
    else:
        cursor.execute("select Domain from domains where TopDomainID is NULL order by Domain")

    data = cursor.fetchall()
    cursor.close()
    connection.close()

    domains_message = ""

    if not data:
        domains_message = "No domains found"

    for row in data:
        domains_message += "\n" + row[0]

    send_message(bot, credentials.telegram_chat_id, domains_message)
    time.sleep(2)
    keyboard = [[InlineKeyboardButton("Data", callback_data='data-' + str(randint(0, 999))),
                 InlineKeyboardButton("Scans", callback_data='scan-' + str(randint(0, 999)))],
                [InlineKeyboardButton("✘ Close", callback_data='close-' + str(randint(0, 999)))]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=credentials.telegram_chat_id, text="Hi again!", reply_markup=reply_markup)
    return BUTTON


def get_domain_urls(bot, update):
    global active
    global limit
    global choice
    choice = ""
    print "domain: " + update.message.text

    connection = MySQLdb.connect(host=credentials.database_server, user=credentials.database_username,
                                 passwd=credentials.database_password, db=credentials.database_name)
    cursor = connection.cursor()

    cursor.execute(
        "select urls from domains where Active and Domain like %s", ('%' + update.message.text + '%',))

    data = cursor.fetchall()
    cursor.close()
    connection.close()

    subdomains_message = ""
    try:
        if not data:
            subdomains_message = "No URL Results found for " + str(update.message.text)
        else:
            for row in data:
                subdomains_message += "\n" + str(row[0])
        send_message(bot, credentials.telegram_chat_id, subdomains_message)
        time.sleep(2)
        keyboard = [[InlineKeyboardButton("Data", callback_data='data-' + str(randint(0, 999))),
                     InlineKeyboardButton("Scans", callback_data='scan-' + str(randint(0, 999)))],
                    [InlineKeyboardButton("✘ Close", callback_data='close-' + str(randint(0, 999)))]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=credentials.telegram_chat_id, text="Hi again!", reply_markup=reply_markup)
        return BUTTON
    except Exception as e:
        send_message(bot, credentials.telegram_chat_id, str(e))
        keyboard = [[InlineKeyboardButton("Data", callback_data='data-' + str(randint(0, 999))),
                     InlineKeyboardButton("Scans", callback_data='scan-' + str(randint(0, 999)))],
                    [InlineKeyboardButton("✘ Close", callback_data='close-' + str(randint(0, 999)))]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=credentials.telegram_chat_id, text="Hi again!", reply_markup=reply_markup)
        return BUTTON


def get_nmap(bot, update):
    global active
    global limit
    global choice
    choice = ""
    print "domain: " + update.message.text

    connection = MySQLdb.connect(host=credentials.database_server, user=credentials.database_username,
                                 passwd=credentials.database_password, db=credentials.database_name)
    cursor = connection.cursor()

    cursor.execute(
        "select Nmap_Result from domains where Domain = %s and Active", (update.message.text,))

    data = cursor.fetchall()
    cursor.close()
    connection.close()

    subdomains_message = ""
    try:
        if not data:
            subdomains_message = "No Nmap Results found for " + str(update.message.text)
            send_message(bot, credentials.telegram_chat_id, subdomains_message)
        else:
            for row in data:
                subdomains_message += "\n" + str(row[0])
            send_message(bot, credentials.telegram_chat_id, subdomains_message)
        time.sleep()
        keyboard = [[InlineKeyboardButton("Data", callback_data='data-' + str(randint(0, 999))),
                     InlineKeyboardButton("Scans", callback_data='scan-' + str(randint(0, 999)))],
                    [InlineKeyboardButton("✘ Close", callback_data='close-' + str(randint(0, 999)))]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=credentials.telegram_chat_id, text="Hi again!", reply_markup=reply_markup)
        return BUTTON
    except Exception as e:
        send_message(bot, credentials.telegram_chat_id, str(e))
        keyboard = [[InlineKeyboardButton("Data", callback_data='data-' + str(randint(0, 999))),
                     InlineKeyboardButton("Scans", callback_data='scan-' + str(randint(0, 999)))],
                    [InlineKeyboardButton("✘ Close", callback_data='close-' + str(randint(0, 999)))]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=credentials.telegram_chat_id, text="Hi again!", reply_markup=reply_markup)
        return BUTTON

def get_all_urls(bot, update):

    global choice
    choice = ""
    connection = MySQLdb.connect(host=credentials.database_server, user=credentials.database_username,
                                 passwd=credentials.database_password, db=credentials.database_name)
    cursor = connection.cursor()

    cursor.execute(
        "select urls from domains where Active")

    data = cursor.fetchall()
    cursor.close()
    connection.close()

    subdomains_message = ""
    try:
        if not data:
            subdomains_message = "No URL Results found "

        else:
            for row in data:
                subdomains_message += "\n" + str(row[0]).strip()

        send_message(bot, credentials.telegram_chat_id, subdomains_message)
        time.sleep(2)
        keyboard = [[InlineKeyboardButton("Data", callback_data='data-' + str(randint(0, 999))),
                     InlineKeyboardButton("Scans", callback_data='scan-' + str(randint(0, 999)))],
                    [InlineKeyboardButton("✘ Close", callback_data='close-' + str(randint(0, 999)))]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=credentials.telegram_chat_id, text="Hi again!", reply_markup=reply_markup)
        return BUTTON
    except Exception as e:
        send_message(bot, credentials.telegram_chat_id, str(e))
        keyboard = [[InlineKeyboardButton("Data", callback_data='data-' + str(randint(0, 999))),
                     InlineKeyboardButton("Scans", callback_data='scan-' + str(randint(0, 999)))],
                    [InlineKeyboardButton("✘ Close", callback_data='close-' + str(randint(0, 999)))]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=credentials.telegram_chat_id, text="Hi again!", reply_markup=reply_markup)
        return BUTTON


def get_all_urls_txt(bot, update):

    global choice
    choice = ""
    connection = MySQLdb.connect(host=credentials.database_server, user=credentials.database_username,
                                 passwd=credentials.database_password, db=credentials.database_name)
    cursor = connection.cursor()

    cursor.execute(
        "select urls from domains where Active")

    data = cursor.fetchall()
    cursor.close()
    connection.close()

    subdomains_message = ""
    try:
        if not data:
            subdomains_message = "No URL Results found "

        else:
            for row in data:
                if "None" in row:
                    pass
                
                else:
                    subdomains_message += "\n" + str(row[0]).strip()

        document = open('/tmp/temp_domains.txt', 'w')
        for i in subdomains_message:
            document.write(i)
        document.close()
        document = open('/tmp/temp_domains.txt', 'rb')
        bot.sendDocument(chat_id=credentials.telegram_chat_id, document=document)
        document.close()
        time.sleep(2)
        keyboard = [[InlineKeyboardButton("Data", callback_data='data-' + str(randint(0, 999))),
                     InlineKeyboardButton("Scans", callback_data='scan-' + str(randint(0, 999)))],
                    [InlineKeyboardButton("✘ Close", callback_data='close-' + str(randint(0, 999)))]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=credentials.telegram_chat_id, text="Hi again!", reply_markup=reply_markup)
        return BUTTON
    except Exception as e:
        send_message(bot, credentials.telegram_chat_id, str(e))
        keyboard = [[InlineKeyboardButton("Data", callback_data='data-' + str(randint(0, 999))),
                     InlineKeyboardButton("Scans", callback_data='scan-' + str(randint(0, 999)))],
                    [InlineKeyboardButton("✘ Close", callback_data='close-' + str(randint(0, 999)))]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=credentials.telegram_chat_id, text="Hi again!", reply_markup=reply_markup)
        return BUTTON

def get_domains(bot, update):
    global active
    global limit
    global choice 
    choice = ""
    print "active: " + str(active)
    print "limit: " + str(limit)
    print "domain: " + update.message.text

    connection = MySQLdb.connect(host=credentials.database_server, user=credentials.database_username,
                                 passwd=credentials.database_password, db=credentials.database_name)
    cursor = connection.cursor()

    cursor.execute(
        "select Domain, Active from domains where TopDomainID = (select DomainID from domains where Domain = %s) order by Domain",
        (update.message.text,))

    data = cursor.fetchall()
    cursor.close()
    connection.close()

    subdomains_message = ""

    if not data:
        subdomains_message = "No subdomains found for " + str(update.message.text)

    if active == True:
        data = [x for x in data if ord(x[1]) == True]

    if limit == True:
        print "Limit is True if"
        data = data[:20]

    for row in data:
        subdomains_message += "\n" + row[0]

    send_update(update, subdomains_message)

    keyboard = [[InlineKeyboardButton("Data", callback_data='data-' + str(randint(0, 999))),
                 InlineKeyboardButton("Scans", callback_data='scan-' + str(randint(0, 999)))],
                [InlineKeyboardButton("✘  Close", callback_data='close-' + str(randint(0, 999)))]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Hi again :wave:", reply_markup=reply_markup)
    return BUTTON


def domains_contain(bot, update):
    print update.message.text
    return BUTTON


def help(bot, update):
    update.message.reply_text("click /start to start :)")


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def cancel(bot, update):
    print "canceled"
    reply_markup = telegram.ReplyKeyboardRemove()
    update.message.reply_text("canceled! Click or type /start to start again", reply_markup=reply_markup)
    return ConversationHandler.END


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(telegram_bot_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            BUTTON: [CallbackQueryHandler(button),
                     CommandHandler('cancel', cancel)],
            CUSTOM_SCAN_ID_INPUT: [MessageHandler(Filters.text, custom_scan_id_input),
                                   CommandHandler('cancel', cancel)],
            ADD_DOMAIN: [MessageHandler(Filters.text, add_domain),
                         CommandHandler('cancel', cancel)],
            EDIT_DOMAIN: [MessageHandler(Filters.text, edit_domain),
                          CommandHandler('cancel', cancel)],
            GET_DOMAINS: [MessageHandler(Filters.text, get_domains),
                          CommandHandler('cancel', cancel)],
            CONTAINS: [MessageHandler(Filters.text, domains_contain),
                       CommandHandler('cancel', cancel)],
            GET_DOMAIN_URLS: [MessageHandler(Filters.text, get_domain_urls)],
            GET_NMAP: [MessageHandler(Filters.text, get_nmap)],
            GET_SERVICE_DOMAIN: [MessageHandler(Filters.text, get_service)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
