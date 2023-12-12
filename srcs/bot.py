from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
import logging
import os
import sys

try:
    TOKEN = os.environ['TOKEN']
except KeyError:
    sys.stderr.write("TOKEN envrionment variable not set.\n")
    exit(1)
try:
    CHAT_ID = os.environ['CHAT_ID']
except KeyError:
    sys.stderr.write("CHAT_ID envrionment variable not set.\n")
    exit(1)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def check_nodes(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHAT_ID, text='Checking nodes')


async def update_node(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHAT_ID, text='updating node info')


async def add_node(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHAT_ID, text='adding node')


async def del_node(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHAT_ID, text='deleting node')


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHAT_ID, text='help message')

application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler('update', update_node))
application.add_handler(CommandHandler('add', add_node))
application.add_handler(CommandHandler('delete', del_node))
application.add_handler(CommandHandler('help', help))

job_queue = application.job_queue
job_queue.run_repeating(check_nodes, interval=3, first=10)

application.run_polling()
