import logging
import os
import psycopg2
from telegram.ext import Updater

# reading token from token file
token_file = '/scripts/bots/Edison42bot_token.txt'
with open(token_file, 'r', encoding='utf-8') as f:
    tok =f.readline()

updater = Updater(token=tok)
dispatcher = updater.dispatcher

# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

start_text = "Hello I am Edison\n\
I can help find weather data\n\n\
Please use the following commands:\n\n\
/pcrp - for precipitation data"

def start(bot, update):
   bot.sendMessage(chat_id=update.message.chat_id, text=start_text)
   
from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
updater.start_polling()

 def prcp(bot, update, args):
    arg_list = args
	arg_len = len(args)
	if arg_len == 3:
		data_text = prcp_srch_3(arg_list[0], arg_list[1], arg_list[2])
    bot.sendMessage(chat_id=update.message.chat_id, text=data_text)

prcp_handler = CommandHandler('prcp', prcp, pass_args=True)
dispatcher.add_handler(prcp_handler)


def prcp_srch_3(pt_id, std, etd):
	conn = psycopg2.connect("dbname='fato'")
	cur = conn.cursor()
	cur.execute("select date||': '||mean as output from cpc_glb_dly_prec.data \
	where pt_id = {pt_id} and date >= '{std}' and date <= '{etd} order by date'".format(
	pt_id=int(pt_id), std=std, etd=etd))
	db_out = cur.fetchall()
	out_text = ""
	for i in db_out:
		dt = i[0]
		out_text = out_text + dt + '\n'
	return out_text
	

	
	