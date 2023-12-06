import telebot
import os
import sys

try:
    KEY = os.environ['TOKEN']
except KeyError:
    sys.stderr.write("KEY envrionment variable not set.\n")
    exit(1)
try:
    CHAT_ID = os.environ['CHAT_ID']
except KeyError:
    sys.stderr.write("CHAT_ID envrionment variable not set.\n")
    exit(1)

bot = telebot.TeleBot(KEY, parse_mode=None)
bot.send_message(CHAT_ID, "Hello Group")
bot.infinity_polling()
