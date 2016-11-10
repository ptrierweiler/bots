#!/usr/bin/python3
import logging
import os
import psycopg2
from telegram.ext import Updater
import telegram
from datetime import datetime, timedelta
import calendar

# reading token from token file
token_file = '/scripts/bots/Edison42bot_token.txt'
with open(token_file, 'r', encoding='utf-8') as f:
    tok = f.readline()

# bot password
pass_file = '/scripts/bots/bot_pass.txt'
with open(pass_file, 'r', encoding='utf-8') as f:
    bot_pass = f.readline()

updater = Updater(token=tok)
dispatcher = updater.dispatcher

def text_loader(text):
    path = "/scripts/bots/texts/"
    textpath = path + text
    with open(textpath, 'r', encoding='utf-8') as f:
        out_text = f.read()
    return(out_text)
	
# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

#start_text = "Hello I am Edison\n\
#I can help find weather data\n\n\
#Please use the following commands:\n\n\
#/help - for help\n\
#/pcrp - for precipitation data"

start_text = text_loader("start.txt")
help_text = text_loader("help.txt")

def start(bot, update):
   bot.sendMessage(chat_id=update.message.chat_id, text=start_text)

def help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=help_text)
    
   
from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', help)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
updater.start_polling()

def prcp(bot, update, args):
    arg_list = args
    arg_len = len(args)
    if arg_len == 3:
        data_text = prcp_srch_3(arg_list[0], arg_list[1], arg_list[2])
    elif arg_len == 2:
        data_text = prcp_srch_2(arg_list[0], arg_list[1])
    bot.sendMessage(chat_id=update.message.chat_id, text=data_text,parse_mode=telegram.ParseMode.MARKDOWN)

mon_list = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    
def prcp_srch_3(pt_id, val1, val2):
	# converting date strings to python datetime 
    if val1.lower()in mon_list:
        mon_num = datetime.strptime(val1,'%b').month
        end_day = calendar.monthrange(int(val2), mon_num)[1]
        std = "{}-{}-{}".format(val2, str(mon_num).zfill(2), '01')
        etd = "{}-{}-{}".format(val2, str(mon_num).zfill(2), end_day)
        pyd_std = datetime.strptime(std, '%Y-%m-%d')
        pyd_etd = datetime.strptime(etd, '%Y-%m-%d') 
    else:            
        pyd_std = datetime.strptime(val1, '%Y-%m-%d')
        pyd_etd = datetime.strptime(val2, '%Y-%m-%d')
    conn = psycopg2.connect("dbname='tlaloc' host='localhost' user='bot' password='{pas}'".format(pas=bot_pass))
    cur = conn.cursor()
    cur.execute("select date, mean, median as output from cpc_glb_dly_prec.data \
    where pt_id = {pt_id} and date >= '{std}' and date <= '{etd}' order by date".format(
    pt_id=int(pt_id), std=pyd_std, etd=pyd_etd))
    db_out = cur.fetchall()
    out_text = "\t date mean median\n"
    for i in db_out:
        dt = i[0]
        mn = i[1]
        md = i[2]
        out_text = out_text + "{dt}: {mn} : {md}\n".format(dt=dt, mn=mn, md=md)
    cur.close()
    conn.close()
    return out_text

    
def prcp_srch_2(pt_id,var):
    conn = psycopg2.connect("dbname='tlaloc' host='localhost' user='bot' password='{pas}'".format(pas=bot_pass))
    cur = conn.cursor()
    cur.execute("select date, mean, median as output from cpc_glb_dly_prec.data \
    where pt_id = {pt_id} and date in (select max(date) from cpc_glb_dly_prec.data) order by date".format(
    pt_id=int(pt_id)))
    max_val = cur.fetchall()
    if var == 'now':
        out_text = "\t date mean median\n"
        for i in max_val:
            dt = i[0]
            mn = i[1]
            md = i[2]
            out_text = out_text + "{dt}: {mn} : {md}\n".format(dt=dt, mn=mn, md=md)
    else:
        max_date = max_val[0][0]
        str_date = max_date - timedelta(int(var))
        cur.execute("select date, mean, median as output from cpc_glb_dly_prec.data \
        where pt_id = {pt_id} and date >= '{std}' and date <= '{etd}' order by date".format(
        pt_id=int(pt_id), std=str_date, etd=max_date))
        db_out = cur.fetchall()
        out_text = "\t date mean median\n"
        for i in db_out:
            dt = i[0]
            mn = i[1]
            md = i[2]
            out_text = out_text + "{dt}: {mn} : {md}\n".format(dt=dt, mn=mn, md=md)
    cur.close()
    conn.close()
    
    return out_text

def prcp_chart(sql_out,geo):
    date = []
    mean = []
    med = []
    for i in sql_out:
        date.append(i[0])
        mean.append(i[1])
        med.append(i[2])
    # g dummy dates
    date.insert(0,min(date) - timedelta(1))
    date.insert(len(date)+ 1, max(date) + timedelta(1))
    # adding dummy values
    mean.insert(0,None)
    mean.insert(len(med + 1),None)
    plt.plot_date(pydates, mean, fmt='bo', tz=None, xdate=True)
    plt.xticks(pydates)
    plt.xticks(rotation=80)
    plt.tight_layout()
    plt.ylabel('PRCP mm')
    plt.xlabel('Dates')

prcp_handler = CommandHandler('prcp', prcp, pass_args=True)
dispatcher.add_handler(prcp_handler)